"""
E. 記憶操作のスキーマ定義
"""

from .base import OperationTemplate


class MemoryOperations:
    """記憶操作の定義"""

    @staticmethod
    def assign_string_variable() -> OperationTemplate:
        """データの記憶（文字）"""
        return OperationTemplate(
            specific_params={
                "variable": "データ",  # 値やウィンドウを保持する変数名
                "string": "",  # メッセージや対象文字列
            }
        )

    @staticmethod
    def assign_password_variable() -> OperationTemplate:
        """パスワードの記憶"""
        return OperationTemplate(
            specific_params={
                "password_type": "type-input",  # 任意設定項目（用途に応じて指定）
                "password": "",  # 任意設定項目（用途に応じて指定）
                "password_id": "パスワード",  # 任意設定項目（用途に応じて指定）
            }
        )

    @staticmethod
    def assign_environment_variable() -> OperationTemplate:
        """データの記憶（環境情報）"""
        return OperationTemplate(
            specific_params={
                "variable": "環境",  # 値やウィンドウを保持する変数名
                "environment": "",  # 任意設定項目（用途に応じて指定）
            }
        )

    @staticmethod
    def assign_date_to_string_variable() -> OperationTemplate:
        """日付を記憶"""
        return OperationTemplate(
            specific_params={
                "variable": "日付",  # 値やウィンドウを保持する変数名
                "offset": 0,  # 任意設定項目（用途に応じて指定）
                "format": "yyyy-mm-dd",  # 任意設定項目（用途に応じて指定）
                "0_option": False,  # True/False - 任意設定項目（用途に応じて指定）
            }
        )

    @staticmethod
    def assign_date_business_to_string_variable() -> OperationTemplate:
        """日付を記憶（営業日）"""
        return OperationTemplate(
            specific_params={
                "variable": "日付",  # 値やウィンドウを保持する変数名
                "offset": 0,  # 任意設定項目（用途に応じて指定）
                "busidays": 1,  # 任意設定項目（用途に応じて指定）
                "mon": False,  # True/False - 任意設定項目（用途に応じて指定）
                "tue": False,  # True/False - 任意設定項目（用途に応じて指定）
                "wed": False,  # True/False - 任意設定項目（用途に応じて指定）
                "thu": False,  # True/False - 任意設定項目（用途に応じて指定）
                "fri": False,  # True/False - 任意設定項目（用途に応じて指定）
                "sat": True,  # True/False - 任意設定項目（用途に応じて指定）
                "sun": True,  # True/False - 任意設定項目（用途に応じて指定）
                "holidays": True,  # True/False - 任意設定項目（用途に応じて指定）
                "holidays_custom": True,  # True/False - 任意設定項目（用途に応じて指定）
                "format": "yyyy-mm-dd",  # 任意設定項目（用途に応じて指定）
                "0_option": False,  # True/False - 任意設定項目（用途に応じて指定）
            }
        )

    @staticmethod
    def assign_date_weekdays_to_string_variable() -> OperationTemplate:
        """日付を記憶（曜日）"""
        return OperationTemplate(
            specific_params={
                "variable": "日付",  # 値やウィンドウを保持する変数名
                "month": 0,  # 任意設定項目（用途に応じて指定）
                "week": 0,  # 任意設定項目（用途に応じて指定）
                "weekdays": 0,  # 任意設定項目（用途に応じて指定）
                "mon": False,  # True/False - 任意設定項目（用途に応じて指定）
                "tue": False,  # True/False - 任意設定項目（用途に応じて指定）
                "wed": False,  # True/False - 任意設定項目（用途に応じて指定）
                "thu": False,  # True/False - 任意設定項目（用途に応じて指定）
                "fri": False,  # True/False - 任意設定項目（用途に応じて指定）
                "sat": False,  # True/False - 任意設定項目（用途に応じて指定）
                "sun": False,  # True/False - 任意設定項目（用途に応じて指定）
                "holidays": False,  # True/False - 任意設定項目（用途に応じて指定）
                "holidays_custom": False,  # True/False - 任意設定項目（用途に応じて指定）
                "adjust": "forward",  # 任意設定項目（用途に応じて指定）
                "format": "yyyy-mm-dd",  # 任意設定項目（用途に応じて指定）
                "0_option": False,  # True/False - 任意設定項目（用途に応じて指定）
            }
        )

    @staticmethod
    def assign_date_calculation_to_string_variable() -> OperationTemplate:
        """日付計算結果を記憶"""
        return OperationTemplate(
            specific_params={
                "variable": "日付",  # 値やウィンドウを保持する変数名
                "input_date": "",  # 任意設定項目（用途に応じて指定）
                "format1": "yyyy-mm-dd",  # 任意設定項目（用途に応じて指定）
                "format2": "yyyy-mm-dd",  # 任意設定項目（用途に応じて指定）
                "operator": "add",  # 任意設定項目（用途に応じて指定）
                "year": "",  # 任意設定項目（用途に応じて指定）
                "month": "",  # 任意設定項目（用途に応じて指定）
                "day": "",  # 任意設定項目（用途に応じて指定）
                "mon": False,  # True/False - 任意設定項目（用途に応じて指定）
                "tue": False,  # True/False - 任意設定項目（用途に応じて指定）
                "wed": False,  # True/False - 任意設定項目（用途に応じて指定）
                "thu": False,  # True/False - 任意設定項目（用途に応じて指定）
                "fri": False,  # True/False - 任意設定項目（用途に応じて指定）
                "sat": False,  # True/False - 任意設定項目（用途に応じて指定）
                "sun": False,  # True/False - 任意設定項目（用途に応じて指定）
                "holidays": False,  # True/False - 任意設定項目（用途に応じて指定）
                "holidays_custom": False,  # True/False - 任意設定項目（用途に応じて指定）
                "count_method": "everyday",  # 任意設定項目（用途に応じて指定）
                "adjust": "forward",  # 任意設定項目（用途に応じて指定）
                "0_option": False,  # True/False - 任意設定項目（用途に応じて指定）
            }
        )

    @staticmethod
    def assign_day_of_week_to_string_variable() -> OperationTemplate:
        """曜日を記憶"""
        return OperationTemplate(
            specific_params={
                "variable": "曜日",  # 値やウィンドウを保持する変数名
                "offset": 0,  # 任意設定項目（用途に応じて指定）
                "format": "月曜日",  # 任意設定項目（用途に応じて指定）
                "type": "today",  # 任意設定項目（用途に応じて指定）
                "date": "",  # 任意設定項目（用途に応じて指定）
                "format_date": "yyyy-mm-dd",  # 任意設定項目（用途に応じて指定）
            }
        )

    @staticmethod
    def assign_timestamp_to_string_variable() -> OperationTemplate:
        """現在の時刻を記憶"""
        return OperationTemplate(
            specific_params={
                "variable": "時刻",  # 値やウィンドウを保持する変数名
                "format": "hh:mm:ss",  # 任意設定項目（用途に応じて指定）
                "language": "",  # 任意設定項目（用途に応じて指定）
                "timezone": "",  # 任意設定項目（用途に応じて指定）
                "0_option": False,  # True/False - 任意設定項目（用途に応じて指定）
            }
        )

    @staticmethod
    def assign_time_calculation_to_string_variable() -> OperationTemplate:
        """時刻計算結果を記憶"""
        return OperationTemplate(
            specific_params={
                "variable": "時刻",  # 値やウィンドウを保持する変数名
                "time": "",  # 任意設定項目（用途に応じて指定）
                "format": "hh:mm:ss",  # 任意設定項目（用途に応じて指定）
                "operator": "add",  # 任意設定項目（用途に応じて指定）
                "hours": "",  # 任意設定項目（用途に応じて指定）
                "minutes": "",  # 任意設定項目（用途に応じて指定）
                "seconds": "",  # 任意設定項目（用途に応じて指定）
                "format2": "hh:mm:ss",  # 任意設定項目（用途に応じて指定）
                "language": "",  # 任意設定項目（用途に応じて指定）
                "timezone": "",  # 任意設定項目（用途に応じて指定）
                "0_option": False,  # True/False - 任意設定項目（用途に応じて指定）
            }
        )

    @staticmethod
    def assign_arithmetic_result_to_string_variable_v2() -> OperationTemplate:
        """計算結果を記憶"""
        return OperationTemplate(
            specific_params={
                "variable": "計算結果",  # 値やウィンドウを保持する変数名
                "number1": "",  # 任意設定項目（用途に応じて指定）
                "number2": "",  # 任意設定項目（用途に応じて指定）
                "operator": "add",  # 任意設定項目（用途に応じて指定）
                "round_type": "none",  # 任意設定項目（用途に応じて指定）
                "precision": "",  # 画像一致の厳しさ（%）
            }
        )

    @staticmethod
    def assign_random_number_to_string_variable() -> OperationTemplate:
        """乱数を記憶"""
        return OperationTemplate(
            specific_params={
                "variable": "データ",  # 値やウィンドウを保持する変数名
                "min_number": 0,  # 任意設定項目（用途に応じて指定）
                "max_number": 100,  # 任意設定項目（用途に応じて指定）
                "precision": 0,  # 画像一致の厳しさ（%）
                "zero_fill": True,  # True/False - 任意設定項目（用途に応じて指定）
            }
        )

    @staticmethod
    def assign_clipboard_to_string_variable() -> OperationTemplate:
        """コピー内容を記憶"""
        return OperationTemplate(
            specific_params={
                "variable": "データ",  # 値やウィンドウを保持する変数名
            }
        )

    @staticmethod
    def copy_to_clipboard() -> OperationTemplate:
        """クリップボードへコピー"""
        return OperationTemplate(
            specific_params={
                "string": "",  # メッセージや対象文字列
            }
        )

    @staticmethod
    def assign_live_input_to_string_variable() -> OperationTemplate:
        """実行中に入力"""
        return OperationTemplate(
            specific_params={
                "variable": "データ",  # 値やウィンドウを保持する変数名
                "string": "",  # メッセージや対象文字列
            }
        )

    @staticmethod
    def assign_file_modification_timestamp_to_string_variable() -> OperationTemplate:
        """ファイル更新日時を記憶"""
        return OperationTemplate(
            specific_params={
                "variable": "日時",  # 値やウィンドウを保持する変数名
                "path": "",  # 実行対象のパス。未設定では動かない
                "timestamp": "modification",  # modification/True/False - タイムスタンプ付与の有無
                "format": "yyyy-mm-dd_hh:mm:ss",  # 任意設定項目（用途に応じて指定）
            }
        )

    @staticmethod
    def assign_file_size_to_string_variable() -> OperationTemplate:
        """ファイルサイズを記憶"""
        return OperationTemplate(
            specific_params={
                "variable": "サイズ",  # 値やウィンドウを保持する変数名
                "path": "",  # 実行対象のパス。未設定では動かない
                "unit": "bytes",  # 任意設定項目（用途に応じて指定）
            }
        )

    @staticmethod
    def find_newest_file_from_fixed_directory() -> OperationTemplate:
        """最新ファイル・フォルダを取得"""
        return OperationTemplate(
            specific_params={
                "variable": "ファイル保存場所",  # 値やウィンドウを保持する変数名
                "file_or_dir": "file",  # 任意設定項目（用途に応じて指定）
                "date_check": "更新日時",  # 任意設定項目（用途に応じて指定）
                "number": 1,  # 任意設定項目（用途に応じて指定）
                "path": "",  # 実行対象のパス。未設定では動かない
            }
        )