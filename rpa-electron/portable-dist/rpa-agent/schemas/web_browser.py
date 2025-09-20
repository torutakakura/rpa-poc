"""
L. ウェブブラウザ操作のスキーマ定義
"""

from .base import OperationTemplate


class WebBrowserOperations:
    """ウェブブラウザ操作の定義"""

    @staticmethod
    def create_operation(operation_type: str) -> OperationTemplate:
        """ウェブブラウザ操作のテンプレートを作成"""
        templates = {
            "open": {
                "url": "",
                "browser": "chrome",
                "incognito": False,
                "maximize": True,
            },
            "close": {
                "target": "current",
            },
            "navigate": {
                "url": "",
                "wait_for_load": True,
            },
            "click": {
                "selector": "",
                "selector_type": "css",
                "wait_before": 0,
            },
            "input": {
                "selector": "",
                "selector_type": "css",
                "text": "",
                "clear_before": True,
            },
            "select": {
                "selector": "",
                "selector_type": "css",
                "value": "",
                "by": "value",
            },
            "get_text": {
                "selector": "",
                "selector_type": "css",
                "storage_key": "",
            },
            "wait": {
                "selector": "",
                "selector_type": "css",
                "timeout": 30,
                "condition": "visible",
            },
            "scroll": {
                "direction": "down",
                "amount": 300,
                "element_selector": "",
            },
            "screenshot": {
                "save_path": "",
                "full_page": False,
                "element_selector": "",
            },
            "execute_js": {
                "script": "",
                "return_value": False,
                "storage_key": "",
            },
            "switch_tab": {
                "tab_index": 0,
                "tab_title": "",
            },
            "refresh": {
                "wait_for_load": True,
                "hard_refresh": False,
            },
        }

        return OperationTemplate(specific_params=templates.get(operation_type, {}))
