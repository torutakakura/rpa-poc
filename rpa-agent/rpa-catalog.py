"""
RPA操作定義システム - Python実装
操作テンプレートの定義とJSON生成
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional, Union

from schemas.app_screen import AppOperations, ScreenOperations

# スキーマモジュールからインポート
from schemas.api import APIOperations
from schemas.base import OperationTemplate
from schemas.branch import BranchOperations
from schemas.excel_csv import ExcelOperations
from schemas.external_scenario import ExternalScenarioOperations
from schemas.file_folder import FileFolderOperations, FileOperations, FolderOperations
from schemas.keyboard import KeyboardOperations
from schemas.loop import LoopOperations
from schemas.mail import MailOperations
from schemas.memory import MemoryOperations
from schemas.mouse import MouseOperations
from schemas.scenario import ScenarioOrganizationOperations
from schemas.special_app import SpecialAppOperations
from schemas.spreadsheet import SpreadsheetOperations
from schemas.text_extract import TextExtractOperations
from schemas.wait_error import WaitErrorOperations
from schemas.web_browser import WebBrowserOperations

# ===========================
# RPAシステムメインクラス
# ===========================


class RPAOperationSystem:
    """RPA操作定義システムのメインクラス"""

    def __init__(self):
        self.operations = {}
        self._build_operations()

    def _build_operations(self):
        """全操作の定義を構築"""

        # A. アプリ・画面
        self.operations["A_アプリ・画面"] = {
            "アプリ": {
                "起動": AppOperations.run_executable(),
                "起動（終了待ち）": AppOperations.run_executable_and_wait(),
            },
            "画面": {
                "最前画面を覚える": ScreenOperations.remember_focused_window(),
                "画面を覚える（名前）": ScreenOperations.remember_named_window(),
                "切り替え（参照ID）": ScreenOperations.focus_window(),
                "切り替え（名前）": ScreenOperations.focus_window_by_name(),
                "画面の名前を取得": ScreenOperations.get_window_title(),
                "移動": ScreenOperations.align_focused_window(),
                "最大化/最小化": ScreenOperations.maximize_focused_window(),
                "スクリーンショットを撮る": ScreenOperations.take_screenshot(),
            },
        }

        # B. 待機・終了・エラー
        self.operations["B_待機・終了・エラー"] = {
            "秒": WaitErrorOperations.pause(),
            "画像出現を待つ": WaitErrorOperations.search_screen_and_branch(),
            "続行確認": WaitErrorOperations.pause_and_ask_to_proceed(),
            "タイマー付き続行確認（秒）": WaitErrorOperations.pause_and_countdown_to_proceed(),
            "コマンド間待機時間を変更": WaitErrorOperations.change_speed_for_command_execution(),
            "作業強制終了": WaitErrorOperations.abort(),
            "エラー発生": WaitErrorOperations.raise_error(),
            "エラー確認・処理": WaitErrorOperations.check_for_errors(),
            "エラー確認・処理（リトライ前処理）": WaitErrorOperations.check_for_errors_2(),
        }

        # C. マウス
        self.operations["C_マウス"] = {
            "移動": {
                "座標": MouseOperations.Move.move_mouse_to_absolute_coordinates(),
                "距離": MouseOperations.Move.move_mouse_to_relative_coordinates(),
                "画像認識": MouseOperations.Move.move_mouse_to_image(),
            },
            "ドラッグ＆ドロップ": {
                "座標（D&D）": MouseOperations.DragAndDrop.drag_and_drop_to_absolute_coordinates(),
                "距離（D&D）": MouseOperations.DragAndDrop.drag_and_drop_to_relative_coordinates(),
                "画像認識（D&D）": MouseOperations.DragAndDrop.drag_and_drop_to_image(),
            },
            "マウスクリック": MouseOperations.click_mouse(),
            "スクロール": MouseOperations.scroll_mouse(),
        }

        # D. キーボード
        self.operations["D_キーボード"] = {
            "入力": {
                "文字": KeyboardOperations.Input.typewrite_static_string(),
                "文字（貼り付け）": KeyboardOperations.Input.typewrite_all_string(),
                "パスワード": KeyboardOperations.Input.typewrite_password(),
                "ショートカットキー": KeyboardOperations.Input.type_hotkeys(),
            }
        }

        # E. 記憶
        self.operations["E_記憶"] = {
            "文字": MemoryOperations.assign_string_variable(),
            "パスワード": MemoryOperations.assign_password_variable(),
            "環境情報": MemoryOperations.assign_environment_variable(),
            "日付": MemoryOperations.assign_date_to_string_variable(),
            "日付（営業日）": MemoryOperations.assign_date_business_to_string_variable(),
            "日付（曜日）": MemoryOperations.assign_date_weekdays_to_string_variable(),
            "日付計算": MemoryOperations.assign_date_calculation_to_string_variable(),
            "曜日": MemoryOperations.assign_day_of_week_to_string_variable(),
            "時刻": MemoryOperations.assign_timestamp_to_string_variable(),
            "時刻計算": MemoryOperations.assign_time_calculation_to_string_variable(),
            "計算": MemoryOperations.assign_arithmetic_result_to_string_variable_v2(),
            "乱数": MemoryOperations.assign_random_number_to_string_variable(),
            "コピー内容": MemoryOperations.assign_clipboard_to_string_variable(),
            "クリップボードへコピー": MemoryOperations.copy_to_clipboard(),
            "実行中に入力": MemoryOperations.assign_live_input_to_string_variable(),
            "ファイル更新日時": MemoryOperations.assign_file_modification_timestamp_to_string_variable(),
            "ファイルサイズ": MemoryOperations.assign_file_size_to_string_variable(),
            "最新ファイル・フォルダ": MemoryOperations.find_newest_file_from_fixed_directory(),
        }

        # F. 文字抽出
        self.operations["F_文字抽出"] = {
            "括弧・引用符号から": TextExtractOperations.from_brackets(),
            "区切り文字から": TextExtractOperations.from_delimiter(),
            "改行・空白を削除": TextExtractOperations.remove_whitespace(),
            "ファイルパスから": TextExtractOperations.from_filepath(),
            "ルールにマッチ": TextExtractOperations.match_pattern(),
            "置換": TextExtractOperations.replace(),
            "文字変換": TextExtractOperations.convert_text(),
            "日付形式変換": TextExtractOperations.convert_date_format(),
            "1行ずつループ": TextExtractOperations.loop_lines(),
        }

        # G. 分岐
        self.operations["G_分岐"] = {
            "文字列": BranchOperations.string_condition(),
            "数値": BranchOperations.numeric_condition(),
            "日付": BranchOperations.date_condition(),
            "ファイル・フォルダの有/無を確認": BranchOperations.file_exists(),
            "画像": BranchOperations.image_exists(),
        }

        # H. 繰り返し
        self.operations["H_繰り返し"] = {
            "繰り返し": LoopOperations.loop(),
            "繰り返しを抜ける": LoopOperations.break_loop(),
            "繰り返しの最初に戻る": LoopOperations.continue_loop(),
        }

        # I. ファイル・フォルダ
        self.operations["I_ファイル・フォルダ"] = {
            "ファイル": {
                "開く": FileOperations.open(),
                "移動": FileOperations.move(),
                "読み込む": FileOperations.read(),
                "書き込む": FileOperations.write(),
            },
            "フォルダ": {
                "開く": FolderOperations.open(),
                "作成": FolderOperations.create(),
                "ループ": FolderOperations.loop(),
            },
            "ファイル・フォルダ名の変更": FileFolderOperations.rename(),
            "ファイル・フォルダをコピー": FileFolderOperations.copy(),
            "ファイル・フォルダを削除": FileFolderOperations.delete(),
            "圧縮・解凍": {
                "ファイル・フォルダを圧縮": FileFolderOperations.Compression.compress(),
                "ファイル・フォルダに解凍": FileFolderOperations.Compression.extract(),
            },
            "ファイル名変更（挿入）": {
                "文字": FileFolderOperations.RenameWithInsert.insert_text(),
                "日付": FileFolderOperations.RenameWithInsert.insert_date(),
                "参照ID": FileFolderOperations.RenameWithInsert.insert_reference(),
            },
        }

        # J. エクセル・CSV
        self.operations["J_エクセル・CSV"] = {
            "ブック": {
                "ブックを開く": ExcelOperations.Workbook.open(),
                "ブックを覚える": ExcelOperations.Workbook.remember(),
                "ブックを保存": ExcelOperations.Workbook.save(),
                "ブックを閉じる": ExcelOperations.Workbook.close(),
            },
            "シート操作": {
                "新規作成": ExcelOperations.Sheet.create(),
                "削除": ExcelOperations.Sheet.delete(),
                "切り替え": ExcelOperations.Sheet.switch(),
                "移動・コピー": ExcelOperations.Sheet.move_or_copy(),
                "名前取得": ExcelOperations.Sheet.get_name(),
                "名前変更": ExcelOperations.Sheet.rename(),
            },
            "セル操作": {
                "範囲指定": ExcelOperations.Cell.select_range(),
                "指定範囲の移動": ExcelOperations.Cell.move_range(),
                "指定範囲の削除": ExcelOperations.Cell.delete_range(),
                "指定範囲にセルを挿入": ExcelOperations.Cell.insert_cells(),
                "値を取得": ExcelOperations.Cell.get_value(),
                "値を入力": ExcelOperations.Cell.set_value(),
                "セルをコピー": ExcelOperations.Cell.copy_cells(),
                "セルを貼り付け": ExcelOperations.Cell.paste_cells(),
                "位置を取得": ExcelOperations.Cell.find_position(),
                "最終行取得": ExcelOperations.Cell.get_last_row(),
                "最終列取得": ExcelOperations.Cell.get_last_column(),
                "列計算": ExcelOperations.Cell.column_calculation(),
                "マクロ実行": ExcelOperations.Cell.run_macro(),
                "行ループ": ExcelOperations.Cell.row_loop(),
                "列ループ": ExcelOperations.Cell.column_loop(),
                "CSV読込ループ": ExcelOperations.Cell.csv_read_loop(),
            },
        }

        # K. スプレッドシート
        self.operations["K_スプレッドシート"] = {
            "スプレッドシート": {
                "作成": SpreadsheetOperations.Spreadsheet.create_spreadsheet(),
                "読み込む": SpreadsheetOperations.Spreadsheet.remember_spreadsheet(),
                "削除": SpreadsheetOperations.Spreadsheet.delete_spreadsheet(),
                "名前変更": SpreadsheetOperations.Spreadsheet.rename_spreadsheet(),
                "URL取得": SpreadsheetOperations.Spreadsheet.get_spreadsheet_url(),
            },
            "シート": {
                "新規作成": SpreadsheetOperations.Sheet.create_spreadsheet_sheet(),
                "削除": SpreadsheetOperations.Sheet.delete_spreadsheet_sheet(),
                "移動": SpreadsheetOperations.Sheet.move_spreadsheet_sheet(),
                "コピー": SpreadsheetOperations.Sheet.copy_spreadsheet_sheet(),
                "名前取得": SpreadsheetOperations.Sheet.get_spreadsheet_sheet_name(),
                "名前変更": SpreadsheetOperations.Sheet.rename_spreadsheet_sheet(),
            },
            "セル操作": {
                "指定範囲の削除": SpreadsheetOperations.Cell.delete_spreadsheet_range(),
                "指定範囲にセルを挿入": SpreadsheetOperations.Cell.insert_spreadsheet_range(),
                "値を取得": SpreadsheetOperations.Cell.get_spreadsheet_values(),
                "値を入力": SpreadsheetOperations.Cell.set_spreadsheet_values(),
                "セルをコピー・貼り付け": SpreadsheetOperations.Cell.copy_paste_spreadsheet(),
                "最終行取得": SpreadsheetOperations.Cell.get_spreadsheet_last_row(),
                "行ループ": SpreadsheetOperations.Cell.loop_spreadsheet_row(),
                "列ループ": SpreadsheetOperations.Cell.loop_spreadsheet_col(),
            },
        }

        # L. ウェブブラウザ
        self.operations["L_ウェブブラウザ"] = {
            "ブラウザを開く": WebBrowserOperations.create_operation("open"),
            "ブラウザを閉じる": WebBrowserOperations.create_operation("close"),
            "ページ移動": WebBrowserOperations.create_operation("navigate"),
            "クリック": WebBrowserOperations.create_operation("click"),
            "入力": WebBrowserOperations.create_operation("input"),
            "選択": WebBrowserOperations.create_operation("select"),
            "読み取り": WebBrowserOperations.create_operation("get_text"),
            "待機": WebBrowserOperations.create_operation("wait"),
            "スクロール": WebBrowserOperations.create_operation("scroll"),
            "スクリーンショット": WebBrowserOperations.create_operation("screenshot"),
            "JavaScript実行": WebBrowserOperations.create_operation("execute_js"),
            "タブ切り替え": WebBrowserOperations.create_operation("switch_tab"),
            "更新": WebBrowserOperations.create_operation("refresh"),
        }

        # M. メール
        self.operations["M_メール"] = {
            "送信": MailOperations.send_email(),
            "受信": MailOperations.receive_emails(),
            "送信（Gmail）": MailOperations.send_email_gmail(),
            "受信（Gmail）": MailOperations.receive_emails_gmail(),
            "送信（Microsoft）": MailOperations.send_email_microsoft(),
            "受信（Microsoft）": MailOperations.receive_emails_microsoft(),
        }

        # N. 特殊アプリ操作
        self.operations["N_特殊アプリ操作"] = {
            "クリック": SpecialAppOperations.click_uia_element(),
            "文字入力": SpecialAppOperations.send_text_to_uia_element(),
            "文字入力（パスワード）": SpecialAppOperations.send_password_to_uia_element(),
            "座標取得": SpecialAppOperations.get_uia_element_clickable_point(),
            "文字取得": SpecialAppOperations.get_text_from_uia_element(),
        }

        # O. API
        self.operations["O_API"] = {
            "Web API": APIOperations.api_web(),
            "JSON": {
                "JSON値取得": APIOperations.JSON.get_json_values(),
                "JSON型確認": APIOperations.JSON.check_json_type(),
            },
        }

        # P. シナリオ整理
        self.operations["P_シナリオ整理"] = {
            "グループ化": ScenarioOrganizationOperations.group_commands(),
            "メモ": ScenarioOrganizationOperations.add_memo(),
            "通知音を再生": ScenarioOrganizationOperations.play_sound(),
        }

        # Q. 別シナリオ実行・継承
        self.operations["Q_別シナリオ実行・継承"] = {
            "別シナリオ実行": ExternalScenarioOperations.run_external_scenario_and_branch(),
            "親シナリオからデータを継承": ExternalScenarioOperations.inherit_variables(),
            "親シナリオからパスワードを継承": ExternalScenarioOperations.inherit_passwords(),
            "親シナリオからウィンドウを継承": ExternalScenarioOperations.inherit_windows(),
            "親シナリオからエクセルを継承": ExternalScenarioOperations.inherit_excel(),
            "親シナリオからブラウザを継承": ExternalScenarioOperations.inherit_browsers(),
        }

    def to_dict(self) -> Dict[str, Any]:
        """操作定義を辞書形式に変換"""
        result = {"operation_templates": {}}

        def convert_value(value):
            if isinstance(value, OperationTemplate):
                return value.to_dict()
            elif isinstance(value, dict):
                return {k: convert_value(v) for k, v in value.items()}
            else:
                return value

        for category, operations in self.operations.items():
            result["operation_templates"][category] = convert_value(operations)

        # 共通パラメータの定義を追加
        result["common_parameter_definitions"] = {
            "memo": {
                "type": "string",
                "description": "ステップに関するメモやコメント",
                "required": False,
                "default": "",
            },
            "timeout": {
                "type": "integer",
                "description": "タイムアウト時間（秒）",
                "required": False,
                "default": 30,
                "min": 1,
                "max": 3600,
            },
            "retry_count": {
                "type": "integer",
                "description": "リトライ回数",
                "required": False,
                "default": 0,
                "min": 0,
                "max": 10,
            },
            "error_handling": {
                "type": "string",
                "description": "エラー時の処理方法",
                "required": False,
                "default": "stop",
                "enum": ["stop", "continue", "retry", "skip"],
            },
        }

        return result

    def to_json(self, indent: int = 2) -> str:
        """操作定義をJSON文字列に変換"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    def save_to_file(self, filepath: Union[str, Path], indent: int = 2):
        """操作定義をJSONファイルに保存"""
        filepath = Path(filepath)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=indent)
        print(f"Saved to {filepath}")

    def get_operation(
        self, category: str, subcategory: str = None, operation: str = None
    ) -> Optional[OperationTemplate]:
        """特定の操作定義を取得"""
        try:
            if subcategory and operation:
                return self.operations[category][subcategory][operation]
            elif operation:
                return self.operations[category][operation]
            else:
                return self.operations[category]
        except KeyError:
            return None


# ===========================
# 使用例
# ===========================

if __name__ == "__main__":
    # RPAシステムのインスタンス作成
    rpa_system = RPAOperationSystem()

    # JSON文字列として出力
    json_str = rpa_system.to_json()
    print("=== RPA Operations JSON ===")
    print(json_str[:1000] + "...")  # 最初の1000文字を表示

    # ファイルに保存
    rpa_system.save_to_file("rpa_operations.json")

    # 特定の操作を取得して使用する例
    app_launch = rpa_system.get_operation("A_アプリ・画面", "アプリ", "起動")
    if app_launch:
        print("\n=== アプリ起動操作の定義 ===")
        print(json.dumps(app_launch.to_dict(), ensure_ascii=False, indent=2))

    # カスタマイズして新しい操作を作成する例
    custom_app_launch = AppOperations.run_executable()
    custom_app_launch.specific_params["path"] = "C:\\Program Files\\MyApp\\app.exe"
    custom_app_launch.specific_params["arguments"] = ""
    custom_app_launch.common_params.timeout = 60
    custom_app_launch.common_params.memo = "カスタムアプリの起動"

    print("\n=== カスタマイズされた操作 ===")
    print(json.dumps(custom_app_launch.to_dict(), ensure_ascii=False, indent=2))
