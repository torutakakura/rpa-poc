"""MCP (Model Context Protocol) utilities."""
import json
import ast
import re
import unicodedata
import difflib
from typing import List, Dict, Any, Tuple, Optional
from functools import lru_cache
from collections import defaultdict
from pathlib import Path
from fastapi import HTTPException
from langchain_openai import ChatOpenAI
from deepmcpagent import HTTPServerSpec, FastMCPMulti, MCPToolLoader

from config import MCP_SERVER_URL, STEP_SCHEMA_DOC, STEP_LIST_PATH, MCP_MAIN_PATH


# Manual command-to-tool mapping (override automatic mapping)
MANUAL_CMD_TOOL_MAP: Dict[str, Optional[str]] = {}


def _normalize_text(value: str) -> str:
    """Normalize text for comparison."""
    if not value:
        return ""
    text = unicodedata.normalize("NFKC", value)
    replacements = ["／", "·", "・"]
    for rep in replacements:
        text = text.replace(rep, "")
    for ch in "（）()　 ,:：-_/\\":
        text = text.replace(ch, "")
    return text


@lru_cache(maxsize=1)
def get_step_tool_mappings() -> Tuple[Dict[str, Optional[str]], Dict[str, Dict[str, Any]]]:
    """Return mapping from step command id to MCP tool name (if available)."""

    cmd_nickname_map: Dict[str, str] = {}
    if STEP_LIST_PATH.exists():
        try:
            data = json.loads(STEP_LIST_PATH.read_text(encoding="utf-8"))
            for step in data.get("sequence", []):
                cmd = step.get("cmd")
                nickname = step.get("cmd-nickname")
                if cmd:
                    cmd_nickname_map[cmd] = nickname or ""
        except Exception:
            pass

    # Map commands to categories using documentation
    cmd_category_map: Dict[str, Optional[str]] = {}
    if STEP_SCHEMA_DOC.exists():
        category_letter_map: Dict[str, str] = {}
        try:
            for line in STEP_SCHEMA_DOC.read_text(encoding="utf-8").splitlines():
                section = line.strip()
                header_match = re.match(r"##\s+([A-Z])\.\s+(.+)", section)
                if header_match:
                    letter, title = header_match.groups()
                    category_letter_map[letter] = f"{letter}_" + title
                    continue
                detail_match = re.match(r"####\s+([A-Z])-\d+\s+.+?\s+\(`([^`]+)`\)", section)
                if detail_match:
                    letter, cmd = detail_match.groups()
                    category = category_letter_map.get(letter)
                    cmd_category_map[cmd] = category
        except Exception:
            pass

    # Build tool name candidates from MCP definitions
    category_tool_entries: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    if MCP_MAIN_PATH.exists():
        try:
            module_ast = ast.parse(MCP_MAIN_PATH.read_text(encoding="utf-8"))
            for node in module_ast.body:
                if not isinstance(node, ast.FunctionDef):
                    continue
                if not any(
                    isinstance(dec, ast.Call) and getattr(dec.func, "attr", None) == "tool"
                    for dec in getattr(node, "decorator_list", [])
                ):
                    continue
                tool_name = node.name
                category = None
                operation = None
                subcategory = None
                for stmt in ast.walk(node):
                    if not isinstance(stmt, ast.Call):
                        continue
                    func = getattr(stmt, "func", None)
                    if isinstance(func, ast.Name) and func.id in {"create_rpa_step_from_template", "create_rpa_step"}:
                        for kw in stmt.keywords:
                            if kw.arg == "category" and isinstance(kw.value, ast.Constant):
                                category = kw.value.value
                            if kw.arg == "operation" and isinstance(kw.value, ast.Constant):
                                operation = kw.value.value
                            if kw.arg == "subcategory" and isinstance(kw.value, ast.Constant):
                                subcategory = kw.value.value
                        break
                if not category or not operation:
                    continue
                name_candidates = {operation}
                if subcategory:
                    name_candidates.add(f"{subcategory}{operation}")
                category_tool_entries[category].append(
                    {
                        "tool": tool_name,
                        "candidates": list(name_candidates),
                    }
                )
        except Exception:
            pass

    cmd_tool_map: Dict[str, Optional[str]] = {}
    metadata: Dict[str, Dict[str, Any]] = {}
    for cmd, nickname in cmd_nickname_map.items():
        category = cmd_category_map.get(cmd)
        auto_tool = None
        auto_score = 0.0
        auto_name = None
        if category and category_tool_entries.get(category):
            target = _normalize_text(nickname)
            for entry in category_tool_entries[category]:
                for candidate_name in entry["candidates"]:
                    score = difflib.SequenceMatcher(
                        None, target, _normalize_text(candidate_name)
                    ).ratio()
                    if score > auto_score:
                        auto_score = score
                        auto_tool = entry["tool"]
                        auto_name = candidate_name
        manual_value = MANUAL_CMD_TOOL_MAP.get(cmd, ...)
        if manual_value is ...:
            final_tool = auto_tool if auto_tool and auto_score >= 0.6 else None
            source = "auto" if final_tool else "none"
        else:
            final_tool = manual_value
            source = "manual"
        cmd_tool_map[cmd] = final_tool
        metadata[cmd] = {
            "category": category,
            "nickname": nickname,
            "source": source,
            "auto_tool": auto_tool,
            "auto_name": auto_name,
            "auto_score": auto_score,
            "tool": final_tool,
        }

    # Include commands that appear in manual map but not in generated list
    for cmd, manual_value in MANUAL_CMD_TOOL_MAP.items():
        if cmd in cmd_tool_map:
            continue
        cmd_tool_map[cmd] = manual_value
        metadata[cmd] = {
            "category": cmd_category_map.get(cmd),
            "nickname": cmd_nickname_map.get(cmd, ""),
            "source": "manual",
            "auto_tool": None,
            "auto_name": None,
            "auto_score": 0.0,
            "tool": manual_value,
        }

    return cmd_tool_map, metadata


def _safe_json(value: Any) -> Any:
    """Safely convert value to JSON-serializable format."""
    if isinstance(value, (dict, list, str, int, float, bool)) or value is None:
        return value
    try:
        json_str = json.dumps(value, ensure_ascii=False)
        return json.loads(json_str)
    except Exception:
        return repr(value)


async def initialize_filtered_agent(
    tool_names: List[str],
    instructions: str,
    model: ChatOpenAI,
    *,
    trace_tools: bool = True,
) -> Tuple[Any, List[str], List[Dict[str, Any]], List[str], List[Dict[str, Any]]]:
    """Build a DeepMCP agent limited to the specified tool names."""

    if not MCP_SERVER_URL:
        raise HTTPException(status_code=500, detail="MCP server URL is not configured")

    tool_call_log: List[Dict[str, Any]] = []

    def _on_before(name: str, kwargs: Dict[str, Any]) -> None:
        entry = {"tool": name, "input": _safe_json(kwargs), "status": "running"}
        tool_call_log.append(entry)

    def _on_after(name: str, result: Any) -> None:
        if tool_call_log and tool_call_log[-1].get("tool") == name and tool_call_log[-1].get("status") == "running":
            tool_call_log[-1]["status"] = "succeeded"
            tool_call_log[-1]["output"] = _safe_json(result)
        else:
            tool_call_log.append(
                {"tool": name, "status": "succeeded", "output": _safe_json(result)}
            )

    def _on_error(name: str, error: Exception) -> None:
        tool_call_log.append(
            {"tool": name, "status": "error", "error": repr(error)}
        )

    servers = {
        "rpa": HTTPServerSpec(
            url=MCP_SERVER_URL,
            transport="http",
        )
    }

    loader = MCPToolLoader(
        FastMCPMulti(servers),
        on_before=_on_before if trace_tools else None,
        on_after=_on_after if trace_tools else None,
        on_error=_on_error if trace_tools else None,
    )

    try:
        discovered_tools = await loader.get_all_tools()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load MCP tools: {exc}") from exc

    tool_map = {tool.name: tool for tool in discovered_tools}
    requested_unique: List[str] = []
    seen_names: set[str] = set()
    for name in tool_names:
        if name and name not in seen_names:
            requested_unique.append(name)
            seen_names.add(name)
    available_tool_objects = [tool_map[name] for name in requested_unique if name in tool_map]
    missing_tools = [name for name in requested_unique if name not in tool_map]

    if not available_tool_objects:
        raise HTTPException(
            status_code=422,
            detail="No matching MCP tools are available for the selected candidate steps",
        )

    # Import here to avoid circular dependency
    from langgraph.prebuilt import create_react_agent

    agent = create_react_agent(
        model=model,
        tools=available_tool_objects,
        state_modifier=instructions,
    )

    tool_info_dicts: List[Dict[str, Any]] = []
    try:
        infos = await loader.list_tool_info()
    except Exception:
        infos = []
    info_map = {info.name: info for info in infos}
    for name in requested_unique:
        info = info_map.get(name)
        if not info:
            continue
        tool_info_dicts.append(
            {
                "name": info.name,
                "description": info.description,
                "input_schema": info.input_schema,
                "server": info.server_guess,
            }
        )

    return (
        agent,
        [tool.name for tool in available_tool_objects],
        tool_info_dicts,
        missing_tools,
        tool_call_log,
    )


def parse_agent_workflow_response(response: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    """Parse agent response and extract workflow JSON."""
    messages = response.get("messages", []) if isinstance(response, dict) else []
    if not messages:
        raise HTTPException(status_code=500, detail="Agent returned no messages")

    last_message = messages[-1]
    if hasattr(last_message, "content"):
        content = last_message.content
    elif isinstance(last_message, dict):
        content = last_message.get("content", "")
    else:
        content = str(last_message)

    default_workflow = {
        "name": "Generated RPA Workflow",
        "description": "ユーザー要件に基づいて生成されたワークフロー",
        "version": "1.0.0",
        "steps": [],
    }

    try:
        json_pattern = r"```json\s*(.*?)\s*```"
        matches = re.findall(json_pattern, content, re.DOTALL)
        workflow_data: Dict[str, Any]
        if matches:
            workflow_data = json.loads(matches[0])
        else:
            workflow_data = json.loads(content)
    except Exception:
        raise HTTPException(status_code=500, detail="Agent response was not valid JSON")

    workflow = {
        "name": workflow_data.get("name", default_workflow["name"]),
        "description": workflow_data.get("description", default_workflow["description"]),
        "version": workflow_data.get("version", "1.0.0"),
        "steps": workflow_data.get("steps", []) or [],
    }
    return workflow, content


def format_workflow_steps(workflow: Dict[str, Any], max_steps: Optional[int] = None) -> Dict[str, Any]:
    """Format workflow steps with sequential IDs."""
    steps = workflow.get("steps") or []
    if not isinstance(steps, list):
        steps = []
    if max_steps is not None:
        steps = steps[:max_steps]
    formatted: List[Dict[str, Any]] = []
    for index, step in enumerate(steps, start=1):
        step_dict = dict(step or {})
        step_dict["id"] = f"step-{index:03d}"
        formatted.append(step_dict)
    workflow["steps"] = formatted
    return workflow

