"""
D_キーボード カテゴリの操作
"""

import asyncio
from typing import Any, Dict

from .base import BaseOperation, OperationResult

# キーボード操作ライブラリをオプショナルでインポート
try:
    import pyautogui

    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False


class TypeTextOperation(BaseOperation):
    """文字入力"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        text = params.get("text", "")
        typing_speed = params.get("typing_speed", "normal")
        clear_before = params.get("clear_before", False)

        error = self.validate_params(params, ["text"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            self.log(
                f"Typing text: {text[:50]}..."
                if len(text) > 50
                else f"Typing text: {text}"
            )

            # 入力前にクリア
            if clear_before and PYAUTOGUI_AVAILABLE:
                pyautogui.hotkey("ctrl", "a")
                pyautogui.press("delete")

            if PYAUTOGUI_AVAILABLE:
                # 入力速度設定
                interval = (
                    0.1
                    if typing_speed == "slow"
                    else 0.05
                    if typing_speed == "normal"
                    else 0.01
                )
                pyautogui.typewrite(text, interval=interval)
            else:
                await asyncio.sleep(len(text) * 0.05)

            return OperationResult(
                status="success",
                data={
                    "text": text,
                    "typing_speed": typing_speed,
                    "clear_before": clear_before,
                },
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to type text: {str(e)}"
            )


class PressKeyOperation(BaseOperation):
    """キー押下"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        key = params.get("key", "")
        repeat = params.get("repeat", 1)
        interval = params.get("interval", 0.1)

        error = self.validate_params(params, ["key"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            self.log(f"Pressing key: {key} (repeat: {repeat})")

            if PYAUTOGUI_AVAILABLE:
                for i in range(repeat):
                    pyautogui.press(key)
                    if i < repeat - 1:
                        await asyncio.sleep(interval)
            else:
                await asyncio.sleep(0.1)

            return OperationResult(
                status="success", data={"key": key, "repeat": repeat}
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to press key: {str(e)}"
            )


class HotkeyOperation(BaseOperation):
    """ホットキー（ショートカット）"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        keys = params.get("keys", [])

        if not keys or len(keys) < 2:
            return OperationResult(
                status="failure", data={}, error="Hotkey requires at least 2 keys"
            )

        try:
            self.log(f"Pressing hotkey: {'+'.join(keys)}")

            if PYAUTOGUI_AVAILABLE:
                pyautogui.hotkey(*keys)
            else:
                await asyncio.sleep(0.1)

            return OperationResult(
                status="success", data={"keys": keys, "combination": "+".join(keys)}
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to press hotkey: {str(e)}"
            )


class CopyOperation(BaseOperation):
    """コピー（Ctrl+C）"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        try:
            self.log("Executing copy (Ctrl+C)")

            if PYAUTOGUI_AVAILABLE:
                pyautogui.hotkey("ctrl", "c")
            else:
                await asyncio.sleep(0.1)

            return OperationResult(status="success", data={"action": "copy"})
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to copy: {str(e)}"
            )


class PasteOperation(BaseOperation):
    """貼り付け（Ctrl+V）"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        try:
            self.log("Executing paste (Ctrl+V)")

            if PYAUTOGUI_AVAILABLE:
                pyautogui.hotkey("ctrl", "v")
            else:
                await asyncio.sleep(0.1)

            return OperationResult(status="success", data={"action": "paste"})
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to paste: {str(e)}"
            )


class CutOperation(BaseOperation):
    """切り取り（Ctrl+X）"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        try:
            self.log("Executing cut (Ctrl+X)")

            if PYAUTOGUI_AVAILABLE:
                pyautogui.hotkey("ctrl", "x")
            else:
                await asyncio.sleep(0.1)

            return OperationResult(status="success", data={"action": "cut"})
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to cut: {str(e)}"
            )


class SelectAllOperation(BaseOperation):
    """全選択（Ctrl+A）"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        try:
            self.log("Selecting all (Ctrl+A)")

            if PYAUTOGUI_AVAILABLE:
                pyautogui.hotkey("ctrl", "a")
            else:
                await asyncio.sleep(0.1)

            return OperationResult(status="success", data={"action": "select_all"})
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to select all: {str(e)}"
            )


class UndoOperation(BaseOperation):
    """元に戻す（Ctrl+Z）"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        try:
            self.log("Executing undo (Ctrl+Z)")

            if PYAUTOGUI_AVAILABLE:
                pyautogui.hotkey("ctrl", "z")
            else:
                await asyncio.sleep(0.1)

            return OperationResult(status="success", data={"action": "undo"})
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to undo: {str(e)}"
            )


class RedoOperation(BaseOperation):
    """やり直し（Ctrl+Y）"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        try:
            self.log("Executing redo (Ctrl+Y)")

            if PYAUTOGUI_AVAILABLE:
                pyautogui.hotkey("ctrl", "y")
            else:
                await asyncio.sleep(0.1)

            return OperationResult(status="success", data={"action": "redo"})
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to redo: {str(e)}"
            )


class TabOperation(BaseOperation):
    """Tabキー"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        count = params.get("count", 1)
        reverse = params.get("reverse", False)

        try:
            self.log(f"Pressing Tab {count} times (reverse: {reverse})")

            if PYAUTOGUI_AVAILABLE:
                for i in range(count):
                    if reverse:
                        pyautogui.hotkey("shift", "tab")
                    else:
                        pyautogui.press("tab")
                    if i < count - 1:
                        await asyncio.sleep(0.1)
            else:
                await asyncio.sleep(0.1)

            return OperationResult(
                status="success", data={"count": count, "reverse": reverse}
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to press Tab: {str(e)}"
            )


class EnterOperation(BaseOperation):
    """Enterキー"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        try:
            self.log("Pressing Enter")

            if PYAUTOGUI_AVAILABLE:
                pyautogui.press("enter")
            else:
                await asyncio.sleep(0.1)

            return OperationResult(status="success", data={"key": "enter"})
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to press Enter: {str(e)}"
            )


class EscapeOperation(BaseOperation):
    """Escキー"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        try:
            self.log("Pressing Escape")

            if PYAUTOGUI_AVAILABLE:
                pyautogui.press("escape")
            else:
                await asyncio.sleep(0.1)

            return OperationResult(status="success", data={"key": "escape"})
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to press Escape: {str(e)}"
            )
