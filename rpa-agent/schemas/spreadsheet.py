"""
K. スプレッドシート操作のスキーマ定義
"""

from .base import OperationTemplate


class SpreadsheetOperations:
    """スプレッドシート操作の定義"""

    class Spreadsheet:
        """スプレッドシート関連"""

        @staticmethod
        def create_spreadsheet() -> OperationTemplate:
            """スプレッドシートを作成"""
            return OperationTemplate(
                specific_params={
                    "account": "",  # 任意設定項目（用途に応じて指定）
                    "name": "",  # 任意設定項目（用途に応じて指定）
                    "spreadsheet": "スプレッドシート",  # 任意設定項目（用途に応じて指定）
                }
            )

        @staticmethod
        def remember_spreadsheet() -> OperationTemplate:
            """スプレッドシートを読み込む"""
            return OperationTemplate(
                specific_params={
                    "account": "",  # 任意設定項目（用途に応じて指定）
                    "spreadsheet": "スプレッドシート",  # 任意設定項目（用途に応じて指定）
                    "method": "url",  # 任意設定項目（用途に応じて指定）
                    "name": "",  # 任意設定項目（用途に応じて指定）
                    "url": "",  # 任意設定項目（用途に応じて指定）
                    "id": "",  # 任意設定項目（用途に応じて指定）
                }
            )

        @staticmethod
        def delete_spreadsheet() -> OperationTemplate:
            """スプレッドシートを削除"""
            return OperationTemplate(
                specific_params={
                    "account": "",  # 任意設定項目（用途に応じて指定）
                    "method": "url",  # 任意設定項目（用途に応じて指定）
                    "name": "",  # 任意設定項目（用途に応じて指定）
                    "url": "",  # 任意設定項目（用途に応じて指定）
                    "id": "",  # 任意設定項目（用途に応じて指定）
                }
            )

        @staticmethod
        def rename_spreadsheet() -> OperationTemplate:
            """スプレッドシート名を変更"""
            return OperationTemplate(
                specific_params={
                    "account": "",  # 任意設定項目（用途に応じて指定）
                    "method": "url",  # 任意設定項目（用途に応じて指定）
                    "name": "",  # 任意設定項目（用途に応じて指定）
                    "url": "",  # 任意設定項目（用途に応じて指定）
                    "id": "",  # 任意設定項目（用途に応じて指定）
                    "rename": "",  # 任意設定項目（用途に応じて指定）
                }
            )

        @staticmethod
        def get_spreadsheet_url() -> OperationTemplate:
            """スプレッドシートのURL取得"""
            return OperationTemplate(
                specific_params={
                    "variable": "url",  # 値やウィンドウを保持する変数名
                    "spreadsheet": "",  # 任意設定項目（用途に応じて指定）
                }
            )

    class Sheet:
        """シート関連"""

        @staticmethod
        def create_spreadsheet_sheet() -> OperationTemplate:
            """新規シート"""
            return OperationTemplate(
                specific_params={
                    "spreadsheet": "",  # 任意設定項目（用途に応じて指定）
                    "sheet_name": "",  # 任意設定項目（用途に応じて指定）
                }
            )

        @staticmethod
        def delete_spreadsheet_sheet() -> OperationTemplate:
            """シート削除"""
            return OperationTemplate(
                specific_params={
                    "spreadsheet": "",  # 任意設定項目（用途に応じて指定）
                    "sheet_name": "",  # 任意設定項目（用途に応じて指定）
                }
            )

        @staticmethod
        def move_spreadsheet_sheet() -> OperationTemplate:
            """スプレッドシートのシート移動"""
            return OperationTemplate(
                specific_params={
                    "spreadsheet": "",  # 任意設定項目（用途に応じて指定）
                    "sheet_name": "",  # 任意設定項目（用途に応じて指定）
                    "target_position": "last",  # 任意設定項目（用途に応じて指定）
                    "target_sheet": "",  # 任意設定項目（用途に応じて指定）
                }
            )

        @staticmethod
        def copy_spreadsheet_sheet() -> OperationTemplate:
            """スプレッドシートのシートコピー"""
            return OperationTemplate(
                specific_params={
                    "spreadsheet": "",  # 任意設定項目（用途に応じて指定）
                    "sheet_name": "",  # 任意設定項目（用途に応じて指定）
                    "target_spreadsheet": "",  # 任意設定項目（用途に応じて指定）
                    "copy_sheet_name": "",  # 任意設定項目（用途に応じて指定）
                }
            )

        @staticmethod
        def get_spreadsheet_sheet_name() -> OperationTemplate:
            """スプレッドシートのシート名取得"""
            return OperationTemplate(
                specific_params={
                    "variable": "名前",  # 値やウィンドウを保持する変数名
                    "spreadsheet": "",  # 任意設定項目（用途に応じて指定）
                    "target_position": "by-index",  # 任意設定項目（用途に応じて指定）
                    "target_index": "",  # 任意設定項目（用途に応じて指定）
                }
            )

        @staticmethod
        def rename_spreadsheet_sheet() -> OperationTemplate:
            """スプレッドシートのシート名変更"""
            return OperationTemplate(
                specific_params={
                    "spreadsheet": "",  # 任意設定項目（用途に応じて指定）
                    "sheet_name": "",  # 任意設定項目（用途に応じて指定）
                    "rename": "",  # 任意設定項目（用途に応じて指定）
                }
            )

    class Cell:
        """セル操作関連"""

        @staticmethod
        def delete_spreadsheet_range() -> OperationTemplate:
            """スプレッドシート指定範囲を削除"""
            return OperationTemplate(
                specific_params={
                    "spreadsheet": "",  # 任意設定項目（用途に応じて指定）
                    "sheet_name": "",  # 任意設定項目（用途に応じて指定）
                    "range": "",  # 任意設定項目（用途に応じて指定）
                    "shift_type": "rows",  # 任意設定項目（用途に応じて指定）
                }
            )

        @staticmethod
        def insert_spreadsheet_range() -> OperationTemplate:
            """スプレッドシート指定範囲にセルを挿入"""
            return OperationTemplate(
                specific_params={
                    "spreadsheet": "",  # 任意設定項目（用途に応じて指定）
                    "sheet_name": "",  # 任意設定項目（用途に応じて指定）
                    "range": "",  # 任意設定項目（用途に応じて指定）
                    "shift_type": "rows",  # 任意設定項目（用途に応じて指定）
                }
            )

        @staticmethod
        def get_spreadsheet_values() -> OperationTemplate:
            """スプレッドシートのセル値を取得"""
            return OperationTemplate(
                specific_params={
                    "spreadsheet": "",  # 任意設定項目（用途に応じて指定）
                    "sheet_name": "",  # 任意設定項目（用途に応じて指定）
                    "range": "",  # 任意設定項目（用途に応じて指定）
                    "variable": "データ",  # 値やウィンドウを保持する変数名
                    "type": "formatted-value",  # 任意設定項目（用途に応じて指定）
                }
            )

        @staticmethod
        def set_spreadsheet_values() -> OperationTemplate:
            """スプレッドシートのセル値を入力"""
            return OperationTemplate(
                specific_params={
                    "spreadsheet": "",  # 任意設定項目（用途に応じて指定）
                    "sheet_name": "",  # 任意設定項目（用途に応じて指定）
                    "range": "",  # 任意設定項目（用途に応じて指定）
                    "single_cell": "single",  # 任意設定項目（用途に応じて指定）
                    "string": "",  # メッセージや対象文字列
                }
            )

        @staticmethod
        def copy_paste_spreadsheet() -> OperationTemplate:
            """スプレッドシートのセルをコピー・貼り付け"""
            return OperationTemplate(
                specific_params={
                    "spreadsheet": "",  # 任意設定項目（用途に応じて指定）
                    "src_sheet": "",  # 任意設定項目（用途に応じて指定）
                    "src_range": "",  # 任意設定項目（用途に応じて指定）
                    "dst_sheet": "",  # 任意設定項目（用途に応じて指定）
                    "dst_range": "",  # 任意設定項目（用途に応じて指定）
                    "paste_type": "PASTE_NORMAL",  # 任意設定項目（用途に応じて指定）
                }
            )

        @staticmethod
        def get_spreadsheet_last_row() -> OperationTemplate:
            """スプレッドシート最終行取得"""
            return OperationTemplate(
                specific_params={
                    "spreadsheet": "",  # 任意設定項目（用途に応じて指定）
                    "sheet_name": "",  # 任意設定項目（用途に応じて指定）
                    "target_type": "col",  # 任意設定項目（用途に応じて指定）
                    "target_col": "",  # 任意設定項目（用途に応じて指定）
                    "variable": "最終行",  # 値やウィンドウを保持する変数名
                }
            )

        @staticmethod
        def loop_spreadsheet_row() -> OperationTemplate:
            """スプレッドシート行ループ"""
            return OperationTemplate(
                specific_params={
                    "spreadsheet": "",  # 任意設定項目（用途に応じて指定）
                    "sheet_name": "",  # 任意設定項目（用途に応じて指定）
                    "count": 1,  # 任意設定項目（用途に応じて指定）
                    "terminate_value": "",  # 任意設定項目（用途に応じて指定）
                    "terminate_row": 1,  # 任意設定項目（用途に応じて指定）
                    "end_condition_type": "row",  # 任意設定項目（用途に応じて指定）
                    "start_cell": "A1",  # 任意設定項目（用途に応じて指定）
                    "variable": "行番号",  # 値やウィンドウを保持する変数名
                    "variable2": "セル値",  # 任意設定項目（用途に応じて指定）
                }
            )

        @staticmethod
        def loop_spreadsheet_col() -> OperationTemplate:
            """スプレッドシート列ループ"""
            return OperationTemplate(
                specific_params={
                    "spreadsheet": "",  # 任意設定項目（用途に応じて指定）
                    "sheet_name": "",  # 任意設定項目（用途に応じて指定）
                    "count": 1,  # 任意設定項目（用途に応じて指定）
                    "terminate_value": "",  # 任意設定項目（用途に応じて指定）
                    "terminate_col": 1,  # 任意設定項目（用途に応じて指定）
                    "end_condition_type": "col",  # 任意設定項目（用途に応じて指定）
                    "start_cell": "A1",  # 任意設定項目（用途に応じて指定）
                    "variable": "列番号",  # 値やウィンドウを保持する変数名
                    "variable2": "セル値",  # 任意設定項目（用途に応じて指定）
                }
            )