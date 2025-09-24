"""
分岐処理関連のステップ定義（簡略版）
"""
from dataclasses import dataclass, field
from typing import List, Optional
from .base import BaseStep, StepParameter


@dataclass
class BranchingStep(BaseStep):
    """分岐ステップの汎用クラス"""
    def __init__(self, cmd: str, cmd_nickname: str, version: int = 1, parameters: dict = None, **kwargs):
        if parameters is None:
            parameters = {}

        # 分岐ステップは2つのシーケンスを持つ
        sequence_0 = kwargs.pop('sequence_0', [])
        sequence_1 = kwargs.pop('sequence_1', [])

        super().__init__(
            cmd=cmd,
            cmd_nickname=cmd_nickname,
            cmd_type="branching",
            version=version,
            parameters=parameters,
            sequence_0=sequence_0,
            sequence_1=sequence_1,
            **kwargs
        )