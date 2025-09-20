"""
G_日時 カテゴリの操作
"""

from datetime import datetime, timedelta
from typing import Any, Dict

from .base import BaseOperation, OperationResult


class GetCurrentDateTimeOperation(BaseOperation):
    """現在の日時を取得"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        format_string = params.get("format", "%Y-%m-%d %H:%M:%S")
        storage_key = params.get("storage_key", "")

        try:
            now = datetime.now()
            formatted = now.strftime(format_string)

            if storage_key:
                self.set_storage(storage_key, formatted)
                self.log(f"Stored current datetime as '{storage_key}': {formatted}")

            return OperationResult(
                status="success",
                data={
                    "datetime": formatted,
                    "timestamp": now.timestamp(),
                    "format": format_string,
                },
            )
        except Exception as e:
            return OperationResult(
                status="failure",
                data={},
                error=f"Failed to get current datetime: {str(e)}",
            )


class AddSubtractTimeOperation(BaseOperation):
    """時間の加算・減算"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        base_datetime = params.get("base_datetime")
        days = params.get("days", 0)
        hours = params.get("hours", 0)
        minutes = params.get("minutes", 0)
        seconds = params.get("seconds", 0)
        storage_key = params.get("storage_key", "")
        format_string = params.get("format", "%Y-%m-%d %H:%M:%S")

        try:
            # 基準日時の設定
            if base_datetime:
                if isinstance(base_datetime, str):
                    base = datetime.strptime(base_datetime, format_string)
                else:
                    base = datetime.fromtimestamp(base_datetime)
            else:
                base = datetime.now()

            # 時間の加算・減算
            delta = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
            result_datetime = base + delta

            formatted = result_datetime.strftime(format_string)

            if storage_key:
                self.set_storage(storage_key, formatted)
                self.log(f"Stored calculated datetime as '{storage_key}': {formatted}")

            return OperationResult(
                status="success",
                data={
                    "result": formatted,
                    "timestamp": result_datetime.timestamp(),
                    "delta": {
                        "days": days,
                        "hours": hours,
                        "minutes": minutes,
                        "seconds": seconds,
                    },
                },
            )
        except Exception as e:
            return OperationResult(
                status="failure",
                data={},
                error=f"Failed to calculate datetime: {str(e)}",
            )


class CompareDateTimeOperation(BaseOperation):
    """日時の比較"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        datetime1 = params.get("datetime1", "")
        datetime2 = params.get("datetime2", "")
        format_string = params.get("format", "%Y-%m-%d %H:%M:%S")
        storage_key = params.get("storage_key", "")

        error = self.validate_params(params, ["datetime1", "datetime2"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            # 日時をパース
            dt1 = datetime.strptime(datetime1, format_string)
            dt2 = datetime.strptime(datetime2, format_string)

            # 比較
            diff_seconds = (dt2 - dt1).total_seconds()
            comparison = (
                "equal"
                if diff_seconds == 0
                else "after"
                if diff_seconds > 0
                else "before"
            )

            result = {
                "datetime1": datetime1,
                "datetime2": datetime2,
                "comparison": comparison,
                "difference_seconds": abs(diff_seconds),
                "difference_days": abs(diff_seconds) / 86400,
            }

            if storage_key:
                self.set_storage(storage_key, result)

            self.log(f"DateTime comparison: {datetime2} is {comparison} {datetime1}")

            return OperationResult(status="success", data=result)
        except Exception as e:
            return OperationResult(
                status="failure",
                data={},
                error=f"Failed to compare datetimes: {str(e)}",
            )


class FormatDateTimeOperation(BaseOperation):
    """日時のフォーマット変換"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        datetime_string = params.get("datetime_string", "")
        input_format = params.get("input_format", "%Y-%m-%d %H:%M:%S")
        output_format = params.get("output_format", "%Y年%m月%d日 %H時%M分")
        storage_key = params.get("storage_key", "")

        error = self.validate_params(params, ["datetime_string"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            # 入力フォーマットでパース
            dt = datetime.strptime(datetime_string, input_format)

            # 出力フォーマットで変換
            formatted = dt.strftime(output_format)

            if storage_key:
                self.set_storage(storage_key, formatted)

            self.log(f"Formatted datetime: {datetime_string} -> {formatted}")

            return OperationResult(
                status="success",
                data={
                    "input": datetime_string,
                    "output": formatted,
                    "input_format": input_format,
                    "output_format": output_format,
                },
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to format datetime: {str(e)}"
            )


class GetWeekdayOperation(BaseOperation):
    """曜日を取得"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        datetime_string = params.get("datetime_string")
        format_string = params.get("format", "%Y-%m-%d")
        storage_key = params.get("storage_key", "")
        language = params.get("language", "ja")

        try:
            # 日時の設定
            if datetime_string:
                dt = datetime.strptime(datetime_string, format_string)
            else:
                dt = datetime.now()

            # 曜日を取得
            weekday_num = dt.weekday()  # 0=月曜日, 6=日曜日

            # 曜日名
            weekdays_ja = ["月", "火", "水", "木", "金", "土", "日"]
            weekdays_en = [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]

            weekday_name = (
                weekdays_ja[weekday_num]
                if language == "ja"
                else weekdays_en[weekday_num]
            )

            result = {
                "date": dt.strftime(format_string),
                "weekday": weekday_name,
                "weekday_number": weekday_num,
                "language": language,
            }

            if storage_key:
                self.set_storage(storage_key, weekday_name)

            self.log(f"Weekday for {dt.strftime(format_string)}: {weekday_name}")

            return OperationResult(status="success", data=result)
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to get weekday: {str(e)}"
            )
