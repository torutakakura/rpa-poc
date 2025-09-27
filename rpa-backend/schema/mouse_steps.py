"""
マウス操作関連のステップ定義
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any
from .base import BaseStep, StepParameter, StepFlags


@dataclass
class MoveMouseAbsoluteParams(StepParameter):
    """マウス移動（座標）パラメータ"""
    x: str = "100"
    y: str = "100"
    click: str = "single"


@dataclass
class MoveMouseAbsoluteStep(BaseStep):
    """マウス移動（座標）ステップ"""
    def __init__(self, x: str = "100", y: str = "100", click: str = "single", **kwargs):
        super().__init__(
            cmd="move_mouse_to_absolute_coordinates",
            cmd_nickname="マウス移動（座標）",
            cmd_type="basic",
            version=2,
            parameters=MoveMouseAbsoluteParams(x=x, y=y, click=click),
            **kwargs
        )


@dataclass
class MoveMouseRelativeParams(StepParameter):
    """マウス移動（距離）パラメータ"""
    x: str = "100"
    y: str = "100"
    click: str = "single"


@dataclass
class MoveMouseRelativeStep(BaseStep):
    """マウス移動（距離）ステップ"""
    def __init__(self, x: str = "100", y: str = "100", click: str = "single", **kwargs):
        super().__init__(
            cmd="move_mouse_to_relative_coordinates",
            cmd_nickname="マウス移動（距離）",
            cmd_type="basic",
            version=2,
            parameters=MoveMouseRelativeParams(x=x, y=y, click=click),
            **kwargs
        )


@dataclass
class MoveMouseToImageParams(StepParameter):
    """マウス移動（画像認識）パラメータ"""
    filename: str = ""
    precision: str = "85"
    noise_filter: str = "100.0"
    search_area_type: str = "screen"
    search_area: str = "(0, 0) ~ (0, 0)"
    click: str = "single"


@dataclass
class MoveMouseToImageStep(BaseStep):
    """マウス移動（画像認識）ステップ"""
    def __init__(self, filename: str = "", **kwargs):
        params_data = kwargs.pop('parameters', {})
        flags_data = kwargs.pop('flags', {})

        # エラーフラグの設定
        error_flag = {
            "flag": False,
            "timestamp": "",
            "msg": ""
        }

        flags = StepFlags(
            checkboxed=flags_data.get('checkboxed', False),
            bookmarked=flags_data.get('bookmarked', False),
            checked=flags_data.get('checked', False),
            error=flags_data.get('error', error_flag)
        )

        super().__init__(
            cmd="move_mouse_to_image",
            cmd_nickname="マウス移動（画像認識）",
            cmd_type="basic",
            version=4,
            parameters=MoveMouseToImageParams(
                filename=filename,
                **params_data
            ),
            flags=flags,
            ext={},
            **kwargs
        )


@dataclass
class ClickMouseParams(StepParameter):
    """マウスクリックパラメータ"""
    type: str = "single"
    key: str = "__null__"


@dataclass
class ClickMouseStep(BaseStep):
    """マウスクリックステップ"""
    def __init__(self, click_type: str = "single", **kwargs):
        super().__init__(
            cmd="click_mouse",
            cmd_nickname="マウスクリック",
            cmd_type="basic",
            version=1,
            parameters=ClickMouseParams(type=click_type, key="__null__"),
            **kwargs
        )


@dataclass
class ScrollMouseParams(StepParameter):
    """マウススクロールパラメータ"""
    direction: str = "up"
    amount: int = 3


@dataclass
class ScrollMouseStep(BaseStep):
    """マウススクロールステップ"""
    def __init__(self, direction: str = "up", amount: int = 3, **kwargs):
        super().__init__(
            cmd="scroll_mouse",
            cmd_nickname="マウススクロール",
            cmd_type="basic",
            version=1,
            parameters=ScrollMouseParams(direction=direction, amount=amount),
            **kwargs
        )


@dataclass
class DragDropAbsoluteParams(StepParameter):
    """ドラッグ&ドロップ（座標）パラメータ"""
    x: str = "100"
    y: str = "100"


@dataclass
class DragDropAbsoluteStep(BaseStep):
    """現在位置からドラッグ&ドロップ（座標）ステップ"""
    def __init__(self, x: str = "100", y: str = "100", **kwargs):
        super().__init__(
            cmd="drag_and_drop_to_absolute_coordinates",
            cmd_nickname="現在位置からドラッグ&ドロップ（座標）",
            cmd_type="basic",
            version=1,
            parameters=DragDropAbsoluteParams(x=x, y=y),
            **kwargs
        )


@dataclass
class DragDropRelativeParams(StepParameter):
    """ドラッグ&ドロップ（距離）パラメータ"""
    x: str = "100"
    y: str = "100"


@dataclass
class DragDropRelativeStep(BaseStep):
    """現在位置からドラッグ&ドロップ（距離）ステップ"""
    def __init__(self, x: str = "100", y: str = "100", **kwargs):
        super().__init__(
            cmd="drag_and_drop_to_relative_coordinates",
            cmd_nickname="現在位置からドラッグ&ドロップ（距離）",
            cmd_type="basic",
            version=1,
            parameters=DragDropRelativeParams(x=x, y=y),
            **kwargs
        )


@dataclass
class DragDropToImageParams(StepParameter):
    """ドラッグ&ドロップ（画像認識）パラメータ"""
    filename: str = ""
    precision: str = "85"
    noise_filter: str = "100.0"
    search_area_type: str = "screen"
    search_area: str = "(0, 0) ~ (0, 0)"


@dataclass
class DragDropToImageStep(BaseStep):
    """現在位置からドラッグ&ドロップ（画像認識）ステップ"""
    def __init__(self, filename: str = "", **kwargs):
        params_data = kwargs.pop('parameters', {})
        flags_data = kwargs.pop('flags', {})

        # エラーフラグの設定
        error_flag = {
            "flag": False,
            "timestamp": "",
            "msg": ""
        }

        flags = StepFlags(
            checkboxed=flags_data.get('checkboxed', False),
            bookmarked=flags_data.get('bookmarked', False),
            checked=flags_data.get('checked', False),
            error=flags_data.get('error', error_flag)
        )

        super().__init__(
            cmd="drag_and_drop_to_image",
            cmd_nickname="現在位置からドラッグ&ドロップ（画像認識）",
            cmd_type="basic",
            version=2,
            parameters=DragDropToImageParams(
                filename=filename,
                **params_data
            ),
            flags=flags,
            ext={},
            **kwargs
        )