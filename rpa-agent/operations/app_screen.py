"""
A_アプリ・画面 カテゴリの操作
"""

import os
import platform
import subprocess
import time
from typing import Any, Dict

from .base import BaseOperation, OperationResult


class LaunchAppOperation(BaseOperation):
    """アプリの起動"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        app_path = params.get("app_path", "")
        wait_time = params.get("wait_time", 5)
        params.get("maximize_window", False)
        arguments = params.get("arguments", "")
        working_directory = params.get("working_directory", "")

        error = self.validate_params(params, ["app_path"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            # コマンドライン引数の構築
            cmd = [app_path]
            if arguments:
                cmd.extend(arguments.split())

            # 作業ディレクトリの設定
            cwd = working_directory if working_directory else None

            # アプリケーションを起動
            self.log(f"Launching application: {app_path}")
            process = subprocess.Popen(cmd, cwd=cwd)

            # 指定時間待機
            time.sleep(wait_time)

            return OperationResult(
                status="success",
                data={"app_path": app_path, "pid": process.pid, "wait_time": wait_time},
            )
        except Exception as e:
            return OperationResult(
                status="failure",
                data={},
                error=f"Failed to launch application: {str(e)}",
            )


class LaunchAppWaitOperation(BaseOperation):
    """アプリの起動（終了待ち）"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        app_path = params.get("app_path", "")
        params.get("maximize_window", False)
        arguments = params.get("arguments", "")
        working_directory = params.get("working_directory", "")

        error = self.validate_params(params, ["app_path"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            # コマンドライン引数の構築
            cmd = [app_path]
            if arguments:
                cmd.extend(arguments.split())

            # 作業ディレクトリの設定
            cwd = working_directory if working_directory else None

            # アプリケーションを起動して終了を待つ
            self.log(f"Launching application and waiting: {app_path}")
            result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)

            return OperationResult(
                status="success" if result.returncode == 0 else "warning",
                data={
                    "app_path": app_path,
                    "return_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                },
            )
        except Exception as e:
            return OperationResult(
                status="failure",
                data={},
                error=f"Failed to launch application: {str(e)}",
            )


class RememberFrontWindowOperation(BaseOperation):
    """最前画面を覚える"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        reference_id = params.get("reference_id", "")

        error = self.validate_params(params, ["reference_id"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            # プラットフォーム別の実装が必要
            # ここでは簡易的な実装
            window_info = {"platform": platform.system(), "timestamp": time.time()}

            # ストレージに保存
            self.set_storage(f"window_{reference_id}", window_info)
            self.log(f"Remembered front window as: {reference_id}")

            return OperationResult(
                status="success",
                data={"reference_id": reference_id, "window_info": window_info},
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to remember window: {str(e)}"
            )


class RememberWindowByNameOperation(BaseOperation):
    """画面を覚える（名前）"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        window_name = params.get("window_name", "")
        reference_id = params.get("reference_id", "")
        partial_match = params.get("partial_match", False)

        error = self.validate_params(params, ["window_name", "reference_id"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            # プラットフォーム別の実装が必要
            window_info = {
                "window_name": window_name,
                "partial_match": partial_match,
                "platform": platform.system(),
                "timestamp": time.time(),
            }

            # ストレージに保存
            self.set_storage(f"window_{reference_id}", window_info)
            self.log(f"Remembered window '{window_name}' as: {reference_id}")

            return OperationResult(
                status="success",
                data={
                    "reference_id": reference_id,
                    "window_name": window_name,
                    "window_info": window_info,
                },
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to remember window: {str(e)}"
            )


class SwitchWindowByIdOperation(BaseOperation):
    """切り替え（参照ID）"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        reference_id = params.get("reference_id", "")

        error = self.validate_params(params, ["reference_id"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            # ストレージから取得
            window_info = self.get_storage(f"window_{reference_id}")
            if not window_info:
                return OperationResult(
                    status="failure",
                    data={},
                    error=f"No window found with reference_id: {reference_id}",
                )

            self.log(f"Switching to window: {reference_id}")
            # プラットフォーム別のウィンドウ切り替え実装が必要

            return OperationResult(
                status="success",
                data={"reference_id": reference_id, "window_info": window_info},
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to switch window: {str(e)}"
            )


class SwitchWindowByNameOperation(BaseOperation):
    """切り替え（名前）"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        window_name = params.get("window_name", "")
        partial_match = params.get("partial_match", False)

        error = self.validate_params(params, ["window_name"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            self.log(f"Switching to window: {window_name}")
            # プラットフォーム別のウィンドウ切り替え実装が必要

            return OperationResult(
                status="success",
                data={"window_name": window_name, "partial_match": partial_match},
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to switch window: {str(e)}"
            )


class GetWindowNameOperation(BaseOperation):
    """画面の名前を取得"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        storage_key = params.get("storage_key", "")

        error = self.validate_params(params, ["storage_key"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            # プラットフォーム別の実装が必要
            window_name = "Current Window"  # 仮の実装

            # ストレージに保存
            self.set_storage(storage_key, window_name)
            self.log(f"Stored window name as '{storage_key}': {window_name}")

            return OperationResult(
                status="success",
                data={"storage_key": storage_key, "window_name": window_name},
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to get window name: {str(e)}"
            )


class MoveWindowOperation(BaseOperation):
    """画面の移動"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        x = params.get("x", 0)
        y = params.get("y", 0)
        width = params.get("width", 800)
        height = params.get("height", 600)

        try:
            self.log(f"Moving window to ({x}, {y}) with size {width}x{height}")
            # プラットフォーム別のウィンドウ移動実装が必要

            return OperationResult(
                status="success",
                data={"x": x, "y": y, "width": width, "height": height},
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to move window: {str(e)}"
            )


class MaximizeMinimizeOperation(BaseOperation):
    """最大化/最小化"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        action = params.get("action", "maximize")

        try:
            self.log(f"Window action: {action}")
            # プラットフォーム別の実装が必要

            return OperationResult(status="success", data={"action": action})
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to {action} window: {str(e)}"
            )


class TakeScreenshotOperation(BaseOperation):
    """スクリーンショットを撮る"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        save_path = params.get("save_path", "")
        capture_area = params.get("capture_area", "full_screen")
        coordinates = params.get("coordinates", {})

        error = self.validate_params(params, ["save_path"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            # スクリーンショット実装が必要（PIL、pyautogui等を使用）
            self.log(f"Taking screenshot: {save_path}")

            # ディレクトリが存在しない場合は作成
            save_dir = os.path.dirname(save_path)
            if save_dir and not os.path.exists(save_dir):
                os.makedirs(save_dir, exist_ok=True)

            # 仮の実装（実際にはスクリーンショットライブラリを使用）
            with open(save_path, "w") as f:
                f.write("Screenshot placeholder")

            return OperationResult(
                status="success",
                data={
                    "save_path": save_path,
                    "capture_area": capture_area,
                    "coordinates": coordinates,
                },
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to take screenshot: {str(e)}"
            )
