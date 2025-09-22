"""
A. アプリ・画面操作のスキーマ定義
"""

from .base import CommonParams, OperationTemplate


class AppOperations:
    """アプリ操作の定義"""

    @staticmethod
    def run_executable() -> OperationTemplate:
        """アプリ起動"""
        return OperationTemplate(
            specific_params={
                "path": "",  # 実行対象のパス（必須）
                "arguments": "",  # コマンドライン引数
                "interval": 3,  # 待機・間隔の秒数
                "maximized": None,  # True/False - 起動時のウィンドウ状態の切替
            }
        )

    @staticmethod
    def run_executable_and_wait() -> OperationTemplate:
        """アプリ起動（終了待ち）"""
        return OperationTemplate(
            specific_params={
                "path": "",  # 実行対象のパス（必須）
                "arguments": "",  # コマンドライン引数
                "timeout": 300,  # 待機の上限時間（秒）
                "output_variable": "",  # 標準出力の格納先変数
                "error_variable": "",  # 標準エラー出力の格納先変数
            }
        )


class ScreenOperations:
    """画面操作の定義"""

    @staticmethod
    def remember_focused_window() -> OperationTemplate:
        """最前画面を覚える"""
        return OperationTemplate(
            specific_params={
                "variable": "",  # 値やウィンドウを保持する変数名
            }
        )

    @staticmethod
    def remember_named_window() -> OperationTemplate:
        """画面を覚える（名前）"""
        return OperationTemplate(
            specific_params={
                "match_type": None,  # contains/equals - タイトル一致方式の切替
                "window_name": "",  # 対象ウィンドウのタイトル文字列（必須）
                "variable": "",  # 値やウィンドウを保持する変数名
            }
        )

    @staticmethod
    def focus_window() -> OperationTemplate:
        """最前画面切り替え"""
        return OperationTemplate(
            specific_params={
                "variable": "",  # 値やウィンドウを保持する変数名（必須）
            }
        )

    @staticmethod
    def focus_window_by_name() -> OperationTemplate:
        """画面切り替え（名前）"""
        return OperationTemplate(
            specific_params={
                "string": "",  # メッセージや対象文字列（必須）
            }
        )

    @staticmethod
    def get_window_title() -> OperationTemplate:
        """画面の名前を取得"""
        return OperationTemplate(
            specific_params={
                "window": "__focused_window__",  # 対象ウィンドウ指定（既定は最前面など）
                "variable": "",  # 値やウィンドウを保持する変数名
            }
        )

    @staticmethod
    def align_focused_window() -> OperationTemplate:
        """ウィンドウを移動"""
        return OperationTemplate(
            specific_params={
                "alignment": None,  # left/right/top/bottom/center - ウィンドウ配置の切替
            }
        )

    @staticmethod
    def maximize_focused_window() -> OperationTemplate:
        """ウィンドウ最大化／最小化"""
        return OperationTemplate(
            specific_params={
                "behavior": None,  # maximize/minimize - ウィンドウ操作種別の切替
            }
        )

    @staticmethod
    def take_screenshot() -> OperationTemplate:
        """スクリーンショットを撮る"""
        return OperationTemplate(
            specific_params={
                "dir_path": "",  # 保存先フォルダ（必須）
                "file_name": "",  # 保存ファイル名（拡張子なし）（必須）
                "area": None,  # area-whole/area-window/area-selection - キャプチャ範囲の切替
                "variable": "",  # 値やウィンドウを保持する変数名
                "timestamp": None,  # False/True - タイムスタンプ付与の有無
                "extension": None,  # png/jpg/bmp - 保存ファイルの拡張子
            }
        )
