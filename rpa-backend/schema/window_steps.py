"""
ウィンドウ操作関連のステップ定義
"""
from dataclasses import dataclass
from typing import Optional
from .base import BaseStep, StepParameter


@dataclass
class RememberFocusedWindowParams(StepParameter):
    """最前面画面を覚えるパラメータ"""
    variable: str = "ウィンドウ"


@dataclass
class RememberFocusedWindowStep(BaseStep):
    """最前面画面を覚えるステップ"""
    def __init__(self, variable: str = "ウィンドウ", **kwargs):
        super().__init__(
            cmd="remember_focused_window",
            cmd_nickname="最前面画面を覚える",
            cmd_type="basic",
            version=1,
            parameters=RememberFocusedWindowParams(variable=variable),
            **kwargs
        )


@dataclass
class RememberNamedWindowParams(StepParameter):
    """画面を覚える（名前）パラメータ"""
    match_type: str = "contains"
    window_name: str = "ウィンドウ"
    variable: str = "ウィンドウ"


@dataclass
class RememberNamedWindowStep(BaseStep):
    """画面を覚える（名前）ステップ"""
    def __init__(self, window_name: str = "ウィンドウ", variable: str = "ウィンドウ", match_type: str = "contains", **kwargs):
        super().__init__(
            cmd="remember_named_window",
            cmd_nickname="画面を覚える（名前）",
            cmd_type="basic",
            version=1,
            parameters=RememberNamedWindowParams(
                match_type=match_type,
                window_name=window_name,
                variable=variable
            ),
            **kwargs
        )


@dataclass
class FocusWindowParams(StepParameter):
    """最前面画面切り替えパラメータ"""
    variable: str = ""


@dataclass
class FocusWindowStep(BaseStep):
    """最前面画面切り替えステップ"""
    def __init__(self, variable: str = "", **kwargs):
        super().__init__(
            cmd="focus_window",
            cmd_nickname="最前面画面切り替え",
            cmd_type="basic",
            version=1,
            parameters=FocusWindowParams(variable=variable),
            **kwargs
        )


@dataclass
class FocusWindowByNameParams(StepParameter):
    """画面切り替え（名前）パラメータ"""
    string: str = ""


@dataclass
class FocusWindowByNameStep(BaseStep):
    """画面切り替え（名前）ステップ"""
    def __init__(self, window_name: str = "", **kwargs):
        super().__init__(
            cmd="focus_window_by_name",
            cmd_nickname="画面切り替え（名前）",
            cmd_type="basic",
            version=1,
            parameters=FocusWindowByNameParams(string=window_name),
            **kwargs
        )


@dataclass
class GetWindowTitleParams(StepParameter):
    """画面の名前を取得パラメータ"""
    window: str = "__focused_window__"
    variable: str = "ウィンドウ名"


@dataclass
class GetWindowTitleStep(BaseStep):
    """画面の名前を取得ステップ"""
    def __init__(self, variable: str = "ウィンドウ名", window: str = "__focused_window__", **kwargs):
        super().__init__(
            cmd="get_window_title",
            cmd_nickname="画面の名前を取得",
            cmd_type="basic",
            version=1,
            parameters=GetWindowTitleParams(window=window, variable=variable),
            **kwargs
        )


@dataclass
class AlignFocusedWindowParams(StepParameter):
    """ウィンドウを移動パラメータ"""
    alignment: str = "left"


@dataclass
class AlignFocusedWindowStep(BaseStep):
    """ウィンドウを移動ステップ"""
    def __init__(self, alignment: str = "left", **kwargs):
        super().__init__(
            cmd="align_focused_window",
            cmd_nickname="ウィンドウを移動",
            cmd_type="basic",
            version=1,
            parameters=AlignFocusedWindowParams(alignment=alignment),
            **kwargs
        )


@dataclass
class MaximizeWindowParams(StepParameter):
    """ウィンドウ最大化/最小化パラメータ"""
    behavior: str = "maximize"


@dataclass
class MaximizeWindowStep(BaseStep):
    """ウィンドウ最大化/最小化ステップ"""
    def __init__(self, behavior: str = "maximize", **kwargs):
        super().__init__(
            cmd="maximize_focused_window",
            cmd_nickname="ウィンドウ最大化／最小化",
            cmd_type="basic",
            version=2,
            parameters=MaximizeWindowParams(behavior=behavior),
            **kwargs
        )