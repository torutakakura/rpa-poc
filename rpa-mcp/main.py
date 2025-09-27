#!/usr/bin/env python3
"""Expose generated_step_list.json entries as FastMCP tools."""

from __future__ import annotations

import copy
import json
import keyword
import re
from pathlib import Path
from typing import Any, Dict

from fastmcp import FastMCP

STEP_LIST_PATH = Path(__file__).parent / "generated_step_list.json"
_IDENTIFIER_PATTERN = re.compile(r"[^0-9a-zA-Z_]+")


def _to_identifier(raw: str, *, prefix: str) -> str:
    sanitized = _IDENTIFIER_PATTERN.sub("_", raw)
    sanitized = sanitized.strip("_")
    if not sanitized:
        sanitized = prefix
    sanitized = sanitized.lower()
    if sanitized[0].isdigit():
        sanitized = f"{prefix}_{sanitized}"
    if keyword.iskeyword(sanitized):
        sanitized = f"{sanitized}_"
    return sanitized


def _unique_name(base: str, existing: set[str]) -> str:
    candidate = base
    suffix = 2
    while candidate in existing:
        candidate = f"{base}_{suffix}"
        suffix += 1
    existing.add(candidate)
    return candidate


def _annotation_for_value(value: Any) -> Any:
    if value is None:
        return Any
    value_type = type(value)
    if value_type in (bool, int, float, str, list, dict):
        return value_type
    return Any


def _load_sequence() -> list[dict[str, Any]]:
    if not STEP_LIST_PATH.exists():
        raise FileNotFoundError(f"{STEP_LIST_PATH} not found")
    with STEP_LIST_PATH.open("r", encoding="utf-8") as source:
        payload = json.load(source)
    sequence = payload.get("sequence", [])
    if not isinstance(sequence, list):
        raise ValueError("'sequence' entry in generated_step_list.json must be a list")
    return sequence


def _build_step_result(index: int, param_map: dict[str, str], provided: dict[str, Any]) -> dict[str, Any]:
    sequence = _load_sequence()
    if index >= len(sequence):
        raise IndexError(
            f"Step index {index} out of range for sequence of length {len(sequence)}"
        )
    step_template = copy.deepcopy(sequence[index])
    parameters = copy.deepcopy(step_template.get("parameters", {}))
    for param_name, original_name in param_map.items():
        if param_name in provided:
            parameters[original_name] = provided[param_name]
    step_template["parameters"] = parameters
    return step_template


mcp = FastMCP("RPA Operations Tool")
_initial_sequence = _load_sequence()
_tool_name_bases: set[str] = set()
_registered_tool_names: list[str] = []

for index, step in enumerate(_initial_sequence):
    parameters = step.get("parameters", {}) or {}
    used_param_names: set[str] = set()
    param_map: dict[str, str] = {}
    param_defs: list[str] = []
    param_annotations: dict[str, Any] = {}

    for original_name, default_value in parameters.items():
        param_base = _to_identifier(original_name, prefix="param")
        param_name = _unique_name(param_base, used_param_names)
        param_map[param_name] = original_name
        param_defs.append(f"{param_name}={repr(default_value)}")
        param_annotations[param_name] = _annotation_for_value(default_value)

    params_signature = ", ".join(param_defs)
    function_base = _to_identifier(step.get("cmd", f"step_{index}"), prefix="step")
    function_name = f"step_{index:03d}_{function_base}"
    param_map_literal = repr(param_map)

    if params_signature:
        function_source = (
            f"def {function_name}({params_signature}):\n"
            f"    return _build_step_result({index}, {param_map_literal}, locals())\n"
        )
    else:
        function_source = (
            f"def {function_name}():\n"
            f"    return _build_step_result({index}, {param_map_literal}, locals())\n"
        )

    namespace: dict[str, Any] = {}
    exec(function_source, {"_build_step_result": _build_step_result}, namespace)
    tool_function = namespace[function_name]

    docstring = step.get("description") or step.get("cmd-nickname") or step.get("cmd")
    if docstring:
        tool_function.__doc__ = docstring

    annotations = {name: annotation for name, annotation in param_annotations.items()}
    annotations["return"] = Dict[str, Any]
    tool_function.__annotations__ = annotations

    tool_base = _to_identifier(step.get("cmd", f"tool_{index}"), prefix="tool")
    tool_name_base = _unique_name(tool_base, _tool_name_bases)
    tool_name = f"{index + 1:03d}_{tool_name_base}"

    tags = step.get("tags") or []
    decorated_tool = mcp.tool(
        name=tool_name,
        title=step.get("cmd-nickname") or None,
        description=step.get("description") or None,
        tags=set(tags) if tags else None,
    )(tool_function)

    globals()[function_name] = decorated_tool
    _registered_tool_names.append(tool_name)

if len(_registered_tool_names) != len(_initial_sequence):
    raise RuntimeError("Failed to register all tools from generated_step_list.json")


if __name__ == "__main__":
    import sys
    if "--http" in sys.argv:
        mcp.run(transport="http", port=8080)
    else:
        mcp.run(transport="stdio")