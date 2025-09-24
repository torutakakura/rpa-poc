"""
基本的なステップの定義
"""
from dataclasses import dataclass, field
from typing import Optional
from .base import BaseStep, StepParameter, StepFlags


@dataclass
class RunExecutableParams(StepParameter):
    """アプリ起動のパラメータ"""
    path: str = ""
    arguments: str = ""
    interval: int = 3
    maximized: bool = True


@dataclass
class RunExecutableStep(BaseStep):
    """アプリ起動ステップ"""
    def __init__(self, **kwargs):
        super().__init__(
            cmd="run-executable",
            cmd_nickname="アプリ起動",
            cmd_type="basic",
            version=3,
            parameters=RunExecutableParams(**kwargs.get('parameters', {})),
            **{k: v for k, v in kwargs.items() if k != 'parameters'}
        )


@dataclass
class RunExecutableAndWaitParams(StepParameter):
    """アプリ起動（終了待ち）のパラメータ"""
    path: str = ""
    arguments: str = ""
    timeout: int = 300
    output_variable: str = ""
    error_variable: str = ""


@dataclass
class RunExecutableAndWaitStep(BaseStep):
    """アプリ起動（終了待ち）ステップ"""
    def __init__(self, **kwargs):
        super().__init__(
            cmd="run-executable-and-wait",
            cmd_nickname="アプリ起動（終了待ち）",
            cmd_type="basic",
            version=1,
            parameters=RunExecutableAndWaitParams(**kwargs.get('parameters', {})),
            **{k: v for k, v in kwargs.items() if k != 'parameters'}
        )


@dataclass
class PauseParams(StepParameter):
    """待機のパラメータ"""
    interval: str = "3"


@dataclass
class PauseStep(BaseStep):
    """待機ステップ"""
    def __init__(self, interval: str = "3", **kwargs):
        super().__init__(
            cmd="pause",
            cmd_nickname="待機（秒）",
            cmd_type="basic",
            version=1,
            parameters=PauseParams(interval=interval),
            **kwargs
        )


@dataclass
class TakeScreenshotParams(StepParameter):
    """スクリーンショットのパラメータ"""
    dir_path: str = ""
    file_name: str = ""
    area: str = "area-whole"
    variable: str = ""
    timestamp: bool = False
    extension: str = "png"


@dataclass
class TakeScreenshotStep(BaseStep):
    """スクリーンショットステップ"""
    def __init__(self, **kwargs):
        super().__init__(
            cmd="take-screenshot",
            cmd_nickname="スクリーンショットを撮る",
            cmd_type="basic",
            version=1,
            parameters=TakeScreenshotParams(**kwargs.get('parameters', {})),
            **{k: v for k, v in kwargs.items() if k != 'parameters'}
        )


@dataclass
class AbortParams(StepParameter):
    """強制終了のパラメータ"""
    result_type: str = "abort"


@dataclass
class AbortStep(BaseStep):
    """作業強制終了ステップ"""
    def __init__(self, **kwargs):
        super().__init__(
            cmd="abort",
            cmd_nickname="作業強制終了",
            cmd_type="basic",
            version=2,
            parameters=AbortParams(),
            **kwargs
        )


@dataclass
class RaiseErrorParams(StepParameter):
    """エラー発生のパラメータ"""
    string: str = ""


@dataclass
class RaiseErrorStep(BaseStep):
    """エラーを発生させるステップ"""
    def __init__(self, error_message: str = "", **kwargs):
        super().__init__(
            cmd="raise-error",
            cmd_nickname="エラーを発生させる",
            cmd_type="basic",
            version=1,
            parameters=RaiseErrorParams(string=error_message),
            **kwargs
        )


@dataclass
class PauseAndAskParams(StepParameter):
    """続行確認のパラメータ"""
    string: str = ""


@dataclass
class PauseAndAskStep(BaseStep):
    """続行確認ステップ"""
    def __init__(self, message: str = "", **kwargs):
        super().__init__(
            cmd="pause-and-ask-to-proceed",
            cmd_nickname="続行確認",
            cmd_type="basic",
            version=2,
            parameters=PauseAndAskParams(string=message),
            **kwargs
        )


@dataclass
class ChangeSpeedParams(StepParameter):
    """コマンド間待機時間変更のパラメータ"""
    interval: float = 0.2


@dataclass
class ChangeSpeedStep(BaseStep):
    """コマンド間の待機時間を変更ステップ"""
    def __init__(self, interval: float = 0.2, **kwargs):
        super().__init__(
            cmd="change-speed-for-command-execution",
            cmd_nickname="コマンド間の待機時間を変更",
            cmd_type="basic",
            version=1,
            parameters=ChangeSpeedParams(interval=interval),
            **kwargs
        )