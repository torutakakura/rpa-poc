"""
変数操作関連のステップ定義
"""
from dataclasses import dataclass
from typing import Optional, List
from .base import BaseStep, StepParameter


@dataclass
class AssignStringVariableParams(StepParameter):
    """データの記憶（文字）パラメータ"""
    variable: str = "データ"
    string: str = ""


@dataclass
class AssignStringVariableStep(BaseStep):
    """データの記憶（文字）ステップ"""
    def __init__(self, variable: str = "データ", value: str = "", **kwargs):
        super().__init__(
            cmd="assign-string-variable",
            cmd_nickname="データの記憶（文字）",
            cmd_type="basic",
            version=1,
            parameters=AssignStringVariableParams(variable=variable, string=value),
            **kwargs
        )


@dataclass
class AssignDateToStringParams(StepParameter):
    """日付を記憶パラメータ"""
    variable: str = "日付"
    offset: str = "0"
    format: str = "yyyy-mm-dd"
    zero_option: bool = False


@dataclass
class AssignDateToStringStep(BaseStep):
    """日付を記憶ステップ"""
    def __init__(self, variable: str = "日付", offset: str = "0", format: str = "yyyy-mm-dd", **kwargs):
        super().__init__(
            cmd="assign-date-to-string-variable",
            cmd_nickname="日付を記憶",
            cmd_type="basic",
            version=3,
            parameters=AssignDateToStringParams(
                variable=variable,
                offset=offset,
                format=format,
                zero_option=False
            ),
            **kwargs
        )


@dataclass
class AssignClipboardParams(StepParameter):
    """コピー内容を記憶パラメータ"""
    variable: str = "データ"


@dataclass
class AssignClipboardStep(BaseStep):
    """コピー内容を記憶ステップ"""
    def __init__(self, variable: str = "データ", **kwargs):
        super().__init__(
            cmd="assign-clipboard-to-string-variable",
            cmd_nickname="コピー内容を記憶",
            cmd_type="basic",
            version=1,
            parameters=AssignClipboardParams(variable=variable),
            **kwargs
        )


@dataclass
class CopyToClipboardParams(StepParameter):
    """クリップボードへコピーパラメータ"""
    string: str = ""


@dataclass
class CopyToClipboardStep(BaseStep):
    """クリップボードへコピーステップ"""
    def __init__(self, text: str = "", **kwargs):
        super().__init__(
            cmd="copy-to-clipboard",
            cmd_nickname="クリップボードへコピー",
            cmd_type="basic",
            version=1,
            parameters=CopyToClipboardParams(string=text),
            **kwargs
        )


@dataclass
class ParseBracketsParams(StepParameter):
    """文字列抽出（括弧・引用符号）パラメータ"""
    src_variable: str = ""
    dst_variable: str = "抽出文字"
    bracket_types: List[str] = None
    index: str = "1"
    strip: bool = True

    def __post_init__(self):
        if self.bracket_types is None:
            self.bracket_types = ["()"]


@dataclass
class ParseBracketsStep(BaseStep):
    """文字列抽出（括弧・引用符号）ステップ"""
    def __init__(self, src: str = "", dst: str = "抽出文字", **kwargs):
        params_data = kwargs.pop('parameters', {})
        super().__init__(
            cmd="parse-brackets",
            cmd_nickname="文字列抽出（括弧・引用符号）",
            cmd_type="basic",
            version=1,
            parameters=ParseBracketsParams(
                src_variable=src,
                dst_variable=dst,
                **params_data
            ),
            **kwargs
        )