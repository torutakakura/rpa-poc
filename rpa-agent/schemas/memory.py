"""
E. 記憶操作のスキーマ定義
"""

from .base import CommonParams, OperationTemplate


class MemoryOperations:
    """記憶操作の定義"""

    @staticmethod
    def store_text() -> OperationTemplate:
        """文字"""
        return OperationTemplate(specific_params={"storage_key": "", "value": ""})

    @staticmethod
    def store_password() -> OperationTemplate:
        """パスワード"""
        return OperationTemplate(
            specific_params={"storage_key": "", "value": "", "encrypted": True}
        )

    @staticmethod
    def store_environment_info() -> OperationTemplate:
        """環境情報"""
        return OperationTemplate(
            specific_params={"storage_key": "", "info_type": "computer_name"}
        )

    @staticmethod
    def store_date() -> OperationTemplate:
        """日付"""
        return OperationTemplate(
            specific_params={
                "storage_key": "",
                "date_type": "today",
                "format": "yyyy/MM/dd",
            }
        )

    @staticmethod
    def store_business_date() -> OperationTemplate:
        """日付（営業日）"""
        return OperationTemplate(
            specific_params={
                "storage_key": "",
                "business_days": 1,
                "format": "yyyy/MM/dd",
                "holiday_calendar": "japan",
            }
        )

    @staticmethod
    def store_weekday_date() -> OperationTemplate:
        """日付（曜日）"""
        return OperationTemplate(
            specific_params={
                "storage_key": "",
                "target_weekday": "monday",
                "direction": "next",
                "format": "yyyy/MM/dd",
            }
        )

    @staticmethod
    def calculate_date() -> OperationTemplate:
        """日付計算"""
        return OperationTemplate(
            specific_params={
                "storage_key": "",
                "base_date": "today",
                "operation": "add",
                "days": 0,
                "months": 0,
                "years": 0,
                "format": "yyyy/MM/dd",
            }
        )

    @staticmethod
    def store_weekday() -> OperationTemplate:
        """曜日"""
        return OperationTemplate(
            specific_params={"storage_key": "", "date": "today", "format": "japanese"}
        )

    @staticmethod
    def store_time() -> OperationTemplate:
        """時刻"""
        return OperationTemplate(
            specific_params={"storage_key": "", "format": "HH:mm:ss"}
        )

    @staticmethod
    def calculate_time() -> OperationTemplate:
        """時刻計算"""
        return OperationTemplate(
            specific_params={
                "storage_key": "",
                "base_time": "now",
                "operation": "add",
                "hours": 0,
                "minutes": 0,
                "seconds": 0,
                "format": "HH:mm:ss",
            }
        )

    @staticmethod
    def calculate() -> OperationTemplate:
        """計算"""
        return OperationTemplate(
            specific_params={"storage_key": "", "expression": "", "decimal_places": 2}
        )

    @staticmethod
    def random_number() -> OperationTemplate:
        """乱数"""
        return OperationTemplate(
            specific_params={"storage_key": "", "min": 0, "max": 100, "type": "integer"}
        )

    @staticmethod
    def get_clipboard() -> OperationTemplate:
        """コピー内容"""
        return OperationTemplate(specific_params={"storage_key": ""})

    @staticmethod
    def set_clipboard() -> OperationTemplate:
        """クリップボードへコピー"""
        return OperationTemplate(specific_params={"value": ""})

    @staticmethod
    def runtime_input() -> OperationTemplate:
        """実行中に入力"""
        return OperationTemplate(
            common_params=CommonParams(timeout=300),
            specific_params={
                "storage_key": "",
                "prompt": "",
                "input_type": "text",
                "default_value": "",
            },
        )

    @staticmethod
    def file_modified_date() -> OperationTemplate:
        """ファイル更新日時"""
        return OperationTemplate(
            specific_params={
                "storage_key": "",
                "file_path": "",
                "format": "yyyy/MM/dd HH:mm:ss",
            }
        )

    @staticmethod
    def file_size() -> OperationTemplate:
        """ファイルサイズ"""
        return OperationTemplate(
            specific_params={"storage_key": "", "file_path": "", "unit": "bytes"}
        )

    @staticmethod
    def latest_file_or_folder() -> OperationTemplate:
        """最新ファイル・フォルダ"""
        return OperationTemplate(
            specific_params={
                "storage_key": "",
                "directory_path": "",
                "target_type": "file",
                "pattern": "*.*",
            }
        )