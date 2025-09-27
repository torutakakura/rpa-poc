"""
ファイル操作関連のステップ定義（簡略版）
"""
from dataclasses import dataclass
from .base import BaseStep


@dataclass
class FileStep(BaseStep):
    """ファイルステップの汎用クラス"""
    def __init__(self, cmd: str, cmd_nickname: str, version: int = 1, parameters: dict = None, **kwargs):
        if parameters is None:
            parameters = {}

        super().__init__(
            cmd=cmd,
            cmd_nickname=cmd_nickname,
            cmd_type="file",
            version=version,
            parameters=parameters,
            **kwargs
        )