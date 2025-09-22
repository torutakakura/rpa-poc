"""
N. 特殊アプリ操作のスキーマ定義
"""

from .base import OperationTemplate


class SpecialAppOperations:
    """特殊アプリ操作の定義"""

    @staticmethod
    def click_uia_element() -> OperationTemplate:
        """アプリをクリック"""
        return OperationTemplate(
            specific_params={
                "window": "__uia_focused_window__",  # 対象ウィンドウ指定（既定は最前面など）
                "controlType": 50000,  # 任意設定項目（用途に応じて指定）
                "frameworkId": "",  # 任意設定項目（用途に応じて指定）
                "className": "",  # 任意設定項目（用途に応じて指定）
                "identifier": "name",  # 任意設定項目（用途に応じて指定）
                "automationId": "",  # 任意設定項目（用途に応じて指定）
                "name": "",  # 任意設定項目（用途に応じて指定）
                "index": "",  # 任意設定項目（用途に応じて指定）
                "depth": "",  # 任意設定項目（用途に応じて指定）
                "ancestors": "None",  # 任意設定項目（用途に応じて指定）
                "search_level": 1,  # 任意設定項目（用途に応じて指定）
                "clicktype": "click-uia",  # 任意設定項目（用途に応じて指定）
            }
        )

    @staticmethod
    def send_text_to_uia_element() -> OperationTemplate:
        """アプリ文字入力"""
        return OperationTemplate(
            specific_params={
                "window": "__uia_focused_window__",  # 対象ウィンドウ指定（既定は最前面など）
                "controlType": 50000,  # 任意設定項目（用途に応じて指定）
                "frameworkId": "",  # 任意設定項目（用途に応じて指定）
                "className": "",  # 任意設定項目（用途に応じて指定）
                "identifier": "name",  # 任意設定項目（用途に応じて指定）
                "automationId": "",  # 任意設定項目（用途に応じて指定）
                "name": "",  # 任意設定項目（用途に応じて指定）
                "index": "",  # 任意設定項目（用途に応じて指定）
                "depth": "",  # 任意設定項目（用途に応じて指定）
                "ancestors": "None",  # 任意設定項目（用途に応じて指定）
                "search_level": 1,  # 任意設定項目（用途に応じて指定）
                "string": "",  # メッセージや対象文字列
            }
        )

    @staticmethod
    def send_password_to_uia_element() -> OperationTemplate:
        """アプリ文字入力（パスワード）"""
        return OperationTemplate(
            specific_params={
                "window": "__uia_focused_window__",  # 対象ウィンドウ指定（既定は最前面など）
                "controlType": 50000,  # 任意設定項目（用途に応じて指定）
                "frameworkId": "",  # 任意設定項目（用途に応じて指定）
                "className": "",  # 任意設定項目（用途に応じて指定）
                "identifier": "name",  # 任意設定項目（用途に応じて指定）
                "automationId": "",  # 任意設定項目（用途に応じて指定）
                "name": "",  # 任意設定項目（用途に応じて指定）
                "index": "",  # 任意設定項目（用途に応じて指定）
                "depth": "",  # 任意設定項目（用途に応じて指定）
                "ancestors": "None",  # 任意設定項目（用途に応じて指定）
                "search_level": 1,  # 任意設定項目（用途に応じて指定）
                "password_type": "type-input",  # 任意設定項目（用途に応じて指定）
                "ciphertext": "",  # 任意設定項目（用途に応じて指定）
                "nonce": "",  # 任意設定項目（用途に応じて指定）
                "encryption": 1,  # 任意設定項目（用途に応じて指定）
            }
        )

    @staticmethod
    def get_uia_element_clickable_point() -> OperationTemplate:
        """アプリ座標取得"""
        return OperationTemplate(
            specific_params={
                "window": "__uia_focused_window__",  # 対象ウィンドウ指定（既定は最前面など）
                "controlType": 50000,  # 任意設定項目（用途に応じて指定）
                "frameworkId": "",  # 任意設定項目（用途に応じて指定）
                "className": "",  # 任意設定項目（用途に応じて指定）
                "identifier": "name",  # 任意設定項目（用途に応じて指定）
                "automationId": "",  # 任意設定項目（用途に応じて指定）
                "name": "",  # 任意設定項目（用途に応じて指定）
                "index": "",  # 任意設定項目（用途に応じて指定）
                "depth": "",  # 任意設定項目（用途に応じて指定）
                "ancestors": "None",  # 任意設定項目（用途に応じて指定）
                "search_level": 1,  # 任意設定項目（用途に応じて指定）
                "x": "X",  # 任意設定項目（用途に応じて指定）
                "y": "Y",  # 任意設定項目（用途に応じて指定）
            }
        )

    @staticmethod
    def get_text_from_uia_element() -> OperationTemplate:
        """アプリ文字取得"""
        return OperationTemplate(
            specific_params={
                "window": "__uia_focused_window__",  # 対象ウィンドウ指定（既定は最前面など）
                "controlType": 50000,  # 任意設定項目（用途に応じて指定）
                "frameworkId": "",  # 任意設定項目（用途に応じて指定）
                "className": "",  # 任意設定項目（用途に応じて指定）
                "identifier": "name",  # 任意設定項目（用途に応じて指定）
                "automationId": "",  # 任意設定項目（用途に応じて指定）
                "name": "",  # 任意設定項目（用途に応じて指定）
                "index": "",  # 任意設定項目（用途に応じて指定）
                "depth": "",  # 任意設定項目（用途に応じて指定）
                "ancestors": "None",  # 任意設定項目（用途に応じて指定）
                "search_level": 1,  # 任意設定項目（用途に応じて指定）
                "variable": "取得文字",  # 値やウィンドウを保持する変数名
            }
        )