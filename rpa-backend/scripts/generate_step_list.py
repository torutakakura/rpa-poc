#!/usr/bin/env python3
"""
RPAステップリストJSONを生成するスクリプト
"""
import json
from pathlib import Path
from datetime import datetime
import sys

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from schema.step_factory import StepFactory  # noqa: E402
from schema.step_descriptions import get_description  # noqa: E402
from schema.step_tags import get_tags  # noqa: E402


class StepListGenerator:
    """ステップリストを生成するクラス"""

    def __init__(self):
        self.factory = StepFactory()
        
    def _normalize_cmd_case(self, step: dict) -> dict:
        """cmdをスネークケースに正規化し、ネストしたsequenceも再帰的に変換"""
        if not isinstance(step, dict):
            return step
        
        def snake_cmd(value: str) -> str:
            return (value or '').replace('-', '_')
        
        normalized = dict(step)
        if 'cmd' in normalized:
            normalized['cmd'] = snake_cmd(normalized['cmd'])
        
        # ネストしたシーケンスを再帰的に正規化
        for key in ['sequence', 'sequence-0', 'sequence-1']:
            if key in normalized and isinstance(normalized[key], list):
                normalized[key] = [self._normalize_cmd_case(s) for s in normalized[key]]
        
        return normalized

    def create_all_steps(self):
        """全177個のステップ定義を生成"""
        steps = []

        # 基本操作
        steps.extend(self._create_basic_steps())

        # ウィンドウ操作
        steps.extend(self._create_window_steps())

        # マウス操作
        steps.extend(self._create_mouse_steps())

        # キーボード操作
        steps.extend(self._create_keyboard_steps())

        # 変数操作
        steps.extend(self._create_variable_steps())

        # Excel操作とファイル操作は_create_other_stepsで元のJSONから読み込むため
        # ここではコメントアウト
        # steps.extend(self._create_excel_steps())
        # steps.extend(self._create_file_steps())

        # 分岐・ループ・エラー処理
        steps.extend(self._create_control_flow_steps())

        # その他の操作
        steps.extend(self._create_other_steps())

        return steps

    def _create_basic_steps(self):
        """基本操作ステップを生成"""
        steps = []

        # 各ステップの定義
        step_configs = [
            ("run_executable", "アプリ起動", 3,
             {"path": "", "arguments": "", "interval": 3, "maximized": True}),
            ("run_executable_and_wait", "アプリ起動（終了待ち）", 1,
             {"path": "", "arguments": "", "timeout": 300,
              "output-variable": "", "error-variable": ""}),
            ("pause", "待機（秒）", 1, {"interval": "3"}),
            ("pause_and_ask_to_proceed", "続行確認", 2, {"string": ""}),
            ("pause_and_countdown_to_proceed", "タイマー付き続行確認", 2,
             {"interval": "3", "string": ""}),
            ("change_speed_for_command_execution", "コマンド間の待機時間を変更", 1,
             {"interval": 0.2}),
            ("abort", "作業強制終了", 2, {"result-type": "abort"}),
            ("raise_error", "エラーを発生させる", 1, {"string": ""}),
            ("take_screenshot", "スクリーンショットを撮る", 1,
             {"dir-path": "", "file-name": "", "area": "area-whole",
              "variable": "", "timestamp": False, "extension": "png"}),
        ]

        for cmd, nickname, version, params in step_configs:
            steps.append(
                self.factory.create_basic_step(
                    cmd, nickname, version, params,
                    description=get_description(cmd),
                    tags=get_tags(cmd)
                )
            )

        return steps

    def _create_window_steps(self):
        """ウィンドウ操作ステップを生成"""
        steps = []

        step_configs = [
            ("remember_focused_window", "最前面画面を覚える", 1,
             {"variable": "ウィンドウ"}),
            ("remember_named_window", "画面を覚える（名前）", 1,
             {"match-type": "contains", "window-name": "ウィンドウ", "variable": "ウィンドウ"}),
            ("focus_window", "最前面画面切り替え", 1, {"variable": ""}),
            ("focus_window_by_name", "画面切り替え（名前）", 1, {"string": ""}),
            ("get_window_title", "画面の名前を取得", 1,
             {"window": "__focused_window__", "variable": "ウィンドウ名"}),
            ("align_focused_window", "ウィンドウを移動", 1, {"alignment": "left"}),
            ("maximize_focused_window", "ウィンドウ最大化／最小化", 2,
             {"behavior": "maximize"}),
        ]

        for cmd, nickname, version, params in step_configs:
            steps.append(
                self.factory.create_basic_step(
                    cmd, nickname, version, params,
                    description=get_description(cmd),
                    tags=get_tags(cmd)
                )
            )

        return steps

    def _create_mouse_steps(self):
        """マウス操作ステップを生成"""
        steps = [
            self.factory.create_basic_step(
                "move_mouse_to_absolute_coordinates", "マウス移動（座標）", 2,
                {"x": "100", "y": "100", "click": "single"},
                description=get_description("move_mouse_to_absolute_coordinates"),
                tags=get_tags("move_mouse_to_absolute_coordinates")
            ),
            self.factory.create_basic_step(
                "move_mouse_to_relative_coordinates", "マウス移動（距離）", 2,
                {"x": "100", "y": "100", "click": "single"},
                description=get_description("move_mouse_to_relative_coordinates"),
                tags=get_tags("move_mouse_to_relative_coordinates")
            ),
            self.factory.create_basic_step(
                "click_mouse", "マウスクリック", 1,
                {"type": "single", "key": "__null__"},
                description=get_description("click_mouse"),
                tags=get_tags("click_mouse")
            ),
            self.factory.create_basic_step(
                "scroll_mouse", "マウススクロール", 1,
                {"direction": "up", "amount": 3},
                description=get_description("scroll_mouse"),
                tags=get_tags("scroll_mouse")
            ),
            self.factory.create_basic_step(
                "drag_and_drop_to_absolute_coordinates", "現在位置からドラッグ＆ドロップ（座標）", 1,
                {"x": "100", "y": "100"},
                description=get_description("drag_and_drop_to_absolute_coordinates"),
                tags=get_tags("drag_and_drop_to_absolute_coordinates")
            ),
            self.factory.create_basic_step(
                "drag_and_drop_to_relative_coordinates", "現在位置からドラッグ＆ドロップ（距離）", 1,
                {"x": "100", "y": "100"},
                description=get_description("drag_and_drop_to_relative_coordinates"),
                tags=get_tags("drag_and_drop_to_relative_coordinates")
            ),
        ]

        # 画像認識系（特殊フラグ付き）
        image_step = self.factory.create_basic_step(
            "move_mouse_to_image", "マウス移動（画像認識）", 4,
            {"filename": "", "precision": "85", "noise-filter": "100.0",
             "search-area-type": "screen", "search-area": "(0, 0) ~ (0, 0)", "click": "single"},
            description=get_description("move_mouse_to_image"),
            tags=get_tags("move_mouse_to_image")
        )
        image_step["flags"]["checked"] = False
        image_step["flags"]["error"] = {"flag": False, "timestamp": "", "msg": ""}
        image_step["ext"] = {}
        steps.append(image_step)

        drag_image_step = self.factory.create_basic_step(
            "drag_and_drop_to_image", "現在位置からドラッグ＆ドロップ（画像認識）", 2,
            {"filename": "", "precision": "85", "noise-filter": "100.0",
             "search-area-type": "screen", "search-area": "(0, 0) ~ (0, 0)"},
            description=get_description("drag_and_drop_to_image"),
            tags=get_tags("drag_and_drop_to_image")
        )
        drag_image_step["flags"]["checked"] = False
        drag_image_step["flags"]["error"] = {"flag": False, "timestamp": "", "msg": ""}
        drag_image_step["ext"] = {}
        steps.append(drag_image_step)

        return steps

    def _create_keyboard_steps(self):
        """キーボード操作ステップを生成"""
        return [
            self.factory.create_basic_step(
                "typewrite_static_string", "キーボード入力（文字）", 2,
                {"string": "", "enter": False},
                description=get_description("typewrite_static_string"),
                tags=get_tags("typewrite_static_string")
            ),
            self.factory.create_basic_step(
                "typewrite_all_string", "キーボード入力（貼り付け）", 1,
                {"string": "", "enter": False},
                description=get_description("typewrite_all_string"),
                tags=get_tags("typewrite_all_string")
            ),
            self.factory.create_basic_step(
                "typewrite_password", "キーボード入力（パスワード）", 4,
                {"enter": False, "password-type": "type-input",
                 "ciphertext": "", "nonce": "", "encryption": 1},
                description=get_description("typewrite_password"),
                tags=get_tags("typewrite_password")
            ),
            self.factory.create_basic_step(
                "type_hotkeys", "ショートカットキーを入力", 1,
                {"key-0": "__null__", "key-1": "__null__",
                 "key-2": "__null__", "key-3": ""},
                description=get_description("type_hotkeys"),
                tags=get_tags("type_hotkeys")
            ),
        ]

    def _create_variable_steps(self):
        """変数操作ステップを生成"""
        return [
            self.factory.create_basic_step(
                "assign_string_variable", "データの記憶（文字）", 1,
                {"variable": "データ", "string": ""},
                description=get_description("assign_string_variable"),
                tags=get_tags("assign_string_variable")
            ),
            self.factory.create_basic_step(
                "assign_password_variable", "パスワードの記憶", 1,
                {"password-type": "type-input", "password": "", "password-id": "パスワード"},
                description=get_description("assign_password_variable"),
                tags=get_tags("assign_password_variable")
            ),
            self.factory.create_basic_step(
                "assign_environment_variable", "データの記憶（環境情報）", 1,
                {"variable": "環境", "environment": ""},
                description=get_description("assign_environment_variable"),
                tags=get_tags("assign_environment_variable")
            ),
            self.factory.create_basic_step(
                "assign_date_to_string_variable", "日付を記憶", 3,
                {"variable": "日付", "offset": "0", "format": "yyyy-mm-dd", "0-option": False},
                description=get_description("assign_date_to_string_variable"),
                tags=get_tags("assign_date_to_string_variable")
            ),
            self.factory.create_basic_step(
                "assign_clipboard_to_string_variable", "コピー内容を記憶", 1,
                {"variable": "データ"},
                description=get_description("assign_clipboard_to_string_variable"),
                tags=get_tags("assign_clipboard_to_string_variable")
            ),
            self.factory.create_basic_step(
                "copy_to_clipboard", "クリップボードへコピー", 1,
                {"string": ""},
                description=get_description("copy_to_clipboard"),
                tags=get_tags("copy_to_clipboard")
            ),
            self.factory.create_basic_step(
                "parse_brackets", "文字列抽出（括弧・引用符号）", 1,
                {"src-variable": "", "dst-variable": "抽出文字",
                 "bracket-types": ["()"], "index": "1", "strip": True},
                description=get_description("parse_brackets"),
                tags=get_tags("parse_brackets")
            ),
            self.factory.create_basic_step(
                "parse_delimiters", "文字列抽出（区切り文字）", 1,
                {"src-variable": "", "dst-variable": "抽出文字",
                 "delimiter-type": ",", "custom-str": "", "index": "1"},
                description=get_description("parse_delimiters"),
                tags=get_tags("parse_delimiters")
            ),
        ]

    def _create_excel_steps(self):
        """Excel操作ステップを生成（一部のみ）"""
        return [
            self.factory.create_step(
                "excel-open", "Excelを起動（新規作成）", "excel", 1,
                {"path": ""},
                description=get_description("excel-open")
            ),
            self.factory.create_step(
                "excel-open-existing", "Excelを起動（既存）", "excel", 1,
                {"path": "", "read-only": True},
                description=get_description("excel-open-existing")
            ),
            self.factory.create_step(
                "excel-close", "Excelを閉じる", "excel", 1,
                {"path": "", "save": False},
                description=get_description("excel-close")
            ),
        ]

    def _create_file_steps(self):
        """ファイル操作ステップを生成（一部のみ）"""
        return [
            self.factory.create_step(
                "file-create-dir", "フォルダを作成", "file", 1,
                {"path": ""},
                description=get_description("file-create-dir")
            ),
            self.factory.create_step(
                "file-create-file", "ファイルを作成", "file", 1,
                {"path": "", "string": ""},
                description=get_description("file-create-file")
            ),
            self.factory.create_step(
                "file-copy", "ファイル・フォルダをコピー", "file", 1,
                {"src-path": "", "dst-path": ""},
                description=get_description("file-copy")
            ),
        ]

    def _create_control_flow_steps(self):
        """制御フローステップを生成"""
        steps = []

        # 分岐ステップ
        branch_step = self.factory.create_branching_step(
            "search_screen_and_branch", "画像出現を待つ", 3,
            {"filename": "", "precision": "85", "interval": "5",
             "noise-filter": "100.0", "search-area-type": "screen",
             "search-area": "(0, 0) ~ (0, 0)"},
            description=get_description("search_screen_and_branch"),
            tags=get_tags("search_screen_and_branch")
        )
        branch_step["flags"]["checked"] = False
        branch_step["flags"]["error"] = {"flag": True, "timestamp": "", "msg": ""}
        branch_step["ext"] = {}
        steps.append(branch_step)

        # エラー処理（グルーピング）
        steps.append(
            self.factory.create_grouping_step(
                "check_for_errors", "直前のコマンドのエラーを確認・処理", 1,
                {"retries": 0, "wait": 1, "err-cmd": "[ERR_CMD]",
                 "err-memo": "[ERR_MEMO]", "err-msg": "[ERR_MSG]",
                 "err-param": "[ERR_PARAM]"},
                description=get_description("check_for_errors"),
                tags=get_tags("check_for_errors")
            )
        )

        # エラー処理（分岐）
        steps.append(
            self.factory.create_branching_step(
                "check_for_errors_2", "直前のコマンドのエラーを確認・処理（リトライ前処理）", 1,
                {"retries": 0, "wait": 1, "err-cmd": "[ERR_CMD]",
                 "err-memo": "[ERR_MEMO]", "err-msg": "[ERR_MSG]",
                 "err-param": "[ERR_PARAM]"},
                description=get_description("check_for_errors_2"),
                tags=get_tags("check_for_errors_2")
            )
        )

        return steps

    def _create_other_steps(self):
        """その他の操作ステップを生成"""
        # 元データ: 優先して既存のgenerated_step_list.jsonを参照、無ければstep_list.json
        original_path = project_root / "generated_step_list.json"
        if not original_path.exists():
            original_path = project_root / "step_list.json"
        if not original_path.exists():
            return []

        with open(original_path, 'r', encoding='utf-8') as f:
            original_data = json.load(f)

        # 既に他のメソッドで実装されているステップ
        # 元のstep_list.jsonには以下のステップがない（Excel/ファイル操作の一部）ため、
        # これらはincluded_cmdsから除外しない
        implemented_cmds = {
            "run_executable", "run_executable_and_wait", "pause", "pause_and_ask_to_proceed",
            "pause_and_countdown_to_proceed", "change_speed_for_command_execution", "abort",
            "raise_error", "take_screenshot", "remember_focused_window", "remember_named_window",
            "focus_window", "focus_window_by_name", "get_window_title", "align_focused_window",
            "maximize_focused_window", "move_mouse_to_absolute_coordinates",
            "move_mouse_to_relative_coordinates", "move_mouse_to_image",
            "drag_and_drop_to_absolute_coordinates", "drag_and_drop_to_relative_coordinates",
            "drag_and_drop_to_image", "click_mouse", "scroll_mouse", "typewrite_static_string",
            "typewrite_all_string", "typewrite_password", "type_hotkeys", "assign_string_variable",
            "assign_password_variable", "assign_environment_variable", "assign_date_to_string_variable",
            "assign_clipboard_to_string_variable", "copy_to_clipboard", "parse_brackets",
            "parse_delimiters", "search_screen_and_branch",
            "check_for_errors", "check_for_errors_2"
        }

        steps = []

        # 元のファイルから不足しているステップを追加
        for original_step in original_data['sequence']:
            # 元データをスネークケースへ正規化（ネスト含む）
            normalized_step = self._normalize_cmd_case(original_step)
            cmd = normalized_step['cmd']

            # 既に実装されているステップはスキップ
            if cmd in implemented_cmds:
                continue

            cmd_nickname = normalized_step.get('cmd-nickname', '')
            cmd_type = normalized_step.get('cmd-type', 'basic')
            version = normalized_step.get('version', 1)
            parameters = normalized_step.get('parameters', {})

            # ステップタイプに応じて生成
            if cmd_type == 'looping':
                step = self.factory.create_looping_step(
                    cmd, cmd_nickname, version, parameters,
                    description=get_description(cmd),
                    tags=get_tags(cmd),
                    sequence=normalized_step.get('sequence', [])
                )
            elif cmd_type == 'branching':
                step = self.factory.create_branching_step(
                    cmd, cmd_nickname, version, parameters,
                    description=get_description(cmd),
                    tags=get_tags(cmd),
                    sequence_0=normalized_step.get('sequence-0', []),
                    sequence_1=normalized_step.get('sequence-1', [])
                )
            elif cmd_type == 'grouping':
                step = self.factory.create_grouping_step(
                    cmd, cmd_nickname, version, parameters,
                    description=get_description(cmd),
                    tags=get_tags(cmd),
                    sequence=normalized_step.get('sequence', [])
                )
            else:  # basic, static, excel, file など
                step = self.factory.create_step(
                    cmd, cmd_nickname, cmd_type, version, parameters,
                    description=get_description(cmd),
                    tags=get_tags(cmd)
                )

            # 特殊なフラグがある場合
            if 'flags' in normalized_step:
                flags = normalized_step['flags']
                if 'error' in flags or 'checked' in flags:
                    step['flags'] = flags

            if 'ext' in normalized_step:
                step['ext'] = normalized_step['ext']

            steps.append(step)

        return steps

    def generate_scenario(self):
        """完全なシナリオを生成"""
        # オリジナルファイルが存在する場合は読み込む（現在は無効化）
        # original_path = project_root / "step_list.json"
        # if original_path.exists():
        #     with open(original_path, 'r', encoding='utf-8') as f:
        #         return json.load(f)

        # 常に新規生成
        steps = self.create_all_steps()

        scenario = {
            "version": "38.0",
            "uuid": str(self.factory.get_or_create_uuid("scenario", 1)),
            "name": "list",
            "description": "",
            "timestamp-created": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
            "timestamp-last-modified": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
            "timestamp-last-run": "",
            "flags": {},
            "sequence": steps
        }

        return scenario


def main():
    """メイン処理"""
    generator = StepListGenerator()
    scenario = generator.generate_scenario()

    # 出力ファイル
    output_file = project_root / "generated_step_list.json"

    # JSONとして保存
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(scenario, f, ensure_ascii=False, indent=2)

    print(f"✅ JSONファイルを生成しました: {output_file}")
    print(f"  - バージョン: {scenario['version']}")
    print(f"  - ステップ数: {len(scenario.get('sequence', []))}")


if __name__ == "__main__":
    main()