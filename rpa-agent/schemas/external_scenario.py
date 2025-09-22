"""
Q. 別シナリオ実行・継承のスキーマ定義
"""

from .base import OperationTemplate


class ExternalScenarioOperations:
    """別シナリオ実行・継承操作の定義"""

    @staticmethod
    def run_external_scenario_and_branch() -> OperationTemplate:
        """別のシナリオを実行"""
        return OperationTemplate(
            specific_params={
                "scenario_name": "",  # 任意設定項目（用途に応じて指定）
                "uuid": "",  # 任意設定項目（用途に応じて指定）
            }
        )

    @staticmethod
    def inherit_variables() -> OperationTemplate:
        """親シナリオからデータを継承"""
        return OperationTemplate(
            specific_params={
                "uuid": "",  # 任意設定項目（用途に応じて指定）
                "variable": "データ",  # 値やウィンドウを保持する変数名
                "overwrite": True,  # True/False - 任意設定項目（用途に応じて指定）
                "scenario_name": "",  # 任意設定項目（用途に応じて指定）
                "type": "single",  # 任意設定項目（用途に応じて指定）
                "variables": [],  # 任意設定項目（用途に応じて指定）
            }
        )

    @staticmethod
    def inherit_passwords() -> OperationTemplate:
        """親シナリオからパスワードを継承"""
        return OperationTemplate(
            specific_params={
                "uuid": "",  # 任意設定項目（用途に応じて指定）
                "password_id": "パスワード",  # 任意設定項目（用途に応じて指定）
                "overwrite": True,  # True/False - 任意設定項目（用途に応じて指定）
                "scenario_name": "",  # 任意設定項目（用途に応じて指定）
                "type": "single",  # 任意設定項目（用途に応じて指定）
                "passwords": [],  # 任意設定項目（用途に応じて指定）
            }
        )

    @staticmethod
    def inherit_windows() -> OperationTemplate:
        """親シナリオからウィンドウを継承"""
        return OperationTemplate(
            specific_params={
                "uuid": "",  # 任意設定項目（用途に応じて指定）
                "variable": "ウィンドウ",  # 値やウィンドウを保持する変数名
                "overwrite": True,  # True/False - 任意設定項目（用途に応じて指定）
                "scenario_name": "",  # 任意設定項目（用途に応じて指定）
                "type": "single",  # 任意設定項目（用途に応じて指定）
                "windows": [],  # 任意設定項目（用途に応じて指定）
            }
        )

    @staticmethod
    def inherit_excel() -> OperationTemplate:
        """親シナリオからエクセルを継承"""
        return OperationTemplate(
            specific_params={
                "uuid": "",  # 任意設定項目（用途に応じて指定）
                "excel": "エクセル",  # 任意設定項目（用途に応じて指定）
                "overwrite": True,  # True/False - 任意設定項目（用途に応じて指定）
                "scenario_name": "",  # 任意設定項目（用途に応じて指定）
                "type": "single",  # 任意設定項目（用途に応じて指定）
                "excels": [],  # 任意設定項目（用途に応じて指定）
            }
        )

    @staticmethod
    def inherit_browsers() -> OperationTemplate:
        """親シナリオからブラウザを継承"""
        return OperationTemplate(
            specific_params={
                "uuid": "",  # 任意設定項目（用途に応じて指定）
                "browser": "ブラウザ",  # 値やウィンドウを保持する変数名
                "overwrite": True,  # True/False - 任意設定項目（用途に応じて指定）
                "scenario_name": "",  # 任意設定項目（用途に応じて指定）
                "type": "single",  # 任意設定項目（用途に応じて指定）
                "browsers": [],  # 任意設定項目（用途に応じて指定）
            }
        )