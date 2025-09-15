"""
操作の実行管理とディスパッチングを担当するモジュール
"""

import json
import sys
from typing import Any, Dict, List, Optional

from operations.app_screen import (
    LaunchAppOperation,
    LaunchAppWaitOperation,
    RememberFrontWindowOperation,
    RememberWindowByNameOperation,
    SwitchWindowByIdOperation,
    SwitchWindowByNameOperation,
    GetWindowNameOperation,
    MoveWindowOperation,
    MaximizeMinimizeOperation,
    TakeScreenshotOperation,
)
from operations.datetime_ops import (
    GetCurrentDateTimeOperation,
    AddSubtractTimeOperation,
    CompareDateTimeOperation,
    FormatDateTimeOperation,
    GetWeekdayOperation,
)
from operations.email import (
    EmailSendOperation,
    EmailReceiveOperation,
    EmailDeleteOperation,
    EmailMoveOperation,
    EmailSearchOperation,
)
from operations.excel import (
    ExcelOpenOperation,
    ExcelReadCellOperation,
    ExcelWriteCellOperation,
    ExcelReadRangeOperation,
    ExcelWriteRangeOperation,
    ExcelSaveOperation,
    ExcelCloseOperation,
)
from operations.file_folder import (
    RenameFileFolderOperation,
    CopyFileFolderOperation,
    DeleteFileFolderOperation,
    CreateFolderOperation,
    ListFilesOperation,
    GetFileInfoOperation,
    ReadFileOperation,
    WriteFileOperation,
    OpenFileOperation,
    MoveFileOperation,
    OpenFolderOperation,
    FolderLoopOperation,
)
from operations.keyboard import (
    TypeTextOperation,
    PressKeyOperation,
    HotkeyOperation,
    CopyOperation,
    PasteOperation,
    CutOperation,
    SelectAllOperation,
    UndoOperation,
    RedoOperation,
    TabOperation,
    EnterOperation,
    EscapeOperation,
)
from operations.memory import (
    EnvironmentInfoOperation,
    StoreValueOperation,
    GetStoredValueOperation,
    ClearStoredValueOperation,
    ListStoredValuesOperation,
    IncrementValueOperation,
    AppendToListOperation,
)
from operations.mouse import (
    MouseMoveCoordinateOperation,
    MouseMoveDistanceOperation,
    MouseMoveImageOperation,
    DragDropCoordinateOperation,
    DragDropDistanceOperation,
    ClickOperation,
    RightClickOperation,
    ScrollOperation,
)
from operations.text import (
    TextConcatOperation,
    TextSplitOperation,
    TextReplaceOperation,
    TextExtractOperation,
    TextLengthOperation,
    TextCaseOperation,
    TextTrimOperation,
    RegexMatchOperation,
)
from operations.wait import (
    WaitSecondsOperation,
    WaitMillisecondsOperation,
    WaitUntilTimeOperation,
    WaitForConditionOperation,
    RandomWaitOperation,
)
from operations.wait_control import (
    WaitImageOperation,
    ContinueConfirmOperation,
    TimerContinueConfirmOperation,
    ChangeCommandIntervalOperation,
    ForceExitOperation,
    RaiseErrorOperation,
    ErrorCheckProcessOperation,
    ErrorCheckRetryOperation,
)
from operations.web_browser import (
    WebBrowserOpenOperation,
    WebBrowserCloseOperation,
    WebBrowserNavigateOperation,
    WebBrowserClickOperation,
    WebBrowserInputTextOperation,
    WebBrowserSelectDropdownOperation,
    WebBrowserGetTextOperation,
    WebBrowserWaitForElementOperation,
    WebBrowserScrollOperation,
    WebBrowserTakeScreenshotOperation,
    WebBrowserExecuteJavaScriptOperation,
    WebBrowserSwitchTabOperation,
    WebBrowserRefreshOperation,
)


class OperationManager:
    """操作の管理とディスパッチングを行うクラス"""

    def __init__(self):
        """初期化"""
        self.operations = self._initialize_operations()
        self.storage = {}  # 操作間で共有するストレージ

    def _initialize_operations(self) -> Dict[str, Dict]:
        """操作マッピングを初期化"""
        return {
            "A_アプリ・画面": {
                "アプリ": {
                    "起動": LaunchAppOperation,
                    "起動（終了待ち）": LaunchAppWaitOperation,
                },
                "画面": {
                    "最前画面を覚える": RememberFrontWindowOperation,
                    "画面を覚える（名前）": RememberWindowByNameOperation,
                    "切り替え（参照ID）": SwitchWindowByIdOperation,
                    "切り替え（名前）": SwitchWindowByNameOperation,
                    "画面の名前を取得": GetWindowNameOperation,
                    "移動": MoveWindowOperation,
                    "最大化/最小化": MaximizeMinimizeOperation,
                    "スクリーンショットを撮る": TakeScreenshotOperation,
                },
            },
            "B_待機・終了・エラー": {
                "秒": WaitSecondsOperation,
                "画像出現を待つ": WaitImageOperation,
                "続行確認": ContinueConfirmOperation,
                "タイマー付き続行確認（秒）": TimerContinueConfirmOperation,
                "コマンド間待機時間を変更": ChangeCommandIntervalOperation,
                "作業強制終了": ForceExitOperation,
                "エラー発生": RaiseErrorOperation,
                "エラー確認・処理": ErrorCheckProcessOperation,
                "エラー確認・処理（リトライ前処理）": ErrorCheckRetryOperation,
            },
            "C_マウス": {
                "移動": {
                    "座標": MouseMoveCoordinateOperation,
                    "距離": MouseMoveDistanceOperation,
                    "画像認識": MouseMoveImageOperation,
                },
                "ドラッグ＆ドロップ": {
                    "座標（D&D）": DragDropCoordinateOperation,
                    "距離（D&D）": DragDropDistanceOperation,
                },
                "マウスクリック": ClickOperation,
                "スクロール": ScrollOperation,
            },
            "D_キーボード": {
                "入力": {
                    "文字": TypeTextOperation,
                    "文字（貼り付け）": PasteOperation,
                    "パスワード": TypeTextOperation,
                    "ショートカットキー": HotkeyOperation,
                },
            },
            "E_記憶": {
                "文字": StoreValueOperation,
                "パスワード": StoreValueOperation,
                "環境情報": EnvironmentInfoOperation,
                "日付": GetCurrentDateTimeOperation,
                "日付（営業日）": GetCurrentDateTimeOperation,
                "日付（曜日）": GetWeekdayOperation,
                "日付計算": AddSubtractTimeOperation,
                "曜日": GetWeekdayOperation,
                "時刻": GetCurrentDateTimeOperation,
                "時刻計算": AddSubtractTimeOperation,
                "計算": StoreValueOperation,
                "乱数": StoreValueOperation,
                "コピー内容": GetStoredValueOperation,
                "クリップボードへコピー": StoreValueOperation,
                "実行中に入力": StoreValueOperation,
                "ファイル更新日時": GetCurrentDateTimeOperation,
                "ファイルサイズ": StoreValueOperation,
                "最新ファイル・フォルダ": StoreValueOperation,
                "日付（今日）": GetCurrentDateTimeOperation,
            },
            "F_文字抽出": {
                "括弧・引用符号から": TextExtractOperation,
                "区切り文字から": TextSplitOperation,
                "改行・空白を削除": TextTrimOperation,
                "ファイルパスから": TextExtractOperation,
                "ルールにマッチ": RegexMatchOperation,
                "置換": TextReplaceOperation,
                "文字変換": TextCaseOperation,
                "日付形式変換": FormatDateTimeOperation,
                "1行ずつループ": TextSplitOperation,
            },
            "G_分岐": {
                # 分岐操作は現在未実装
            },
            "H_メール": {
                "送信": EmailSendOperation,
                "受信": EmailReceiveOperation,
                "返信": EmailSendOperation,
                "転送": EmailSendOperation,
                "削除": EmailDeleteOperation,
                "フォルダ移動": EmailMoveOperation,
                "既読にする": EmailMoveOperation,
                "添付を保存": EmailReceiveOperation,
                "検索": EmailSearchOperation,
            },
            "I_ファイル・フォルダ": {
                "ファイル": {
                    "開く": OpenFileOperation,
                    "移動": MoveFileOperation,
                    "読み込む": ReadFileOperation,
                    "書き込む": WriteFileOperation,
                },
                "フォルダ": {
                    "開く": OpenFolderOperation,
                    "作成": CreateFolderOperation,
                    "ループ": FolderLoopOperation,
                },
                "ファイル・フォルダ名の変更": RenameFileFolderOperation,
                "ファイル・フォルダをコピー": CopyFileFolderOperation,
                "ファイル・フォルダを削除": DeleteFileFolderOperation,
                "ファイル一覧取得": ListFilesOperation,
                "ファイル情報取得": GetFileInfoOperation,
            },
            "J_Excel": {
                "ファイルを開く": ExcelOpenOperation,
                "セル読み込み": ExcelReadCellOperation,
                "セル書き込み": ExcelWriteCellOperation,
                "範囲読み込み": ExcelReadRangeOperation,
                "範囲書き込み": ExcelWriteRangeOperation,
                "保存": ExcelSaveOperation,
                "閉じる": ExcelCloseOperation,
            },
            "K_CSV": {
                # CSV操作は現在未実装
            },
            "L_ウェブブラウザ": {
                "ブラウザを開く": WebBrowserOpenOperation,
                "ブラウザを閉じる": WebBrowserCloseOperation,
                "ページ移動": WebBrowserNavigateOperation,
                "クリック": WebBrowserClickOperation,
                "入力": WebBrowserInputTextOperation,
                "選択": WebBrowserSelectDropdownOperation,
                "読み取り": WebBrowserGetTextOperation,
                "待機": WebBrowserWaitForElementOperation,
                "スクロール": WebBrowserScrollOperation,
                "スクリーンショット": WebBrowserTakeScreenshotOperation,
                "JavaScript実行": WebBrowserExecuteJavaScriptOperation,
                "タブ切り替え": WebBrowserSwitchTabOperation,
                "更新": WebBrowserRefreshOperation,
            },
        }

    async def execute_operation(
        self, category: str, subcategory: Optional[str], operation: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """操作を実行する"""
        try:
            # 操作クラスを取得
            operation_class = self._get_operation_class(category, subcategory, operation)
            if not operation_class:
                return {
                    "status": "failure",
                    "error": f"Operation not found: {category}/{subcategory}/{operation}",
                }

            # 操作インスタンスを作成して実行
            op_instance = operation_class(self.storage)
            result = await op_instance.execute(params)

            return {
                "status": result.status,
                "data": result.data,
                "error": result.error,
            }
        except Exception as e:
            return {
                "status": "failure",
                "error": str(e),
            }

    def _get_operation_class(self, category: str, subcategory: Optional[str], operation: str):
        """操作クラスを取得する"""
        if category not in self.operations:
            return None

        category_ops = self.operations[category]

        # サブカテゴリがある場合
        if subcategory and subcategory in category_ops:
            if isinstance(category_ops[subcategory], dict):
                return category_ops[subcategory].get(operation)
            else:
                # サブカテゴリ自体が操作の場合
                if subcategory == operation:
                    return category_ops[subcategory]

        # サブカテゴリがない場合、直接操作を探す
        if operation in category_ops:
            return category_ops[operation]

        return None

    def get_available_operations(self) -> Dict[str, List[str]]:
        """利用可能な操作の一覧を取得する"""
        available_ops = {}
        for category, ops in self.operations.items():
            category_list = []
            for key, value in ops.items():
                if isinstance(value, dict):
                    # サブカテゴリがある場合
                    for op_name in value.keys():
                        category_list.append(f"{key}/{op_name}")
                else:
                    # 直接操作の場合
                    category_list.append(key)
            available_ops[category] = category_list
        return available_ops

    def get_operation_template(self, category: str, operation: str) -> Optional[Dict[str, Any]]:
        """操作のテンプレートを取得する"""
        # rpa_operations.jsonからテンプレートを読み込む
        try:
            with open("rpa_operations.json", "r", encoding="utf-8") as f:
                templates = json.load(f)
                if category in templates and operation in templates[category]:
                    return templates[category][operation]
        except Exception:
            pass
        return None

    async def execute_workflow_steps(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """複数のステップを一括実行する（ワークフロー実行）

        Args:
            steps: 実行するステップのリスト。各ステップは以下の形式:
                {
                    "id": "step-123",
                    "category": "A_アプリ・画面",
                    "subcategory": None,
                    "operation": "アプリ起動",
                    "params": {...},
                    "description": "説明（オプション）"
                }

        Returns:
            各ステップの実行結果のリスト
        """
        results = []

        for i, step in enumerate(steps):
            step_id = step.get("id", f"step-{i}")

            try:
                # ステップ情報をログ出力（デバッグ用）
                print(f"Executing step {i+1}/{len(steps)}: {step_id}", file=sys.stderr)

                # 各ステップを実行
                category = step.get("category")
                subcategory = step.get("subcategory")
                operation = step.get("operation")
                params = step.get("params", {})

                # 操作を実行
                result = await self.execute_operation(category, subcategory, operation, params)

                # 結果を記録
                results.append({
                    "id": step_id,
                    "status": "completed",
                    "result": result,
                    "index": i
                })

            except Exception as e:
                # エラーが発生した場合
                import traceback
                error_info = {
                    "id": step_id,
                    "status": "error",
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                    "index": i
                }
                results.append(error_info)

                # エラーが発生したら、以降のステップは実行しない
                print(f"Error in step {step_id}: {str(e)}", file=sys.stderr)

                # 残りのステップをスキップ済みとしてマーク
                for j in range(i + 1, len(steps)):
                    skipped_step = steps[j]
                    results.append({
                        "id": skipped_step.get("id", f"step-{j}"),
                        "status": "skipped",
                        "reason": f"Skipped due to error in step {step_id}",
                        "index": j
                    })
                break

        return results