"""
J. エクセル・CSV操作のスキーマ定義
"""

from .base import CommonParams, OperationTemplate


class ExcelOperations:
    """エクセル・CSV操作の定義"""

    class Workbook:
        @staticmethod
        def open() -> OperationTemplate:
            """ブックを開く"""
            return OperationTemplate(
                specific_params={
                    "file_path": "",
                    "reference_id": "",
                    "read_only": False,
                    "password": "",
                    "update_links": False,
                }
            )

        @staticmethod
        def remember() -> OperationTemplate:
            """ブックを覚える"""
            return OperationTemplate(
                specific_params={"reference_id": "", "workbook_name": ""}
            )

        @staticmethod
        def save() -> OperationTemplate:
            """ブックを保存"""
            return OperationTemplate(
                specific_params={
                    "reference_id": "",
                    "save_as": False,
                    "file_path": "",
                    "file_format": "xlsx",
                }
            )

        @staticmethod
        def close() -> OperationTemplate:
            """ブックを閉じる"""
            return OperationTemplate(
                specific_params={"reference_id": "", "save_changes": True}
            )

    class Sheet:
        @staticmethod
        def create() -> OperationTemplate:
            """新規作成"""
            return OperationTemplate(
                specific_params={
                    "reference_id": "",
                    "sheet_name": "",
                    "position": "last",
                }
            )

        @staticmethod
        def delete() -> OperationTemplate:
            """削除"""
            return OperationTemplate(
                specific_params={"reference_id": "", "sheet_name": ""}
            )

        @staticmethod
        def switch() -> OperationTemplate:
            """切り替え"""
            return OperationTemplate(
                specific_params={
                    "reference_id": "",
                    "sheet_name": "",
                    "sheet_index": None,
                }
            )

        @staticmethod
        def move_or_copy() -> OperationTemplate:
            """移動・コピー"""
            return OperationTemplate(
                specific_params={
                    "reference_id": "",
                    "source_sheet": "",
                    "action": "move",
                    "position": "last",
                    "new_name": "",
                }
            )

        @staticmethod
        def get_name() -> OperationTemplate:
            """名前取得"""
            return OperationTemplate(
                specific_params={
                    "reference_id": "",
                    "storage_key": "",
                    "sheet_index": None,
                }
            )

        @staticmethod
        def rename() -> OperationTemplate:
            """名前変更"""
            return OperationTemplate(
                specific_params={"reference_id": "", "old_name": "", "new_name": ""}
            )

    class Cell:
        @staticmethod
        def select_range() -> OperationTemplate:
            """範囲指定"""
            return OperationTemplate(
                specific_params={"reference_id": "", "range": "A1", "select": True}
            )

        @staticmethod
        def move_range() -> OperationTemplate:
            """指定範囲の移動"""
            return OperationTemplate(
                specific_params={
                    "reference_id": "",
                    "source_range": "A1",
                    "target_range": "B1",
                    "cut": True,
                }
            )

        @staticmethod
        def delete_range() -> OperationTemplate:
            """指定範囲の削除"""
            return OperationTemplate(
                specific_params={"reference_id": "", "range": "A1", "shift": "up"}
            )

        @staticmethod
        def insert_cells() -> OperationTemplate:
            """指定範囲にセルを挿入"""
            return OperationTemplate(
                specific_params={"reference_id": "", "range": "A1", "shift": "down"}
            )

        @staticmethod
        def get_value() -> OperationTemplate:
            """値を取得"""
            return OperationTemplate(
                specific_params={
                    "reference_id": "",
                    "range": "A1",
                    "storage_key": "",
                    "value_type": "value",
                }
            )

        @staticmethod
        def set_value() -> OperationTemplate:
            """値を入力"""
            return OperationTemplate(
                specific_params={
                    "reference_id": "",
                    "range": "A1",
                    "value": "",
                    "value_type": "value",
                }
            )

        @staticmethod
        def copy_cells() -> OperationTemplate:
            """セルをコピー"""
            return OperationTemplate(
                specific_params={"reference_id": "", "range": "A1"}
            )

        @staticmethod
        def paste_cells() -> OperationTemplate:
            """セルを貼り付け"""
            return OperationTemplate(
                specific_params={"reference_id": "", "range": "A1", "paste_type": "all"}
            )

        @staticmethod
        def find_position() -> OperationTemplate:
            """位置を取得"""
            return OperationTemplate(
                specific_params={
                    "reference_id": "",
                    "search_value": "",
                    "search_range": "",
                    "row_storage_key": "",
                    "column_storage_key": "",
                }
            )

        @staticmethod
        def get_last_row() -> OperationTemplate:
            """最終行取得"""
            return OperationTemplate(
                specific_params={"reference_id": "", "column": "A", "storage_key": ""}
            )

        @staticmethod
        def get_last_column() -> OperationTemplate:
            """最終列取得"""
            return OperationTemplate(
                specific_params={"reference_id": "", "row": 1, "storage_key": ""}
            )

        @staticmethod
        def column_calculation() -> OperationTemplate:
            """列計算"""
            return OperationTemplate(
                specific_params={
                    "reference_id": "",
                    "range": "A:A",
                    "operation": "sum",
                    "storage_key": "",
                }
            )

        @staticmethod
        def run_macro() -> OperationTemplate:
            """マクロ実行"""
            return OperationTemplate(
                common_params=CommonParams(timeout=60),
                specific_params={"reference_id": "", "macro_name": "", "arguments": []},
            )

        @staticmethod
        def row_loop() -> OperationTemplate:
            """行ループ"""
            return OperationTemplate(
                specific_params={
                    "reference_id": "",
                    "start_row": 1,
                    "end_row": None,
                    "row_storage_key": "",
                    "loop_steps": [],
                }
            )

        @staticmethod
        def column_loop() -> OperationTemplate:
            """列ループ"""
            return OperationTemplate(
                specific_params={
                    "reference_id": "",
                    "start_column": "A",
                    "end_column": None,
                    "column_storage_key": "",
                    "loop_steps": [],
                }
            )

        @staticmethod
        def csv_read_loop() -> OperationTemplate:
            """CSV読込ループ"""
            return OperationTemplate(
                specific_params={
                    "file_path": "",
                    "encoding": "utf-8",
                    "delimiter": ",",
                    "has_header": True,
                    "row_storage_keys": {},
                    "loop_steps": [],
                }
            )
