"""
F_待機 カテゴリの操作
"""

import asyncio
import contextlib
import time
from typing import Any, Dict

from .base import BaseOperation, OperationResult


class WaitSecondsOperation(BaseOperation):
    """指定秒数待機"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        wait_seconds = params.get("wait_seconds", 1)

        try:
            self.log(f"Waiting for {wait_seconds} seconds")
            await asyncio.sleep(wait_seconds)

            return OperationResult(
                status="success", data={"wait_seconds": wait_seconds}
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to wait: {str(e)}"
            )


class WaitMillisecondsOperation(BaseOperation):
    """指定ミリ秒待機"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        wait_milliseconds = params.get("wait_milliseconds", 100)

        try:
            wait_seconds = wait_milliseconds / 1000
            self.log(f"Waiting for {wait_milliseconds} milliseconds")
            await asyncio.sleep(wait_seconds)

            return OperationResult(
                status="success", data={"wait_milliseconds": wait_milliseconds}
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to wait: {str(e)}"
            )


class WaitUntilTimeOperation(BaseOperation):
    """指定時刻まで待機"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        target_time = params.get("target_time", "")  # Format: "HH:MM:SS"

        error = self.validate_params(params, ["target_time"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            from datetime import datetime
            from datetime import time as dtime

            # 時刻をパース
            time_parts = target_time.split(":")
            if len(time_parts) != 3:
                return OperationResult(
                    status="failure",
                    data={},
                    error=f"Invalid time format: {target_time}. Use HH:MM:SS",
                )

            hour = int(time_parts[0])
            minute = int(time_parts[1])
            second = int(time_parts[2])

            target = dtime(hour, minute, second)
            now = datetime.now()
            target_datetime = datetime.combine(now.date(), target)

            # 既に過ぎている場合は翌日まで待つ
            if target_datetime <= now:
                from datetime import timedelta

                target_datetime += timedelta(days=1)

            wait_seconds = (target_datetime - now).total_seconds()
            self.log(f"Waiting until {target_time} ({wait_seconds:.1f} seconds)")

            await asyncio.sleep(wait_seconds)

            return OperationResult(
                status="success",
                data={"target_time": target_time, "wait_seconds": wait_seconds},
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to wait until time: {str(e)}"
            )


class WaitForConditionOperation(BaseOperation):
    """条件を満たすまで待機"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        condition_key = params.get("condition_key", "")
        condition_value = params.get("condition_value", "")
        condition_type = params.get(
            "condition_type", "equals"
        )  # equals, not_equals, greater, less
        timeout_seconds = params.get("timeout_seconds", 60)
        check_interval = params.get("check_interval", 1)

        error = self.validate_params(params, ["condition_key", "condition_value"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            start_time = time.time()
            self.log(
                f"Waiting for condition: {condition_key} {condition_type} {condition_value}"
            )

            while True:
                current_value = self.get_storage(condition_key)

                # 条件チェック
                condition_met = False
                if condition_type == "equals":
                    condition_met = str(current_value) == str(condition_value)
                elif condition_type == "not_equals":
                    condition_met = str(current_value) != str(condition_value)
                elif condition_type == "greater":
                    with contextlib.suppress(ValueError, TypeError):
                        condition_met = float(current_value) > float(condition_value)
                elif condition_type == "less":
                    with contextlib.suppress(ValueError, TypeError):
                        condition_met = float(current_value) < float(condition_value)

                if condition_met:
                    elapsed = time.time() - start_time
                    self.log(f"Condition met after {elapsed:.1f} seconds")
                    return OperationResult(
                        status="success",
                        data={
                            "condition_key": condition_key,
                            "condition_value": condition_value,
                            "current_value": current_value,
                            "elapsed_seconds": elapsed,
                        },
                    )

                # タイムアウトチェック
                if time.time() - start_time > timeout_seconds:
                    return OperationResult(
                        status="failure",
                        data={
                            "condition_key": condition_key,
                            "condition_value": condition_value,
                            "current_value": current_value,
                        },
                        error=f"Timeout waiting for condition after {timeout_seconds} seconds",
                    )

                await asyncio.sleep(check_interval)

        except Exception as e:
            return OperationResult(
                status="failure",
                data={},
                error=f"Failed to wait for condition: {str(e)}",
            )


class RandomWaitOperation(BaseOperation):
    """ランダムな時間待機"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        min_seconds = params.get("min_seconds", 1)
        max_seconds = params.get("max_seconds", 5)

        try:
            import random

            wait_seconds = random.uniform(min_seconds, max_seconds)
            self.log(
                f"Waiting for {wait_seconds:.2f} seconds (random between {min_seconds} and {max_seconds})"
            )

            await asyncio.sleep(wait_seconds)

            return OperationResult(
                status="success",
                data={
                    "min_seconds": min_seconds,
                    "max_seconds": max_seconds,
                    "actual_wait": wait_seconds,
                },
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to wait: {str(e)}"
            )
