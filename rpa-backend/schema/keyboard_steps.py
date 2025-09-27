"""
キーボード操作関連のステップ定義
"""
from dataclasses import dataclass
from .base import BaseStep, StepParameter


@dataclass
class TypeWriteStaticParams(StepParameter):
    """キーボード入力（文字）パラメータ"""
    string: str = ""
    enter: bool = False


@dataclass
class TypeWriteStaticStep(BaseStep):
    """キーボード入力（文字）ステップ"""
    def __init__(self, text: str = "", enter: bool = False, **kwargs):
        super().__init__(
            cmd="typewrite_static_string",
            cmd_nickname="キーボード入力（文字）",
            cmd_type="basic",
            version=2,
            parameters=TypeWriteStaticParams(string=text, enter=enter),
            **kwargs
        )


@dataclass
class TypeWriteAllParams(StepParameter):
    """キーボード入力（貼り付け）パラメータ"""
    string: str = ""
    enter: bool = False


@dataclass
class TypeWriteAllStep(BaseStep):
    """キーボード入力（貼り付け）ステップ"""
    def __init__(self, text: str = "", enter: bool = False, **kwargs):
        super().__init__(
            cmd="typewrite_all_string",
            cmd_nickname="キーボード入力（貼り付け）",
            cmd_type="basic",
            version=1,
            parameters=TypeWriteAllParams(string=text, enter=enter),
            **kwargs
        )


@dataclass
class TypeWritePasswordParams(StepParameter):
    """キーボード入力（パスワード）パラメータ"""
    enter: bool = False
    password_type: str = "type-input"
    ciphertext: str = ""
    nonce: str = ""
    encryption: int = 1


@dataclass
class TypeWritePasswordStep(BaseStep):
    """キーボード入力（パスワード）ステップ"""
    def __init__(self, **kwargs):
        params_data = kwargs.pop('parameters', {})
        super().__init__(
            cmd="typewrite_password",
            cmd_nickname="キーボード入力（パスワード）",
            cmd_type="basic",
            version=4,
            parameters=TypeWritePasswordParams(**params_data),
            **kwargs
        )


@dataclass
class TypeHotkeysParams(StepParameter):
    """ショートカットキーパラメータ"""
    key_0: str = "__null__"
    key_1: str = "__null__"
    key_2: str = "__null__"
    key_3: str = ""


@dataclass
class TypeHotkeysStep(BaseStep):
    """ショートカットキーを入力ステップ"""
    def __init__(self, **kwargs):
        params_data = kwargs.pop('parameters', {})
        super().__init__(
            cmd="type_hotkeys",
            cmd_nickname="ショートカットキーを入力",
            cmd_type="basic",
            version=1,
            parameters=TypeHotkeysParams(**params_data),
            **kwargs
        )