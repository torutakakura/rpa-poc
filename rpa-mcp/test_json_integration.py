#!/usr/bin/env python
"""RPA MCPツールのテストスクリプト - JSONテンプレート統合テスト"""

import json
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from main import create_rpa_step_from_template

# テスト1: アプリ起動
print("=== テスト1: アプリ起動 ===")
result = create_rpa_step_from_template(
    category="A_アプリ・画面",
    operation="起動",
    params={"app_path": "メモ帳"},
    subcategory="アプリ",
    step_id="step-001",
    description="メモ帳を起動"
)
print(json.dumps(result, ensure_ascii=False, indent=2))

# テスト2: 待機
print("\n=== テスト2: 待機 ===")
result = create_rpa_step_from_template(
    category="B_待機・終了・エラー",
    operation="秒",
    params={"wait_seconds": 2},
    step_id="step-002",
    description="2秒待機"
)
print(json.dumps(result, ensure_ascii=False, indent=2))

# テスト3: キーボード入力
print("\n=== テスト3: キーボード入力 ===")
result = create_rpa_step_from_template(
    category="D_キーボード",
    operation="文字",
    params={"text": "Hello, RPA World!"},
    subcategory="入力",
    step_id="step-003",
    description="テキストを入力"
)
print(json.dumps(result, ensure_ascii=False, indent=2))

# テスト4: ショートカットキー
print("\n=== テスト4: ショートカットキー ===")
result = create_rpa_step_from_template(
    category="D_キーボード",
    operation="ショートカットキー",
    params={"keys": ["Enter"], "hold_duration": 0},
    subcategory="入力",
    step_id="step-004",
    description="Enterキーを押す"
)
print(json.dumps(result, ensure_ascii=False, indent=2))

# テスト5: ブラウザ操作
print("\n=== テスト5: ブラウザ操作 ===")
result = create_rpa_step_from_template(
    category="L_ウェブブラウザ",
    operation="ブラウザを開く",
    params={
        "url": "https://www.google.com",
        "browser": "chrome",
        "incognito": False,
        "maximize": True
    },
    step_id="step-005",
    description="https://www.google.comを開く"
)
print(json.dumps(result, ensure_ascii=False, indent=2))

# ワークフロー例
print("\n=== ワークフロー例（JSONテンプレート使用） ===")
workflow = {
    "name": "テストワークフロー",
    "description": "rpa_operations.jsonテンプレートを使用したRPAワークフロー",
    "version": "1.0.0",
    "steps": [
        create_rpa_step_from_template(
            category="A_アプリ・画面",
            operation="起動",
            params={"app_path": "メモ帳"},
            subcategory="アプリ",
            step_id="step-001",
            description="メモ帳を起動"
        ),
        create_rpa_step_from_template(
            category="B_待機・終了・エラー",
            operation="秒",
            params={"wait_seconds": 2},
            step_id="step-002",
            description="2秒待機"
        ),
        create_rpa_step_from_template(
            category="D_キーボード",
            operation="文字",
            params={"text": "Hello, RPA World!"},
            subcategory="入力",
            step_id="step-003",
            description="テキストを入力"
        ),
        create_rpa_step_from_template(
            category="D_キーボード",
            operation="ショートカットキー",
            params={"keys": ["Enter"]},
            subcategory="入力",
            step_id="step-004",
            description="Enterキーを押す"
        ),
        create_rpa_step_from_template(
            category="D_キーボード",
            operation="文字",
            params={"text": "これはRPAのテストです。"},
            subcategory="入力",
            step_id="step-005",
            description="追加テキストを入力"
        )
    ]
}

print(json.dumps(workflow, ensure_ascii=False, indent=2))

# テンプレートのデフォルト値の確認
print("\n=== テンプレートのデフォルト値確認 ===")
result = create_rpa_step_from_template(
    category="A_アプリ・画面",
    operation="起動",
    params={"app_path": "notepad.exe"},  # 最小限のパラメータ
    subcategory="アプリ",
    step_id="step-006"
)
print("最小限のパラメータでのアプリ起動:")
print(json.dumps(result, ensure_ascii=False, indent=2))