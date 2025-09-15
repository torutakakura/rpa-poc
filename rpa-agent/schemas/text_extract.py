"""
F. 文字抽出操作のスキーマ定義
"""

from .base import OperationTemplate


class TextExtractOperations:
    """文字抽出操作の定義"""

    @staticmethod
    def from_brackets() -> OperationTemplate:
        """括弧・引用符号から"""
        return OperationTemplate(
            specific_params={
                "storage_key": "",
                "source_text": "",
                "bracket_type": "parentheses",
                "occurrence": 1,
            }
        )

    @staticmethod
    def from_delimiter() -> OperationTemplate:
        """区切り文字から"""
        return OperationTemplate(
            specific_params={
                "storage_key": "",
                "source_text": "",
                "delimiter": ",",
                "position": 1,
            }
        )

    @staticmethod
    def remove_whitespace() -> OperationTemplate:
        """改行・空白を削除"""
        return OperationTemplate(
            specific_params={
                "storage_key": "",
                "source_text": "",
                "remove_newlines": True,
                "remove_spaces": True,
                "remove_tabs": True,
            }
        )

    @staticmethod
    def from_filepath() -> OperationTemplate:
        """ファイルパスから"""
        return OperationTemplate(
            specific_params={
                "storage_key": "",
                "file_path": "",
                "extract_type": "filename",
            }
        )

    @staticmethod
    def match_pattern() -> OperationTemplate:
        """ルールにマッチ"""
        return OperationTemplate(
            specific_params={
                "storage_key": "",
                "source_text": "",
                "pattern": "",
                "regex": False,
                "occurrence": 1,
            }
        )

    @staticmethod
    def replace() -> OperationTemplate:
        """置換"""
        return OperationTemplate(
            specific_params={
                "storage_key": "",
                "source_text": "",
                "find": "",
                "replace": "",
                "replace_all": True,
            }
        )

    @staticmethod
    def convert_text() -> OperationTemplate:
        """文字変換"""
        return OperationTemplate(
            specific_params={
                "storage_key": "",
                "source_text": "",
                "conversion_type": "uppercase",
            }
        )

    @staticmethod
    def convert_date_format() -> OperationTemplate:
        """日付形式変換"""
        return OperationTemplate(
            specific_params={
                "storage_key": "",
                "source_date": "",
                "source_format": "yyyy/MM/dd",
                "target_format": "yyyy-MM-dd",
            }
        )

    @staticmethod
    def loop_lines() -> OperationTemplate:
        """1行ずつループ"""
        return OperationTemplate(
            specific_params={
                "source_text": "",
                "line_storage_key": "",
                "index_storage_key": "",
                "loop_steps": [],
            }
        )