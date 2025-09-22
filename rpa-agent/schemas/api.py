"""
O. API操作のスキーマ定義
"""

from .base import OperationTemplate


class APIOperations:
    """API操作の定義"""

    @staticmethod
    def api_web() -> OperationTemplate:
        """Web API"""
        return OperationTemplate(
            specific_params={
                "method": "GET",  # 任意設定項目（用途に応じて指定）
                "services": "custom-get",  # 任意設定項目（用途に応じて指定）
                "url": "",  # 任意設定項目（用途に応じて指定）
                "queries": {},  # 任意設定項目（用途に応じて指定）
                "headers": {},  # 任意設定項目（用途に応じて指定）
                "body": "form-data",  # 任意設定項目（用途に応じて指定）
                "form_data": {},  # 任意設定項目（用途に応じて指定）
                "raw": "",  # 任意設定項目（用途に応じて指定）
                "json": "",  # 任意設定項目（用途に応じて指定）
                "timeout": 10,  # 待機の上限時間（秒）
                "res_status": "[応答ステータス]",  # 格納先変数
                "res_headers": "[応答ヘッダ]",  # 格納先変数
                "res_data": "[応答データ]",  # 格納先変数
                "res_content_type": "[応答コンテントタイプ]",  # 格納先変数
            }
        )

    class JSON:
        """JSON関連操作"""

        @staticmethod
        def get_json_values() -> OperationTemplate:
            """JSON値取得"""
            return OperationTemplate(
                specific_params={
                    "src_variable": "",  # 任意設定項目（用途に応じて指定）
                    "dst_variable": "データ",  # 任意設定項目（用途に応じて指定）
                    "type": "dict",  # 任意設定項目（用途に応じて指定）
                    "dict": "",  # 任意設定項目（用途に応じて指定）
                    "array": 1,  # 任意設定項目（用途に応じて指定）
                    "custom": "",  # 任意設定項目（用途に応じて指定）
                }
            )

        @staticmethod
        def check_json_type() -> OperationTemplate:
            """JSON型確認"""
            return OperationTemplate(
                specific_params={
                    "variable": "",  # 値やウィンドウを保持する変数名
                    "type": "dict",  # 任意設定項目（用途に応じて指定）
                    "dict": "",  # 任意設定項目（用途に応じて指定）
                    "array": 1,  # 任意設定項目（用途に応じて指定）
                    "custom": "",  # 任意設定項目（用途に応じて指定）
                    "check_type": "string",  # 任意設定項目（用途に応じて指定）
                }
            )