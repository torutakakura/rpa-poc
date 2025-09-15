"""
I_ファイル・フォルダ カテゴリの操作
"""

import glob
import os
import shutil
from typing import Any, Dict

from .base import BaseOperation, OperationResult


class RenameFileFolderOperation(BaseOperation):
    """ファイル・フォルダ名の変更"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        target_path = params.get("target_path", "")
        new_name = params.get("new_name", "")
        keep_extension = params.get("keep_extension", False)

        error = self.validate_params(params, ["target_path", "new_name"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            # パスを展開
            target_path = os.path.expanduser(target_path)
            new_name = os.path.expanduser(new_name)

            # 対象が存在するか確認
            if not os.path.exists(target_path):
                return OperationResult(
                    status="failure",
                    data={},
                    error=f"Target does not exist: {target_path}",
                )

            # 拡張子を保持する場合の処理
            if keep_extension and os.path.isfile(target_path):
                _, ext = os.path.splitext(target_path)
                if not new_name.endswith(ext):
                    new_name += ext

            # 移動先のディレクトリが存在しない場合は作成
            dest_dir = os.path.dirname(new_name)
            if dest_dir and not os.path.exists(dest_dir):
                os.makedirs(dest_dir, exist_ok=True)
                self.log(f"Created directory: {dest_dir}")

            # ファイル/フォルダを移動
            shutil.move(target_path, new_name)
            self.log(f"Moved/Renamed: {target_path} -> {new_name}")

            return OperationResult(
                status="success",
                data={
                    "original_path": target_path,
                    "new_path": new_name,
                    "is_directory": os.path.isdir(new_name),
                },
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to move/rename: {str(e)}"
            )


class CopyFileFolderOperation(BaseOperation):
    """ファイル・フォルダのコピー"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        source_path = params.get("source_path", "")
        destination_path = params.get("destination_path", "")
        overwrite = params.get("overwrite", False)

        error = self.validate_params(params, ["source_path", "destination_path"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            # パスを展開
            source_path = os.path.expanduser(source_path)
            destination_path = os.path.expanduser(destination_path)

            # ソースが存在するか確認
            if not os.path.exists(source_path):
                return OperationResult(
                    status="failure",
                    data={},
                    error=f"Source does not exist: {source_path}",
                )

            # 上書き確認
            if os.path.exists(destination_path) and not overwrite:
                return OperationResult(
                    status="failure",
                    data={},
                    error=f"Destination already exists: {destination_path}",
                )

            # コピー実行
            if os.path.isfile(source_path):
                # ファイルのコピー
                dest_dir = os.path.dirname(destination_path)
                if dest_dir and not os.path.exists(dest_dir):
                    os.makedirs(dest_dir, exist_ok=True)
                shutil.copy2(source_path, destination_path)
            else:
                # フォルダのコピー
                if os.path.exists(destination_path):
                    shutil.rmtree(destination_path)
                shutil.copytree(source_path, destination_path)

            self.log(f"Copied: {source_path} -> {destination_path}")

            return OperationResult(
                status="success",
                data={
                    "source_path": source_path,
                    "destination_path": destination_path,
                    "is_directory": os.path.isdir(destination_path),
                },
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to copy: {str(e)}"
            )


class DeleteFileFolderOperation(BaseOperation):
    """ファイル・フォルダの削除"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        target_path = params.get("target_path", "")
        confirm = params.get("confirm", False)

        error = self.validate_params(params, ["target_path"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        if not confirm:
            return OperationResult(
                status="failure",
                data={},
                error="Deletion requires confirmation (set confirm=True)",
            )

        try:
            # パスを展開
            target_path = os.path.expanduser(target_path)

            # 対象が存在するか確認
            if not os.path.exists(target_path):
                return OperationResult(
                    status="warning",
                    data={"target_path": target_path},
                    error=f"Target does not exist: {target_path}",
                )

            # 削除実行
            if os.path.isfile(target_path):
                os.remove(target_path)
                self.log(f"Deleted file: {target_path}")
            else:
                shutil.rmtree(target_path)
                self.log(f"Deleted folder: {target_path}")

            return OperationResult(status="success", data={"deleted_path": target_path})
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to delete: {str(e)}"
            )


class CreateFolderOperation(BaseOperation):
    """フォルダの作成"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        folder_path = params.get("folder_path", "")
        create_parents = params.get("create_parents", True)

        error = self.validate_params(params, ["folder_path"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            # パスを展開
            folder_path = os.path.expanduser(folder_path)

            # 既に存在する場合
            if os.path.exists(folder_path):
                return OperationResult(
                    status="warning",
                    data={"folder_path": folder_path},
                    error=f"Folder already exists: {folder_path}",
                )

            # フォルダ作成
            if create_parents:
                os.makedirs(folder_path, exist_ok=True)
            else:
                os.mkdir(folder_path)

            self.log(f"Created folder: {folder_path}")

            return OperationResult(status="success", data={"folder_path": folder_path})
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to create folder: {str(e)}"
            )


class ListFilesOperation(BaseOperation):
    """ファイル一覧を取得"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        folder_path = params.get("folder_path", ".")
        pattern = params.get("pattern", "*")
        recursive = params.get("recursive", False)
        storage_key = params.get("storage_key", "")

        try:
            # パスを展開
            folder_path = os.path.expanduser(folder_path)

            # パターンでファイルを検索
            if recursive:
                search_pattern = os.path.join(folder_path, "**", pattern)
                files = glob.glob(search_pattern, recursive=True)
            else:
                search_pattern = os.path.join(folder_path, pattern)
                files = glob.glob(search_pattern)

            # 相対パスに変換（オプション）
            files = [os.path.relpath(f, folder_path) for f in files]

            # ストレージに保存（指定された場合）
            if storage_key:
                self.set_storage(storage_key, files)
                self.log(f"Stored file list as '{storage_key}'")

            self.log(f"Found {len(files)} files matching '{pattern}' in {folder_path}")

            return OperationResult(
                status="success",
                data={
                    "folder_path": folder_path,
                    "pattern": pattern,
                    "files": files,
                    "count": len(files),
                },
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to list files: {str(e)}"
            )


class GetFileInfoOperation(BaseOperation):
    """ファイル情報を取得"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        file_path = params.get("file_path", "")
        storage_key = params.get("storage_key", "")

        error = self.validate_params(params, ["file_path"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            # パスを展開
            file_path = os.path.expanduser(file_path)

            # ファイルが存在するか確認
            if not os.path.exists(file_path):
                return OperationResult(
                    status="failure", data={}, error=f"File does not exist: {file_path}"
                )

            # ファイル情報を取得
            stat = os.stat(file_path)
            file_info = {
                "path": file_path,
                "name": os.path.basename(file_path),
                "size": stat.st_size,
                "is_file": os.path.isfile(file_path),
                "is_directory": os.path.isdir(file_path),
                "modified_time": stat.st_mtime,
                "created_time": stat.st_ctime,
                "extension": os.path.splitext(file_path)[1]
                if os.path.isfile(file_path)
                else None,
            }

            # ストレージに保存（指定された場合）
            if storage_key:
                self.set_storage(storage_key, file_info)
                self.log(f"Stored file info as '{storage_key}'")

            self.log(f"Got info for: {file_path}")

            return OperationResult(status="success", data=file_info)
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to get file info: {str(e)}"
            )


class ReadFileOperation(BaseOperation):
    """ファイルの読み込み"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        file_path = params.get("file_path", "")
        encoding = params.get("encoding", "utf-8")
        storage_key = params.get("storage_key", "")

        error = self.validate_params(params, ["file_path"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            # パスを展開
            file_path = os.path.expanduser(file_path)

            # ファイルを読み込み
            with open(file_path, encoding=encoding) as f:
                content = f.read()

            # ストレージに保存（指定された場合）
            if storage_key:
                self.set_storage(storage_key, content)
                self.log(f"Stored file content as '{storage_key}'")

            self.log(f"Read file: {file_path} ({len(content)} characters)")

            return OperationResult(
                status="success",
                data={"file_path": file_path, "content": content, "size": len(content)},
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to read file: {str(e)}"
            )


class WriteFileOperation(BaseOperation):
    """ファイルの書き込み"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        file_path = params.get("file_path", "")
        content = params.get("content", "")
        encoding = params.get("encoding", "utf-8")
        append = params.get("append", False)

        error = self.validate_params(params, ["file_path", "content"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            # パスを展開
            file_path = os.path.expanduser(file_path)

            # ディレクトリが存在しない場合は作成
            dir_path = os.path.dirname(file_path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)

            # ファイルに書き込み
            mode = "a" if append else "w"
            with open(file_path, mode, encoding=encoding) as f:
                f.write(content)

            self.log(f"{'Appended to' if append else 'Wrote'} file: {file_path}")

            return OperationResult(
                status="success",
                data={"file_path": file_path, "size": len(content), "append": append},
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to write file: {str(e)}"
            )
