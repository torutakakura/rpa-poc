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
            ("run-executable", "アプリ起動", 3,
             {"path": "", "arguments": "", "interval": 3, "maximized": True}),
            ("run-executable-and-wait", "アプリ起動（終了待ち）", 1,
             {"path": "", "arguments": "", "timeout": 300,
              "output-variable": "", "error-variable": ""}),
            ("pause", "待機（秒）", 1, {"interval": "3"}),
            ("pause-and-ask-to-proceed", "続行確認", 2, {"string": ""}),
            ("pause-and-countdown-to-proceed", "タイマー付き続行確認", 2,
             {"interval": "3", "string": ""}),
            ("change-speed-for-command-execution", "コマンド間の待機時間を変更", 1,
             {"interval": 0.2}),
            ("abort", "作業強制終了", 2, {"result-type": "abort"}),
            ("raise-error", "エラーを発生させる", 1, {"string": ""}),
            ("take-screenshot", "スクリーンショットを撮る", 1,
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
            ("remember-focused-window", "最前面画面を覚える", 1,
             {"variable": "ウィンドウ"}),
            ("remember-named-window", "画面を覚える（名前）", 1,
             {"match-type": "contains", "window-name": "ウィンドウ", "variable": "ウィンドウ"}),
            ("focus-window", "最前面画面切り替え", 1, {"variable": ""}),
            ("focus-window-by-name", "画面切り替え（名前）", 1, {"string": ""}),
            ("get-window-title", "画面の名前を取得", 1,
             {"window": "__focused_window__", "variable": "ウィンドウ名"}),
            ("align-focused-window", "ウィンドウを移動", 1, {"alignment": "left"}),
            ("maximize-focused-window", "ウィンドウ最大化／最小化", 2,
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
                "move-mouse-to-absolute-coordinates", "マウス移動（座標）", 2,
                {"x": "100", "y": "100", "click": "single"},
                description=get_description("move-mouse-to-absolute-coordinates"),
                tags=get_tags("move-mouse-to-absolute-coordinates")
            ),
            self.factory.create_basic_step(
                "move-mouse-to-relative-coordinates", "マウス移動（距離）", 2,
                {"x": "100", "y": "100", "click": "single"},
                description=get_description("move-mouse-to-relative-coordinates"),
                tags=get_tags("move-mouse-to-relative-coordinates")
            ),
            self.factory.create_basic_step(
                "click-mouse", "マウスクリック", 1,
                {"type": "single", "key": "__null__"},
                description=get_description("click-mouse"),
                tags=get_tags("click-mouse")
            ),
            self.factory.create_basic_step(
                "scroll-mouse", "マウススクロール", 1,
                {"direction": "up", "amount": 3},
                description=get_description("scroll-mouse"),
                tags=get_tags("scroll-mouse")
            ),
            self.factory.create_basic_step(
                "drag-and-drop-to-absolute-coordinates", "現在位置からドラッグ＆ドロップ（座標）", 1,
                {"x": "100", "y": "100"},
                description=get_description("drag-and-drop-to-absolute-coordinates"),
                tags=get_tags("drag-and-drop-to-absolute-coordinates")
            ),
            self.factory.create_basic_step(
                "drag-and-drop-to-relative-coordinates", "現在位置からドラッグ＆ドロップ（距離）", 1,
                {"x": "100", "y": "100"},
                description=get_description("drag-and-drop-to-relative-coordinates"),
                tags=get_tags("drag-and-drop-to-relative-coordinates")
            ),
        ]

        # 画像認識系（特殊フラグ付き）
        image_step = self.factory.create_basic_step(
            "move-mouse-to-image", "マウス移動（画像認識）", 4,
            {"filename": "", "precision": "85", "noise-filter": "100.0",
             "search-area-type": "screen", "search-area": "(0, 0) ~ (0, 0)", "click": "single"},
            description=get_description("move-mouse-to-image"),
            tags=get_tags("move-mouse-to-image")
        )
        image_step["flags"]["checked"] = False
        image_step["flags"]["error"] = {"flag": False, "timestamp": "", "msg": ""}
        image_step["ext"] = {}
        steps.append(image_step)

        drag_image_step = self.factory.create_basic_step(
            "drag-and-drop-to-image", "現在位置からドラッグ＆ドロップ（画像認識）", 2,
            {"filename": "", "precision": "85", "noise-filter": "100.0",
             "search-area-type": "screen", "search-area": "(0, 0) ~ (0, 0)"},
            description=get_description("drag-and-drop-to-image"),
            tags=get_tags("drag-and-drop-to-image")
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
                "typewrite-static-string", "キーボード入力（文字）", 2,
                {"string": "", "enter": False},
                description=get_description("typewrite-static-string"),
                tags=get_tags("typewrite-static-string")
            ),
            self.factory.create_basic_step(
                "typewrite-all-string", "キーボード入力（貼り付け）", 1,
                {"string": "", "enter": False},
                description=get_description("typewrite-all-string"),
                tags=get_tags("typewrite-all-string")
            ),
            self.factory.create_basic_step(
                "typewrite-password", "キーボード入力（パスワード）", 4,
                {"enter": False, "password-type": "type-input",
                 "ciphertext": "", "nonce": "", "encryption": 1},
                description=get_description("typewrite-password"),
                tags=get_tags("typewrite-password")
            ),
            self.factory.create_basic_step(
                "type-hotkeys", "ショートカットキーを入力", 1,
                {"key-0": "__null__", "key-1": "__null__",
                 "key-2": "__null__", "key-3": ""},
                description=get_description("type-hotkeys"),
                tags=get_tags("type-hotkeys")
            ),
        ]

    def _create_variable_steps(self):
        """変数操作ステップを生成"""
        return [
            self.factory.create_basic_step(
                "assign-string-variable", "データの記憶（文字）", 1,
                {"variable": "データ", "string": ""},
                description=get_description("assign-string-variable"),
                tags=get_tags("assign-string-variable")
            ),
            self.factory.create_basic_step(
                "assign-password-variable", "パスワードの記憶", 1,
                {"password-type": "type-input", "password": "", "password-id": "パスワード"},
                description=get_description("assign-password-variable"),
                tags=get_tags("assign-password-variable")
            ),
            self.factory.create_basic_step(
                "assign-environment-variable", "データの記憶（環境情報）", 1,
                {"variable": "環境", "environment": ""},
                description=get_description("assign-environment-variable"),
                tags=get_tags("assign-environment-variable")
            ),
            self.factory.create_basic_step(
                "assign-date-to-string-variable", "日付を記憶", 3,
                {"variable": "日付", "offset": "0", "format": "yyyy-mm-dd", "0-option": False},
                description=get_description("assign-date-to-string-variable"),
                tags=get_tags("assign-date-to-string-variable")
            ),
            self.factory.create_basic_step(
                "assign-clipboard-to-string-variable", "コピー内容を記憶", 1,
                {"variable": "データ"},
                description=get_description("assign-clipboard-to-string-variable"),
                tags=get_tags("assign-clipboard-to-string-variable")
            ),
            self.factory.create_basic_step(
                "copy-to-clipboard", "クリップボードへコピー", 1,
                {"string": ""},
                description=get_description("copy-to-clipboard"),
                tags=get_tags("copy-to-clipboard")
            ),
            self.factory.create_basic_step(
                "parse-brackets", "文字列抽出（括弧・引用符号）", 1,
                {"src-variable": "", "dst-variable": "抽出文字",
                 "bracket-types": ["()"], "index": "1", "strip": True},
                description=get_description("parse-brackets"),
                tags=get_tags("parse-brackets")
            ),
            self.factory.create_basic_step(
                "parse-delimiters", "文字列抽出（区切り文字）", 1,
                {"src-variable": "", "dst-variable": "抽出文字",
                 "delimiter-type": ",", "custom-str": "", "index": "1"},
                description=get_description("parse-delimiters"),
                tags=get_tags("parse-delimiters")
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
            "search-screen-and-branch", "画像出現を待つ", 3,
            {"filename": "", "precision": "85", "interval": "5",
             "noise-filter": "100.0", "search-area-type": "screen",
             "search-area": "(0, 0) ~ (0, 0)"},
            description=get_description("search-screen-and-branch"),
            tags=get_tags("search-screen-and-branch")
        )
        branch_step["flags"]["checked"] = False
        branch_step["flags"]["error"] = {"flag": True, "timestamp": "", "msg": ""}
        branch_step["ext"] = {}
        steps.append(branch_step)

        # エラー処理（グルーピング）
        steps.append(
            self.factory.create_grouping_step(
                "check-for-errors", "直前のコマンドのエラーを確認・処理", 1,
                {"retries": 0, "wait": 1, "err-cmd": "[ERR_CMD]",
                 "err-memo": "[ERR_MEMO]", "err-msg": "[ERR_MSG]",
                 "err-param": "[ERR_PARAM]"},
                description=get_description("check-for-errors"),
                tags=get_tags("check-for-errors")
            )
        )

        # エラー処理（分岐）
        steps.append(
            self.factory.create_branching_step(
                "check-for-errors-2", "直前のコマンドのエラーを確認・処理（リトライ前処理）", 1,
                {"retries": 0, "wait": 1, "err-cmd": "[ERR_CMD]",
                 "err-memo": "[ERR_MEMO]", "err-msg": "[ERR_MSG]",
                 "err-param": "[ERR_PARAM]"},
                description=get_description("check-for-errors-2"),
                tags=get_tags("check-for-errors-2")
            )
        )

        return steps

    def _create_other_steps(self):
        """その他の操作ステップを生成"""
        # 元のstep_list.jsonから残りの132個のステップをすべて追加
        original_path = project_root / "step_list.json"
        if not original_path.exists():
            return []

        with open(original_path, 'r', encoding='utf-8') as f:
            original_data = json.load(f)

        # 既に他のメソッドで実装されているステップ
        # 元のstep_list.jsonには以下のステップがない（Excel/ファイル操作の一部）ため、
        # これらはincluded_cmdsから除外しない
        implemented_cmds = {
            "run-executable", "run-executable-and-wait", "pause", "pause-and-ask-to-proceed",
            "pause-and-countdown-to-proceed", "change-speed-for-command-execution", "abort",
            "raise-error", "take-screenshot", "remember-focused-window", "remember-named-window",
            "focus-window", "focus-window-by-name", "get-window-title", "align-focused-window",
            "maximize-focused-window", "move-mouse-to-absolute-coordinates",
            "move-mouse-to-relative-coordinates", "move-mouse-to-image",
            "drag-and-drop-to-absolute-coordinates", "drag-and-drop-to-relative-coordinates",
            "drag-and-drop-to-image", "click-mouse", "scroll-mouse", "typewrite-static-string",
            "typewrite-all-string", "typewrite-password", "type-hotkeys", "assign-string-variable",
            "assign-password-variable", "assign-environment-variable", "assign-date-to-string-variable",
            "assign-clipboard-to-string-variable", "copy-to-clipboard", "parse-brackets",
            "parse-delimiters", "search-screen-and-branch",
            "check-for-errors", "check-for-errors-2"
        }

        steps = []

        # 元のファイルから不足しているステップを追加
        for original_step in original_data['sequence']:
            cmd = original_step['cmd']

            # 既に実装されているステップはスキップ
            if cmd in implemented_cmds:
                continue

            cmd_nickname = original_step.get('cmd-nickname', '')
            cmd_type = original_step.get('cmd-type', 'basic')
            version = original_step.get('version', 1)
            parameters = original_step.get('parameters', {})

            # ステップタイプに応じて生成
            if cmd_type == 'looping':
                step = self.factory.create_looping_step(
                    cmd, cmd_nickname, version, parameters,
                    description=get_description(cmd),
                    tags=get_tags(cmd),
                    sequence=original_step.get('sequence', [])
                )
            elif cmd_type == 'branching':
                step = self.factory.create_branching_step(
                    cmd, cmd_nickname, version, parameters,
                    description=get_description(cmd),
                    tags=get_tags(cmd),
                    sequence_0=original_step.get('sequence-0', []),
                    sequence_1=original_step.get('sequence-1', [])
                )
            elif cmd_type == 'grouping':
                step = self.factory.create_grouping_step(
                    cmd, cmd_nickname, version, parameters,
                    description=get_description(cmd),
                    tags=get_tags(cmd),
                    sequence=original_step.get('sequence', [])
                )
            else:  # basic, static, excel, file など
                step = self.factory.create_step(
                    cmd, cmd_nickname, cmd_type, version, parameters,
                    description=get_description(cmd),
                    tags=get_tags(cmd)
                )

            # 特殊なフラグがある場合
            if 'flags' in original_step:
                flags = original_step['flags']
                if 'error' in flags or 'checked' in flags:
                    step['flags'] = flags

            if 'ext' in original_step:
                step['ext'] = original_step['ext']

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