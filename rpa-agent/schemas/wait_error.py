"""
B. 待機・終了・エラー操作のスキーマ定義
"""

from .base import CommonParams, ErrorHandling, OperationTemplate


class WaitErrorOperations:
    """待機・終了・エラー操作の定義"""

    @staticmethod
    def wait_seconds() -> OperationTemplate:
        """秒"""
        return OperationTemplate(specific_params={"wait_seconds": 1})

    @staticmethod
    def wait_for_image() -> OperationTemplate:
        """画像出現を待つ"""
        return OperationTemplate(
            common_params=CommonParams(timeout=60),
            specific_params={
                "image_path": "",
                "accuracy": 0.8,
                "search_area": "full_screen",
                "coordinates": {"x": 0, "y": 0, "width": 0, "height": 0},
            },
        )

    @staticmethod
    def continue_confirmation() -> OperationTemplate:
        """続行確認"""
        return OperationTemplate(specific_params={"message": "", "title": "続行確認"})

    @staticmethod
    def timed_continue_confirmation() -> OperationTemplate:
        """タイマー付き続行確認（秒）"""
        return OperationTemplate(
            specific_params={
                "message": "",
                "title": "続行確認",
                "countdown_seconds": 10,
            }
        )

    @staticmethod
    def change_command_interval() -> OperationTemplate:
        """コマンド間待機時間を変更"""
        return OperationTemplate(specific_params={"interval_ms": 500})

    @staticmethod
    def force_terminate() -> OperationTemplate:
        """作業強制終了"""
        return OperationTemplate(specific_params={"exit_code": 0})

    @staticmethod
    def raise_error() -> OperationTemplate:
        """エラー発生"""
        return OperationTemplate(
            specific_params={"error_message": "", "error_code": ""}
        )

    @staticmethod
    def error_handling() -> OperationTemplate:
        """エラー確認・処理"""
        return OperationTemplate(
            common_params=CommonParams(error_handling=ErrorHandling.CONTINUE.value),
            specific_params={"on_error_steps": [], "clear_error": True},
        )

    @staticmethod
    def error_handling_with_retry() -> OperationTemplate:
        """エラー確認・処理（リトライ前処理）"""
        return OperationTemplate(
            common_params=CommonParams(
                retry_count=3, error_handling=ErrorHandling.RETRY.value
            ),
            specific_params={
                "retry_interval": 5,
                "on_retry_steps": [],
                "on_error_steps": [],
            },
        )
