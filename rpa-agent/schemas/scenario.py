"""
P. シナリオ整理のスキーマ定義
"""

from .base import OperationTemplate


class ScenarioOrganizationOperations:
    """シナリオ整理操作の定義"""

    @staticmethod
    def group_commands() -> OperationTemplate:
        """グループ"""
        return OperationTemplate(
            specific_params={
                "name": "",  # 任意設定項目（用途に応じて指定）
            }
        )

    @staticmethod
    def add_memo() -> OperationTemplate:
        """メモ"""
        return OperationTemplate(
            specific_params={
                "string": "",  # メモの内容
            }
        )

    @staticmethod
    def play_sound() -> OperationTemplate:
        """通知音を再生"""
        return OperationTemplate(
            specific_params={
                "sound": "Beep",  # 任意設定項目（用途に応じて指定）
                "path": "",  # 実行対象のパス。未設定では動かない
                "count": 1,  # 任意設定項目（用途に応じて指定）
                "interval": 1,  # 待機・間隔の秒数
                "async": False,  # True/False - 任意設定項目（用途に応じて指定）
            }
        )