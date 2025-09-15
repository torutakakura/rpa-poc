"""
H. 繰り返し操作のスキーマ定義
"""

from .base import OperationTemplate


class LoopOperations:
    """繰り返し操作の定義"""

    @staticmethod
    def loop() -> OperationTemplate:
        """繰り返し"""
        return OperationTemplate(
            specific_params={
                "loop_type": "count",
                "count": 10,
                "condition": "",
                "max_iterations": 1000,
                "index_storage_key": "",
                "loop_steps": [],
            }
        )

    @staticmethod
    def break_loop() -> OperationTemplate:
        """繰り返しを抜ける"""
        return OperationTemplate(specific_params={"condition": ""})

    @staticmethod
    def continue_loop() -> OperationTemplate:
        """繰り返しの最初に戻る"""
        return OperationTemplate(specific_params={"condition": ""})
