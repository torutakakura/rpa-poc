"""
RPA操作定義システム - Python実装
操作テンプレートの定義とJSON生成
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Union

# ===========================
# 共通定義
# ===========================


class ErrorHandling(Enum):
    """エラーハンドリングの種類"""

    STOP = "stop"
    CONTINUE = "continue"
    RETRY = "retry"
    SKIP = "skip"


@dataclass
class CommonParams:
    """全操作共通のパラメータ"""

    memo: str = ""
    timeout: int = 30
    retry_count: int = 0
    error_handling: str = ErrorHandling.STOP.value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "memo": self.memo,
            "timeout": self.timeout,
            "retry_count": self.retry_count,
            "error_handling": self.error_handling,
        }


@dataclass
class OperationTemplate:
    """操作テンプレートの基底クラス"""

    common_params: CommonParams = field(default_factory=CommonParams)
    specific_params: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "common_params": self.common_params.to_dict(),
            "specific_params": self.specific_params,
        }


# ===========================
# A. アプリ・画面
# ===========================


class AppOperations:
    """アプリ操作の定義"""

    @staticmethod
    def launch() -> OperationTemplate:
        """起動"""
        return OperationTemplate(
            specific_params={
                "app_path": "",
                "wait_time": 5,
                "maximize_window": False,
                "arguments": "",
                "working_directory": "",
            }
        )

    @staticmethod
    def launch_and_wait() -> OperationTemplate:
        """起動（終了待ち）"""
        return OperationTemplate(
            common_params=CommonParams(timeout=300),
            specific_params={
                "app_path": "",
                "maximize_window": False,
                "arguments": "",
                "working_directory": "",
            },
        )


class ScreenOperations:
    """画面操作の定義"""

    @staticmethod
    def remember_foreground() -> OperationTemplate:
        """最前画面を覚える"""
        return OperationTemplate(specific_params={"reference_id": ""})

    @staticmethod
    def remember_by_name() -> OperationTemplate:
        """画面を覚える（名前）"""
        return OperationTemplate(
            specific_params={
                "window_name": "",
                "reference_id": "",
                "partial_match": False,
            }
        )

    @staticmethod
    def switch_by_reference() -> OperationTemplate:
        """切り替え（参照ID）"""
        return OperationTemplate(specific_params={"reference_id": ""})

    @staticmethod
    def switch_by_name() -> OperationTemplate:
        """切り替え（名前）"""
        return OperationTemplate(
            specific_params={"window_name": "", "partial_match": False}
        )

    @staticmethod
    def get_window_name() -> OperationTemplate:
        """画面の名前を取得"""
        return OperationTemplate(specific_params={"storage_key": ""})

    @staticmethod
    def move() -> OperationTemplate:
        """移動"""
        return OperationTemplate(
            specific_params={"x": 0, "y": 0, "width": 800, "height": 600}
        )

    @staticmethod
    def maximize_minimize() -> OperationTemplate:
        """最大化/最小化"""
        return OperationTemplate(specific_params={"action": "maximize"})

    @staticmethod
    def take_screenshot() -> OperationTemplate:
        """スクリーンショットを撮る"""
        return OperationTemplate(
            specific_params={
                "save_path": "",
                "capture_area": "full_screen",
                "coordinates": {"x": 0, "y": 0, "width": 0, "height": 0},
            }
        )


# ===========================
# B. 待機・終了・エラー
# ===========================


class WaitErrorOperations:
    """待機・終了・エラー操作の定義"""

    @staticmethod
    def wait_seconds() -> OperationTemplate:
        """秒"""
        return OperationTemplate(specific_params={"wait_seconds": 1})

    @staticmethod
    def wait_for_image() -> OperationTemplate:
        """画像出現を待つ"""
        return OperationTemplate(
            common_params=CommonParams(timeout=60),
            specific_params={
                "image_path": "",
                "accuracy": 0.8,
                "search_area": "full_screen",
                "coordinates": {"x": 0, "y": 0, "width": 0, "height": 0},
            },
        )

    @staticmethod
    def continue_confirmation() -> OperationTemplate:
        """続行確認"""
        return OperationTemplate(specific_params={"message": "", "title": "続行確認"})

    @staticmethod
    def timed_continue_confirmation() -> OperationTemplate:
        """タイマー付き続行確認（秒）"""
        return OperationTemplate(
            specific_params={
                "message": "",
                "title": "続行確認",
                "countdown_seconds": 10,
            }
        )

    @staticmethod
    def change_command_interval() -> OperationTemplate:
        """コマンド間待機時間を変更"""
        return OperationTemplate(specific_params={"interval_ms": 500})

    @staticmethod
    def force_terminate() -> OperationTemplate:
        """作業強制終了"""
        return OperationTemplate(specific_params={"exit_code": 0})

    @staticmethod
    def raise_error() -> OperationTemplate:
        """エラー発生"""
        return OperationTemplate(
            specific_params={"error_message": "", "error_code": ""}
        )

    @staticmethod
    def error_handling() -> OperationTemplate:
        """エラー確認・処理"""
        return OperationTemplate(
            common_params=CommonParams(error_handling=ErrorHandling.CONTINUE.value),
            specific_params={"on_error_steps": [], "clear_error": True},
        )

    @staticmethod
    def error_handling_with_retry() -> OperationTemplate:
        """エラー確認・処理（リトライ前処理）"""
        return OperationTemplate(
            common_params=CommonParams(
                retry_count=3, error_handling=ErrorHandling.RETRY.value
            ),
            specific_params={
                "retry_interval": 5,
                "on_retry_steps": [],
                "on_error_steps": [],
            },
        )


# ===========================
# C. マウス
# ===========================


class MouseOperations:
    """マウス操作の定義"""

    class Move:
        @staticmethod
        def by_coordinates() -> OperationTemplate:
            """座標"""
            return OperationTemplate(
                specific_params={"x": 0, "y": 0, "move_speed": "normal"}
            )

        @staticmethod
        def by_distance() -> OperationTemplate:
            """距離"""
            return OperationTemplate(
                specific_params={"dx": 0, "dy": 0, "move_speed": "normal"}
            )

        @staticmethod
        def by_image() -> OperationTemplate:
            """画像認識"""
            return OperationTemplate(
                specific_params={
                    "image_path": "",
                    "accuracy": 0.8,
                    "click_position": "center",
                    "offset_x": 0,
                    "offset_y": 0,
                }
            )

    class DragAndDrop:
        @staticmethod
        def by_coordinates() -> OperationTemplate:
            """座標（D&D）"""
            return OperationTemplate(
                specific_params={
                    "start_x": 0,
                    "start_y": 0,
                    "end_x": 0,
                    "end_y": 0,
                    "drag_speed": "normal",
                }
            )

        @staticmethod
        def by_distance() -> OperationTemplate:
            """距離（D&D）"""
            return OperationTemplate(
                specific_params={"dx": 0, "dy": 0, "drag_speed": "normal"}
            )

        @staticmethod
        def by_image() -> OperationTemplate:
            """画像認識（D&D）"""
            return OperationTemplate(
                specific_params={
                    "start_image_path": "",
                    "end_image_path": "",
                    "accuracy": 0.8,
                    "drag_speed": "normal",
                }
            )

    @staticmethod
    def click() -> OperationTemplate:
        """マウスクリック"""
        return OperationTemplate(
            specific_params={
                "button": "left",
                "click_type": "single",
                "x": None,
                "y": None,
            }
        )

    @staticmethod
    def scroll() -> OperationTemplate:
        """スクロール"""
        return OperationTemplate(specific_params={"direction": "down", "amount": 3})


# ===========================
# D. キーボード
# ===========================


class KeyboardOperations:
    """キーボード操作の定義"""

    class Input:
        @staticmethod
        def text() -> OperationTemplate:
            """文字"""
            return OperationTemplate(
                specific_params={
                    "text": "",
                    "typing_speed": "normal",
                    "clear_before": False,
                }
            )

        @staticmethod
        def paste() -> OperationTemplate:
            """文字（貼り付け）"""
            return OperationTemplate(
                specific_params={"text": "", "clear_before": False}
            )

        @staticmethod
        def password() -> OperationTemplate:
            """パスワード"""
            return OperationTemplate(
                specific_params={
                    "password_key": "",
                    "clear_before": False,
                    "encrypted": True,
                }
            )

        @staticmethod
        def shortcut() -> OperationTemplate:
            """ショートカットキー"""
            return OperationTemplate(specific_params={"keys": [], "hold_duration": 0})


# ===========================
# E. 記憶
# ===========================


class MemoryOperations:
    """記憶操作の定義"""

    @staticmethod
    def store_text() -> OperationTemplate:
        """文字"""
        return OperationTemplate(specific_params={"storage_key": "", "value": ""})

    @staticmethod
    def store_password() -> OperationTemplate:
        """パスワード"""
        return OperationTemplate(
            specific_params={"storage_key": "", "value": "", "encrypted": True}
        )

    @staticmethod
    def store_environment_info() -> OperationTemplate:
        """環境情報"""
        return OperationTemplate(
            specific_params={"storage_key": "", "info_type": "computer_name"}
        )

    @staticmethod
    def store_date() -> OperationTemplate:
        """日付"""
        return OperationTemplate(
            specific_params={
                "storage_key": "",
                "date_type": "today",
                "format": "yyyy/MM/dd",
            }
        )

    @staticmethod
    def store_business_date() -> OperationTemplate:
        """日付（営業日）"""
        return OperationTemplate(
            specific_params={
                "storage_key": "",
                "business_days": 1,
                "format": "yyyy/MM/dd",
                "holiday_calendar": "japan",
            }
        )

    @staticmethod
    def store_weekday_date() -> OperationTemplate:
        """日付（曜日）"""
        return OperationTemplate(
            specific_params={
                "storage_key": "",
                "target_weekday": "monday",
                "direction": "next",
                "format": "yyyy/MM/dd",
            }
        )

    @staticmethod
    def calculate_date() -> OperationTemplate:
        """日付計算"""
        return OperationTemplate(
            specific_params={
                "storage_key": "",
                "base_date": "today",
                "operation": "add",
                "days": 0,
                "months": 0,
                "years": 0,
                "format": "yyyy/MM/dd",
            }
        )

    @staticmethod
    def store_weekday() -> OperationTemplate:
        """曜日"""
        return OperationTemplate(
            specific_params={"storage_key": "", "date": "today", "format": "japanese"}
        )

    @staticmethod
    def store_time() -> OperationTemplate:
        """時刻"""
        return OperationTemplate(
            specific_params={"storage_key": "", "format": "HH:mm:ss"}
        )

    @staticmethod
    def calculate_time() -> OperationTemplate:
        """時刻計算"""
        return OperationTemplate(
            specific_params={
                "storage_key": "",
                "base_time": "now",
                "operation": "add",
                "hours": 0,
                "minutes": 0,
                "seconds": 0,
                "format": "HH:mm:ss",
            }
        )

    @staticmethod
    def calculate() -> OperationTemplate:
        """計算"""
        return OperationTemplate(
            specific_params={"storage_key": "", "expression": "", "decimal_places": 2}
        )

    @staticmethod
    def random_number() -> OperationTemplate:
        """乱数"""
        return OperationTemplate(
            specific_params={"storage_key": "", "min": 0, "max": 100, "type": "integer"}
        )

    @staticmethod
    def get_clipboard() -> OperationTemplate:
        """コピー内容"""
        return OperationTemplate(specific_params={"storage_key": ""})

    @staticmethod
    def set_clipboard() -> OperationTemplate:
        """クリップボードへコピー"""
        return OperationTemplate(specific_params={"value": ""})

    @staticmethod
    def runtime_input() -> OperationTemplate:
        """実行中に入力"""
        return OperationTemplate(
            common_params=CommonParams(timeout=300),
            specific_params={
                "storage_key": "",
                "prompt": "",
                "input_type": "text",
                "default_value": "",
            },
        )

    @staticmethod
    def file_modified_date() -> OperationTemplate:
        """ファイル更新日時"""
        return OperationTemplate(
            specific_params={
                "storage_key": "",
                "file_path": "",
                "format": "yyyy/MM/dd HH:mm:ss",
            }
        )

    @staticmethod
    def file_size() -> OperationTemplate:
        """ファイルサイズ"""
        return OperationTemplate(
            specific_params={"storage_key": "", "file_path": "", "unit": "bytes"}
        )

    @staticmethod
    def latest_file_or_folder() -> OperationTemplate:
        """最新ファイル・フォルダ"""
        return OperationTemplate(
            specific_params={
                "storage_key": "",
                "directory_path": "",
                "target_type": "file",
                "pattern": "*.*",
            }
        )


# ===========================
# F. 文字抽出
# ===========================


class TextExtractOperations:
    """文字抽出操作の定義"""

    @staticmethod
    def from_brackets() -> OperationTemplate:
        """括弧・引用符号から"""
        return OperationTemplate(
            specific_params={
                "storage_key": "",
                "source_text": "",
                "bracket_type": "parentheses",
                "occurrence": 1,
            }
        )

    @staticmethod
    def from_delimiter() -> OperationTemplate:
        """区切り文字から"""
        return OperationTemplate(
            specific_params={
                "storage_key": "",
                "source_text": "",
                "delimiter": ",",
                "position": 1,
            }
        )

    @staticmethod
    def remove_whitespace() -> OperationTemplate:
        """改行・空白を削除"""
        return OperationTemplate(
            specific_params={
                "storage_key": "",
                "source_text": "",
                "remove_newlines": True,
                "remove_spaces": True,
                "remove_tabs": True,
            }
        )

    @staticmethod
    def from_filepath() -> OperationTemplate:
        """ファイルパスから"""
        return OperationTemplate(
            specific_params={
                "storage_key": "",
                "file_path": "",
                "extract_type": "filename",
            }
        )

    @staticmethod
    def match_pattern() -> OperationTemplate:
        """ルールにマッチ"""
        return OperationTemplate(
            specific_params={
                "storage_key": "",
                "source_text": "",
                "pattern": "",
                "regex": False,
                "occurrence": 1,
            }
        )

    @staticmethod
    def replace() -> OperationTemplate:
        """置換"""
        return OperationTemplate(
            specific_params={
                "storage_key": "",
                "source_text": "",
                "find": "",
                "replace": "",
                "replace_all": True,
            }
        )

    @staticmethod
    def convert_text() -> OperationTemplate:
        """文字変換"""
        return OperationTemplate(
            specific_params={
                "storage_key": "",
                "source_text": "",
                "conversion_type": "uppercase",
            }
        )

    @staticmethod
    def convert_date_format() -> OperationTemplate:
        """日付形式変換"""
        return OperationTemplate(
            specific_params={
                "storage_key": "",
                "source_date": "",
                "source_format": "yyyy/MM/dd",
                "target_format": "yyyy-MM-dd",
            }
        )

    @staticmethod
    def loop_lines() -> OperationTemplate:
        """1行ずつループ"""
        return OperationTemplate(
            specific_params={
                "source_text": "",
                "line_storage_key": "",
                "index_storage_key": "",
                "loop_steps": [],
            }
        )


# ===========================
# G. 分岐
# ===========================


class BranchOperations:
    """分岐操作の定義"""

    @staticmethod
    def string_condition() -> OperationTemplate:
        """文字列"""
        return OperationTemplate(
            specific_params={
                "left_value": "",
                "operator": "equals",
                "right_value": "",
                "case_sensitive": True,
                "true_steps": [],
                "false_steps": [],
            }
        )

    @staticmethod
    def numeric_condition() -> OperationTemplate:
        """数値"""
        return OperationTemplate(
            specific_params={
                "left_value": 0,
                "operator": "equals",
                "right_value": 0,
                "true_steps": [],
                "false_steps": [],
            }
        )

    @staticmethod
    def date_condition() -> OperationTemplate:
        """日付"""
        return OperationTemplate(
            specific_params={
                "left_date": "",
                "operator": "equals",
                "right_date": "",
                "date_format": "yyyy/MM/dd",
                "true_steps": [],
                "false_steps": [],
            }
        )

    @staticmethod
    def file_exists() -> OperationTemplate:
        """ファイル・フォルダの有/無を確認"""
        return OperationTemplate(
            specific_params={
                "path": "",
                "check_type": "exists",
                "true_steps": [],
                "false_steps": [],
            }
        )

    @staticmethod
    def image_exists() -> OperationTemplate:
        """画像"""
        return OperationTemplate(
            specific_params={
                "image_path": "",
                "accuracy": 0.8,
                "search_area": "full_screen",
                "found_steps": [],
                "not_found_steps": [],
            }
        )


# ===========================
# H. 繰り返し
# ===========================


class LoopOperations:
    """繰り返し操作の定義"""

    @staticmethod
    def loop() -> OperationTemplate:
        """繰り返し"""
        return OperationTemplate(
            specific_params={
                "loop_type": "count",
                "count": 10,
                "condition": "",
                "max_iterations": 1000,
                "index_storage_key": "",
                "loop_steps": [],
            }
        )

    @staticmethod
    def break_loop() -> OperationTemplate:
        """繰り返しを抜ける"""
        return OperationTemplate(specific_params={"condition": ""})

    @staticmethod
    def continue_loop() -> OperationTemplate:
        """繰り返しの最初に戻る"""
        return OperationTemplate(specific_params={"condition": ""})


# ===========================
# I. ファイル・フォルダ
# ===========================


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


# ===========================
# J. エクセル・CSV
# ===========================


class ExcelOperations:
    """エクセル・CSV操作の定義"""

    class Workbook:
        @staticmethod
        def open() -> OperationTemplate:
            """ブックを開く"""
            return OperationTemplate(
                specific_params={
                    "file_path": "",
                    "reference_id": "",
                    "read_only": False,
                    "password": "",
                    "update_links": False,
                }
            )

        @staticmethod
        def remember() -> OperationTemplate:
            """ブックを覚える"""
            return OperationTemplate(
                specific_params={"reference_id": "", "workbook_name": ""}
            )

        @staticmethod
        def save() -> OperationTemplate:
            """ブックを保存"""
            return OperationTemplate(
                specific_params={
                    "reference_id": "",
                    "save_as": False,
                    "file_path": "",
                    "file_format": "xlsx",
                }
            )

        @staticmethod
        def close() -> OperationTemplate:
            """ブックを閉じる"""
            return OperationTemplate(
                specific_params={"reference_id": "", "save_changes": True}
            )

    class Sheet:
        @staticmethod
        def create() -> OperationTemplate:
            """新規作成"""
            return OperationTemplate(
                specific_params={
                    "reference_id": "",
                    "sheet_name": "",
                    "position": "last",
                }
            )

        @staticmethod
        def delete() -> OperationTemplate:
            """削除"""
            return OperationTemplate(
                specific_params={"reference_id": "", "sheet_name": ""}
            )

        @staticmethod
        def switch() -> OperationTemplate:
            """切り替え"""
            return OperationTemplate(
                specific_params={
                    "reference_id": "",
                    "sheet_name": "",
                    "sheet_index": None,
                }
            )

        @staticmethod
        def move_or_copy() -> OperationTemplate:
            """移動・コピー"""
            return OperationTemplate(
                specific_params={
                    "reference_id": "",
                    "source_sheet": "",
                    "action": "move",
                    "position": "last",
                    "new_name": "",
                }
            )

        @staticmethod
        def get_name() -> OperationTemplate:
            """名前取得"""
            return OperationTemplate(
                specific_params={
                    "reference_id": "",
                    "storage_key": "",
                    "sheet_index": None,
                }
            )

        @staticmethod
        def rename() -> OperationTemplate:
            """名前変更"""
            return OperationTemplate(
                specific_params={"reference_id": "", "old_name": "", "new_name": ""}
            )

    class Cell:
        @staticmethod
        def select_range() -> OperationTemplate:
            """範囲指定"""
            return OperationTemplate(
                specific_params={"reference_id": "", "range": "A1", "select": True}
            )

        @staticmethod
        def move_range() -> OperationTemplate:
            """指定範囲の移動"""
            return OperationTemplate(
                specific_params={
                    "reference_id": "",
                    "source_range": "A1",
                    "target_range": "B1",
                    "cut": True,
                }
            )

        @staticmethod
        def delete_range() -> OperationTemplate:
            """指定範囲の削除"""
            return OperationTemplate(
                specific_params={"reference_id": "", "range": "A1", "shift": "up"}
            )

        @staticmethod
        def insert_cells() -> OperationTemplate:
            """指定範囲にセルを挿入"""
            return OperationTemplate(
                specific_params={"reference_id": "", "range": "A1", "shift": "down"}
            )

        @staticmethod
        def get_value() -> OperationTemplate:
            """値を取得"""
            return OperationTemplate(
                specific_params={
                    "reference_id": "",
                    "range": "A1",
                    "storage_key": "",
                    "value_type": "value",
                }
            )

        @staticmethod
        def set_value() -> OperationTemplate:
            """値を入力"""
            return OperationTemplate(
                specific_params={
                    "reference_id": "",
                    "range": "A1",
                    "value": "",
                    "value_type": "value",
                }
            )

        @staticmethod
        def copy_cells() -> OperationTemplate:
            """セルをコピー"""
            return OperationTemplate(
                specific_params={"reference_id": "", "range": "A1"}
            )

        @staticmethod
        def paste_cells() -> OperationTemplate:
            """セルを貼り付け"""
            return OperationTemplate(
                specific_params={"reference_id": "", "range": "A1", "paste_type": "all"}
            )

        @staticmethod
        def find_position() -> OperationTemplate:
            """位置を取得"""
            return OperationTemplate(
                specific_params={
                    "reference_id": "",
                    "search_value": "",
                    "search_range": "",
                    "row_storage_key": "",
                    "column_storage_key": "",
                }
            )

        @staticmethod
        def get_last_row() -> OperationTemplate:
            """最終行取得"""
            return OperationTemplate(
                specific_params={"reference_id": "", "column": "A", "storage_key": ""}
            )

        @staticmethod
        def get_last_column() -> OperationTemplate:
            """最終列取得"""
            return OperationTemplate(
                specific_params={"reference_id": "", "row": 1, "storage_key": ""}
            )

        @staticmethod
        def column_calculation() -> OperationTemplate:
            """列計算"""
            return OperationTemplate(
                specific_params={
                    "reference_id": "",
                    "range": "A:A",
                    "operation": "sum",
                    "storage_key": "",
                }
            )

        @staticmethod
        def run_macro() -> OperationTemplate:
            """マクロ実行"""
            return OperationTemplate(
                common_params=CommonParams(timeout=60),
                specific_params={"reference_id": "", "macro_name": "", "arguments": []},
            )

        @staticmethod
        def row_loop() -> OperationTemplate:
            """行ループ"""
            return OperationTemplate(
                specific_params={
                    "reference_id": "",
                    "start_row": 1,
                    "end_row": None,
                    "row_storage_key": "",
                    "loop_steps": [],
                }
            )

        @staticmethod
        def column_loop() -> OperationTemplate:
            """列ループ"""
            return OperationTemplate(
                specific_params={
                    "reference_id": "",
                    "start_column": "A",
                    "end_column": None,
                    "column_storage_key": "",
                    "loop_steps": [],
                }
            )

        @staticmethod
        def csv_read_loop() -> OperationTemplate:
            """CSV読込ループ"""
            return OperationTemplate(
                specific_params={
                    "file_path": "",
                    "encoding": "utf-8",
                    "delimiter": ",",
                    "has_header": True,
                    "row_storage_keys": {},
                    "loop_steps": [],
                }
            )


# ===========================
# RPAシステムメインクラス
# ===========================


class RPAOperationSystem:
    """RPA操作定義システムのメインクラス"""

    def __init__(self):
        self.operations = {}
        self._build_operations()

    def _build_operations(self):
        """全操作の定義を構築"""

        # A. アプリ・画面
        self.operations["A_アプリ・画面"] = {
            "アプリ": {
                "起動": AppOperations.launch(),
                "起動（終了待ち）": AppOperations.launch_and_wait(),
            },
            "画面": {
                "最前画面を覚える": ScreenOperations.remember_foreground(),
                "画面を覚える（名前）": ScreenOperations.remember_by_name(),
                "切り替え（参照ID）": ScreenOperations.switch_by_reference(),
                "切り替え（名前）": ScreenOperations.switch_by_name(),
                "画面の名前を取得": ScreenOperations.get_window_name(),
                "移動": ScreenOperations.move(),
                "最大化/最小化": ScreenOperations.maximize_minimize(),
                "スクリーンショットを撮る": ScreenOperations.take_screenshot(),
            },
        }

        # B. 待機・終了・エラー
        self.operations["B_待機・終了・エラー"] = {
            "秒": WaitErrorOperations.wait_seconds(),
            "画像出現を待つ": WaitErrorOperations.wait_for_image(),
            "続行確認": WaitErrorOperations.continue_confirmation(),
            "タイマー付き続行確認（秒）": WaitErrorOperations.timed_continue_confirmation(),
            "コマンド間待機時間を変更": WaitErrorOperations.change_command_interval(),
            "作業強制終了": WaitErrorOperations.force_terminate(),
            "エラー発生": WaitErrorOperations.raise_error(),
            "エラー確認・処理": WaitErrorOperations.error_handling(),
            "エラー確認・処理（リトライ前処理）": WaitErrorOperations.error_handling_with_retry(),
        }

        # C. マウス
        self.operations["C_マウス"] = {
            "移動": {
                "座標": MouseOperations.Move.by_coordinates(),
                "距離": MouseOperations.Move.by_distance(),
                "画像認識": MouseOperations.Move.by_image(),
            },
            "ドラッグ＆ドロップ": {
                "座標（D&D）": MouseOperations.DragAndDrop.by_coordinates(),
                "距離（D&D）": MouseOperations.DragAndDrop.by_distance(),
                "画像認識（D&D）": MouseOperations.DragAndDrop.by_image(),
            },
            "マウスクリック": MouseOperations.click(),
            "スクロール": MouseOperations.scroll(),
        }

        # D. キーボード
        self.operations["D_キーボード"] = {
            "入力": {
                "文字": KeyboardOperations.Input.text(),
                "文字（貼り付け）": KeyboardOperations.Input.paste(),
                "パスワード": KeyboardOperations.Input.password(),
                "ショートカットキー": KeyboardOperations.Input.shortcut(),
            }
        }

        # E. 記憶
        self.operations["E_記憶"] = {
            "文字": MemoryOperations.store_text(),
            "パスワード": MemoryOperations.store_password(),
            "環境情報": MemoryOperations.store_environment_info(),
            "日付": MemoryOperations.store_date(),
            "日付（営業日）": MemoryOperations.store_business_date(),
            "日付（曜日）": MemoryOperations.store_weekday_date(),
            "日付計算": MemoryOperations.calculate_date(),
            "曜日": MemoryOperations.store_weekday(),
            "時刻": MemoryOperations.store_time(),
            "時刻計算": MemoryOperations.calculate_time(),
            "計算": MemoryOperations.calculate(),
            "乱数": MemoryOperations.random_number(),
            "コピー内容": MemoryOperations.get_clipboard(),
            "クリップボードへコピー": MemoryOperations.set_clipboard(),
            "実行中に入力": MemoryOperations.runtime_input(),
            "ファイル更新日時": MemoryOperations.file_modified_date(),
            "ファイルサイズ": MemoryOperations.file_size(),
            "最新ファイル・フォルダ": MemoryOperations.latest_file_or_folder(),
        }

        # F. 文字抽出
        self.operations["F_文字抽出"] = {
            "括弧・引用符号から": TextExtractOperations.from_brackets(),
            "区切り文字から": TextExtractOperations.from_delimiter(),
            "改行・空白を削除": TextExtractOperations.remove_whitespace(),
            "ファイルパスから": TextExtractOperations.from_filepath(),
            "ルールにマッチ": TextExtractOperations.match_pattern(),
            "置換": TextExtractOperations.replace(),
            "文字変換": TextExtractOperations.convert_text(),
            "日付形式変換": TextExtractOperations.convert_date_format(),
            "1行ずつループ": TextExtractOperations.loop_lines(),
        }

        # G. 分岐
        self.operations["G_分岐"] = {
            "文字列": BranchOperations.string_condition(),
            "数値": BranchOperations.numeric_condition(),
            "日付": BranchOperations.date_condition(),
            "ファイル・フォルダの有/無を確認": BranchOperations.file_exists(),
            "画像": BranchOperations.image_exists(),
        }

        # H. 繰り返し
        self.operations["H_繰り返し"] = {
            "繰り返し": LoopOperations.loop(),
            "繰り返しを抜ける": LoopOperations.break_loop(),
            "繰り返しの最初に戻る": LoopOperations.continue_loop(),
        }

        # I. ファイル・フォルダ
        self.operations["I_ファイル・フォルダ"] = {
            "ファイル": {
                "開く": FileOperations.open(),
                "移動": FileOperations.move(),
                "読み込む": FileOperations.read(),
                "書き込む": FileOperations.write(),
            },
            "フォルダ": {
                "開く": FolderOperations.open(),
                "作成": FolderOperations.create(),
                "ループ": FolderOperations.loop(),
            },
            "ファイル・フォルダ名の変更": FileFolderOperations.rename(),
            "ファイル・フォルダをコピー": FileFolderOperations.copy(),
            "ファイル・フォルダを削除": FileFolderOperations.delete(),
            "圧縮・解凍": {
                "ファイル・フォルダを圧縮": FileFolderOperations.Compression.compress(),
                "ファイル・フォルダに解凍": FileFolderOperations.Compression.extract(),
            },
            "ファイル名変更（挿入）": {
                "文字": FileFolderOperations.RenameWithInsert.insert_text(),
                "日付": FileFolderOperations.RenameWithInsert.insert_date(),
                "参照ID": FileFolderOperations.RenameWithInsert.insert_reference(),
            },
        }

        # J. エクセル・CSV
        self.operations["J_エクセル・CSV"] = {
            "ブック": {
                "ブックを開く": ExcelOperations.Workbook.open(),
                "ブックを覚える": ExcelOperations.Workbook.remember(),
                "ブックを保存": ExcelOperations.Workbook.save(),
                "ブックを閉じる": ExcelOperations.Workbook.close(),
            },
            "シート操作": {
                "新規作成": ExcelOperations.Sheet.create(),
                "削除": ExcelOperations.Sheet.delete(),
                "切り替え": ExcelOperations.Sheet.switch(),
                "移動・コピー": ExcelOperations.Sheet.move_or_copy(),
                "名前取得": ExcelOperations.Sheet.get_name(),
                "名前変更": ExcelOperations.Sheet.rename(),
            },
            "セル操作": {
                "範囲指定": ExcelOperations.Cell.select_range(),
                "指定範囲の移動": ExcelOperations.Cell.move_range(),
                "指定範囲の削除": ExcelOperations.Cell.delete_range(),
                "指定範囲にセルを挿入": ExcelOperations.Cell.insert_cells(),
                "値を取得": ExcelOperations.Cell.get_value(),
                "値を入力": ExcelOperations.Cell.set_value(),
                "セルをコピー": ExcelOperations.Cell.copy_cells(),
                "セルを貼り付け": ExcelOperations.Cell.paste_cells(),
                "位置を取得": ExcelOperations.Cell.find_position(),
                "最終行取得": ExcelOperations.Cell.get_last_row(),
                "最終列取得": ExcelOperations.Cell.get_last_column(),
                "列計算": ExcelOperations.Cell.column_calculation(),
                "マクロ実行": ExcelOperations.Cell.run_macro(),
                "行ループ": ExcelOperations.Cell.row_loop(),
                "列ループ": ExcelOperations.Cell.column_loop(),
                "CSV読込ループ": ExcelOperations.Cell.csv_read_loop(),
            },
        }

        # 注: K〜Q の操作定義も同様に実装可能
        # ここでは簡潔性のため、A〜Jまでの実装を示しています

    def to_dict(self) -> Dict[str, Any]:
        """操作定義を辞書形式に変換"""
        result = {"operation_templates": {}}

        def convert_value(value):
            if isinstance(value, OperationTemplate):
                return value.to_dict()
            elif isinstance(value, dict):
                return {k: convert_value(v) for k, v in value.items()}
            else:
                return value

        for category, operations in self.operations.items():
            result["operation_templates"][category] = convert_value(operations)

        # 共通パラメータの定義を追加
        result["common_parameter_definitions"] = {
            "memo": {
                "type": "string",
                "description": "ステップに関するメモやコメント",
                "required": False,
                "default": "",
            },
            "timeout": {
                "type": "integer",
                "description": "タイムアウト時間（秒）",
                "required": False,
                "default": 30,
                "min": 1,
                "max": 3600,
            },
            "retry_count": {
                "type": "integer",
                "description": "リトライ回数",
                "required": False,
                "default": 0,
                "min": 0,
                "max": 10,
            },
            "error_handling": {
                "type": "string",
                "description": "エラー時の処理方法",
                "required": False,
                "default": "stop",
                "enum": ["stop", "continue", "retry", "skip"],
            },
        }

        return result

    def to_json(self, indent: int = 2) -> str:
        """操作定義をJSON文字列に変換"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    def save_to_file(self, filepath: Union[str, Path], indent: int = 2):
        """操作定義をJSONファイルに保存"""
        filepath = Path(filepath)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=indent)
        print(f"Saved to {filepath}")

    def get_operation(
        self, category: str, subcategory: str = None, operation: str = None
    ) -> Optional[OperationTemplate]:
        """特定の操作定義を取得"""
        try:
            if subcategory and operation:
                return self.operations[category][subcategory][operation]
            elif operation:
                return self.operations[category][operation]
            else:
                return self.operations[category]
        except KeyError:
            return None


# ===========================
# 使用例
# ===========================

if __name__ == "__main__":
    # RPAシステムのインスタンス作成
    rpa_system = RPAOperationSystem()

    # JSON文字列として出力
    json_str = rpa_system.to_json()
    print("=== RPA Operations JSON ===")
    print(json_str[:1000] + "...")  # 最初の1000文字を表示

    # ファイルに保存
    rpa_system.save_to_file("rpa_operations.json")

    # 特定の操作を取得して使用する例
    app_launch = rpa_system.get_operation("A_アプリ・画面", "アプリ", "起動")
    if app_launch:
        print("\n=== アプリ起動操作の定義 ===")
        print(json.dumps(app_launch.to_dict(), ensure_ascii=False, indent=2))

    # カスタマイズして新しい操作を作成する例
    custom_app_launch = AppOperations.launch()
    custom_app_launch.specific_params["app_path"] = "C:\\Program Files\\MyApp\\app.exe"
    custom_app_launch.specific_params["wait_time"] = 10
    custom_app_launch.common_params.timeout = 60
    custom_app_launch.common_params.memo = "カスタムアプリの起動"

    print("\n=== カスタマイズされた操作 ===")
    print(json.dumps(custom_app_launch.to_dict(), ensure_ascii=False, indent=2))
