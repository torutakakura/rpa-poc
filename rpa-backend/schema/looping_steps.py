"""
ループ処理関連のステップ定義（簡略版）
"""
from dataclasses import dataclass, field
from typing import List, Optional
from .base import BaseStep, StepParameter


@dataclass
class LoopingStep(BaseStep):
    """ループステップの汎用クラス"""
    def __init__(self, cmd: str, cmd_nickname: str, version: int = 1, parameters: dict = None, **kwargs):
        if parameters is None:
            parameters = {}

        # ループステップは内部シーケンスを持つ
        sequence = kwargs.pop('sequence', [])

        super().__init__(
            cmd=cmd,
            cmd_nickname=cmd_nickname,
            cmd_type="looping",
            version=version,
            parameters=parameters,
            sequence=sequence,
            **kwargs
        )