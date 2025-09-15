"""
I. ファイル・フォルダ操作のスキーマ定義
"""

from .base import OperationTemplate


class FileOperations:
    """ファイル操作の定義"""

    @staticmethod
    def open() -> OperationTemplate:
        """開く"""
        return OperationTemplate(
            specific_params={
                "file_path": "",
                "application": "default",
                "wait_for_open": True,
            }
        )

    @staticmethod
    def move() -> OperationTemplate:
        """移動"""
        return OperationTemplate(
            specific_params={
                "source_path": "",
                "destination_path": "",
                "overwrite": False,
                "create_directory": True,
            }
        )

    @staticmethod
    def read() -> OperationTemplate:
        """読み込む"""
        return OperationTemplate(
            specific_params={
                "file_path": "",
                "encoding": "utf-8",
                "storage_key": "",
                "read_mode": "text",
            }
        )

    @staticmethod
    def write() -> OperationTemplate:
        """書き込む"""
        return OperationTemplate(
            specific_params={
                "file_path": "",
                "content": "",
                "encoding": "utf-8",
                "write_mode": "overwrite",
                "create_directory": True,
            }
        )


class FolderOperations:
    """フォルダ操作の定義"""

    @staticmethod
    def open() -> OperationTemplate:
        """開く"""
        return OperationTemplate(
            specific_params={"folder_path": "", "explorer_window": True}
        )

    @staticmethod
    def create() -> OperationTemplate:
        """作成"""
        return OperationTemplate(
            specific_params={
                "folder_path": "",
                "create_parents": True,
                "exist_ok": True,
            }
        )

    @staticmethod
    def loop() -> OperationTemplate:
        """ループ"""
        return OperationTemplate(
            specific_params={
                "folder_path": "",
                "pattern": "*.*",
                "include_subfolders": False,
                "file_storage_key": "",
                "path_storage_key": "",
                "loop_steps": [],
            }
        )


class FileFolderOperations:
    """ファイル・フォルダ共通操作の定義"""

    @staticmethod
    def rename() -> OperationTemplate:
        """ファイル・フォルダ名の変更"""
        return OperationTemplate(
            specific_params={"target_path": "", "new_name": "", "keep_extension": True}
        )

    @staticmethod
    def copy() -> OperationTemplate:
        """ファイル・フォルダをコピー"""
        return OperationTemplate(
            specific_params={
                "source_path": "",
                "destination_path": "",
                "overwrite": False,
                "copy_permissions": True,
            }
        )

    @staticmethod
    def delete() -> OperationTemplate:
        """ファイル・フォルダを削除"""
        return OperationTemplate(
            specific_params={"target_path": "", "move_to_trash": True, "confirm": True}
        )

    class Compression:
        @staticmethod
        def compress() -> OperationTemplate:
            """ファイル・フォルダを圧縮"""
            return OperationTemplate(
                specific_params={
                    "source_paths": [],
                    "archive_path": "",
                    "compression_type": "zip",
                    "compression_level": 6,
                    "password": "",
                }
            )

        @staticmethod
        def extract() -> OperationTemplate:
            """ファイル・フォルダに解凍"""
            return OperationTemplate(
                specific_params={
                    "archive_path": "",
                    "destination_path": "",
                    "password": "",
                    "create_folder": True,
                    "overwrite": False,
                }
            )

    class RenameWithInsert:
        @staticmethod
        def insert_text() -> OperationTemplate:
            """文字"""
            return OperationTemplate(
                specific_params={
                    "target_path": "",
                    "insert_text": "",
                    "position": "prefix",
                    "separator": "_",
                }
            )

        @staticmethod
        def insert_date() -> OperationTemplate:
            """日付"""
            return OperationTemplate(
                specific_params={
                    "target_path": "",
                    "date_format": "yyyyMMdd",
                    "position": "prefix",
                    "separator": "_",
                }
            )

        @staticmethod
        def insert_reference() -> OperationTemplate:
            """参照ID"""
            return OperationTemplate(
                specific_params={
                    "target_path": "",
                    "reference_id": "",
                    "position": "prefix",
                    "separator": "_",
                }
            )