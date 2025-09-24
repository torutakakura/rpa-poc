"""
RPAステップの基底クラスとスキーマ定義
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
import uuid as uuid_module


@dataclass
class StepFlags:
    """ステップのフラグ設定"""
    checkboxed: bool = False
    bookmarked: bool = False
    expanded: Optional[bool] = None
    checked: Optional[bool] = None
    error: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        if self.checkboxed is not None:
            result['checkboxed'] = self.checkboxed
        if self.bookmarked is not None:
            result['bookmarked'] = self.bookmarked
        if self.expanded is not None:
            result['expanded'] = self.expanded
        if self.checked is not None:
            result['checked'] = self.checked
        if self.error is not None:
            result['error'] = self.error
        return result


@dataclass
class StepParameter:
    """ステップのパラメータ基底クラス"""

    def to_dict(self) -> Dict[str, Any]:
        """パラメータを辞書形式に変換"""
        result = {}
        for key, value in asdict(self).items():
            if value is not None:
                result[key] = value
        return result


@dataclass
class BaseStep:
    """RPAステップの基底クラス"""
    cmd: str
    cmd_nickname: str
    cmd_type: str
    version: int
    uuid: str = field(default_factory=lambda: str(uuid_module.uuid4()))
    memo: str = ""
    parameters: StepParameter = field(default_factory=StepParameter)
    flags: StepFlags = field(default_factory=StepFlags)
    ext: Optional[Dict[str, Any]] = None
    sequence: Optional[List['BaseStep']] = None
    sequence_0: Optional[List['BaseStep']] = None
    sequence_1: Optional[List['BaseStep']] = None

    def to_dict(self) -> Dict[str, Any]:
        """ステップを辞書形式に変換"""
        result = {
            'cmd': self.cmd,
            'cmd-nickname': self.cmd_nickname,
            'cmd-type': self.cmd_type,
            'version': self.version,
            'uuid': self.uuid,
            'memo': self.memo,
            'parameters': self.parameters.to_dict() if isinstance(self.parameters, StepParameter) else self.parameters,
            'flags': self.flags.to_dict() if isinstance(self.flags, StepFlags) else self.flags,
        }

        if self.ext is not None:
            result['ext'] = self.ext

        if self.sequence is not None:
            result['sequence'] = [step.to_dict() for step in self.sequence]

        if self.sequence_0 is not None:
            result['sequence-0'] = [step.to_dict() for step in self.sequence_0]

        if self.sequence_1 is not None:
            result['sequence-1'] = [step.to_dict() for step in self.sequence_1]

        return result


@dataclass
class ScenarioConfig:
    """シナリオ全体の設定"""
    version: str = "38.0"
    uuid: str = field(default_factory=lambda: str(uuid_module.uuid4()))
    name: str = ""
    description: str = ""
    timestamp_created: str = field(default_factory=lambda: datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
    timestamp_last_modified: str = field(default_factory=lambda: datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
    timestamp_last_run: str = ""
    flags: Dict[str, Any] = field(default_factory=dict)
    sequence: List[BaseStep] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """シナリオを辞書形式に変換"""
        return {
            'version': self.version,
            'uuid': self.uuid,
            'name': self.name,
            'description': self.description,
            'timestamp-created': self.timestamp_created,
            'timestamp-last-modified': self.timestamp_last_modified,
            'timestamp-last-run': self.timestamp_last_run,
            'flags': self.flags,
            'sequence': [step.to_dict() for step in self.sequence]
        }