"""
RPA操作モジュール
各カテゴリの操作クラスを定義
"""

# このディレクトリには操作の定義のみを配置
# 操作の実行管理は operation_manager.py で行う

from .base import BaseOperation, OperationResult

__all__ = [
    "BaseOperation",
    "OperationResult",
]
