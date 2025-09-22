"""
D. キーボード操作のスキーマ定義
"""

from .base import OperationTemplate


class KeyboardOperations:
    """キーボード操作の定義"""

    class Input:
        @staticmethod
        def typewrite_static_string() -> OperationTemplate:
            """キーボード入力（文字）"""
            return OperationTemplate(
                specific_params={
                    "string": "",  # メッセージや対象文字列
                    "enter": False,  # True/False - 任意設定項目（用途に応じて指定）
                }
            )

        @staticmethod
        def typewrite_all_string() -> OperationTemplate:
            """キーボード入力（貼り付け）"""
            return OperationTemplate(
                specific_params={
                    "string": "",  # メッセージや対象文字列
                    "enter": False,  # True/False - 任意設定項目（用途に応じて指定）
                }
            )

        @staticmethod
        def typewrite_password() -> OperationTemplate:
            """キーボード入力（パスワード）"""
            return OperationTemplate(
                specific_params={
                    "enter": False,  # True/False - 任意設定項目（用途に応じて指定）
                    "password_type": "type-input",  # type-input/ほか - 任意設定項目（用途に応じて指定）
                    "ciphertext": "",  # 任意設定項目（用途に応じて指定）
                    "nonce": "",  # 任意設定項目（用途に応じて指定）
                    "encryption": 1,  # 任意設定項目（用途に応じて指定）
                }
            )

        @staticmethod
        def type_hotkeys() -> OperationTemplate:
            """ショートカットキーを入力"""
            return OperationTemplate(
                specific_params={
                    "key_0": "__null__",  # 任意設定項目（用途に応じて指定）
                    "key_1": "__null__",  # 任意設定項目（用途に応じて指定）
                    "key_2": "__null__",  # 任意設定項目（用途に応じて指定）
                    "key_3": "",  # 任意設定項目（用途に応じて指定）
                }
            )
