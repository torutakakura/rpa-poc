"""
操作の実行管理とディスパッチングを担当するモジュール
"""

import asyncio
import json
from typing import Any, Dict, List, Optional

from operations.app_screen import (
    AppLaunchOperation,
    AppLaunchAndWaitOperation,
    GetActiveWindowOperation,
    MaximizeMinimizeWindowOperation,
    MoveWindowOperation,
    RememberWindowByNameOperation,
    RememberWindowOperation,
    ScreenshotOperation,
    SwitchWindowByNameOperation,
    SwitchWindowByRefOperation,
    WindowNameOperation,
)
from operations.datetime_ops import (
    BusinessDateOperation,
    CalculateOperation,
    CurrentTimeOperation,
    DateCalculationOperation,
    DateOperation,
    RandomNumberOperation,
    TimeCalculationOperation,
    WeekdayDateOperation,
    WeekdayOperation,
)
from operations.email import (
    EmailDeleteOperation,
    EmailForwardOperation,
    EmailMarkReadOperation,
    EmailMoveToFolderOperation,
    EmailReceiveOperation,
    EmailReplyOperation,
    EmailSaveAttachmentsOperation,
    EmailSearchOperation,
    EmailSendOperation,
)
from operations.excel import (
    ExcelCellCopyOperation,
    ExcelCellLoopOperation,
    ExcelCellPasteOperation,
    ExcelCellPositionOperation,
    ExcelCellRangeDeleteOperation,
    ExcelCellRangeInsertOperation,
    ExcelCellRangeMoveOperation,
    ExcelCellRangeSelectOperation,
    ExcelCloseWorkbookOperation,
    ExcelColumnCalculationOperation,
    ExcelColumnLoopOperation,
    ExcelCSVLoopOperation,
    ExcelGetCellValueOperation,
    ExcelGetLastColumnOperation,
    ExcelGetLastRowOperation,
    ExcelMacroOperation,
    ExcelOpenOperation,
    ExcelRememberWorkbookOperation,
    ExcelRowLoopOperation,
    ExcelSaveWorkbookOperation,
    ExcelSetCellValueOperation,
    ExcelSheetCopyMoveOperation,
    ExcelSheetCreateOperation,
    ExcelSheetDeleteOperation,
    ExcelSheetNameChangeOperation,
    ExcelSheetNameGetOperation,
    ExcelSheetSwitchOperation,
)
from operations.file_folder import (
    FileCompressOperation,
    FileCopyOperation,
    FileDecompressOperation,
    FileDeleteOperation,
    FileFolderRenameOperation,
    FileMoveOperation,
    FileOpenOperation,
    FileReadOperation,
    FileRenameInsertDateOperation,
    FileRenameInsertRefOperation,
    FileRenameInsertTextOperation,
    FileWriteOperation,
    FolderCreateOperation,
    FolderLoopOperation,
    FolderOpenOperation,
)
from operations.keyboard import (
    KeyboardInputOperation,
    KeyboardPasteOperation,
    KeyboardPasswordOperation,
    KeyboardShortcutOperation,
)
from operations.memory import (
    ClipboardCopyOperation,
    ClipboardGetOperation,
    DateMemoryOperation,
    EnvironmentMemoryOperation,
    FileModifiedTimeOperation,
    FileSizeOperation,
    LatestFileOperation,
    MemoryOperation,
    PasswordMemoryOperation,
    RuntimeInputOperation,
)
from operations.mouse import (
    MouseClickOperation,
    MouseDragDropCoordinatesOperation,
    MouseDragDropDistanceOperation,
    MouseDragDropImageOperation,
    MouseMoveCoordinatesOperation,
    MouseMoveDistanceOperation,
    MouseMoveImageOperation,
    MouseScrollOperation,
)
from operations.text import (
    DateFormatConversionOperation,
    ExtractFromBracketsOperation,
    ExtractFromDelimiterOperation,
    ExtractFromPathOperation,
    LineLoopOperation,
    MatchPatternOperation,
    RemoveWhitespaceOperation,
    ReplaceTextOperation,
    TextConversionOperation,
)
from operations.wait import (
    CommandIntervalOperation,
    ContinueConfirmOperation,
    ErrorCheckOperation,
    ErrorCheckRetryOperation,
    ErrorRaiseOperation,
    ForceExitOperation,
    TimedContinueConfirmOperation,
    WaitOperation,
)
from operations.wait_control import (
    BreakLoopOperation,
    BranchDateOperation,
    BranchFileOperation,
    BranchImageOperation,
    BranchNumberOperation,
    BranchStringOperation,
    ContinueLoopOperation,
    LoopOperation,
    WaitForImageOperation,
)
from operations.web_browser import (
    WebBrowserClickOperation,
    WebBrowserCloseOperation,
    WebBrowserExecuteJavaScriptOperation,
    WebBrowserGetTextOperation,
    WebBrowserInputTextOperation,
    WebBrowserNavigateOperation,
    WebBrowserOpenOperation,
    WebBrowserRefreshOperation,
    WebBrowserScrollOperation,
    WebBrowserSelectDropdownOperation,
    WebBrowserSwitchTabOperation,
    WebBrowserTakeScreenshotOperation,
    WebBrowserWaitForElementOperation,
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
                    "起動": AppLaunchOperation,
                    "起動（終了待ち）": AppLaunchAndWaitOperation,
                },
                "画面": {
                    "最前画面を覚える": RememberWindowOperation,
                    "画面を覚える（名前）": RememberWindowByNameOperation,
                    "切り替え（参照ID）": SwitchWindowByRefOperation,
                    "切り替え（名前）": SwitchWindowByNameOperation,
                    "画面の名前を取得": WindowNameOperation,
                    "移動": MoveWindowOperation,
                    "最大化/最小化": MaximizeMinimizeWindowOperation,
                    "スクリーンショットを撮る": ScreenshotOperation,
                    "最前画面を取得": GetActiveWindowOperation,
                },
            },
            "B_待機・終了・エラー": {
                "秒": WaitOperation,
                "画像出現を待つ": WaitForImageOperation,
                "続行確認": ContinueConfirmOperation,
                "タイマー付き続行確認（秒）": TimedContinueConfirmOperation,
                "コマンド間待機時間を変更": CommandIntervalOperation,
                "作業強制終了": ForceExitOperation,
                "エラー発生": ErrorRaiseOperation,
                "エラー確認・処理": ErrorCheckOperation,
                "エラー確認・処理（リトライ前処理）": ErrorCheckRetryOperation,
            },
            "C_マウス": {
                "移動": {
                    "座標": MouseMoveCoordinatesOperation,
                    "距離": MouseMoveDistanceOperation,
                    "画像認識": MouseMoveImageOperation,
                },
                "ドラッグ＆ドロップ": {
                    "座標（D&D）": MouseDragDropCoordinatesOperation,
                    "距離（D&D）": MouseDragDropDistanceOperation,
                    "画像認識（D&D）": MouseDragDropImageOperation,
                },
                "マウスクリック": MouseClickOperation,
                "スクロール": MouseScrollOperation,
            },
            "D_キーボード": {
                "入力": {
                    "文字": KeyboardInputOperation,
                    "文字（貼り付け）": KeyboardPasteOperation,
                    "パスワード": KeyboardPasswordOperation,
                    "ショートカットキー": KeyboardShortcutOperation,
                },
            },
            "E_記憶": {
                "文字": MemoryOperation,
                "パスワード": PasswordMemoryOperation,
                "環境情報": EnvironmentMemoryOperation,
                "日付": DateMemoryOperation,
                "日付（営業日）": BusinessDateOperation,
                "日付（曜日）": WeekdayDateOperation,
                "日付計算": DateCalculationOperation,
                "曜日": WeekdayOperation,
                "時刻": CurrentTimeOperation,
                "時刻計算": TimeCalculationOperation,
                "計算": CalculateOperation,
                "乱数": RandomNumberOperation,
                "コピー内容": ClipboardGetOperation,
                "クリップボードへコピー": ClipboardCopyOperation,
                "実行中に入力": RuntimeInputOperation,
                "ファイル更新日時": FileModifiedTimeOperation,
                "ファイルサイズ": FileSizeOperation,
                "最新ファイル・フォルダ": LatestFileOperation,
                "日付（今日）": DateOperation,
            },
            "F_文字抽出": {
                "括弧・引用符号から": ExtractFromBracketsOperation,
                "区切り文字から": ExtractFromDelimiterOperation,
                "改行・空白を削除": RemoveWhitespaceOperation,
                "ファイルパスから": ExtractFromPathOperation,
                "ルールにマッチ": MatchPatternOperation,
                "置換": ReplaceTextOperation,
                "文字変換": TextConversionOperation,
                "日付形式変換": DateFormatConversionOperation,
                "1行ずつループ": LineLoopOperation,
            },
            "G_分岐": {
                "文字列": BranchStringOperation,
                "数値": BranchNumberOperation,
                "日付": BranchDateOperation,
                "ファイル・フォルダの有/無を確認": BranchFileOperation,
                "画像": BranchImageOperation,
            },
            "H_繰り返し": {
                "繰り返し": LoopOperation,
                "繰り返しを抜ける": BreakLoopOperation,
                "繰り返しの最初に戻る": ContinueLoopOperation,
            },
            "I_ファイル・フォルダ": {
                "ファイル": {
                    "開く": FileOpenOperation,
                    "移動": FileMoveOperation,
                    "読み込む": FileReadOperation,
                    "書き込む": FileWriteOperation,
                },
                "フォルダ": {
                    "開く": FolderOpenOperation,
                    "作成": FolderCreateOperation,
                    "ループ": FolderLoopOperation,
                },
                "ファイル・フォルダ名の変更": FileFolderRenameOperation,
                "ファイル・フォルダをコピー": FileCopyOperation,
                "ファイル・フォルダを削除": FileDeleteOperation,
                "圧縮・解凍": {
                    "ファイル・フォルダを圧縮": FileCompressOperation,
                    "ファイル・フォルダに解凍": FileDecompressOperation,
                },
                "ファイル名変更（挿入）": {
                    "文字": FileRenameInsertTextOperation,
                    "日付": FileRenameInsertDateOperation,
                    "参照ID": FileRenameInsertRefOperation,
                },
            },
            "J_エクセル・CSV": {
                "ブック": {
                    "ブックを開く": ExcelOpenOperation,
                    "ブックを覚える": ExcelRememberWorkbookOperation,
                    "ブックを保存": ExcelSaveWorkbookOperation,
                    "ブックを閉じる": ExcelCloseWorkbookOperation,
                },
                "シート操作": {
                    "新規作成": ExcelSheetCreateOperation,
                    "削除": ExcelSheetDeleteOperation,
                    "切り替え": ExcelSheetSwitchOperation,
                    "移動・コピー": ExcelSheetCopyMoveOperation,
                    "名前取得": ExcelSheetNameGetOperation,
                    "名前変更": ExcelSheetNameChangeOperation,
                },
                "セル操作": {
                    "範囲指定": ExcelCellRangeSelectOperation,
                    "指定範囲の移動": ExcelCellRangeMoveOperation,
                    "指定範囲の削除": ExcelCellRangeDeleteOperation,
                    "指定範囲にセルを挿入": ExcelCellRangeInsertOperation,
                    "値を取得": ExcelGetCellValueOperation,
                    "値を入力": ExcelSetCellValueOperation,
                    "セルをコピー": ExcelCellCopyOperation,
                    "セルを貼り付け": ExcelCellPasteOperation,
                    "位置を取得": ExcelCellPositionOperation,
                    "最終行取得": ExcelGetLastRowOperation,
                    "最終列取得": ExcelGetLastColumnOperation,
                    "列計算": ExcelColumnCalculationOperation,
                    "マクロ実行": ExcelMacroOperation,
                    "行ループ": ExcelRowLoopOperation,
                    "列ループ": ExcelColumnLoopOperation,
                    "CSV読込ループ": ExcelCSVLoopOperation,
                    "セルループ": ExcelCellLoopOperation,
                },
            },
            "K_メール": {
                "送信": EmailSendOperation,
                "受信": EmailReceiveOperation,
                "返信": EmailReplyOperation,
                "転送": EmailForwardOperation,
                "削除": EmailDeleteOperation,
                "既読にする": EmailMarkReadOperation,
                "フォルダへ移動": EmailMoveToFolderOperation,
                "検索": EmailSearchOperation,
                "添付ファイル保存": EmailSaveAttachmentsOperation,
            },
            "L_ウェブブラウザ": {
                "開く": WebBrowserOpenOperation,
                "閉じる": WebBrowserCloseOperation,
                "ページ遷移": WebBrowserNavigateOperation,
                "クリック": WebBrowserClickOperation,
                "テキスト入力": WebBrowserInputTextOperation,
                "ドロップダウン選択": WebBrowserSelectDropdownOperation,
                "テキスト取得": WebBrowserGetTextOperation,
                "要素待機": WebBrowserWaitForElementOperation,
                "スクロール": WebBrowserScrollOperation,
                "スクリーンショット": WebBrowserTakeScreenshotOperation,
                "JavaScript実行": WebBrowserExecuteJavaScriptOperation,
                "タブ切り替え": WebBrowserSwitchTabOperation,
                "更新": WebBrowserRefreshOperation,
            },
        }

    async def execute_operation(
        self, category: str, subcategory: str, operation: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """操作を実行"""
        try:
            # 操作クラスを取得
            operation_class = self._get_operation_class(category, subcategory, operation)
            if not operation_class:
                return {
                    "status": "failure",
                    "error": f"Operation not found: {category}/{subcategory}/{operation}",
                }

            # 操作インスタンスを作成（ストレージを渡す）
            operation_instance = operation_class(self.storage)

            # 操作を実行
            result = await operation_instance.execute(params)

            # 結果を辞書形式で返す
            return {
                "status": result.status,
                "data": result.data,
                "error": result.error,
            }

        except Exception as e:
            return {"status": "failure", "error": str(e)}

    def _get_operation_class(
        self, category: str, subcategory: Optional[str], operation: str
    ):
        """操作クラスを取得"""
        try:
            if category not in self.operations:
                return None

            category_ops = self.operations[category]

            # サブカテゴリがある場合
            if subcategory:
                if subcategory in category_ops:
                    subcategory_ops = category_ops[subcategory]
                    if operation in subcategory_ops:
                        return subcategory_ops[operation]
            else:
                # サブカテゴリがない場合、直接操作を探す
                if operation in category_ops:
                    return category_ops[operation]

                # サブカテゴリを探索
                for subcategory in category_ops.values():
                    if isinstance(subcategory, dict) and operation in subcategory:
                        return subcategory[operation]

            return None
        except Exception:
            return None

    def get_available_operations(self) -> Dict[str, List[str]]:
        """利用可能な操作リストを返す"""
        available_ops = {}

        for category, category_ops in self.operations.items():
            operations = []
            for key, value in category_ops.items():
                if isinstance(value, type):
                    # 直接操作の場合
                    operations.append(key)
                elif isinstance(value, dict):
                    # サブカテゴリの場合
                    for sub_op in value:
                        operations.append(f"{key}/{sub_op}")
            available_ops[category] = operations

        return available_ops

    def get_operation_template(
        self, category: str, subcategory: Optional[str], operation: str
    ) -> Optional[Dict[str, Any]]:
        """操作のテンプレートを取得"""
        # rpa_operations.jsonから読み込む
        try:
            with open("rpa_operations.json", "r", encoding="utf-8") as f:
                templates = json.load(f)

            if category not in templates["operation_templates"]:
                return None

            category_templates = templates["operation_templates"][category]

            if subcategory:
                if subcategory in category_templates:
                    subcategory_templates = category_templates[subcategory]
                    if operation in subcategory_templates:
                        return subcategory_templates[operation]
            else:
                if operation in category_templates:
                    return category_templates[operation]

                # サブカテゴリを探索
                for sub_templates in category_templates.values():
                    if isinstance(sub_templates, dict) and operation in sub_templates:
                        return sub_templates[operation]

            return None
        except Exception:
            return None