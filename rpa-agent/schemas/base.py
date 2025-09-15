"""
共通定義とベースクラス
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict


class ErrorHandling(Enum):
    """エラーハンドリングの種類"""

    STOP = "stop"
    CONTINUE = "continue"
    RETRY = "retry"
    SKIP = "skip"


@dataclass
class CommonParams:
    """全操作共通のパラメータ"""

    memo: str = ""
    timeout: int = 30
    retry_count: int = 0
    error_handling: str = ErrorHandling.STOP.value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "memo": self.memo,
            "timeout": self.timeout,
            "retry_count": self.retry_count,
            "error_handling": self.error_handling,
        }


@dataclass
class OperationTemplate:
    """操作テンプレートの基底クラス"""

    common_params: CommonParams = field(default_factory=CommonParams)
    specific_params: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "common_params": self.common_params.to_dict(),
            "specific_params": self.specific_params,
        }
