#!/usr/bin/env python3
"""Mapping between cmd values and MCP tool names."""

import json
from pathlib import Path
from typing import Dict, List, Optional


def get_cmd_to_tool_mapping() -> Dict[str, str]:
    """
    generated_step_list.jsonのcmd値からMCPツール名へのマッピングを生成

    Returns:
        Dict[str, str]: cmd -> MCPツール名のマッピング
    """
    # generated_step_list.jsonのパスを見つける
    current_dir = Path(__file__).parent
    step_list_path = current_dir.parent / "rpa-mcp" / "generated_step_list.json"

    if not step_list_path.exists():
        # 別の場所を試す
        step_list_path = current_dir / "generated_step_list.json"

    if not step_list_path.exists():
        raise FileNotFoundError(f"generated_step_list.json not found at {step_list_path}")

    # JSONを読み込み
    with open(step_list_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # マッピングを生成
    mapping = {}
    sequence = data.get('sequence', [])

    for i, step in enumerate(sequence):
        cmd = step.get('cmd')
        if cmd:
            # MCPツール名は "001_run_executable" のような形式
            # cmdの"-"を"_"に変換
            tool_name = f"{i+1:03d}_{cmd.replace('-', '_')}"
            mapping[cmd] = tool_name

    return mapping


def convert_cmd_list_to_tool_names(cmd_list: List[str]) -> List[str]:
    """
    cmdのリストをMCPツール名のリストに変換

    Args:
        cmd_list: cmdのリスト（例: ["run_executable", "pause"]）

    Returns:
        List[str]: MCPツール名のリスト（例: ["001_run_executable", "003_pause"]）
    """
    mapping = get_cmd_to_tool_mapping()
    tool_names = []

    for cmd in cmd_list:
        # ハイフンとアンダースコアの両方を試す
        if cmd in mapping:
            tool_names.append(mapping[cmd])
        elif cmd.replace('_', '-') in mapping:
            tool_names.append(mapping[cmd.replace('_', '-')])
        elif cmd.replace('-', '_') in mapping:
            tool_names.append(mapping[cmd.replace('-', '_')])
        else:
            # マッピングが見つからない場合は警告を出すがスキップ
            print(f"⚠️ Warning: No mapping found for cmd: {cmd}")

    return tool_names


def get_tool_name_for_cmd(cmd: str) -> Optional[str]:
    """
    単一のcmdに対応するMCPツール名を取得

    Args:
        cmd: cmd値（例: "run_executable"）

    Returns:
        Optional[str]: MCPツール名、見つからない場合はNone
    """
    mapping = get_cmd_to_tool_mapping()

    # ハイフンとアンダースコアの両方を試す
    if cmd in mapping:
        return mapping[cmd]
    elif cmd.replace('_', '-') in mapping:
        return mapping[cmd.replace('_', '-')]
    elif cmd.replace('-', '_') in mapping:
        return mapping[cmd.replace('-', '_')]

    return None


if __name__ == "__main__":
    # テスト用
    mapping = get_cmd_to_tool_mapping()
    print(f"Total mappings: {len(mapping)}")
    print("\nFirst 10 mappings:")
    for i, (cmd, tool) in enumerate(list(mapping.items())[:10]):
        print(f"  {cmd} → {tool}")

    # 変換テスト
    test_cmds = ["run_executable", "pause", "click_mouse", "invalid_cmd"]
    print(f"\nTest conversion: {test_cmds}")
    print(f"Result: {convert_cmd_list_to_tool_names(test_cmds)}")