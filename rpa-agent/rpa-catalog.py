"""
RPA操作定義システム - フラットJSON生成専用
"""

import json
import re
from pathlib import Path
from typing import Any

# スキーマモジュールからインポート
from schemas.api import APIOperations
from schemas.app_screen import AppOperations, ScreenOperations
from schemas.base import OperationTemplate
from schemas.branch import BranchOperations
from schemas.excel_csv import ExcelOperations
from schemas.external_scenario import ExternalScenarioOperations
from schemas.file_folder import FileOperations, FileFolderOperations, FolderOperations
from schemas.keyboard import KeyboardOperations
from schemas.loop import LoopOperations
from schemas.mail import MailOperations
from schemas.memory import MemoryOperations
from schemas.mouse import MouseOperations
from schemas.scenario import ScenarioOrganizationOperations
from schemas.special_app import SpecialAppOperations
from schemas.spreadsheet import SpreadsheetOperations
from schemas.text_extract import TextExtractOperations
from schemas.wait_error import WaitErrorOperations
from schemas.web_browser import WebBrowserOperations


class RPAOperationSystem:
    """RPA操作定義をフラットJSON形式で生成するクラス"""

    # カテゴリマッピング
    CATEGORY_MAPPING: dict[str, str] = {
        "A_アプリ・画面": "app_screen",
        "B_待機・終了・エラー": "wait_error",
        "C_マウス": "mouse",
        "D_キーボード": "keyboard",
        "E_記憶": "memory",
        "F_文字抽出": "text_extraction",
        "G_分岐": "branch",
        "H_繰り返し": "loop",
        "I_ファイル・フォルダ": "file_folder",
        "J_エクセル・CSV": "excel_csv",
        "K_スプレッドシート": "spreadsheet",
        "L_ウェブブラウザ": "web_browser",
        "M_メール": "mail",
        "N_特殊アプリ操作": "special_app",
        "O_API": "api",
        "P_シナリオ整理": "scenario",
        "Q_別シナリオ実行・継承": "scenario_exec",
    }

    # サブカテゴリマッピング
    SUBCATEGORY_MAPPING: dict[str, str] = {
        "アプリ": "app",
        "画面": "screen",
        "秒": "seconds",
        "移動": "move",
        "ドラッグ＆ドロップ": "drag_drop",
        "入力": "input",
        "文字": "text",
        "ブック": "book",
        "シート操作": "sheet",
        "セル操作": "cell",
        "スプレッドシート": "spreadsheet",
        "シート": "sheet",
        "ファイル": "file",
        "フォルダ": "folder",
        "圧縮・解凍": "archive",
        "ファイル名変更（挿入）": "rename_with_insert",
        "JSON": "json",
    }

    # ステップ名マッピング（日本語 → 英語）
    STEP_NAME_MAPPING: dict[str, str] = {
        # アプリ・画面
        "起動": "launch",
        "起動（終了待ち）": "launch_wait",
        "最前画面を覚える": "remember_front",
        "画面を覚える（名前）": "remember_by_name",
        "画面を覚える": "remember",
        "切り替え（参照ID）": "switch_by_id",
        "切り替え（名前）": "switch_by_name",
        "切り替え": "switch",
        "画面の名前を取得": "get_window_name",
        "移動": "move",
        "最大化/最小化": "maximize_minimize",
        "スクリーンショットを撮る": "screenshot",

        # 待機・エラー
        "画像出現を待つ": "wait_for_image",
        "続行確認": "continue_confirm",
        "タイマー付き続行確認（秒）": "timer_continue_confirm",
        "コマンド間待機時間を変更": "change_command_wait_time",
        "作業強制終了": "force_stop",
        "エラー発生": "raise_error",
        "エラー確認・処理": "check_and_handle_error",
        "エラー確認・処理（リトライ前処理）": "check_and_handle_error_with_retry",

        # マウス
        "座標": "coordinate",
        "距離": "distance",
        "画像認識": "image_recognition",
        "座標（D&D）": "coordinate_dd",
        "距離（D&D）": "distance_dd",
        "画像認識（D&D）": "image_recognition_dd",
        "マウスクリック": "click",
        "スクロール": "scroll",

        # キーボード
        "文字": "text",
        "文字（貼り付け）": "text_paste",
        "パスワード": "password",
        "ショートカットキー": "shortcut",

        # 記憶
        "環境情報": "environment_info",
        "日付": "date",
        "日付（営業日）": "date_business_day",
        "日付（曜日）": "date_weekday",
        "日付計算": "date_calculation",
        "曜日": "weekday",
        "時刻": "time",
        "時刻計算": "time_calculation",
        "計算": "calculation",
        "乱数": "random_number",
        "コピー内容": "clipboard_content",
        "クリップボードへコピー": "copy_to_clipboard",
        "実行中に入力": "runtime_input",
        "ファイル更新日時": "file_modification_time",
        "ファイルサイズ": "file_size",
        "最新ファイル・フォルダ": "latest_file_folder",

        # 文字抽出
        "括弧・引用符号から": "from_brackets",
        "区切り文字から": "from_delimiter",
        "改行・空白を削除": "remove_whitespace",
        "ファイルパスから": "from_filepath",
        "ルールにマッチ": "match_rule",
        "置換": "replace",
        "文字変換": "text_conversion",
        "日付形式変換": "date_format_conversion",
        "1行ずつループ": "loop_by_line",

        # 分岐
        "文字列": "string_condition",
        "数値": "numeric_condition",
        "ファイル・フォルダの有/無を確認": "check_file_folder_exists",
        "画像": "image_condition",

        # 繰り返し
        "繰り返し": "repeat",
        "繰り返しを抜ける": "break_loop",
        "繰り返しの最初に戻る": "continue_loop",

        # ファイル・フォルダ
        "開く": "open",
        "読み込む": "read",
        "書き込む": "write",
        "作成": "create",
        "削除": "delete",
        "ループ": "loop",
        "名前変更": "rename",
        "コピー": "copy",
        "ファイル・フォルダ名の変更": "rename_file_folder",
        "ファイル・フォルダをコピー": "copy_file_folder",
        "ファイル・フォルダを削除": "delete_file_folder",
        "ファイル・フォルダを圧縮": "compress_file_folder",
        "ファイル・フォルダに解凍": "extract_file_folder",
        "参照ID": "reference_id",

        # エクセル・CSV
        "ブックを開く": "open_workbook",
        "ブックを覚える": "remember_workbook",
        "ブックを保存": "save_workbook",
        "ブックを閉じる": "close_workbook",
        "新規作成": "create_new",
        "移動・コピー": "move_or_copy",
        "名前取得": "get_name",
        "範囲指定": "select_range",
        "指定範囲の移動": "move_range",
        "指定範囲の削除": "delete_range",
        "指定範囲にセルを挿入": "insert_cells_in_range",
        "値を取得": "get_value",
        "値を入力": "set_value",
        "セルをコピー": "copy_cells",
        "セルを貼り付け": "paste_cells",
        "位置を取得": "get_position",
        "最終行取得": "get_last_row",
        "最終列取得": "get_last_column",
        "列計算": "column_calculation",
        "マクロ実行": "run_macro",
        "行ループ": "row_loop",
        "列ループ": "column_loop",
        "CSV読込ループ": "csv_read_loop",

        # スプレッドシート
        "URL取得": "get_url",
        "セルをコピー・貼り付け": "copy_and_paste_cells",

        # ウェブブラウザ
        "ブラウザを開く": "open_browser",
        "ブラウザを閉じる": "close_browser",
        "ページ移動": "navigate_page",
        "クリック": "click",
        "入力": "input",
        "選択": "select",
        "読み取り": "read_text",
        "待機": "wait",
        "スクリーンショット": "screenshot",
        "JavaScript実行": "execute_javascript",
        "タブ切り替え": "switch_tab",
        "更新": "refresh",

        # メール
        "送信": "send",
        "受信": "receive",
        "送信（Gmail）": "send_gmail",
        "受信（Gmail）": "receive_gmail",
        "送信（Microsoft）": "send_microsoft",
        "受信（Microsoft）": "receive_microsoft",

        # 特殊アプリ操作
        "文字入力": "text_input",
        "文字入力（パスワード）": "password_input",
        "座標取得": "get_coordinates",
        "文字取得": "get_text",

        # API
        "JSON値取得": "get_json_value",
        "JSON型確認": "check_json_type",

        # シナリオ
        "グループ化": "group",
        "メモ": "memo",
        "通知音を再生": "play_notification",
        "別シナリオ実行": "execute_scenario",
        "親シナリオからデータを継承": "inherit_data",
        "親シナリオからパスワードを継承": "inherit_passwords",
        "親シナリオからウィンドウを継承": "inherit_windows",
        "親シナリオからエクセルを継承": "inherit_excel",
        "親シナリオからブラウザを継承": "inherit_browsers",
    }

    # ステップの詳細な説明
    STEP_DESCRIPTIONS: dict[str, str] = {
        # アプリ・画面
        "起動": "指定したアプリケーションやファイルを起動します。パスや引数、ウィンドウ表示状態を設定できます。",
        "起動（終了待ち）": "アプリケーションを起動し、そのプロセスが終了するまで待機します。実行結果を変数に格納できます。",
        "最前画面を覚える": "現在最前面に表示されているウィンドウの参照を変数に記憶し、後で切り替えや操作に使用できます。",
        "画面を覚える（名前）": "ウィンドウ名を指定して特定のウィンドウの参照を記憶します。部分一致や正規表現での指定も可能です。",
        "切り替え（参照ID）": "変数に記憶したウィンドウ参照を使用して、該当ウィンドウを最前面に切り替えます。",
        "切り替え（名前）": "ウィンドウ名を指定して、該当するウィンドウを最前面に切り替えます。",
        "画面の名前を取得": "指定したウィンドウのタイトルバーに表示されている名前を取得し、変数に格納します。",
        "移動": "最前面のウィンドウを画面内の指定位置（左上、中央、右下など）に配置します。",
        "最大化/最小化": "最前面のウィンドウを最大化、最小化、または通常サイズに変更します。",
        "スクリーンショットを撮る": "画面全体または指定範囲のスクリーンショットを撮影し、ファイルに保存します。",

        # 待機・エラー
        "秒": "指定した秒数だけ処理を一時停止します。他の処理の完了を待つ際に使用します。",
        "画像出現を待つ": "指定した画像が画面上に表示されるまで待機します。タイムアウト設定も可能です。",
        "続行確認": "処理を一時停止し、ユーザーの確認を待ちます。メッセージ表示も可能です。",
        "タイマー付き続行確認（秒）": "指定秒数のカウントダウン付きで処理を一時停止し、ユーザーの確認を待ちます。",
        "コマンド間待機時間を変更": "各コマンド実行間のデフォルト待機時間を変更します。処理速度の調整に使用します。",
        "作業強制終了": "現在実行中のシナリオを強制的に終了します。エラーまたは成功として終了を選択できます。",
        "エラー発生": "意図的にエラーを発生させ、シナリオを中断します。エラーメッセージの指定も可能です。",
        "エラー確認・処理": "直前のコマンドでエラーが発生したかを確認し、エラー時の処理を定義できます。",
        "エラー確認・処理（リトライ前処理）": "エラー発生時にリトライ前の処理を実行してから再試行します。",

        # マウス
        "座標": "画面上の指定した絶対座標にマウスカーソルを移動します。クリック動作も指定可能です。",
        "距離": "現在のマウス位置から指定したピクセル分だけ相対的に移動します。",
        "画像認識": "指定した画像を画面上から検索し、見つかった位置にマウスを移動します。",
        "座標（D&D）": "指定した絶対座標までドラッグ＆ドロップを実行します。",
        "距離（D&D）": "現在位置から指定距離までドラッグ＆ドロップを実行します。",
        "画像認識（D&D）": "画像認識で見つけた位置までドラッグ＆ドロップを実行します。",
        "マウスクリック": "現在のマウス位置でクリック（左、右、ダブル）を実行します。修飾キーの同時押しも可能です。",
        "スクロール": "マウスホイールによるスクロールを実行します。方向と量を指定できます。",

        # キーボード
        "文字": "指定した文字列をキーボードから入力します。タイピング速度の調整も可能です。",
        "文字（貼り付け）": "文字列をクリップボード経由で貼り付けます。大量テキストの高速入力に使用します。",
        "パスワード": "暗号化されたパスワードを復号化して入力します。パスワードの安全な管理が可能です。",
        "ショートカットキー": "複数のキーの同時押し（Ctrl+C など）を実行します。最大4つのキーを組み合わせ可能です。",

        # 記憶
        "環境情報": "PC名、ユーザー名、実行パスなどの環境情報を取得し、変数に格納します。",
        "日付": "現在日付または指定日数後の日付を、指定形式で変数に格納します。",
        "日付（営業日）": "営業日を考慮した日付計算を行い、結果を変数に格納します。祝日設定も可能です。",
        "日付（曜日）": "特定の曜日（第2月曜日など）の日付を計算し、変数に格納します。",
        "日付計算": "日付の加減算や営業日計算を行い、結果を変数に格納します。",
        "曜日": "指定日付の曜日を取得し、変数に格納します。各種形式での出力が可能です。",
        "時刻": "現在時刻を指定形式で取得し、変数に格納します。タイムゾーン指定も可能です。",
        "時刻計算": "時刻の加減算を行い、結果を変数に格納します。",
        "計算": "四則演算や剰余計算を行い、結果を変数に格納します。丸め処理も指定可能です。",
        "乱数": "指定範囲内の乱数を生成し、変数に格納します。小数点以下の桁数も指定可能です。",
        "コピー内容": "クリップボードの内容を取得し、変数に格納します。",
        "クリップボードへコピー": "指定した文字列をクリップボードにコピーします。",
        "実行中に入力": "シナリオ実行中にユーザーからの入力を受け付け、変数に格納します。",
        "ファイル更新日時": "ファイルの最終更新日時を取得し、指定形式で変数に格納します。",
        "ファイルサイズ": "ファイルのサイズを取得し、指定単位（バイト、KB、MBなど）で変数に格納します。",
        "最新ファイル・フォルダ": "指定フォルダ内の最新または最古のファイル・フォルダを検索し、パスを変数に格納します。",

        # 文字抽出
        "括弧・引用符号から": "文字列から括弧や引用符で囲まれた部分を抽出し、変数に格納します。",
        "区切り文字から": "指定した区切り文字で分割し、特定の位置の文字列を抽出します。",
        "改行・空白を削除": "文字列から改行、空白、タブを削除し、整形済み文字列を変数に格納します。",
        "ファイルパスから": "ファイルパスからファイル名、拡張子、ディレクトリなどを抽出します。",
        "ルールにマッチ": "正規表現パターンにマッチする文字列を抽出し、変数に格納します。",
        "置換": "文字列内の特定パターンを別の文字列に置換します。全置換・部分置換を選択可能です。",
        "文字変換": "大文字・小文字変換、全角・半角変換などの文字種変換を行います。",
        "日付形式変換": "日付文字列を別の形式に変換します。様々な日付形式に対応しています。",
        "1行ずつループ": "複数行テキストを1行ずつ処理するループを実行します。",

        # 分岐
        "文字列": "文字列の条件（含む、等しい、正規表現など）に基づいて処理を分岐します。",
        "数値": "数値の比較条件（大きい、小さい、等しいなど）に基づいて処理を分岐します。",
        "日付": "日付の比較条件に基づいて処理を分岐します。営業日の考慮も可能です。",
        "ファイル・フォルダの有/無を確認": "指定したファイルまたはフォルダの存在を確認し、結果に基づいて処理を分岐します。",
        "画像": "画面上に指定画像が存在するかを確認し、結果に基づいて処理を分岐します。",

        # 繰り返し
        "繰り返し": "指定回数または条件を満たすまで、一連の処理を繰り返し実行します。",
        "繰り返しを抜ける": "現在実行中のループを強制的に終了し、ループの次の処理に進みます。",
        "繰り返しの最初に戻る": "現在のループの残りの処理をスキップし、次の繰り返しを開始します。",

        # ファイル・フォルダ
        "開く": "ファイルまたはフォルダを既定のアプリケーションで開きます。",
        "読み込む": "ファイルの内容を読み込み、変数に格納します。エンコーディングの指定も可能です。",
        "書き込む": "変数の内容をファイルに書き込みます。上書きまたは追記を選択できます。",
        "作成": "新しいファイルまたはフォルダを作成します。",
        "削除": "指定したファイルまたはフォルダを削除します。",
        "ループ": "フォルダ内のファイルまたはサブフォルダを順次処理するループを実行します。",
        "移動": "ファイルを別の場所に移動します。",
        "名前変更": "ファイルまたはフォルダの名前を変更します。",
        "コピー": "ファイルまたはフォルダを指定した場所にコピーします。",
        "ファイル・フォルダ名の変更": "ファイルまたはフォルダの名前を動的に変更します。",
        "ファイル・フォルダをコピー": "ファイルまたはフォルダを別の場所に複製します。",
        "ファイル・フォルダを削除": "指定したファイルまたはフォルダを完全に削除します。",
        "ファイル・フォルダを圧縮": "ファイルまたはフォルダをZIP形式で圧縮します。",
        "ファイル・フォルダに解凍": "ZIP形式の圧縮ファイルを指定場所に解凍します。",
        "参照ID": "ファイル名に変数の値を挿入して動的に名前を変更します。",

        # エクセル・CSV
        "ブックを開く": "Excel/CSVファイルを開き、操作可能な状態にします。",
        "ブックを覚える": "現在アクティブなブックの参照を変数に記憶します。",
        "ブックを保存": "開いているブックを保存します。別名保存も可能です。",
        "ブックを閉じる": "開いているブックを閉じます。保存オプションの指定も可能です。",
        "新規作成": "新しいシートを作成します。",
        "移動・コピー": "シートを別の位置に移動またはコピーします。",
        "名前取得": "シート名の一覧を取得し、変数に格納します。",
        "範囲指定": "操作対象のセル範囲を指定します。",
        "指定範囲の移動": "選択したセル範囲を別の位置に移動します。",
        "指定範囲の削除": "選択したセル範囲のデータを削除します。",
        "指定範囲にセルを挿入": "指定位置に新しいセルを挿入し、既存セルをシフトします。",
        "値を取得": "セルの値を取得し、変数に格納します。",
        "値を入力": "セルに値を入力します。数式の入力も可能です。",
        "セルをコピー": "セル範囲をクリップボードにコピーします。",
        "セルを貼り付け": "クリップボードの内容をセルに貼り付けます。",
        "セルをコピー・貼り付け": "セル範囲を一度の操作でコピーして貼り付けます。",
        "位置を取得": "アクティブセルの位置（行番号、列番号）を取得します。",
        "最終行取得": "データが入力されている最終行の番号を取得します。",
        "最終列取得": "データが入力されている最終列の番号を取得します。",
        "列計算": "列の合計、平均、最大、最小などの計算を実行します。",
        "マクロ実行": "Excelファイル内のマクロを実行します。",
        "行ループ": "指定範囲の行を順次処理するループを実行します。",
        "列ループ": "指定範囲の列を順次処理するループを実行します。",
        "CSV読込ループ": "CSVファイルの各行を順次読み込んで処理します。",

        # スプレッドシート
        "URL取得": "スプレッドシートのURLを取得し、変数に格納します。",

        # ウェブブラウザ
        "ブラウザを開く": "指定したブラウザでWebページを開きます。",
        "ブラウザを閉じる": "開いているブラウザを閉じます。",
        "ページ移動": "指定したURLにページを遷移させます。",
        "クリック": "Web要素（ボタン、リンクなど）をクリックします。",
        "入力": "テキストボックスなどに文字を入力します。",
        "選択": "ドロップダウンリストから項目を選択します。",
        "読み取り": "Web要素のテキストを読み取り、変数に格納します。",
        "待機": "指定した要素が表示されるまで待機します。",
        "スクリーンショット": "Webページのスクリーンショットを撮影します。",
        "JavaScript実行": "カスタムJavaScriptコードを実行します。",
        "タブ切り替え": "ブラウザのタブを切り替えます。",
        "更新": "現在のページを再読み込みします。",

        # メール
        "送信": "メールを送信します。添付ファイルの指定も可能です。",
        "受信": "メールを受信し、内容を変数に格納します。",
        "送信（Gmail）": "Gmail経由でメールを送信します。",
        "受信（Gmail）": "Gmailからメールを受信します。",
        "送信（Microsoft）": "Outlook/Exchange経由でメールを送信します。",
        "受信（Microsoft）": "Outlook/Exchangeからメールを受信します。",

        # 特殊アプリ操作
        "文字入力": "UIオートメーション要素に文字を入力します。",
        "文字入力（パスワード）": "UIオートメーション要素にパスワードを安全に入力します。",
        "座標取得": "UIオートメーション要素の画面上の座標を取得します。",
        "文字取得": "UIオートメーション要素からテキストを取得します。",

        # API
        "JSON値取得": "JSON文字列から指定したキーの値を取得します。",
        "JSON型確認": "JSON文字列の指定したキーの値の型を確認します。",

        # シナリオ整理
        "グループ化": "複数のコマンドをグループ化して管理しやすくします。",
        "メモ": "シナリオ内にコメントやメモを追加します。",
        "通知音を再生": "処理の完了や注意を促すために通知音を再生します。",

        # 別シナリオ実行・継承
        "別シナリオ実行": "別のシナリオファイルを実行し、結果に基づいて分岐します。",
        "親シナリオからデータを継承": "親シナリオの変数データを引き継ぎます。",
        "親シナリオからパスワードを継承": "親シナリオのパスワード情報を安全に引き継ぎます。",
        "親シナリオからウィンドウを継承": "親シナリオで開いたウィンドウの参照を引き継ぎます。",
        "親シナリオからエクセルを継承": "親シナリオで開いたExcelブックの参照を引き継ぎます。",
        "親シナリオからブラウザを継承": "親シナリオで開いたブラウザセッションを引き継ぎます。",
    }

    def __init__(self):
        self.operations = {}
        self._build_operations()

    def _build_operations(self):
        """全操作の定義を構築"""
        # A. アプリ・画面
        self.operations["A_アプリ・画面"] = {
            "アプリ": {
                "起動": AppOperations.run_executable(),
                "起動（終了待ち）": AppOperations.run_executable_and_wait(),
            },
            "画面": {
                "最前画面を覚える": ScreenOperations.remember_focused_window(),
                "画面を覚える（名前）": ScreenOperations.remember_named_window(),
                "切り替え（参照ID）": ScreenOperations.focus_window(),
                "切り替え（名前）": ScreenOperations.focus_window_by_name(),
                "画面の名前を取得": ScreenOperations.get_window_title(),
                "移動": ScreenOperations.align_focused_window(),
                "最大化/最小化": ScreenOperations.maximize_focused_window(),
                "スクリーンショットを撮る": ScreenOperations.take_screenshot(),
            },
        }

        # B. 待機・終了・エラー
        self.operations["B_待機・終了・エラー"] = {
            "秒": WaitErrorOperations.pause(),
            "画像出現を待つ": WaitErrorOperations.search_screen_and_branch(),
            "続行確認": WaitErrorOperations.pause_and_ask_to_proceed(),
            "タイマー付き続行確認（秒）": WaitErrorOperations.pause_and_countdown_to_proceed(),
            "コマンド間待機時間を変更": WaitErrorOperations.change_speed_for_command_execution(),
            "作業強制終了": WaitErrorOperations.abort(),
            "エラー発生": WaitErrorOperations.raise_error(),
            "エラー確認・処理": WaitErrorOperations.check_for_errors(),
            "エラー確認・処理（リトライ前処理）": WaitErrorOperations.check_for_errors_2(),
        }

        # C. マウス
        self.operations["C_マウス"] = {
            "移動": {
                "座標": MouseOperations.Move.move_mouse_to_absolute_coordinates(),
                "距離": MouseOperations.Move.move_mouse_to_relative_coordinates(),
                "画像認識": MouseOperations.Move.move_mouse_to_image(),
            },
            "ドラッグ＆ドロップ": {
                "座標（D&D）": MouseOperations.DragAndDrop.drag_and_drop_to_absolute_coordinates(),
                "距離（D&D）": MouseOperations.DragAndDrop.drag_and_drop_to_relative_coordinates(),
                "画像認識（D&D）": MouseOperations.DragAndDrop.drag_and_drop_to_image(),
            },
            "マウスクリック": MouseOperations.click_mouse(),
            "スクロール": MouseOperations.scroll_mouse(),
        }

        # D. キーボード
        self.operations["D_キーボード"] = {
            "入力": {
                "文字": KeyboardOperations.Input.typewrite_static_string(),
                "文字（貼り付け）": KeyboardOperations.Input.typewrite_all_string(),
                "パスワード": KeyboardOperations.Input.typewrite_password(),
                "ショートカットキー": KeyboardOperations.Input.type_hotkeys(),
            },
        }

        # E. 記憶
        self.operations["E_記憶"] = {
            "環境情報": MemoryOperations.assign_environment_variable(),
            "日付": MemoryOperations.assign_date_to_string_variable(),
            "日付（営業日）": MemoryOperations.assign_date_business_to_string_variable(),
            "日付（曜日）": MemoryOperations.assign_date_weekdays_to_string_variable(),
            "日付計算": MemoryOperations.assign_date_calculation_to_string_variable(),
            "曜日": MemoryOperations.assign_day_of_week_to_string_variable(),
            "時刻": MemoryOperations.assign_timestamp_to_string_variable(),
            "時刻計算": MemoryOperations.assign_time_calculation_to_string_variable(),
            "計算": MemoryOperations.assign_arithmetic_result_to_string_variable_v2(),
            "乱数": MemoryOperations.assign_random_number_to_string_variable(),
            "コピー内容": MemoryOperations.assign_clipboard_to_string_variable(),
            "クリップボードへコピー": MemoryOperations.copy_to_clipboard(),
            "実行中に入力": MemoryOperations.assign_live_input_to_string_variable(),
            "ファイル更新日時": MemoryOperations.assign_file_modification_timestamp_to_string_variable(),
            "ファイルサイズ": MemoryOperations.assign_file_size_to_string_variable(),
            "最新ファイル・フォルダ": MemoryOperations.find_newest_file_from_fixed_directory(),
        }

        # F. 文字抽出
        self.operations["F_文字抽出"] = {
            "文字": {
                "括弧・引用符号から": TextExtractOperations.from_brackets(),
                "区切り文字から": TextExtractOperations.from_delimiter(),
                "改行・空白を削除": TextExtractOperations.remove_whitespace(),
                "ファイルパスから": TextExtractOperations.from_filepath(),
                "ルールにマッチ": TextExtractOperations.match_pattern(),
                "置換": TextExtractOperations.replace(),
                "文字変換": TextExtractOperations.convert_text(),
                "日付形式変換": TextExtractOperations.convert_date_format(),
                "1行ずつループ": TextExtractOperations.loop_lines(),
            },
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
                "読み込む": FileOperations.read(),
                "書き込む": FileOperations.write(),
                "移動": FileOperations.move(),
            },
            "フォルダ": {
                "開く": FolderOperations.open(),
                "作成": FolderOperations.create(),
                "ループ": FolderOperations.loop(),
            },
            "圧縮・解凍": {
                "ファイル・フォルダを圧縮": FileFolderOperations.Compression.compress(),
                "ファイル・フォルダに解凍": FileFolderOperations.Compression.extract(),
            },
            "ファイル名変更（挿入）": {
                "名前変更": FileFolderOperations.rename(),
                "コピー": FileFolderOperations.copy(),
                "削除": FileFolderOperations.delete(),
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
                "移動・コピー": ExcelOperations.Sheet.move_or_copy(),
                "名前取得": ExcelOperations.Sheet.get_name(),
                "参照ID": ExcelOperations.Sheet.switch(),
                "削除": ExcelOperations.Sheet.delete(),
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

        # K. スプレッドシート
        self.operations["K_スプレッドシート"] = {
            "スプレッドシート": {
                "ブックを開く": SpreadsheetOperations.Spreadsheet.create_spreadsheet(),
                "ブックを覚える": SpreadsheetOperations.Spreadsheet.remember_spreadsheet(),
                "URL取得": SpreadsheetOperations.Spreadsheet.get_spreadsheet_url(),
            },
            "シート": {
                "新規作成": SpreadsheetOperations.Sheet.create_spreadsheet_sheet(),
                "移動・コピー": SpreadsheetOperations.Sheet.move_spreadsheet_sheet(),
                "名前取得": SpreadsheetOperations.Sheet.get_spreadsheet_sheet_name(),
                "参照ID": SpreadsheetOperations.Sheet.copy_spreadsheet_sheet(),
                "削除": SpreadsheetOperations.Sheet.delete_spreadsheet_sheet(),
            },
            "セル操作": {
                "範囲指定": SpreadsheetOperations.Cell.get_spreadsheet_values(),
                "指定範囲の削除": SpreadsheetOperations.Cell.delete_spreadsheet_range(),
                "指定範囲にセルを挿入": SpreadsheetOperations.Cell.insert_spreadsheet_range(),
                "値を取得": SpreadsheetOperations.Cell.get_spreadsheet_values(),
                "値を入力": SpreadsheetOperations.Cell.set_spreadsheet_values(),
                "セルをコピー・貼り付け": SpreadsheetOperations.Cell.copy_paste_spreadsheet(),
                "最終行取得": SpreadsheetOperations.Cell.get_spreadsheet_last_row(),
                "行ループ": SpreadsheetOperations.Cell.loop_spreadsheet_row(),
                "列ループ": SpreadsheetOperations.Cell.loop_spreadsheet_col(),
            },
        }

        # L. ウェブブラウザ
        self.operations["L_ウェブブラウザ"] = {
            "ブラウザを開く": WebBrowserOperations.create_operation("open"),
            "ブラウザを閉じる": WebBrowserOperations.create_operation("close"),
            "ページ移動": WebBrowserOperations.create_operation("navigate"),
            "クリック": WebBrowserOperations.create_operation("click"),
            "入力": WebBrowserOperations.create_operation("input"),
            "選択": WebBrowserOperations.create_operation("select"),
            "読み取り": WebBrowserOperations.create_operation("get_text"),
            "待機": WebBrowserOperations.create_operation("wait"),
            "スクリーンショット": WebBrowserOperations.create_operation("screenshot"),
            "JavaScript実行": WebBrowserOperations.create_operation("execute_js"),
            "タブ切り替え": WebBrowserOperations.create_operation("switch_tab"),
            "更新": WebBrowserOperations.create_operation("refresh"),
        }

        # M. メール
        self.operations["M_メール"] = {
            "送信": MailOperations.send_email(),
            "受信": MailOperations.receive_emails(),
            "送信（Gmail）": MailOperations.send_email_gmail(),
            "受信（Gmail）": MailOperations.receive_emails_gmail(),
            "送信（Microsoft）": MailOperations.send_email_microsoft(),
            "受信（Microsoft）": MailOperations.receive_emails_microsoft(),
        }

        # N. 特殊アプリ操作
        self.operations["N_特殊アプリ操作"] = {
            "文字入力": SpecialAppOperations.send_text_to_uia_element(),
            "文字入力（パスワード）": SpecialAppOperations.send_password_to_uia_element(),
            "座標取得": SpecialAppOperations.get_uia_element_clickable_point(),
            "文字取得": SpecialAppOperations.get_text_from_uia_element(),
        }

        # O. API
        self.operations["O_API"] = {
            "JSON": {
                "JSON値取得": APIOperations.JSON.get_json_values(),
                "JSON型確認": APIOperations.JSON.check_json_type(),
            },
        }

        # P. シナリオ整理
        self.operations["P_シナリオ整理"] = {
            "グループ化": ScenarioOrganizationOperations.group_commands(),
            "メモ": ScenarioOrganizationOperations.add_memo(),
            "通知音を再生": ScenarioOrganizationOperations.play_sound(),
        }

        # Q. 別シナリオ実行・継承
        self.operations["Q_別シナリオ実行・継承"] = {
            "別シナリオ実行": ExternalScenarioOperations.run_external_scenario_and_branch(),
            "親シナリオからデータを継承": ExternalScenarioOperations.inherit_variables(),
            "親シナリオからパスワードを継承": ExternalScenarioOperations.inherit_passwords(),
            "親シナリオからウィンドウを継承": ExternalScenarioOperations.inherit_windows(),
            "親シナリオからエクセルを継承": ExternalScenarioOperations.inherit_excel(),
            "親シナリオからブラウザを継承": ExternalScenarioOperations.inherit_browsers(),
        }

    def _normalize_step_name(self, name: str) -> str:
        """括弧内を削除してステップ名を正規化"""
        name = re.sub(r"（.*?）", "", name)
        name = re.sub(r"\(.*?\)", "", name)
        return name.strip()

    def _generate_dot_id(self, category: str, subcategory: str, step_name: str) -> str:
        """ドット区切りのIDを生成"""
        cat_id = self.CATEGORY_MAPPING.get(category, category.lower().replace(" ", "_"))
        subcat_id = self.SUBCATEGORY_MAPPING.get(subcategory, subcategory.lower().replace(" ", "_"))

        # まず元のステップ名でマッピングを試みる
        step_id = self.STEP_NAME_MAPPING.get(step_name)
        if not step_id:
            norm_step = self._normalize_step_name(step_name)
            step_id = self.STEP_NAME_MAPPING.get(norm_step, norm_step.lower().replace(" ", "_"))

        if subcategory == step_name:
            # 単一レベルの場合
            sid = self.STEP_NAME_MAPPING.get(step_name)
            if not sid:
                norm_step = self._normalize_step_name(step_name)
                sid = self.STEP_NAME_MAPPING.get(norm_step)
            if sid:
                return f"{cat_id}.{sid}"
            sid2 = self.SUBCATEGORY_MAPPING.get(subcategory, subcategory.lower().replace(" ", "_"))
            return f"{cat_id}.{sid2}"
        return f"{cat_id}.{subcat_id}.{step_id}"

    def _generate_tags(self, step_name: str, subcategory: str, category: str) -> list[str]:
        """ステップに関連するタグを生成"""
        tags: list[str] = []
        if ("アプリ" in category) or ("アプリ" in subcategory):
            tags += ["アプリケーション", "プログラム", "ソフトウェア"]
        if ("画面" in category) or ("画面" in subcategory):
            tags += ["ウィンドウ", "画面", "window"]
        if "マウス" in category:
            tags += ["マウス", "クリック", "mouse"]
        if "キーボード" in category:
            tags += ["キーボード", "入力", "keyboard"]
        if ("ファイル" in category) or ("フォルダ" in category):
            tags += ["ファイル", "フォルダ", "file", "folder"]
        if ("エクセル" in category) or ("CSV" in category):
            tags += ["Excel", "エクセル", "CSV", "表計算"]
        if "ブラウザ" in category:
            tags += ["ブラウザ", "Web", "browser", "Chrome"]
        if "メール" in category:
            tags += ["メール", "email", "送信", "受信"]

        step_name_norm = self._normalize_step_name(step_name)
        if "起動" in step_name_norm:
            tags += ["起動", "開く", "実行", "start", "launch"]
        if "待" in step_name_norm:
            tags += ["待機", "待つ", "wait"]
        if "クリック" in step_name_norm:
            tags += ["クリック", "押す", "click"]
        if "入力" in step_name_norm:
            tags += ["入力", "タイプ", "input", "type"]
        if "取得" in step_name_norm:
            tags += ["取得", "読み取り", "get", "read"]
        if ("ループ" in step_name_norm) or ("繰り返し" in step_name_norm):
            tags += ["ループ", "繰り返し", "反復", "loop"]

        return list(dict.fromkeys(tags))  # 重複を削除

    def _infer_type(self, v: Any) -> str:
        """値から型を推論"""
        if isinstance(v, bool):
            return "boolean"
        if isinstance(v, int) and not isinstance(v, bool):
            return "integer"
        if isinstance(v, float):
            return "number"
        if isinstance(v, list):
            return "array"
        if isinstance(v, dict):
            return "object"
        return "string"

    def _build_flat_entries(self) -> list[dict[str, Any]]:
        """フラット形式のエントリーを構築"""
        flat: list[dict[str, Any]] = []

        for category_key, cat_obj in self.operations.items():
            if not isinstance(cat_obj, dict):
                continue
            for subcat_key, sub_obj in cat_obj.items():
                # 単一ステップの場合
                if isinstance(sub_obj, OperationTemplate):
                    step_name = subcat_key
                    dot_id = self._generate_dot_id(category_key, subcat_key, step_name)
                    spec_defs: dict[str, dict[str, Any]] = {}
                    for k, dv in sub_obj.specific_params.items():
                        spec_defs[k] = {
                            "type": self._infer_type(dv),
                            "description": "",
                            "required": False,
                        }
                    detailed_desc = self.STEP_DESCRIPTIONS.get(step_name, f"{step_name}を実行します。")
                    flat.append({
                        "id": dot_id,
                        "name": step_name,
                        "description": detailed_desc,
                        "tags": self._generate_tags(step_name, subcat_key, category_key),
                        "specific_params": spec_defs,
                    })
                    continue

                # 複数ステップの場合
                if isinstance(sub_obj, dict):
                    for step_name, step_tpl in sub_obj.items():
                        if not isinstance(step_tpl, OperationTemplate):
                            continue
                        dot_id = self._generate_dot_id(category_key, subcat_key, step_name)
                        spec_defs: dict[str, dict[str, Any]] = {}
                        for k, dv in step_tpl.specific_params.items():
                            spec_defs[k] = {
                                "type": self._infer_type(dv),
                                "description": "",
                                "required": False,
                            }
                        detailed_desc = self.STEP_DESCRIPTIONS.get(step_name, f"{step_name}を実行します。")
                        flat.append({
                            "id": dot_id,
                            "name": step_name,
                            "description": detailed_desc,
                            "tags": self._generate_tags(step_name, subcat_key, category_key),
                            "specific_params": spec_defs,
                        })
        return flat

    def save_flat_to_file(self, filepath: str | Path, indent: int = 2):
        """フラット形式のJSONをファイルに保存"""
        entries = self._build_flat_entries()
        filepath = Path(filepath)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False, indent=indent)
        print(f"Saved flat operations to {filepath} ({len(entries)} entries)")


if __name__ == "__main__":
    # RPAシステムのインスタンス作成
    rpa_system = RPAOperationSystem()

    # フラット形式でファイルに保存
    rpa_system.save_flat_to_file("rpa_operations.json")
