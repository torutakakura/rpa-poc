"""
B. 待機・終了・エラー操作のスキーマ定義
"""

from .base import CommonParams, ErrorHandling, OperationTemplate


class WaitErrorOperations:
    """待機・終了・エラー操作の定義"""

    @staticmethod
    def pause() -> OperationTemplate:
        """待機（秒）"""
        return OperationTemplate(
            specific_params={
                "interval": 3,  # 待機・間隔の秒数
            }
        )

    @staticmethod
    def search_screen_and_branch() -> OperationTemplate:
        """画像出現を待つ"""
        return OperationTemplate(
            specific_params={
                "filename": "",  # 任意設定項目（用途に応じて指定）（必須）
                "precision": 85,  # 画像一致の厳しさ（%）
                "interval": 5,  # 待機・間隔の秒数
                "noise_filter": 100.0,  # 画像検索時のノイズ除去率
                "search_area_type": None,  # screen/window/area - 検索範囲の種類
                "search_area": "(0,0)-(0,0)",  # rect (x1,y1)-(x2,y2) - 検索座標の範囲指定
            }
        )

    @staticmethod
    def pause_and_ask_to_proceed() -> OperationTemplate:
        """続行確認"""
        return OperationTemplate(
            specific_params={
                "string": "",  # メッセージや対象文字列
            }
        )

    @staticmethod
    def pause_and_countdown_to_proceed() -> OperationTemplate:
        """タイマー付き続行確認"""
        return OperationTemplate(
            specific_params={
                "interval": 3,  # 待機・間隔の秒数
                "string": "",  # メッセージや対象文字列
            }
        )

    @staticmethod
    def change_speed_for_command_execution() -> OperationTemplate:
        """コマンド間の待機時間を変更"""
        return OperationTemplate(
            specific_params={
                "interval": 0.2,  # 待機・間隔の秒数
            }
        )

    @staticmethod
    def abort() -> OperationTemplate:
        """作業強制終了"""
        return OperationTemplate(
            specific_params={
                "result_type": None,  # abort/exit - 終了動作の種類
            }
        )

    @staticmethod
    def raise_error() -> OperationTemplate:
        """エラーを発生させる"""
        return OperationTemplate(
            specific_params={
                "string": "",  # メッセージや対象文字列
            }
        )

    @staticmethod
    def check_for_errors() -> OperationTemplate:
        """直前のコマンドのエラーを確認・処理"""
        return OperationTemplate(
            specific_params={
                "retries": 0,  # リトライ回数
                "wait": 1,  # リトライ間隔（秒）
                "err_cmd": "[ERR_CMD]",  # エラー発生コマンド名の格納先
                "err_memo": "[ERR_MEMO]",  # エラーメモの格納先
                "err_msg": "[ERR_MSG]",  # エラーメッセージの格納先
                "err_param": "[ERR_PARAM]",  # エラー時パラメータの格納先
            }
        )

    @staticmethod
    def check_for_errors_2() -> OperationTemplate:
        """直前のコマンドのエラーを確認・処理（リトライ前処理）"""
        return OperationTemplate(
            specific_params={
                "retries": 0,  # リトライ回数
                "wait": 1,  # リトライ間隔（秒）
                "err_cmd": "[ERR_CMD]",  # エラー発生コマンド名の格納先
                "err_memo": "[ERR_MEMO]",  # エラーメモの格納先
                "err_msg": "[ERR_MSG]",  # エラーメッセージの格納先
                "err_param": "[ERR_PARAM]",  # エラー時パラメータの格納先
            }
        )
