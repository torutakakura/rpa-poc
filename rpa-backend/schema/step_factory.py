"""
RPAステップを生成するファクトリークラス
"""
import uuid
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class StepVersion:
    """ステップのバージョン管理"""
    cmd: str
    version: int
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))

    def update_version(self, new_version: int) -> str:
        """バージョンを更新し、新しいUUIDを生成"""
        if new_version != self.version:
            self.version = new_version
            self.uuid = str(uuid.uuid4())
        return self.uuid


class StepFactory:
    """ステップを生成するファクトリークラス"""

    # ステップバージョン管理用の辞書
    _step_versions: Dict[str, StepVersion] = {}

    @classmethod
    def get_or_create_uuid(cls, cmd: str, version: int) -> str:
        """
        コマンドとバージョンに基づいてUUIDを取得または生成
        バージョンが変更された場合は新しいUUIDを生成
        """
        if cmd not in cls._step_versions:
            cls._step_versions[cmd] = StepVersion(cmd, version)
        else:
            current = cls._step_versions[cmd]
            if current.version != version:
                current.update_version(version)

        return cls._step_versions[cmd].uuid

    @classmethod
    def create_step(cls, cmd: str, cmd_nickname: str, cmd_type: str,
                   version: int, parameters: Optional[Dict[str, Any]] = None,
                   description: str = "", tags: Optional[List[str]] = None,
                   **kwargs) -> Dict[str, Any]:
        """
        汎用的なステップを生成

        Args:
            cmd: コマンド名
            cmd_nickname: コマンドのニックネーム（日本語名）
            cmd_type: コマンドタイプ（basic, branching, looping等）
            version: バージョン番号
            parameters: パラメータ辞書
            description: ステップの説明文
            tags: タグリスト
            **kwargs: その他の属性

        Returns:
            ステップの辞書表現
        """
        if parameters is None:
            parameters = {}
        if tags is None:
            tags = []

        step = {
            "cmd": cmd,
            "cmd-nickname": cmd_nickname,
            "cmd-type": cmd_type,
            "version": version,
            "uuid": cls.get_or_create_uuid(cmd, version),
            "memo": kwargs.get("memo", ""),
            "description": description,
            "tags": tags,
            "parameters": parameters,
            "flags": kwargs.get("flags", {
                "checkboxed": False,
                "bookmarked": False
            })
        }

        # オプション属性を追加
        if "ext" in kwargs:
            step["ext"] = kwargs["ext"]

        if "sequence" in kwargs:
            step["sequence"] = kwargs["sequence"]

        if "sequence-0" in kwargs:
            step["sequence-0"] = kwargs["sequence-0"]

        if "sequence-1" in kwargs:
            step["sequence-1"] = kwargs["sequence-1"]

        return step

    @classmethod
    def create_basic_step(cls, cmd: str, cmd_nickname: str, version: int,
                         parameters: Optional[Dict[str, Any]] = None,
                         description: str = "", tags: Optional[List[str]] = None,
                         **kwargs) -> Dict[str, Any]:
        """基本ステップを生成"""
        return cls.create_step(cmd, cmd_nickname, "basic", version, parameters, description, tags, **kwargs)

    @classmethod
    def create_branching_step(cls, cmd: str, cmd_nickname: str, version: int,
                             parameters: Optional[Dict[str, Any]] = None,
                             description: str = "", tags: Optional[List[str]] = None,
                             sequence_0: Optional[List] = None,
                             sequence_1: Optional[List] = None,
                             **kwargs) -> Dict[str, Any]:
        """分岐ステップを生成"""
        if sequence_0 is None:
            sequence_0 = []
        if sequence_1 is None:
            sequence_1 = []

        kwargs["sequence-0"] = sequence_0
        kwargs["sequence-1"] = sequence_1

        return cls.create_step(cmd, cmd_nickname, "branching", version, parameters, description, tags, **kwargs)

    @classmethod
    def create_looping_step(cls, cmd: str, cmd_nickname: str, version: int,
                           parameters: Optional[Dict[str, Any]] = None,
                           description: str = "", tags: Optional[List[str]] = None,
                           sequence: Optional[List] = None,
                           **kwargs) -> Dict[str, Any]:
        """ループステップを生成"""
        if sequence is None:
            sequence = []

        kwargs["sequence"] = sequence
        return cls.create_step(cmd, cmd_nickname, "looping", version, parameters, description, tags, **kwargs)

    @classmethod
    def create_grouping_step(cls, cmd: str, cmd_nickname: str, version: int,
                            parameters: Optional[Dict[str, Any]] = None,
                            description: str = "", tags: Optional[List[str]] = None,
                            sequence: Optional[List] = None,
                            **kwargs) -> Dict[str, Any]:
        """グルーピングステップを生成"""
        if sequence is None:
            sequence = []

        kwargs["sequence"] = sequence
        return cls.create_step(cmd, cmd_nickname, "grouping", version, parameters, description, tags, **kwargs)

    @classmethod
    def reset_versions(cls):
        """バージョン管理をリセット（テスト用）"""
        cls._step_versions.clear()