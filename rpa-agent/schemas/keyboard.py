"""
D. キーボード操作のスキーマ定義
"""

from .base import OperationTemplate


class KeyboardOperations:
    """キーボード操作の定義"""

    class Input:
        @staticmethod
        def text() -> OperationTemplate:
            """文字"""
            return OperationTemplate(
                specific_params={
                    "text": "",
                    "typing_speed": "normal",
                    "clear_before": False,
                }
            )

        @staticmethod
        def paste() -> OperationTemplate:
            """文字（貼り付け）"""
            return OperationTemplate(
                specific_params={"text": "", "clear_before": False}
            )

        @staticmethod
        def password() -> OperationTemplate:
            """パスワード"""
            return OperationTemplate(
                specific_params={
                    "password_key": "",
                    "clear_before": False,
                    "encrypted": True,
                }
            )

        @staticmethod
        def shortcut() -> OperationTemplate:
            """ショートカットキー"""
            return OperationTemplate(specific_params={"keys": [], "hold_duration": 0})
