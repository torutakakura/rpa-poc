"""
B_待機・終了・エラー カテゴリの操作
"""

import asyncio
import sys
import time
from typing import Any, Dict

from .base import BaseOperation, OperationResult


class WaitImageOperation(BaseOperation):
    """画像出現を待つ"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        image_path = params.get("image_path", "")
        accuracy = params.get("accuracy", 0.8)
        params.get("search_area", "full_screen")
        params.get("coordinates", {})
        timeout = params.get("timeout", 60)

        error = self.validate_params(params, ["image_path"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            self.log(f"Waiting for image: {image_path} (accuracy: {accuracy})")

            # 画像認識の実装が必要（pyautogui, opencv等を使用）
            # ここでは簡易的な実装
            start_time = time.time()
            while time.time() - start_time < timeout:
                # 実際の画像検索処理をここに実装
                await asyncio.sleep(1)

                # デモ用：5秒後に見つかったことにする
                if time.time() - start_time > 5:
                    return OperationResult(
                        status="success",
                        data={
                            "image_path": image_path,
                            "found": True,
                            "position": {"x": 100, "y": 100},
                        },
                    )

            return OperationResult(
                status="failure",
                data={},
                error=f"Image not found after {timeout} seconds",
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to wait for image: {str(e)}"
            )


class ContinueConfirmOperation(BaseOperation):
    """続行確認"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        message = params.get("message", "続行しますか？")
        title = params.get("title", "続行確認")

        try:
            self.log(f"Showing continue confirmation: {message}")

            # GUI実装が必要（tkinter等を使用）
            # ここでは自動的に続行することにする
            await asyncio.sleep(1)

            return OperationResult(
                status="success",
                data={"message": message, "title": title, "user_response": "continue"},
            )
        except Exception as e:
            return OperationResult(
                status="failure",
                data={},
                error=f"Failed to show confirmation: {str(e)}",
            )


class TimerContinueConfirmOperation(BaseOperation):
    """タイマー付き続行確認（秒）"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        message = params.get("message", "続行しますか？")
        title = params.get("title", "続行確認")
        countdown_seconds = params.get("countdown_seconds", 10)

        try:
            self.log(
                f"Showing timer confirmation: {message} (countdown: {countdown_seconds}s)"
            )

            # カウントダウン処理
            for i in range(countdown_seconds, 0, -1):
                self.log(f"Countdown: {i} seconds remaining", "debug")
                await asyncio.sleep(1)

            return OperationResult(
                status="success",
                data={
                    "message": message,
                    "title": title,
                    "countdown_seconds": countdown_seconds,
                    "user_response": "timeout_continue",
                },
            )
        except Exception as e:
            return OperationResult(
                status="failure",
                data={},
                error=f"Failed to show timer confirmation: {str(e)}",
            )


class ChangeCommandIntervalOperation(BaseOperation):
    """コマンド間待機時間を変更"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        interval_ms = params.get("interval_ms", 500)

        try:
            self.log(f"Changing command interval to {interval_ms}ms")

            # エージェントのコマンド間隔を設定
            if self.agent:
                self.agent.command_interval = interval_ms / 1000

            return OperationResult(status="success", data={"interval_ms": interval_ms})
        except Exception as e:
            return OperationResult(
                status="failure",
                data={},
                error=f"Failed to change command interval: {str(e)}",
            )


class ForceExitOperation(BaseOperation):
    """作業強制終了"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        exit_code = params.get("exit_code", 0)

        try:
            self.log(f"Force exiting with code {exit_code}", "warning")

            # クリーンアップ処理
            if self.agent:
                # 実行中のタスクを停止
                self.agent.running_tasks.clear()

            # システム終了
            sys.exit(exit_code)

        except SystemExit:
            # 正常な終了
            raise
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to force exit: {str(e)}"
            )


class RaiseErrorOperation(BaseOperation):
    """エラー発生"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        error_message = params.get("error_message", "User defined error")
        error_code = params.get("error_code", "USER_ERROR")

        try:
            self.log(f"Raising error: {error_message} (code: {error_code})", "error")

            return OperationResult(
                status="failure",
                data={"error_code": error_code, "error_message": error_message},
                error=error_message,
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to raise error: {str(e)}"
            )


class ErrorCheckProcessOperation(BaseOperation):
    """エラー確認・処理"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        on_error_steps = params.get("on_error_steps", [])
        clear_error = params.get("clear_error", True)

        try:
            # 最後のエラーをチェック
            last_error = None
            if self.agent and hasattr(self.agent, "last_error"):
                last_error = self.agent.last_error

            if last_error:
                self.log(f"Error detected: {last_error}", "warning")

                # エラー時の処理ステップを実行
                for step in on_error_steps:
                    self.log(f"Executing error handling step: {step}", "info")
                    # ステップ実行のロジックをここに実装

                # エラーをクリア
                if clear_error and self.agent:
                    self.agent.last_error = None

                return OperationResult(
                    status="success",
                    data={
                        "error_detected": True,
                        "error": last_error,
                        "steps_executed": len(on_error_steps),
                        "error_cleared": clear_error,
                    },
                )
            else:
                return OperationResult(status="success", data={"error_detected": False})
        except Exception as e:
            return OperationResult(
                status="failure",
                data={},
                error=f"Failed to check/process error: {str(e)}",
            )


class ErrorCheckRetryOperation(BaseOperation):
    """エラー確認・処理（リトライ前処理）"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        retry_interval = params.get("retry_interval", 5)
        on_retry_steps = params.get("on_retry_steps", [])
        on_error_steps = params.get("on_error_steps", [])
        max_retry = params.get("retry_count", 3)

        try:
            # 最後のエラーをチェック
            last_error = None
            if self.agent and hasattr(self.agent, "last_error"):
                last_error = self.agent.last_error

            if last_error:
                self.log("Error detected, starting retry process", "warning")

                # リトライ処理
                for attempt in range(max_retry):
                    self.log(f"Retry attempt {attempt + 1}/{max_retry}", "info")

                    # リトライ前の処理ステップを実行
                    for step in on_retry_steps:
                        self.log(f"Executing retry step: {step}", "info")
                        # ステップ実行のロジックをここに実装

                    # リトライ間隔待機
                    await asyncio.sleep(retry_interval)

                    # エラーが解消されたかチェック（実装が必要）
                    # ここでは3回目で成功することにする
                    if attempt == max_retry - 1:
                        if self.agent:
                            self.agent.last_error = None
                        return OperationResult(
                            status="success",
                            data={"retry_count": attempt + 1, "error_resolved": True},
                        )

                # 最大リトライ後もエラーの場合
                for step in on_error_steps:
                    self.log(f"Executing error step: {step}", "error")
                    # ステップ実行のロジックをここに実装

                return OperationResult(
                    status="failure",
                    data={"retry_count": max_retry, "error_resolved": False},
                    error=f"Failed after {max_retry} retries",
                )
            else:
                return OperationResult(status="success", data={"error_detected": False})
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed in retry process: {str(e)}"
            )
