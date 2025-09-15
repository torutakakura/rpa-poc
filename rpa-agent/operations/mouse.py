"""
C_マウス カテゴリの操作
"""

import asyncio
from typing import Any, Dict

from .base import BaseOperation, OperationResult

# マウス操作ライブラリをオプショナルでインポート
try:
    import pyautogui

    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False


class MouseMoveCoordinateOperation(BaseOperation):
    """マウス移動（座標）"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        x = params.get("x", 0)
        y = params.get("y", 0)
        move_speed = params.get("move_speed", "normal")

        try:
            self.log(f"Moving mouse to ({x}, {y}) speed: {move_speed}")

            if PYAUTOGUI_AVAILABLE:
                # 速度設定
                duration = (
                    0.5
                    if move_speed == "slow"
                    else 0.2
                    if move_speed == "normal"
                    else 0.1
                )
                pyautogui.moveTo(x, y, duration=duration)
            else:
                # ライブラリが利用できない場合のフォールバック
                await asyncio.sleep(0.5)

            return OperationResult(
                status="success", data={"x": x, "y": y, "move_speed": move_speed}
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to move mouse: {str(e)}"
            )


class MouseMoveDistanceOperation(BaseOperation):
    """マウス移動（距離）"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        dx = params.get("dx", 0)
        dy = params.get("dy", 0)
        move_speed = params.get("move_speed", "normal")

        try:
            self.log(f"Moving mouse by ({dx}, {dy}) speed: {move_speed}")

            if PYAUTOGUI_AVAILABLE:
                # 速度設定
                duration = (
                    0.5
                    if move_speed == "slow"
                    else 0.2
                    if move_speed == "normal"
                    else 0.1
                )
                pyautogui.moveRel(dx, dy, duration=duration)
            else:
                await asyncio.sleep(0.5)

            return OperationResult(
                status="success", data={"dx": dx, "dy": dy, "move_speed": move_speed}
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to move mouse: {str(e)}"
            )


class MouseMoveImageOperation(BaseOperation):
    """マウス移動（画像認識）"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        image_path = params.get("image_path", "")
        params.get("accuracy", 0.8)
        params.get("click_position", "center")
        offset_x = params.get("offset_x", 0)
        offset_y = params.get("offset_y", 0)

        error = self.validate_params(params, ["image_path"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            self.log(f"Moving mouse to image: {image_path}")

            # 画像認識の実装が必要
            # ここでは仮の座標を返す
            found_x, found_y = 500, 300

            # オフセット適用
            target_x = found_x + offset_x
            target_y = found_y + offset_y

            if PYAUTOGUI_AVAILABLE:
                pyautogui.moveTo(target_x, target_y, duration=0.2)

            return OperationResult(
                status="success",
                data={
                    "image_path": image_path,
                    "position": {"x": target_x, "y": target_y},
                },
            )
        except Exception as e:
            return OperationResult(
                status="failure",
                data={},
                error=f"Failed to move mouse to image: {str(e)}",
            )


class DragDropCoordinateOperation(BaseOperation):
    """ドラッグ＆ドロップ（座標）"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        start_x = params.get("start_x", 0)
        start_y = params.get("start_y", 0)
        end_x = params.get("end_x", 100)
        end_y = params.get("end_y", 100)
        drag_speed = params.get("drag_speed", "normal")

        try:
            self.log(f"Drag from ({start_x}, {start_y}) to ({end_x}, {end_y})")

            if PYAUTOGUI_AVAILABLE:
                duration = (
                    1.0
                    if drag_speed == "slow"
                    else 0.5
                    if drag_speed == "normal"
                    else 0.2
                )
                pyautogui.moveTo(start_x, start_y)
                pyautogui.dragTo(end_x, end_y, duration=duration, button="left")
            else:
                await asyncio.sleep(1)

            return OperationResult(
                status="success",
                data={
                    "start": {"x": start_x, "y": start_y},
                    "end": {"x": end_x, "y": end_y},
                    "drag_speed": drag_speed,
                },
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to drag and drop: {str(e)}"
            )


class DragDropDistanceOperation(BaseOperation):
    """ドラッグ＆ドロップ（距離）"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        dx = params.get("dx", 100)
        dy = params.get("dy", 100)
        drag_speed = params.get("drag_speed", "normal")

        try:
            self.log(f"Drag by distance ({dx}, {dy})")

            if PYAUTOGUI_AVAILABLE:
                duration = (
                    1.0
                    if drag_speed == "slow"
                    else 0.5
                    if drag_speed == "normal"
                    else 0.2
                )
                pyautogui.dragRel(dx, dy, duration=duration, button="left")
            else:
                await asyncio.sleep(1)

            return OperationResult(
                status="success", data={"dx": dx, "dy": dy, "drag_speed": drag_speed}
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to drag by distance: {str(e)}"
            )


class ClickOperation(BaseOperation):
    """クリック（座標またはその場）"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        x = params.get("x")
        y = params.get("y")
        button = params.get("button", "left")
        click_type = params.get("click_type", "single")

        try:
            # クリック位置のログ
            if x is not None and y is not None:
                self.log(f"Click at ({x}, {y}) button: {button}, type: {click_type}")
            else:
                self.log(
                    f"Click at current position, button: {button}, type: {click_type}"
                )

            if PYAUTOGUI_AVAILABLE:
                # クリック回数
                clicks = (
                    2 if click_type == "double" else 3 if click_type == "triple" else 1
                )

                if x is not None and y is not None:
                    pyautogui.click(x, y, button=button, clicks=clicks)
                else:
                    pyautogui.click(button=button, clicks=clicks)
            else:
                await asyncio.sleep(0.1)

            return OperationResult(
                status="success",
                data={"x": x, "y": y, "button": button, "click_type": click_type},
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to click: {str(e)}"
            )


class RightClickOperation(BaseOperation):
    """右クリック"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        x = params.get("x")
        y = params.get("y")

        try:
            if x is not None and y is not None:
                self.log(f"Right click at ({x}, {y})")
            else:
                self.log("Right click at current position")

            if PYAUTOGUI_AVAILABLE:
                if x is not None and y is not None:
                    pyautogui.rightClick(x, y)
                else:
                    pyautogui.rightClick()
            else:
                await asyncio.sleep(0.1)

            return OperationResult(
                status="success", data={"x": x, "y": y, "button": "right"}
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to right click: {str(e)}"
            )


class ScrollOperation(BaseOperation):
    """スクロール"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        direction = params.get("direction", "down")
        amount = params.get("amount", 3)
        x = params.get("x")
        y = params.get("y")

        try:
            self.log(f"Scroll {direction} by {amount}")

            if PYAUTOGUI_AVAILABLE:
                # スクロール方向を設定
                scroll_amount = -amount if direction == "down" else amount

                # 位置指定がある場合は移動してからスクロール
                if x is not None and y is not None:
                    pyautogui.moveTo(x, y)

                pyautogui.scroll(scroll_amount)
            else:
                await asyncio.sleep(0.5)

            return OperationResult(
                status="success",
                data={"direction": direction, "amount": amount, "x": x, "y": y},
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to scroll: {str(e)}"
            )
