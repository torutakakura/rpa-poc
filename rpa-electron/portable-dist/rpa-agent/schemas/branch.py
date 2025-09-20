"""
G. 分岐操作のスキーマ定義
"""

from .base import OperationTemplate


class BranchOperations:
    """分岐操作の定義"""

    @staticmethod
    def string_condition() -> OperationTemplate:
        """文字列"""
        return OperationTemplate(
            specific_params={
                "left_value": "",
                "operator": "equals",
                "right_value": "",
                "case_sensitive": True,
                "true_steps": [],
                "false_steps": [],
            }
        )

    @staticmethod
    def numeric_condition() -> OperationTemplate:
        """数値"""
        return OperationTemplate(
            specific_params={
                "left_value": 0,
                "operator": "equals",
                "right_value": 0,
                "true_steps": [],
                "false_steps": [],
            }
        )

    @staticmethod
    def date_condition() -> OperationTemplate:
        """日付"""
        return OperationTemplate(
            specific_params={
                "left_date": "",
                "operator": "equals",
                "right_date": "",
                "date_format": "yyyy/MM/dd",
                "true_steps": [],
                "false_steps": [],
            }
        )

    @staticmethod
    def file_exists() -> OperationTemplate:
        """ファイル・フォルダの有/無を確認"""
        return OperationTemplate(
            specific_params={
                "path": "",
                "check_type": "exists",
                "true_steps": [],
                "false_steps": [],
            }
        )

    @staticmethod
    def image_exists() -> OperationTemplate:
        """画像"""
        return OperationTemplate(
            specific_params={
                "image_path": "",
                "accuracy": 0.8,
                "search_area": "full_screen",
                "found_steps": [],
                "not_found_steps": [],
            }
        )
