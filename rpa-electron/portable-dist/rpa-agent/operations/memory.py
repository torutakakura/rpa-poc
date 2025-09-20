"""
E_記憶 カテゴリの操作
"""

import getpass
import os
import platform
import socket
from typing import Any, Dict

from .base import BaseOperation, OperationResult


class EnvironmentInfoOperation(BaseOperation):
    """環境情報を取得して記憶"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        storage_key = params.get("storage_key", "")
        info_type = params.get("info_type", "")

        error = self.validate_params(params, ["storage_key", "info_type"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            value = None
            if info_type == "computer_name":
                value = platform.node()
            elif info_type == "user_name":
                value = getpass.getuser()
            elif info_type == "os_version":
                value = f"{platform.system()} {platform.release()}"
            elif info_type == "ip_address":
                try:
                    hostname = socket.gethostname()
                    value = socket.gethostbyname(hostname)
                except Exception:
                    value = "127.0.0.1"
            elif info_type == "current_directory":
                value = os.getcwd()
            elif info_type == "home_directory":
                value = os.path.expanduser("~")
            elif info_type == "python_version":
                value = platform.python_version()
            else:
                return OperationResult(
                    status="failure", data={}, error=f"Unknown info_type: {info_type}"
                )

            # 値を記憶
            self.set_storage(storage_key, value)
            self.log(f"Stored {info_type} as '{storage_key}': {value}")

            return OperationResult(
                status="success",
                data={
                    "storage_key": storage_key,
                    "value": value,
                    "info_type": info_type,
                },
            )
        except Exception as e:
            return OperationResult(
                status="failure",
                data={},
                error=f"Failed to get environment info: {str(e)}",
            )


class StoreValueOperation(BaseOperation):
    """値を記憶"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        storage_key = params.get("storage_key", "")
        value = params.get("value", "")
        value_type = params.get("value_type", "string")

        error = self.validate_params(params, ["storage_key", "value"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            # 型変換
            if value_type == "number":
                try:
                    value = float(value) if "." in str(value) else int(value)
                except ValueError:
                    return OperationResult(
                        status="failure",
                        data={},
                        error=f"Cannot convert '{value}' to number",
                    )
            elif value_type == "boolean":
                value = str(value).lower() in ["true", "1", "yes"]

            # 値を記憶
            self.set_storage(storage_key, value)
            self.log(f"Stored value as '{storage_key}': {value} (type: {value_type})")

            return OperationResult(
                status="success",
                data={
                    "storage_key": storage_key,
                    "value": value,
                    "value_type": value_type,
                },
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to store value: {str(e)}"
            )


class GetStoredValueOperation(BaseOperation):
    """記憶した値の取得"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        storage_key = params.get("storage_key", "")
        default_value = params.get("default_value")

        error = self.validate_params(params, ["storage_key"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            value = self.get_storage(storage_key, default_value)

            if value is None and default_value is None:
                return OperationResult(
                    status="warning",
                    data={"storage_key": storage_key},
                    error=f"No value found for key: {storage_key}",
                )

            self.log(f"Retrieved stored value for '{storage_key}': {value}")

            return OperationResult(
                status="success", data={"storage_key": storage_key, "value": value}
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to get stored value: {str(e)}"
            )


class ClearStoredValueOperation(BaseOperation):
    """記憶した値をクリア"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        storage_key = params.get("storage_key", "")
        clear_all = params.get("clear_all", False)

        try:
            if clear_all:
                # 全てクリア
                if self.agent and hasattr(self.agent, "storage"):
                    self.agent.storage.clear()
                    self.log("Cleared all stored values")
            else:
                # 特定のキーをクリア
                error = self.validate_params(params, ["storage_key"])
                if error:
                    return OperationResult(status="failure", data={}, error=error)

                if self.agent and hasattr(self.agent, "storage"):
                    if storage_key in self.agent.storage:
                        del self.agent.storage[storage_key]
                        self.log(f"Cleared stored value for '{storage_key}'")
                    else:
                        return OperationResult(
                            status="warning",
                            data={"storage_key": storage_key},
                            error=f"No value found for key: {storage_key}",
                        )

            return OperationResult(
                status="success",
                data={
                    "storage_key": storage_key if not clear_all else "all",
                    "clear_all": clear_all,
                },
            )
        except Exception as e:
            return OperationResult(
                status="failure",
                data={},
                error=f"Failed to clear stored value: {str(e)}",
            )


class ListStoredValuesOperation(BaseOperation):
    """記憶した値の一覧を取得"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        try:
            stored_values = {}
            if self.agent and hasattr(self.agent, "storage"):
                stored_values = dict(self.agent.storage)

            self.log(f"Listed {len(stored_values)} stored values")

            return OperationResult(
                status="success",
                data={"count": len(stored_values), "values": stored_values},
            )
        except Exception as e:
            return OperationResult(
                status="failure",
                data={},
                error=f"Failed to list stored values: {str(e)}",
            )


class IncrementValueOperation(BaseOperation):
    """値をインクリメント"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        storage_key = params.get("storage_key", "")
        increment_by = params.get("increment_by", 1)

        error = self.validate_params(params, ["storage_key"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            current_value = self.get_storage(storage_key, 0)

            # 数値に変換
            try:
                current_value = (
                    float(current_value)
                    if "." in str(current_value)
                    else int(current_value)
                )
            except (ValueError, TypeError):
                current_value = 0

            new_value = current_value + increment_by
            self.set_storage(storage_key, new_value)

            self.log(f"Incremented '{storage_key}': {current_value} -> {new_value}")

            return OperationResult(
                status="success",
                data={
                    "storage_key": storage_key,
                    "old_value": current_value,
                    "new_value": new_value,
                    "increment_by": increment_by,
                },
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to increment value: {str(e)}"
            )


class AppendToListOperation(BaseOperation):
    """リストに値を追加"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        storage_key = params.get("storage_key", "")
        value = params.get("value", "")

        error = self.validate_params(params, ["storage_key", "value"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            current_list = self.get_storage(storage_key, [])

            # リストでない場合は新しいリストを作成
            if not isinstance(current_list, list):
                current_list = []

            current_list.append(value)
            self.set_storage(storage_key, current_list)

            self.log(f"Appended to list '{storage_key}': {value}")

            return OperationResult(
                status="success",
                data={
                    "storage_key": storage_key,
                    "value": value,
                    "list_size": len(current_list),
                },
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to append to list: {str(e)}"
            )
