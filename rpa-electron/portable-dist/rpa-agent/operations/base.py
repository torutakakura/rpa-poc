"""
Base classes for RPA operations
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class OperationResult:
    """操作結果を表すクラス"""

    status: str  # "success", "failure", "warning"
    data: Dict[str, Any]
    error: Optional[str] = None
    logs: Optional[list] = None


class BaseOperation(ABC):
    """全ての操作の基底クラス"""

    def __init__(self, agent=None):
        """
        Args:
            agent: RPAAgent インスタンス（ログ、ストレージへのアクセス用）
        """
        self.agent = agent

    def log(self, message: str, level: str = "info"):
        """ログを出力"""
        if self.agent and hasattr(self.agent, "log"):
            self.agent.log(message, level)
        else:
            print(f"[{level.upper()}] {message}")

    def get_storage(self, key: str, default=None):
        """ストレージから値を取得"""
        if self.agent and hasattr(self.agent, "storage"):
            return self.agent.storage.get(key, default)
        return default

    def set_storage(self, key: str, value: Any):
        """ストレージに値を保存"""
        if self.agent and hasattr(self.agent, "storage"):
            self.agent.storage[key] = value

    @abstractmethod
    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        """
        操作を実行する

        Args:
            params: 操作パラメータ

        Returns:
            OperationResult: 実行結果
        """
        pass

    def validate_params(self, params: Dict[str, Any], required: list) -> Optional[str]:
        """
        必須パラメータをチェック

        Args:
            params: パラメータ辞書
            required: 必須パラメータのリスト

        Returns:
            エラーメッセージ（問題がない場合はNone）
        """
        missing = [key for key in required if key not in params or params[key] is None]
        if missing:
            return f"Missing required parameters: {', '.join(missing)}"
        return None
