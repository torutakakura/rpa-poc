"""
A. アプリ・画面操作のスキーマ定義
"""

from .base import CommonParams, OperationTemplate


class AppOperations:
    """アプリ操作の定義"""

    @staticmethod
    def launch() -> OperationTemplate:
        """起動"""
        return OperationTemplate(
            specific_params={
                "app_path": "",
                "wait_time": 5,
                "maximize_window": False,
                "arguments": "",
                "working_directory": "",
            }
        )

    @staticmethod
    def launch_and_wait() -> OperationTemplate:
        """起動（終了待ち）"""
        return OperationTemplate(
            common_params=CommonParams(timeout=300),
            specific_params={
                "app_path": "",
                "maximize_window": False,
                "arguments": "",
                "working_directory": "",
            },
        )


class ScreenOperations:
    """画面操作の定義"""

    @staticmethod
    def remember_foreground() -> OperationTemplate:
        """最前画面を覚える"""
        return OperationTemplate(specific_params={"reference_id": ""})

    @staticmethod
    def remember_by_name() -> OperationTemplate:
        """画面を覚える（名前）"""
        return OperationTemplate(
            specific_params={
                "window_name": "",
                "reference_id": "",
                "partial_match": False,
            }
        )

    @staticmethod
    def switch_by_reference() -> OperationTemplate:
        """切り替え（参照ID）"""
        return OperationTemplate(specific_params={"reference_id": ""})

    @staticmethod
    def switch_by_name() -> OperationTemplate:
        """切り替え（名前）"""
        return OperationTemplate(
            specific_params={"window_name": "", "partial_match": False}
        )

    @staticmethod
    def get_window_name() -> OperationTemplate:
        """画面の名前を取得"""
        return OperationTemplate(specific_params={"storage_key": ""})

    @staticmethod
    def move() -> OperationTemplate:
        """移動"""
        return OperationTemplate(
            specific_params={"x": 0, "y": 0, "width": 800, "height": 600}
        )

    @staticmethod
    def maximize_minimize() -> OperationTemplate:
        """最大化/最小化"""
        return OperationTemplate(specific_params={"action": "maximize"})

    @staticmethod
    def take_screenshot() -> OperationTemplate:
        """スクリーンショットを撮る"""
        return OperationTemplate(
            specific_params={
                "save_path": "",
                "capture_area": "full_screen",
                "coordinates": {"x": 0, "y": 0, "width": 0, "height": 0},
            }
        )