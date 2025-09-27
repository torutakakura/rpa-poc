#!/usr/bin/env python3
"""
RPA MCP Server
generated_step_list.jsonのRPAステップをMCPツールとして提供
"""

from fastmcp import FastMCP
import json
import uuid
from pathlib import Path
from typing import Optional, Dict, Any

mcp = FastMCP("RPA Operations Tool")

# generated_step_list.jsonのパスを設定
STEP_LIST_PATH = Path(__file__).parent / "generated_step_list.json"

# 起動時にJSONファイルを読み込み
def load_step_list():
    """generated_step_list.jsonを読み込む"""
    try:
        with open(STEP_LIST_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {STEP_LIST_PATH} not found")
        return {"sequence": []}
    except Exception as e:
        print(f"Error loading generated_step_list.json: {e}")
        return {"sequence": []}

# グローバル変数として操作定義を保持
STEP_LIST = load_step_list()

# 汎用的なステップ生成関数
def create_step_from_template(cmd: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """generated_step_list.jsonのテンプレートから該当するステップを生成"""
    # テンプレートを探す
    template = None
    for step in STEP_LIST.get("sequence", []):
        if step.get("cmd") == cmd:
            template = step.copy()
            break

    if not template:
        # テンプレートが見つからない場合は基本構造を作成
        template = {
            "cmd": cmd,
            "cmd-nickname": cmd,
            "cmd-type": "basic",
            "version": 1,
            "uuid": str(uuid.uuid4()),
            "memo": "",
            "description": "",
            "tags": [],
            "parameters": {},
            "flags": {
                "checkboxed": False,
                "bookmarked": False
            }
        }
    else:
        # 新しいUUIDを生成
        template["uuid"] = str(uuid.uuid4())

    # パラメータをマージ（提供された値で上書き）
    if "parameters" in template:
        for key, value in params.items():
            if value is not None:  # Noneでない値のみ上書き
                template["parameters"][key] = value

    return template

# ====================
# 基本操作ツール
# ====================

@mcp.tool()
def run_executable(
    path: str,
    arguments: Optional[str] = "",
    interval: Optional[int] = 3,
    maximized: Optional[bool] = True
) -> Dict[str, Any]:
    """アプリケーションを起動"""
    params = {
        "path": path,
        "arguments": arguments if arguments is not None else "",
        "interval": interval if interval is not None else 3,
        "maximized": maximized if maximized is not None else True
    }
    return create_step_from_template("run-executable", params)

@mcp.tool()
def run_executable_and_wait(
    path: str,
    arguments: Optional[str] = "",
    timeout: Optional[int] = 300,
    output_variable: Optional[str] = "",
    error_variable: Optional[str] = ""
) -> Dict[str, Any]:
    """アプリケーションを起動して終了を待つ"""
    params = {
        "path": path,
        "arguments": arguments if arguments is not None else "",
        "timeout": timeout if timeout is not None else 300,
        "output-variable": output_variable if output_variable is not None else "",
        "error-variable": error_variable if error_variable is not None else ""
    }
    return create_step_from_template("run-executable-and-wait", params)

@mcp.tool()
def pause(
    interval: Optional[str] = "3"
) -> Dict[str, Any]:
    """指定秒数待機"""
    params = {
        "interval": interval if interval is not None else "3"
    }
    return create_step_from_template("pause", params)

@mcp.tool()
def pause_and_ask_to_proceed(
    string: Optional[str] = ""
) -> Dict[str, Any]:
    """続行確認ダイアログを表示"""
    params = {
        "string": string if string is not None else ""
    }
    return create_step_from_template("pause-and-ask-to-proceed", params)

@mcp.tool()
def pause_and_countdown_to_proceed(
    interval: Optional[str] = "3",
    string: Optional[str] = ""
) -> Dict[str, Any]:
    """タイマー付き続行確認"""
    params = {
        "interval": interval if interval is not None else "3",
        "string": string if string is not None else ""
    }
    return create_step_from_template("pause-and-countdown-to-proceed", params)

@mcp.tool()
def change_speed_for_command_execution(
    interval: Optional[float] = 0.2
) -> Dict[str, Any]:
    """コマンド間の待機時間を変更"""
    params = {
        "interval": interval if interval is not None else 0.2
    }
    return create_step_from_template("change-speed-for-command-execution", params)

@mcp.tool()
def abort(
    result_type: Optional[str] = "abort"
) -> Dict[str, Any]:
    """作業を強制終了"""
    params = {
        "result-type": result_type if result_type is not None else "abort"
    }
    return create_step_from_template("abort", params)

@mcp.tool()
def raise_error(
    string: Optional[str] = ""
) -> Dict[str, Any]:
    """エラーを発生させる"""
    params = {
        "string": string if string is not None else ""
    }
    return create_step_from_template("raise-error", params)

@mcp.tool()
def take_screenshot(
    dir_path: Optional[str] = "",
    file_name: Optional[str] = "",
    area: Optional[str] = "area-whole",
    variable: Optional[str] = "",
    timestamp: Optional[bool] = False,
    extension: Optional[str] = "png"
) -> Dict[str, Any]:
    """スクリーンショットを撮る"""
    params = {
        "dir-path": dir_path if dir_path is not None else "",
        "file-name": file_name if file_name is not None else "",
        "area": area if area is not None else "area-whole",
        "variable": variable if variable is not None else "",
        "timestamp": timestamp if timestamp is not None else False,
        "extension": extension if extension is not None else "png"
    }
    return create_step_from_template("take-screenshot", params)

# ====================
# ウィンドウ操作ツール
# ====================

@mcp.tool()
def remember_focused_window(
    variable: Optional[str] = "ウィンドウ"
) -> Dict[str, Any]:
    """最前面画面を覚える"""
    params = {
        "variable": variable if variable is not None else "ウィンドウ"
    }
    return create_step_from_template("remember-focused-window", params)

@mcp.tool()
def remember_named_window(
    match_type: Optional[str] = "contains",
    window_name: Optional[str] = "ウィンドウ",
    variable: Optional[str] = "ウィンドウ"
) -> Dict[str, Any]:
    """画面を覚える（名前）"""
    params = {
        "match-type": match_type if match_type is not None else "contains",
        "window-name": window_name if window_name is not None else "ウィンドウ",
        "variable": variable if variable is not None else "ウィンドウ"
    }
    return create_step_from_template("remember-named-window", params)

@mcp.tool()
def focus_window(
    variable: Optional[str] = ""
) -> Dict[str, Any]:
    """最前面画面切り替え"""
    params = {
        "variable": variable if variable is not None else ""
    }
    return create_step_from_template("focus-window", params)

@mcp.tool()
def focus_window_by_name(
    string: Optional[str] = ""
) -> Dict[str, Any]:
    """画面切り替え（名前）"""
    params = {
        "string": string if string is not None else ""
    }
    return create_step_from_template("focus-window-by-name", params)

@mcp.tool()
def get_window_title(
    window: Optional[str] = "__focused_window__",
    variable: Optional[str] = "ウィンドウ名"
) -> Dict[str, Any]:
    """画面の名前を取得"""
    params = {
        "window": window if window is not None else "__focused_window__",
        "variable": variable if variable is not None else "ウィンドウ名"
    }
    return create_step_from_template("get-window-title", params)

@mcp.tool()
def align_focused_window(
    alignment: Optional[str] = "left"
) -> Dict[str, Any]:
    """ウィンドウを移動"""
    params = {
        "alignment": alignment if alignment is not None else "left"
    }
    return create_step_from_template("align-focused-window", params)

@mcp.tool()
def maximize_focused_window(
    behavior: Optional[str] = "maximize"
) -> Dict[str, Any]:
    """ウィンドウ最大化／最小化"""
    params = {
        "behavior": behavior if behavior is not None else "maximize"
    }
    return create_step_from_template("maximize-focused-window", params)

# ====================
# マウス操作ツール
# ====================

@mcp.tool()
def move_mouse_to_absolute_coordinates(
    x: Optional[str] = "100",
    y: Optional[str] = "100",
    click: Optional[str] = "single"
) -> Dict[str, Any]:
    """マウス移動（座標）"""
    params = {
        "x": x if x is not None else "100",
        "y": y if y is not None else "100",
        "click": click if click is not None else "single"
    }
    return create_step_from_template("move-mouse-to-absolute-coordinates", params)

@mcp.tool()
def move_mouse_to_relative_coordinates(
    x: Optional[str] = "100",
    y: Optional[str] = "100",
    click: Optional[str] = "single"
) -> Dict[str, Any]:
    """マウス移動（距離）"""
    params = {
        "x": x if x is not None else "100",
        "y": y if y is not None else "100",
        "click": click if click is not None else "single"
    }
    return create_step_from_template("move-mouse-to-relative-coordinates", params)

@mcp.tool()
def click_mouse(
    type: Optional[str] = "single",
    key: Optional[str] = "__null__"
) -> Dict[str, Any]:
    """マウスクリック"""
    params = {
        "type": type if type is not None else "single",
        "key": key if key is not None else "__null__"
    }
    return create_step_from_template("click-mouse", params)

@mcp.tool()
def scroll_mouse(
    direction: Optional[str] = "up",
    amount: Optional[int] = 3
) -> Dict[str, Any]:
    """マウススクロール"""
    params = {
        "direction": direction if direction is not None else "up",
        "amount": amount if amount is not None else 3
    }
    return create_step_from_template("scroll-mouse", params)

@mcp.tool()
def drag_and_drop_to_absolute_coordinates(
    x: Optional[str] = "100",
    y: Optional[str] = "100"
) -> Dict[str, Any]:
    """現在位置からドラッグ＆ドロップ（座標）"""
    params = {
        "x": x if x is not None else "100",
        "y": y if y is not None else "100"
    }
    return create_step_from_template("drag-and-drop-to-absolute-coordinates", params)

@mcp.tool()
def drag_and_drop_to_relative_coordinates(
    x: Optional[str] = "100",
    y: Optional[str] = "100"
) -> Dict[str, Any]:
    """現在位置からドラッグ＆ドロップ（距離）"""
    params = {
        "x": x if x is not None else "100",
        "y": y if y is not None else "100"
    }
    return create_step_from_template("drag-and-drop-to-relative-coordinates", params)

@mcp.tool()
def move_mouse_to_image(
    filename: Optional[str] = "",
    precision: Optional[str] = "85",
    noise_filter: Optional[str] = "100.0",
    search_area_type: Optional[str] = "screen",
    search_area: Optional[str] = "(0, 0) ~ (0, 0)",
    click: Optional[str] = "single"
) -> Dict[str, Any]:
    """マウス移動（画像認識）"""
    params = {
        "filename": filename if filename is not None else "",
        "precision": precision if precision is not None else "85",
        "noise-filter": noise_filter if noise_filter is not None else "100.0",
        "search-area-type": search_area_type if search_area_type is not None else "screen",
        "search-area": search_area if search_area is not None else "(0, 0) ~ (0, 0)",
        "click": click if click is not None else "single"
    }
    return create_step_from_template("move-mouse-to-image", params)

@mcp.tool()
def drag_and_drop_to_image(
    filename: Optional[str] = "",
    precision: Optional[str] = "85",
    noise_filter: Optional[str] = "100.0",
    search_area_type: Optional[str] = "screen",
    search_area: Optional[str] = "(0, 0) ~ (0, 0)"
) -> Dict[str, Any]:
    """現在位置からドラッグ＆ドロップ（画像認識）"""
    params = {
        "filename": filename if filename is not None else "",
        "precision": precision if precision is not None else "85",
        "noise-filter": noise_filter if noise_filter is not None else "100.0",
        "search-area-type": search_area_type if search_area_type is not None else "screen",
        "search-area": search_area if search_area is not None else "(0, 0) ~ (0, 0)"
    }
    return create_step_from_template("drag-and-drop-to-image", params)

# ====================
# キーボード操作ツール
# ====================

@mcp.tool()
def typewrite_static_string(
    string: Optional[str] = "",
    enter: Optional[bool] = False
) -> Dict[str, Any]:
    """キーボード入力（文字）"""
    params = {
        "string": string if string is not None else "",
        "enter": enter if enter is not None else False
    }
    return create_step_from_template("typewrite-static-string", params)

@mcp.tool()
def typewrite_all_string(
    string: Optional[str] = "",
    enter: Optional[bool] = False
) -> Dict[str, Any]:
    """キーボード入力（貼り付け）"""
    params = {
        "string": string if string is not None else "",
        "enter": enter if enter is not None else False
    }
    return create_step_from_template("typewrite-all-string", params)

@mcp.tool()
def typewrite_password(
    enter: Optional[bool] = False,
    password_type: Optional[str] = "type-input",
    ciphertext: Optional[str] = "",
    nonce: Optional[str] = "",
    encryption: Optional[int] = 1
) -> Dict[str, Any]:
    """キーボード入力（パスワード）"""
    params = {
        "enter": enter if enter is not None else False,
        "password-type": password_type if password_type is not None else "type-input",
        "ciphertext": ciphertext if ciphertext is not None else "",
        "nonce": nonce if nonce is not None else "",
        "encryption": encryption if encryption is not None else 1
    }
    return create_step_from_template("typewrite-password", params)

@mcp.tool()
def type_hotkeys(
    key_0: Optional[str] = "__null__",
    key_1: Optional[str] = "__null__",
    key_2: Optional[str] = "__null__",
    key_3: Optional[str] = ""
) -> Dict[str, Any]:
    """ショートカットキーを入力"""
    params = {
        "key-0": key_0 if key_0 is not None else "__null__",
        "key-1": key_1 if key_1 is not None else "__null__",
        "key-2": key_2 if key_2 is not None else "__null__",
        "key-3": key_3 if key_3 is not None else ""
    }
    return create_step_from_template("type-hotkeys", params)

# ====================
# 変数操作ツール
# ====================

@mcp.tool()
def assign_string_variable(
    variable: Optional[str] = "データ",
    string: Optional[str] = ""
) -> Dict[str, Any]:
    """データの記憶（文字）"""
    params = {
        "variable": variable if variable is not None else "データ",
        "string": string if string is not None else ""
    }
    return create_step_from_template("assign-string-variable", params)

@mcp.tool()
def assign_password_variable(
    password_type: Optional[str] = "type-input",
    password: Optional[str] = "",
    password_id: Optional[str] = "パスワード"
) -> Dict[str, Any]:
    """パスワードの記憶"""
    params = {
        "password-type": password_type if password_type is not None else "type-input",
        "password": password if password is not None else "",
        "password-id": password_id if password_id is not None else "パスワード"
    }
    return create_step_from_template("assign-password-variable", params)

@mcp.tool()
def assign_environment_variable(
    variable: Optional[str] = "環境",
    environment: Optional[str] = ""
) -> Dict[str, Any]:
    """データの記憶（環境情報）"""
    params = {
        "variable": variable if variable is not None else "環境",
        "environment": environment if environment is not None else ""
    }
    return create_step_from_template("assign-environment-variable", params)

@mcp.tool()
def assign_date_to_string_variable(
    variable: Optional[str] = "日付",
    offset: Optional[str] = "0",
    format: Optional[str] = "yyyy-mm-dd",
    zero_option: Optional[bool] = False
) -> Dict[str, Any]:
    """日付を記憶"""
    params = {
        "variable": variable if variable is not None else "日付",
        "offset": offset if offset is not None else "0",
        "format": format if format is not None else "yyyy-mm-dd",
        "0-option": zero_option if zero_option is not None else False
    }
    return create_step_from_template("assign-date-to-string-variable", params)

@mcp.tool()
def assign_clipboard_to_string_variable(
    variable: Optional[str] = "データ"
) -> Dict[str, Any]:
    """コピー内容を記憶"""
    params = {
        "variable": variable if variable is not None else "データ"
    }
    return create_step_from_template("assign-clipboard-to-string-variable", params)

@mcp.tool()
def copy_to_clipboard(
    string: Optional[str] = ""
) -> Dict[str, Any]:
    """クリップボードへコピー"""
    params = {
        "string": string if string is not None else ""
    }
    return create_step_from_template("copy-to-clipboard", params)

# ====================
# 文字列操作ツール
# ====================

@mcp.tool()
def parse_brackets(
    src_variable: Optional[str] = "",
    dst_variable: Optional[str] = "抽出文字",
    bracket_types: Optional[list] = None,
    index: Optional[str] = "1",
    strip: Optional[bool] = True
) -> Dict[str, Any]:
    """文字列抽出（括弧・引用符号）"""
    params = {
        "src-variable": src_variable if src_variable is not None else "",
        "dst-variable": dst_variable if dst_variable is not None else "抽出文字",
        "bracket-types": bracket_types if bracket_types is not None else ["()"],
        "index": index if index is not None else "1",
        "strip": strip if strip is not None else True
    }
    return create_step_from_template("parse-brackets", params)

@mcp.tool()
def parse_delimiters(
    src_variable: Optional[str] = "",
    dst_variable: Optional[str] = "抽出文字",
    delimiter_type: Optional[str] = ",",
    custom_str: Optional[str] = "",
    index: Optional[str] = "1"
) -> Dict[str, Any]:
    """文字列抽出（区切り文字）"""
    params = {
        "src-variable": src_variable if src_variable is not None else "",
        "dst-variable": dst_variable if dst_variable is not None else "抽出文字",
        "delimiter-type": delimiter_type if delimiter_type is not None else ",",
        "custom-str": custom_str if custom_str is not None else "",
        "index": index if index is not None else "1"
    }
    return create_step_from_template("parse-delimiters", params)

# ====================
# 画像認識・分岐ツール
# ====================

@mcp.tool()
def search_screen_and_branch(
    filename: Optional[str] = "",
    precision: Optional[str] = "85",
    interval: Optional[str] = "5",
    noise_filter: Optional[str] = "100.0",
    search_area_type: Optional[str] = "screen",
    search_area: Optional[str] = "(0, 0) ~ (0, 0)"
) -> Dict[str, Any]:
    """画像出現を待つ"""
    params = {
        "filename": filename if filename is not None else "",
        "precision": precision if precision is not None else "85",
        "interval": interval if interval is not None else "5",
        "noise-filter": noise_filter if noise_filter is not None else "100.0",
        "search-area-type": search_area_type if search_area_type is not None else "screen",
        "search-area": search_area if search_area is not None else "(0, 0) ~ (0, 0)"
    }
    return create_step_from_template("search-screen-and-branch", params)

# ====================
# エラー処理ツール
# ====================

@mcp.tool()
def check_for_errors(
    retries: Optional[int] = 0,
    wait: Optional[int] = 1,
    err_cmd: Optional[str] = "[ERR_CMD]",
    err_memo: Optional[str] = "[ERR_MEMO]",
    err_msg: Optional[str] = "[ERR_MSG]",
    err_param: Optional[str] = "[ERR_PARAM]"
) -> Dict[str, Any]:
    """直前のコマンドのエラーを確認・処理"""
    params = {
        "retries": retries if retries is not None else 0,
        "wait": wait if wait is not None else 1,
        "err-cmd": err_cmd if err_cmd is not None else "[ERR_CMD]",
        "err-memo": err_memo if err_memo is not None else "[ERR_MEMO]",
        "err-msg": err_msg if err_msg is not None else "[ERR_MSG]",
        "err-param": err_param if err_param is not None else "[ERR_PARAM]"
    }
    return create_step_from_template("check-for-errors", params)

@mcp.tool()
def check_for_errors_2(
    retries: Optional[int] = 0,
    wait: Optional[int] = 1,
    err_cmd: Optional[str] = "[ERR_CMD]",
    err_memo: Optional[str] = "[ERR_MEMO]",
    err_msg: Optional[str] = "[ERR_MSG]",
    err_param: Optional[str] = "[ERR_PARAM]"
) -> Dict[str, Any]:
    """直前のコマンドのエラーを確認・処理（リトライ前処理）"""
    params = {
        "retries": retries if retries is not None else 0,
        "wait": wait if wait is not None else 1,
        "err-cmd": err_cmd if err_cmd is not None else "[ERR_CMD]",
        "err-memo": err_memo if err_memo is not None else "[ERR_MEMO]",
        "err-msg": err_msg if err_msg is not None else "[ERR_MSG]",
        "err-param": err_param if err_param is not None else "[ERR_PARAM]"
    }
    return create_step_from_template("check-for-errors-2", params)

# ====================
# 日付・時刻操作ツール（拡張）
# ====================

@mcp.tool()
def assign_date_business_to_string_variable(
    variable: Optional[str] = "日付",
    offset: Optional[str] = "0",
    busidays: Optional[str] = "1",
    mon: Optional[bool] = False,
    tue: Optional[bool] = False,
    wed: Optional[bool] = False,
    thu: Optional[bool] = False,
    fri: Optional[bool] = False,
    sat: Optional[bool] = True,
    sun: Optional[bool] = True,
    holidays: Optional[bool] = True,
    holidays_custom: Optional[bool] = True,
    format: Optional[str] = "yyyy-mm-dd",
    zero_option: Optional[bool] = False
) -> Dict[str, Any]:
    """日付を記憶（営業日）"""
    params = {
        "variable": variable if variable is not None else "日付",
        "offset": offset if offset is not None else "0",
        "busidays": busidays if busidays is not None else "1",
        "mon": mon if mon is not None else False,
        "tue": tue if tue is not None else False,
        "wed": wed if wed is not None else False,
        "thu": thu if thu is not None else False,
        "fri": fri if fri is not None else False,
        "sat": sat if sat is not None else True,
        "sun": sun if sun is not None else True,
        "holidays": holidays if holidays is not None else True,
        "holidays-custom": holidays_custom if holidays_custom is not None else True,
        "format": format if format is not None else "yyyy-mm-dd",
        "0-option": zero_option if zero_option is not None else False
    }
    return create_step_from_template("assign-date-business-to-string-variable", params)

@mcp.tool()
def assign_date_weekdays_to_string_variable(
    variable: Optional[str] = "日付",
    month: Optional[str] = "0",
    week: Optional[str] = "0",
    weekdays: Optional[str] = "0",
    mon: Optional[bool] = False,
    tue: Optional[bool] = False,
    wed: Optional[bool] = False,
    thu: Optional[bool] = False,
    fri: Optional[bool] = False,
    sat: Optional[bool] = False,
    sun: Optional[bool] = False,
    holidays: Optional[bool] = False,
    holidays_custom: Optional[bool] = False,
    adjust: Optional[str] = "forward",
    format: Optional[str] = "yyyy-mm-dd",
    zero_option: Optional[bool] = False
) -> Dict[str, Any]:
    """日付を記憶（曜日）"""
    params = {
        "variable": variable if variable is not None else "日付",
        "month": month if month is not None else "0",
        "week": week if week is not None else "0",
        "weekdays": weekdays if weekdays is not None else "0",
        "mon": mon if mon is not None else False,
        "tue": tue if tue is not None else False,
        "wed": wed if wed is not None else False,
        "thu": thu if thu is not None else False,
        "fri": fri if fri is not None else False,
        "sat": sat if sat is not None else False,
        "sun": sun if sun is not None else False,
        "holidays": holidays if holidays is not None else False,
        "holidays-custom": holidays_custom if holidays_custom is not None else False,
        "adjust": adjust if adjust is not None else "forward",
        "format": format if format is not None else "yyyy-mm-dd",
        "0-option": zero_option if zero_option is not None else False
    }
    return create_step_from_template("assign-date-weekdays-to-string-variable", params)

@mcp.tool()
def assign_date_calculation_to_string_variable(
    variable: Optional[str] = "日付",
    input_date: Optional[str] = "",
    format1: Optional[str] = "yyyy-mm-dd",
    format2: Optional[str] = "yyyy-mm-dd",
    operator: Optional[str] = "add",
    year: Optional[str] = "",
    month: Optional[str] = "",
    day: Optional[str] = "",
    mon: Optional[bool] = False,
    tue: Optional[bool] = False,
    wed: Optional[bool] = False,
    thu: Optional[bool] = False,
    fri: Optional[bool] = False,
    sat: Optional[bool] = False,
    sun: Optional[bool] = False,
    holidays: Optional[bool] = False,
    holidays_custom: Optional[bool] = False,
    count_method: Optional[str] = "everyday",
    adjust: Optional[str] = "forward",
    zero_option: Optional[bool] = False
) -> Dict[str, Any]:
    """日付計算結果を記憶"""
    params = {
        "variable": variable if variable is not None else "日付",
        "input-date": input_date if input_date is not None else "",
        "format1": format1 if format1 is not None else "yyyy-mm-dd",
        "format2": format2 if format2 is not None else "yyyy-mm-dd",
        "operator": operator if operator is not None else "add",
        "year": year if year is not None else "",
        "month": month if month is not None else "",
        "day": day if day is not None else "",
        "mon": mon if mon is not None else False,
        "tue": tue if tue is not None else False,
        "wed": wed if wed is not None else False,
        "thu": thu if thu is not None else False,
        "fri": fri if fri is not None else False,
        "sat": sat if sat is not None else False,
        "sun": sun if sun is not None else False,
        "holidays": holidays if holidays is not None else False,
        "holidays-custom": holidays_custom if holidays_custom is not None else False,
        "count-method": count_method if count_method is not None else "everyday",
        "adjust": adjust if adjust is not None else "forward",
        "0-option": zero_option if zero_option is not None else False
    }
    return create_step_from_template("assign-date-calculation-to-string-variable", params)

@mcp.tool()
def assign_day_of_week_to_string_variable(
    variable: Optional[str] = "曜日",
    offset: Optional[str] = "0",
    format: Optional[str] = "月曜日",
    type: Optional[str] = "today",
    date: Optional[str] = "",
    format_date: Optional[str] = "yyyy-mm-dd"
) -> Dict[str, Any]:
    """曜日を記憶"""
    params = {
        "variable": variable if variable is not None else "曜日",
        "offset": offset if offset is not None else "0",
        "format": format if format is not None else "月曜日",
        "type": type if type is not None else "today",
        "date": date if date is not None else "",
        "format-date": format_date if format_date is not None else "yyyy-mm-dd"
    }
    return create_step_from_template("assign-day-of-week-to-string-variable", params)

@mcp.tool()
def assign_timestamp_to_string_variable(
    variable: Optional[str] = "時刻",
    format: Optional[str] = "hh:mm:ss",
    language: Optional[str] = "",
    timezone: Optional[str] = "",
    zero_option: Optional[bool] = False
) -> Dict[str, Any]:
    """現在の時刻を記憶"""
    params = {
        "variable": variable if variable is not None else "時刻",
        "format": format if format is not None else "hh:mm:ss",
        "language": language if language is not None else "",
        "timezone": timezone if timezone is not None else "",
        "0-option": zero_option if zero_option is not None else False
    }
    return create_step_from_template("assign-timestamp-to-string-variable", params)

@mcp.tool()
def assign_time_calculation_to_string_variable(
    variable: Optional[str] = "時刻",
    time: Optional[str] = "",
    format: Optional[str] = "hh:mm:ss",
    operator: Optional[str] = "add",
    hours: Optional[str] = "",
    minutes: Optional[str] = "",
    seconds: Optional[str] = "",
    format2: Optional[str] = "hh:mm:ss",
    language: Optional[str] = "",
    timezone: Optional[str] = "",
    zero_option: Optional[bool] = False
) -> Dict[str, Any]:
    """時刻計算結果を記憶"""
    params = {
        "variable": variable if variable is not None else "時刻",
        "time": time if time is not None else "",
        "format": format if format is not None else "hh:mm:ss",
        "operator": operator if operator is not None else "add",
        "hours": hours if hours is not None else "",
        "minutes": minutes if minutes is not None else "",
        "seconds": seconds if seconds is not None else "",
        "format2": format2 if format2 is not None else "hh:mm:ss",
        "language": language if language is not None else "",
        "timezone": timezone if timezone is not None else "",
        "0-option": zero_option if zero_option is not None else False
    }
    return create_step_from_template("assign-time-calculation-to-string-variable", params)

# ====================
# 数値計算ツール
# ====================

@mcp.tool()
def assign_arithmetic_result_to_string_variable_v2(
    variable: Optional[str] = "計算結果",
    number1: Optional[str] = "",
    number2: Optional[str] = "",
    operator: Optional[str] = "add",
    round_type: Optional[str] = "none",
    precision: Optional[str] = ""
) -> Dict[str, Any]:
    """計算結果を記憶"""
    params = {
        "variable": variable if variable is not None else "計算結果",
        "number1": number1 if number1 is not None else "",
        "number2": number2 if number2 is not None else "",
        "operator": operator if operator is not None else "add",
        "round-type": round_type if round_type is not None else "none",
        "precision": precision if precision is not None else ""
    }
    return create_step_from_template("assign-arithmetic-result-to-string-variable-v2", params)

@mcp.tool()
def assign_random_number_to_string_variable(
    variable: Optional[str] = "データ",
    min_number: Optional[str] = "0",
    max_number: Optional[str] = "100",
    precision: Optional[str] = "0",
    zero_fill: Optional[bool] = True
) -> Dict[str, Any]:
    """乱数を記憶"""
    params = {
        "variable": variable if variable is not None else "データ",
        "min-number": min_number if min_number is not None else "0",
        "max-number": max_number if max_number is not None else "100",
        "precision": precision if precision is not None else "0",
        "zero-fill": zero_fill if zero_fill is not None else True
    }
    return create_step_from_template("assign-random-number-to-string-variable", params)

@mcp.tool()
def assign_live_input_to_string_variable(
    variable: Optional[str] = "データ",
    string: Optional[str] = ""
) -> Dict[str, Any]:
    """実行中に入力"""
    params = {
        "variable": variable if variable is not None else "データ",
        "string": string if string is not None else ""
    }
    return create_step_from_template("assign-live-input-to-string-variable", params)

# ====================
# ファイル情報ツール
# ====================

@mcp.tool()
def assign_file_modification_timestamp_to_string_variable(
    variable: Optional[str] = "日時",
    path: Optional[str] = "",
    timestamp: Optional[str] = "modification",
    format: Optional[str] = "yyyy-mm-dd_hh:mm:ss"
) -> Dict[str, Any]:
    """ファイル更新日時を記憶"""
    params = {
        "variable": variable if variable is not None else "日時",
        "path": path if path is not None else "",
        "timestamp": timestamp if timestamp is not None else "modification",
        "format": format if format is not None else "yyyy-mm-dd_hh:mm:ss"
    }
    return create_step_from_template("assign-file-modification-timestamp-to-string-variable", params)

@mcp.tool()
def assign_file_size_to_string_variable(
    variable: Optional[str] = "サイズ",
    path: Optional[str] = "",
    unit: Optional[str] = "bytes"
) -> Dict[str, Any]:
    """ファイルサイズを記憶"""
    params = {
        "variable": variable if variable is not None else "サイズ",
        "path": path if path is not None else "",
        "unit": unit if unit is not None else "bytes"
    }
    return create_step_from_template("assign-file-size-to-string-variable", params)

@mcp.tool()
def find_newest_file_from_fixed_directory(
    variable: Optional[str] = "ファイル保存場所",
    file_or_dir: Optional[str] = "file",
    date_check: Optional[str] = "更新日時",
    number: Optional[int] = 1,
    path: Optional[str] = ""
) -> Dict[str, Any]:
    """最新ファイル・フォルダを取得"""
    params = {
        "variable": variable if variable is not None else "ファイル保存場所",
        "file-or-dir": file_or_dir if file_or_dir is not None else "file",
        "date-check": date_check if date_check is not None else "更新日時",
        "number": number if number is not None else 1,
        "path": path if path is not None else ""
    }
    return create_step_from_template("find-newest-file-from-fixed-directory", params)

# ====================
# 文字列処理ツール（拡張）
# ====================

@mcp.tool()
def parse_break_and_space(
    break_space: Optional[str] = "break",
    variable: Optional[str] = "",
    all: Optional[bool] = False,
    head: Optional[bool] = False,
    end: Optional[bool] = True
) -> Dict[str, Any]:
    """文字列抽出（改行・空白を削除）"""
    params = {
        "break-space": break_space if break_space is not None else "break",
        "variable": variable if variable is not None else "",
        "all": all if all is not None else False,
        "head": head if head is not None else False,
        "end": end if end is not None else True
    }
    return create_step_from_template("parse-break-and-space", params)

@mcp.tool()
def extract_fname(
    src_variable: Optional[str] = "",
    dst_variable: Optional[str] = "ファイル名",
    extension: Optional[bool] = False
) -> Dict[str, Any]:
    """ファイル・フォルダ名抽出（ファイルパス）"""
    params = {
        "src-variable": src_variable if src_variable is not None else "",
        "dst-variable": dst_variable if dst_variable is not None else "ファイル名",
        "extension": extension if extension is not None else False
    }
    return create_step_from_template("extract-fname", params)

@mcp.tool()
def parse_regex(
    src_variable: Optional[str] = "",
    dst_variable: Optional[str] = "抽出文字",
    regex: Optional[str] = "",
    option: Optional[str] = ""
) -> Dict[str, Any]:
    """文字列抽出（ルールにマッチする）"""
    params = {
        "src-variable": src_variable if src_variable is not None else "",
        "dst-variable": dst_variable if dst_variable is not None else "抽出文字",
        "regex": regex if regex is not None else "",
        "option": option if option is not None else ""
    }
    return create_step_from_template("parse-regex", params)

@mcp.tool()
def replace_strings(
    src_variable: Optional[str] = "",
    dst_variable: Optional[str] = "置換結果",
    src_str: Optional[str] = "",
    dst_str: Optional[str] = ""
) -> Dict[str, Any]:
    """文字を置換"""
    params = {
        "src-variable": src_variable if src_variable is not None else "",
        "dst-variable": dst_variable if dst_variable is not None else "置換結果",
        "src-str": src_str if src_str is not None else "",
        "dst-str": dst_str if dst_str is not None else ""
    }
    return create_step_from_template("replace-strings", params)

@mcp.tool()
def convert_character_type(
    string: Optional[str] = "",
    type: Optional[str] = "z2h-all",
    variable: Optional[str] = "データ"
) -> Dict[str, Any]:
    """文字変換"""
    params = {
        "string": string if string is not None else "",
        "type": type if type is not None else "z2h-all",
        "variable": variable if variable is not None else "データ"
    }
    return create_step_from_template("convert-character-type", params)

@mcp.tool()
def convert_date_format(
    date: Optional[str] = "",
    before_format: Optional[str] = "yyyy/mm/dd",
    before_custom: Optional[str] = "",
    format: Optional[str] = "yyyy/mm/dd",
    custom: Optional[str] = "",
    variable: Optional[str] = "変換結果"
) -> Dict[str, Any]:
    """日付の形式を変換"""
    params = {
        "date": date if date is not None else "",
        "before-format": before_format if before_format is not None else "yyyy/mm/dd",
        "before-custom": before_custom if before_custom is not None else "",
        "format": format if format is not None else "yyyy/mm/dd",
        "custom": custom if custom is not None else "",
        "variable": variable if variable is not None else "変換結果"
    }
    return create_step_from_template("convert-date-format", params)

# ====================
# ループ処理ツール
# ====================

@mcp.tool()
def loop_by_line(
    src_variable: Optional[str] = "",
    dst_variable: Optional[str] = "ライン"
) -> Dict[str, Any]:
    """文字抽出ループ（1行ずつ）"""
    params = {
        "src-variable": src_variable if src_variable is not None else "",
        "dst-variable": dst_variable if dst_variable is not None else "ライン"
    }
    return create_step_from_template("loop-by-line", params)

# ====================
# 分岐ツール
# ====================

@mcp.tool()
def compare_strings_and_branch(
    string1: Optional[str] = "",
    string2: Optional[str] = "",
    match: Optional[str] = "full"
) -> Dict[str, Any]:
    """文字列比較"""
    params = {
        "string1": string1 if string1 is not None else "",
        "string2": string2 if string2 is not None else "",
        "match": match if match is not None else "full"
    }
    return create_step_from_template("compare-strings-and-branch", params)

@mcp.tool()
def compare_numbers_and_branch(
    variable: Optional[str] = "",
    number: Optional[str] = "0",
    comparator: Optional[str] = "=="
) -> Dict[str, Any]:
    """数値比較"""
    params = {
        "variable": variable if variable is not None else "",
        "number": number if number is not None else "0",
        "comparator": comparator if comparator is not None else "=="
    }
    return create_step_from_template("compare-numbers-and-branch", params)

@mcp.tool()
def compare_dates_and_branch(
    date1: Optional[str] = "",
    date2: Optional[str] = "",
    format1: Optional[str] = "yyyy-mm-dd",
    format2: Optional[str] = "yyyy-mm-dd",
    comparator: Optional[str] = "eq"
) -> Dict[str, Any]:
    """日付比較"""
    params = {
        "date1": date1 if date1 is not None else "",
        "date2": date2 if date2 is not None else "",
        "format1": format1 if format1 is not None else "yyyy-mm-dd",
        "format2": format2 if format2 is not None else "yyyy-mm-dd",
        "comparator": comparator if comparator is not None else "eq"
    }
    return create_step_from_template("compare-dates-and-branch", params)

@mcp.tool()
def search_file_from_directory_and_branch(
    file_name: Optional[str] = "",
    file_or_dir: Optional[str] = "file",
    dir_path: Optional[str] = ""
) -> Dict[str, Any]:
    """ファイル・フォルダの有/無を確認"""
    params = {
        "file-name": file_name if file_name is not None else "",
        "file-or-dir": file_or_dir if file_or_dir is not None else "file",
        "dir-path": dir_path if dir_path is not None else ""
    }
    return create_step_from_template("search-file-from-directory-and-branch", params)

@mcp.tool()
def find_image_and_branch(
    filename: Optional[str] = "",
    precision: Optional[str] = "85",
    interval: Optional[str] = "5",
    noise_filter: Optional[str] = "100.0",
    search_area_type: Optional[str] = "screen",
    search_area: Optional[str] = "(0, 0) ~ (0, 0)"
) -> Dict[str, Any]:
    """画像を探す"""
    params = {
        "filename": filename if filename is not None else "",
        "precision": precision if precision is not None else "85",
        "interval": interval if interval is not None else "5",
        "noise-filter": noise_filter if noise_filter is not None else "100.0",
        "search-area-type": search_area_type if search_area_type is not None else "screen",
        "search-area": search_area if search_area is not None else "(0, 0) ~ (0, 0)"
    }
    return create_step_from_template("find-image-and-branch", params)

# ====================
# ループ制御ツール
# ====================

@mcp.tool()
def loop_n_times(
    count: Optional[str] = "1",
    type: Optional[str] = "times"
) -> Dict[str, Any]:
    """繰り返し"""
    params = {
        "count": count if count is not None else "1",
        "type": type if type is not None else "times"
    }
    return create_step_from_template("loop-n-times", params)

@mcp.tool()
def break_loop() -> Dict[str, Any]:
    """繰り返しを抜ける"""
    return create_step_from_template("break-loop", {})

@mcp.tool()
def continue_loop() -> Dict[str, Any]:
    """繰り返しの最初に戻る"""
    return create_step_from_template("continue-loop", {})

# ====================
# ファイル操作ツール
# ====================

@mcp.tool()
def open_static_file_name(
    path: Optional[str] = "",
    interval: Optional[int] = 3,
    maximized: Optional[bool] = True
) -> Dict[str, Any]:
    """ファイルを開く"""
    params = {
        "path": path if path is not None else "",
        "interval": interval if interval is not None else 3,
        "maximized": maximized if maximized is not None else True
    }
    return create_step_from_template("open-static-file-name", params)

@mcp.tool()
def move_fixed_file_to_fixed_directory(
    src_path: Optional[str] = "",
    dst_path: Optional[str] = "",
    variable: Optional[str] = ""
) -> Dict[str, Any]:
    """ファイルを移動"""
    params = {
        "src-path": src_path if src_path is not None else "",
        "dst-path": dst_path if dst_path is not None else "",
        "variable": variable if variable is not None else ""
    }
    return create_step_from_template("move-fixed-file-to-fixed-directory", params)

@mcp.tool()
def read_file(
    path: Optional[str] = "",
    variable: Optional[str] = "データ",
    encoding: Optional[str] = "auto",
    custom_encoding: Optional[str] = ""
) -> Dict[str, Any]:
    """テキストファイルを読み込む"""
    params = {
        "path": path if path is not None else "",
        "variable": variable if variable is not None else "データ",
        "encoding": encoding if encoding is not None else "auto",
        "custom-encoding": custom_encoding if custom_encoding is not None else ""
    }
    return create_step_from_template("read-file", params)

@mcp.tool()
def write_file(
    string: Optional[str] = "",
    path: Optional[str] = "",
    mode: Optional[str] = "create",
    encoding: Optional[str] = "system-default",
    custom_encoding: Optional[str] = ""
) -> Dict[str, Any]:
    """テキストファイルに書き込む"""
    params = {
        "string": string if string is not None else "",
        "path": path if path is not None else "",
        "mode": mode if mode is not None else "create",
        "encoding": encoding if encoding is not None else "system-default",
        "custom-encoding": custom_encoding if custom_encoding is not None else ""
    }
    return create_step_from_template("write-file", params)

# ====================
# フォルダ操作ツール
# ====================

@mcp.tool()
def open_fixed_directory_name(
    path: Optional[str] = ""
) -> Dict[str, Any]:
    """フォルダを開く"""
    params = {
        "path": path if path is not None else ""
    }
    return create_step_from_template("open-fixed-directory-name", params)

@mcp.tool()
def create_directory(
    dir_path: Optional[str] = "",
    dir_name: Optional[str] = "",
    variable: Optional[str] = ""
) -> Dict[str, Any]:
    """フォルダを作成"""
    params = {
        "dir-path": dir_path if dir_path is not None else "",
        "dir-name": dir_name if dir_name is not None else "",
        "variable": variable if variable is not None else ""
    }
    return create_step_from_template("create-directory", params)

@mcp.tool()
def loop_directory_contents(
    variable: Optional[str] = "ファイル保存場所",
    target: Optional[str] = "file",
    path: Optional[str] = "",
    extension: Optional[str] = ".txt",
    order: Optional[str] = "dict_windows",
    case_sensitive: Optional[str] = "case-disable"
) -> Dict[str, Any]:
    """フォルダ内をループ"""
    params = {
        "variable": variable if variable is not None else "ファイル保存場所",
        "target": target if target is not None else "file",
        "path": path if path is not None else "",
        "extension": extension if extension is not None else ".txt",
        "order": order if order is not None else "dict_windows",
        "case-sensitive": case_sensitive if case_sensitive is not None else "case-disable"
    }
    return create_step_from_template("loop-directory-contents", params)

# ====================
# ファイル・フォルダ共通操作ツール
# ====================

@mcp.tool()
def rename_file_or_directory(
    src_path: Optional[str] = "",
    extension_opt: Optional[str] = "extension-yes",
    rename: Optional[str] = "",
    act_option: Optional[str] = "overwrite",
    variable: Optional[str] = ""
) -> Dict[str, Any]:
    """ファイル・フォルダ名の変更"""
    params = {
        "src-path": src_path if src_path is not None else "",
        "extension-opt": extension_opt if extension_opt is not None else "extension-yes",
        "rename": rename if rename is not None else "",
        "act-option": act_option if act_option is not None else "overwrite",
        "variable": variable if variable is not None else ""
    }
    return create_step_from_template("rename-file-or-directory", params)

@mcp.tool()
def copy_file_or_directory(
    src_path: Optional[str] = "",
    dst_path: Optional[str] = "",
    act_check: Optional[str] = "",
    variable: Optional[str] = ""
) -> Dict[str, Any]:
    """ファイル・フォルダをコピー"""
    params = {
        "src-path": src_path if src_path is not None else "",
        "dst-path": dst_path if dst_path is not None else "",
        "act-check": act_check if act_check is not None else "",
        "variable": variable if variable is not None else ""
    }
    return create_step_from_template("copy-file-or-directory", params)

@mcp.tool()
def delete_file_or_directory(
    src_path: Optional[str] = "",
    delete: Optional[bool] = False
) -> Dict[str, Any]:
    """ファイル・フォルダを削除"""
    params = {
        "src-path": src_path if src_path is not None else "",
        "delete": delete if delete is not None else False
    }
    return create_step_from_template("delete-file-or-directory", params)

# ====================
# 圧縮・解凍ツール
# ====================

@mcp.tool()
def compress_file_or_directory(
    compression_method: Optional[str] = "zip",
    src_path: Optional[str] = "",
    dst_path: Optional[str] = "",
    password_type: Optional[str] = "type-empty",
    password: Optional[str] = "",
    variable: Optional[str] = ""
) -> Dict[str, Any]:
    """ファイル・フォルダを圧縮"""
    params = {
        "compression-method": compression_method if compression_method is not None else "zip",
        "src-path": src_path if src_path is not None else "",
        "dst-path": dst_path if dst_path is not None else "",
        "password-type": password_type if password_type is not None else "type-empty",
        "password": password if password is not None else "",
        "variable": variable if variable is not None else ""
    }
    return create_step_from_template("compress-file-or-directory", params)

@mcp.tool()
def decompress_file(
    decompression_method: Optional[str] = "zip",
    src_path: Optional[str] = "",
    dst_path: Optional[str] = "",
    password_type: Optional[str] = "type-empty",
    password: Optional[str] = "",
    variable: Optional[str] = ""
) -> Dict[str, Any]:
    """ファイル・フォルダに解凍"""
    params = {
        "decompression-method": decompression_method if decompression_method is not None else "zip",
        "src-path": src_path if src_path is not None else "",
        "dst-path": dst_path if dst_path is not None else "",
        "password-type": password_type if password_type is not None else "type-empty",
        "password": password if password is not None else "",
        "variable": variable if variable is not None else ""
    }
    return create_step_from_template("decompress-file", params)

# ====================
# ファイル名変更ツール
# ====================

@mcp.tool()
def prepend_string_to_variable_filename(
    variable: Optional[str] = "",
    string: Optional[str] = "",
    position: Optional[str] = "head",
    update: Optional[bool] = False
) -> Dict[str, Any]:
    """文字をファイル名に挿入"""
    params = {
        "variable": variable if variable is not None else "",
        "string": string if string is not None else "",
        "position": position if position is not None else "head",
        "update": update if update is not None else False
    }
    return create_step_from_template("prepend-string-to-variable-filename", params)

@mcp.tool()
def prepend_date_to_variable_filename(
    variable: Optional[str] = "",
    position: Optional[str] = "head",
    update: Optional[bool] = False
) -> Dict[str, Any]:
    """日付をファイル名に挿入"""
    params = {
        "variable": variable if variable is not None else "",
        "position": position if position is not None else "head",
        "update": update if update is not None else False
    }
    return create_step_from_template("prepend-date-to-variable-filename", params)

@mcp.tool()
def prepend_variable_to_file(
    variable: Optional[str] = "",
    path: Optional[str] = "",
    position: Optional[str] = "head",
    update_var: Optional[str] = ""
) -> Dict[str, Any]:
    """参照IDをファイル名に挿入"""
    params = {
        "variable": variable if variable is not None else "",
        "path": path if path is not None else "",
        "position": position if position is not None else "head",
        "update-var": update_var if update_var is not None else ""
    }
    return create_step_from_template("prepend-variable-to-file", params)

# =================================================
# スプレッドシート操作
# =================================================

@mcp.tool()
def create_spreadsheet(name: str = None, template_url: str = None) -> Dict[str, Any]:
    """新しいスプレッドシートを作成"""
    params = {
        "name": name if name is not None else "",
        "template-url": template_url if template_url is not None else ""
    }
    return create_step_from_template("create-spreadsheet", params)

@mcp.tool()
def open_spreadsheet(spreadsheet: str = None) -> Dict[str, Any]:
    """指定したスプレッドシートを開く"""
    params = {
        "spreadsheet": spreadsheet if spreadsheet is not None else ""
    }
    return create_step_from_template("open-spreadsheet", params)

@mcp.tool()
def get_spreadsheet_sheet_names(spreadsheet: str = None, variable: str = None) -> Dict[str, Any]:
    """スプレッドシートの全シート名を取得"""
    params = {
        "spreadsheet": spreadsheet if spreadsheet is not None else "",
        "variable": variable if variable is not None else "シート名"
    }
    return create_step_from_template("get-spreadsheet-sheet-names", params)

@mcp.tool()
def create_spreadsheet_sheet(spreadsheet: str = None, sheet_name: str = None) -> Dict[str, Any]:
    """スプレッドシートに新しいシートを作成"""
    params = {
        "spreadsheet": spreadsheet if spreadsheet is not None else "",
        "sheet-name": sheet_name if sheet_name is not None else ""
    }
    return create_step_from_template("create-spreadsheet-sheet", params)

@mcp.tool()
def delete_spreadsheet_sheet(spreadsheet: str = None, sheet_name: str = None) -> Dict[str, Any]:
    """スプレッドシートのシートを削除"""
    params = {
        "spreadsheet": spreadsheet if spreadsheet is not None else "",
        "sheet-name": sheet_name if sheet_name is not None else ""
    }
    return create_step_from_template("delete-spreadsheet-sheet", params)

@mcp.tool()
def move_spreadsheet_sheet(
    spreadsheet: str = None,
    sheet_name: str = None,
    target_position: str = None,
    target_sheet: str = None
) -> Dict[str, Any]:
    """スプレッドシートのシートを移動"""
    params = {
        "spreadsheet": spreadsheet if spreadsheet is not None else "",
        "sheet-name": sheet_name if sheet_name is not None else "",
        "target-position": target_position if target_position is not None else "last",
        "target-sheet": target_sheet if target_sheet is not None else ""
    }
    return create_step_from_template("move-spreadsheet-sheet", params)

@mcp.tool()
def copy_spreadsheet_sheet(
    spreadsheet: str = None,
    sheet_name: str = None,
    target_spreadsheet: str = None,
    copy_sheet_name: str = None
) -> Dict[str, Any]:
    """スプレッドシートのシートをコピー"""
    params = {
        "spreadsheet": spreadsheet if spreadsheet is not None else "",
        "sheet-name": sheet_name if sheet_name is not None else "",
        "target-spreadsheet": target_spreadsheet if target_spreadsheet is not None else "",
        "copy-sheet-name": copy_sheet_name if copy_sheet_name is not None else ""
    }
    return create_step_from_template("copy-spreadsheet-sheet", params)

@mcp.tool()
def get_spreadsheet_sheet_name(
    variable: str = None,
    spreadsheet: str = None,
    target_position: str = None,
    target_index: str = None
) -> Dict[str, Any]:
    """スプレッドシートのシート名を取得"""
    params = {
        "variable": variable if variable is not None else "名前",
        "spreadsheet": spreadsheet if spreadsheet is not None else "",
        "target-position": target_position if target_position is not None else "by-index",
        "target-index": target_index if target_index is not None else ""
    }
    return create_step_from_template("get-spreadsheet-sheet-name", params)

@mcp.tool()
def rename_spreadsheet_sheet(
    spreadsheet: str = None,
    sheet_name: str = None,
    rename: str = None
) -> Dict[str, Any]:
    """スプレッドシートのシート名を変更"""
    params = {
        "spreadsheet": spreadsheet if spreadsheet is not None else "",
        "sheet-name": sheet_name if sheet_name is not None else "",
        "rename": rename if rename is not None else ""
    }
    return create_step_from_template("rename-spreadsheet-sheet", params)

@mcp.tool()
def delete_spreadsheet_range(
    spreadsheet: str = None,
    sheet_name: str = None,
    range: str = None,
    shift_type: str = None
) -> Dict[str, Any]:
    """スプレッドシートの指定範囲を削除"""
    params = {
        "spreadsheet": spreadsheet if spreadsheet is not None else "",
        "sheet-name": sheet_name if sheet_name is not None else "",
        "range": range if range is not None else "",
        "shift-type": shift_type if shift_type is not None else "rows"
    }
    return create_step_from_template("delete-spreadsheet-range", params)

@mcp.tool()
def insert_spreadsheet_range(
    spreadsheet: str = None,
    sheet_name: str = None,
    range: str = None,
    shift_type: str = None
) -> Dict[str, Any]:
    """スプレッドシートに行や列を挿入"""
    params = {
        "spreadsheet": spreadsheet if spreadsheet is not None else "",
        "sheet-name": sheet_name if sheet_name is not None else "",
        "range": range if range is not None else "",
        "shift-type": shift_type if shift_type is not None else "rows"
    }
    return create_step_from_template("insert-spreadsheet-range", params)

@mcp.tool()
def get_spreadsheet_values(
    spreadsheet: str = None,
    sheet_name: str = None,
    range: str = None,
    variable: str = None,
    type: str = None
) -> Dict[str, Any]:
    """スプレッドシートのセル値を取得"""
    params = {
        "spreadsheet": spreadsheet if spreadsheet is not None else "",
        "sheet-name": sheet_name if sheet_name is not None else "",
        "range": range if range is not None else "",
        "variable": variable if variable is not None else "データ",
        "type": type if type is not None else "formatted-value"
    }
    return create_step_from_template("get-spreadsheet-values", params)

@mcp.tool()
def set_spreadsheet_values(
    spreadsheet: str = None,
    sheet_name: str = None,
    range: str = None,
    single_cell: str = None,
    string: str = None
) -> Dict[str, Any]:
    """スプレッドシートのセルに値を設定"""
    params = {
        "spreadsheet": spreadsheet if spreadsheet is not None else "",
        "sheet-name": sheet_name if sheet_name is not None else "",
        "range": range if range is not None else "",
        "single-cell": single_cell if single_cell is not None else "single",
        "string": string if string is not None else ""
    }
    return create_step_from_template("set-spreadsheet-values", params)

@mcp.tool()
def copy_paste_spreadsheet(
    spreadsheet: str = None,
    src_sheet: str = None,
    src_range: str = None,
    dst_sheet: str = None,
    dst_range: str = None,
    paste_type: str = None
) -> Dict[str, Any]:
    """スプレッドシートの範囲をコピーして貼り付け"""
    params = {
        "spreadsheet": spreadsheet if spreadsheet is not None else "",
        "src-sheet": src_sheet if src_sheet is not None else "",
        "src-range": src_range if src_range is not None else "",
        "dst-sheet": dst_sheet if dst_sheet is not None else "",
        "dst-range": dst_range if dst_range is not None else "",
        "paste-type": paste_type if paste_type is not None else "PASTE_NORMAL"
    }
    return create_step_from_template("copy-paste-spreadsheet", params)

@mcp.tool()
def clear_spreadsheet_range(
    spreadsheet: str = None,
    sheet_name: str = None,
    range: str = None,
    clear_type: str = None
) -> Dict[str, Any]:
    """スプレッドシートの範囲をクリア"""
    params = {
        "spreadsheet": spreadsheet if spreadsheet is not None else "",
        "sheet-name": sheet_name if sheet_name is not None else "",
        "range": range if range is not None else "",
        "clear-type": clear_type if clear_type is not None else "values"
    }
    return create_step_from_template("clear-spreadsheet-range", params)

@mcp.tool()
def sort_spreadsheet_range(
    spreadsheet: str = None,
    sheet_name: str = None,
    range: str = None,
    column: int = None,
    order: str = None
) -> Dict[str, Any]:
    """スプレッドシートの範囲をソート"""
    params = {
        "spreadsheet": spreadsheet if spreadsheet is not None else "",
        "sheet-name": sheet_name if sheet_name is not None else "",
        "range": range if range is not None else "",
        "column": column if column is not None else 1,
        "order": order if order is not None else "ascending"
    }
    return create_step_from_template("sort-spreadsheet-range", params)

@mcp.tool()
def find_in_spreadsheet(
    spreadsheet: str = None,
    sheet_name: str = None,
    range: str = None,
    search_text: str = None,
    variable: str = None
) -> Dict[str, Any]:
    """スプレッドシート内でテキストを検索"""
    params = {
        "spreadsheet": spreadsheet if spreadsheet is not None else "",
        "sheet-name": sheet_name if sheet_name is not None else "",
        "range": range if range is not None else "",
        "search-text": search_text if search_text is not None else "",
        "variable": variable if variable is not None else "検索結果"
    }
    return create_step_from_template("find-in-spreadsheet", params)

@mcp.tool()
def filter_spreadsheet_range(
    spreadsheet: str = None,
    sheet_name: str = None,
    range: str = None,
    filter_criteria: str = None
) -> Dict[str, Any]:
    """スプレッドシートの範囲にフィルターを適用"""
    params = {
        "spreadsheet": spreadsheet if spreadsheet is not None else "",
        "sheet-name": sheet_name if sheet_name is not None else "",
        "range": range if range is not None else "",
        "filter-criteria": filter_criteria if filter_criteria is not None else ""
    }
    return create_step_from_template("filter-spreadsheet-range", params)

@mcp.tool()
def format_spreadsheet_cells(
    spreadsheet: str = None,
    sheet_name: str = None,
    range: str = None,
    format_type: str = None,
    format_value: str = None
) -> Dict[str, Any]:
    """スプレッドシートのセルの書式を設定"""
    params = {
        "spreadsheet": spreadsheet if spreadsheet is not None else "",
        "sheet-name": sheet_name if sheet_name is not None else "",
        "range": range if range is not None else "",
        "format-type": format_type if format_type is not None else "bold",
        "format-value": format_value if format_value is not None else ""
    }
    return create_step_from_template("format-spreadsheet-cells", params)

@mcp.tool()
def protect_spreadsheet_range(
    spreadsheet: str = None,
    sheet_name: str = None,
    range: str = None,
    protection_type: str = None
) -> Dict[str, Any]:
    """スプレッドシートの範囲を保護"""
    params = {
        "spreadsheet": spreadsheet if spreadsheet is not None else "",
        "sheet-name": sheet_name if sheet_name is not None else "",
        "range": range if range is not None else "",
        "protection-type": protection_type if protection_type is not None else "warning"
    }
    return create_step_from_template("protect-spreadsheet-range", params)

# =================================================
# Excel操作
# =================================================

@mcp.tool()
def open_excel(file: str = None) -> Dict[str, Any]:
    """Excelファイルを開く"""
    params = {
        "file": file if file is not None else ""
    }
    return create_step_from_template("open-excel", params)

@mcp.tool()
def close_excel(save: bool = None) -> Dict[str, Any]:
    """Excelファイルを閉じる"""
    params = {
        "save": save if save is not None else True
    }
    return create_step_from_template("close-excel", params)

@mcp.tool()
def save_excel(file_path: str = None) -> Dict[str, Any]:
    """Excelファイルを保存"""
    params = {
        "file-path": file_path if file_path is not None else ""
    }
    return create_step_from_template("save-excel", params)

@mcp.tool()
def create_excel_sheet(sheet_name: str = None) -> Dict[str, Any]:
    """Excelに新しいシートを作成"""
    params = {
        "sheet-name": sheet_name if sheet_name is not None else ""
    }
    return create_step_from_template("create-excel-sheet", params)

@mcp.tool()
def delete_excel_sheet(sheet_name: str = None) -> Dict[str, Any]:
    """Excelのシートを削除"""
    params = {
        "sheet-name": sheet_name if sheet_name is not None else ""
    }
    return create_step_from_template("delete-excel-sheet", params)

@mcp.tool()
def rename_excel_sheet(old_name: str = None, new_name: str = None) -> Dict[str, Any]:
    """Excelのシート名を変更"""
    params = {
        "old-name": old_name if old_name is not None else "",
        "new-name": new_name if new_name is not None else ""
    }
    return create_step_from_template("rename-excel-sheet", params)

@mcp.tool()
def select_excel_sheet(sheet_name: str = None) -> Dict[str, Any]:
    """Excelのシートを選択"""
    params = {
        "sheet-name": sheet_name if sheet_name is not None else ""
    }
    return create_step_from_template("select-excel-sheet", params)

@mcp.tool()
def get_excel_cell_value(
    sheet_name: str = None,
    cell: str = None,
    variable: str = None
) -> Dict[str, Any]:
    """Excelのセルの値を取得"""
    params = {
        "sheet-name": sheet_name if sheet_name is not None else "",
        "cell": cell if cell is not None else "A1",
        "variable": variable if variable is not None else "値"
    }
    return create_step_from_template("get-excel-cell-value", params)

@mcp.tool()
def set_excel_cell_value(
    sheet_name: str = None,
    cell: str = None,
    value: str = None
) -> Dict[str, Any]:
    """Excelのセルに値を設定"""
    params = {
        "sheet-name": sheet_name if sheet_name is not None else "",
        "cell": cell if cell is not None else "A1",
        "value": value if value is not None else ""
    }
    return create_step_from_template("set-excel-cell-value", params)

@mcp.tool()
def get_excel_range_values(
    sheet_name: str = None,
    range: str = None,
    variable: str = None
) -> Dict[str, Any]:
    """Excelの範囲の値を取得"""
    params = {
        "sheet-name": sheet_name if sheet_name is not None else "",
        "range": range if range is not None else "",
        "variable": variable if variable is not None else "データ"
    }
    return create_step_from_template("get-excel-range-values", params)

@mcp.tool()
def set_excel_range_values(
    sheet_name: str = None,
    range: str = None,
    values: str = None
) -> Dict[str, Any]:
    """Excelの範囲に値を設定"""
    params = {
        "sheet-name": sheet_name if sheet_name is not None else "",
        "range": range if range is not None else "",
        "values": values if values is not None else ""
    }
    return create_step_from_template("set-excel-range-values", params)

@mcp.tool()
def copy_excel_range(
    sheet_name: str = None,
    range: str = None
) -> Dict[str, Any]:
    """Excelの範囲をコピー"""
    params = {
        "sheet-name": sheet_name if sheet_name is not None else "",
        "range": range if range is not None else ""
    }
    return create_step_from_template("copy-excel-range", params)

@mcp.tool()
def paste_excel_range(
    sheet_name: str = None,
    cell: str = None,
    paste_type: str = None
) -> Dict[str, Any]:
    """Excelに貼り付け"""
    params = {
        "sheet-name": sheet_name if sheet_name is not None else "",
        "cell": cell if cell is not None else "A1",
        "paste-type": paste_type if paste_type is not None else "all"
    }
    return create_step_from_template("paste-excel-range", params)

@mcp.tool()
def clear_excel_range(
    sheet_name: str = None,
    range: str = None,
    clear_type: str = None
) -> Dict[str, Any]:
    """Excelの範囲をクリア"""
    params = {
        "sheet-name": sheet_name if sheet_name is not None else "",
        "range": range if range is not None else "",
        "clear-type": clear_type if clear_type is not None else "contents"
    }
    return create_step_from_template("clear-excel-range", params)

@mcp.tool()
def insert_excel_rows(
    sheet_name: str = None,
    row: int = None,
    count: int = None
) -> Dict[str, Any]:
    """Excelに行を挿入"""
    params = {
        "sheet-name": sheet_name if sheet_name is not None else "",
        "row": row if row is not None else 1,
        "count": count if count is not None else 1
    }
    return create_step_from_template("insert-excel-rows", params)

@mcp.tool()
def insert_excel_columns(
    sheet_name: str = None,
    column: str = None,
    count: int = None
) -> Dict[str, Any]:
    """Excelに列を挿入"""
    params = {
        "sheet-name": sheet_name if sheet_name is not None else "",
        "column": column if column is not None else "A",
        "count": count if count is not None else 1
    }
    return create_step_from_template("insert-excel-columns", params)

@mcp.tool()
def delete_excel_rows(
    sheet_name: str = None,
    row: int = None,
    count: int = None
) -> Dict[str, Any]:
    """Excelの行を削除"""
    params = {
        "sheet-name": sheet_name if sheet_name is not None else "",
        "row": row if row is not None else 1,
        "count": count if count is not None else 1
    }
    return create_step_from_template("delete-excel-rows", params)

@mcp.tool()
def delete_excel_columns(
    sheet_name: str = None,
    column: str = None,
    count: int = None
) -> Dict[str, Any]:
    """Excelの列を削除"""
    params = {
        "sheet-name": sheet_name if sheet_name is not None else "",
        "column": column if column is not None else "A",
        "count": count if count is not None else 1
    }
    return create_step_from_template("delete-excel-columns", params)

@mcp.tool()
def sort_excel_range(
    sheet_name: str = None,
    range: str = None,
    column: int = None,
    order: str = None
) -> Dict[str, Any]:
    """Excelの範囲をソート"""
    params = {
        "sheet-name": sheet_name if sheet_name is not None else "",
        "range": range if range is not None else "",
        "column": column if column is not None else 1,
        "order": order if order is not None else "ascending"
    }
    return create_step_from_template("sort-excel-range", params)

@mcp.tool()
def filter_excel_range(
    sheet_name: str = None,
    range: str = None,
    column: int = None,
    criteria: str = None
) -> Dict[str, Any]:
    """Excelの範囲にフィルタを適用"""
    params = {
        "sheet-name": sheet_name if sheet_name is not None else "",
        "range": range if range is not None else "",
        "column": column if column is not None else 1,
        "criteria": criteria if criteria is not None else ""
    }
    return create_step_from_template("filter-excel-range", params)

@mcp.tool()
def find_in_excel(
    sheet_name: str = None,
    search_text: str = None,
    variable: str = None
) -> Dict[str, Any]:
    """Excel内でテキストを検索"""
    params = {
        "sheet-name": sheet_name if sheet_name is not None else "",
        "search-text": search_text if search_text is not None else "",
        "variable": variable if variable is not None else "検索結果"
    }
    return create_step_from_template("find-in-excel", params)

# =================================================
# CSV操作
# =================================================

@mcp.tool()
def read_csv(
    file_path: str = None,
    variable: str = None,
    encoding: str = None,
    delimiter: str = None
) -> Dict[str, Any]:
    """CSVファイルを読み込み"""
    params = {
        "file-path": file_path if file_path is not None else "",
        "variable": variable if variable is not None else "CSVデータ",
        "encoding": encoding if encoding is not None else "utf-8",
        "delimiter": delimiter if delimiter is not None else ","
    }
    return create_step_from_template("read-csv", params)

@mcp.tool()
def write_csv(
    file_path: str = None,
    data: str = None,
    encoding: str = None,
    delimiter: str = None
) -> Dict[str, Any]:
    """CSVファイルに書き込み"""
    params = {
        "file-path": file_path if file_path is not None else "",
        "data": data if data is not None else "",
        "encoding": encoding if encoding is not None else "utf-8",
        "delimiter": delimiter if delimiter is not None else ","
    }
    return create_step_from_template("write-csv", params)

@mcp.tool()
def append_to_csv(
    file_path: str = None,
    data: str = None,
    encoding: str = None
) -> Dict[str, Any]:
    """CSVファイルに追記"""
    params = {
        "file-path": file_path if file_path is not None else "",
        "data": data if data is not None else "",
        "encoding": encoding if encoding is not None else "utf-8"
    }
    return create_step_from_template("append-to-csv", params)

@mcp.tool()
def get_csv_column(
    file_path: str = None,
    column_index: int = None,
    variable: str = None
) -> Dict[str, Any]:
    """CSVファイルの特定列を取得"""
    params = {
        "file-path": file_path if file_path is not None else "",
        "column-index": column_index if column_index is not None else 0,
        "variable": variable if variable is not None else "列データ"
    }
    return create_step_from_template("get-csv-column", params)

@mcp.tool()
def get_csv_row(
    file_path: str = None,
    row_index: int = None,
    variable: str = None
) -> Dict[str, Any]:
    """CSVファイルの特定行を取得"""
    params = {
        "file-path": file_path if file_path is not None else "",
        "row-index": row_index if row_index is not None else 0,
        "variable": variable if variable is not None else "行データ"
    }
    return create_step_from_template("get-csv-row", params)

@mcp.tool()
def filter_csv_data(
    file_path: str = None,
    filter_column: int = None,
    filter_value: str = None,
    variable: str = None
) -> Dict[str, Any]:
    """CSVデータをフィルタリング"""
    params = {
        "file-path": file_path if file_path is not None else "",
        "filter-column": filter_column if filter_column is not None else 0,
        "filter-value": filter_value if filter_value is not None else "",
        "variable": variable if variable is not None else "フィルタ結果"
    }
    return create_step_from_template("filter-csv-data", params)

@mcp.tool()
def sort_csv_data(
    file_path: str = None,
    sort_column: int = None,
    order: str = None,
    output_path: str = None
) -> Dict[str, Any]:
    """CSVデータをソート"""
    params = {
        "file-path": file_path if file_path is not None else "",
        "sort-column": sort_column if sort_column is not None else 0,
        "order": order if order is not None else "ascending",
        "output-path": output_path if output_path is not None else ""
    }
    return create_step_from_template("sort-csv-data", params)

@mcp.tool()
def merge_csv_files(
    file1: str = None,
    file2: str = None,
    output_path: str = None,
    merge_type: str = None
) -> Dict[str, Any]:
    """複数のCSVファイルを結合"""
    params = {
        "file1": file1 if file1 is not None else "",
        "file2": file2 if file2 is not None else "",
        "output-path": output_path if output_path is not None else "",
        "merge-type": merge_type if merge_type is not None else "vertical"
    }
    return create_step_from_template("merge-csv-files", params)

@mcp.tool()
def csv_to_excel(
    csv_path: str = None,
    excel_path: str = None,
    sheet_name: str = None
) -> Dict[str, Any]:
    """CSVファイルをExcelに変換"""
    params = {
        "csv-path": csv_path if csv_path is not None else "",
        "excel-path": excel_path if excel_path is not None else "",
        "sheet-name": sheet_name if sheet_name is not None else "Sheet1"
    }
    return create_step_from_template("csv-to-excel", params)

@mcp.tool()
def excel_to_csv(
    excel_path: str = None,
    csv_path: str = None,
    sheet_name: str = None
) -> Dict[str, Any]:
    """ExcelファイルをCSVに変換"""
    params = {
        "excel-path": excel_path if excel_path is not None else "",
        "csv-path": csv_path if csv_path is not None else "",
        "sheet-name": sheet_name if sheet_name is not None else ""
    }
    return create_step_from_template("excel-to-csv", params)

# =================================================
# ブラウザ操作
# =================================================

@mcp.tool()
def open_browser(url: str = None, browser_type: str = None) -> Dict[str, Any]:
    """ブラウザを開く"""
    params = {
        "url": url if url is not None else "",
        "browser-type": browser_type if browser_type is not None else "chrome"
    }
    return create_step_from_template("open-browser", params)

@mcp.tool()
def close_browser() -> Dict[str, Any]:
    """ブラウザを閉じる"""
    return create_step_from_template("close-browser", {})

@mcp.tool()
def navigate_to_url(url: str = None) -> Dict[str, Any]:
    """URLに移動"""
    params = {
        "url": url if url is not None else ""
    }
    return create_step_from_template("navigate-to-url", params)

@mcp.tool()
def browser_back() -> Dict[str, Any]:
    """ブラウザで戻る"""
    return create_step_from_template("browser-back", {})

@mcp.tool()
def browser_forward() -> Dict[str, Any]:
    """ブラウザで進む"""
    return create_step_from_template("browser-forward", {})

@mcp.tool()
def browser_refresh() -> Dict[str, Any]:
    """ブラウザを更新"""
    return create_step_from_template("browser-refresh", {})

@mcp.tool()
def get_page_title(variable: str = None) -> Dict[str, Any]:
    """ページタイトルを取得"""
    params = {
        "variable": variable if variable is not None else "タイトル"
    }
    return create_step_from_template("get-page-title", params)

@mcp.tool()
def get_page_url(variable: str = None) -> Dict[str, Any]:
    """ページURLを取得"""
    params = {
        "variable": variable if variable is not None else "URL"
    }
    return create_step_from_template("get-page-url", params)

@mcp.tool()
def click_web_element(
    selector: str = None,
    selector_type: str = None
) -> Dict[str, Any]:
    """Web要素をクリック"""
    params = {
        "selector": selector if selector is not None else "",
        "selector-type": selector_type if selector_type is not None else "css"
    }
    return create_step_from_template("click-web-element", params)

@mcp.tool()
def input_to_web_element(
    selector: str = None,
    text: str = None,
    selector_type: str = None
) -> Dict[str, Any]:
    """Web要素にテキストを入力"""
    params = {
        "selector": selector if selector is not None else "",
        "text": text if text is not None else "",
        "selector-type": selector_type if selector_type is not None else "css"
    }
    return create_step_from_template("input-to-web-element", params)

@mcp.tool()
def get_web_element_text(
    selector: str = None,
    variable: str = None,
    selector_type: str = None
) -> Dict[str, Any]:
    """Web要素のテキストを取得"""
    params = {
        "selector": selector if selector is not None else "",
        "variable": variable if variable is not None else "テキスト",
        "selector-type": selector_type if selector_type is not None else "css"
    }
    return create_step_from_template("get-web-element-text", params)

@mcp.tool()
def get_web_element_attribute(
    selector: str = None,
    attribute: str = None,
    variable: str = None,
    selector_type: str = None
) -> Dict[str, Any]:
    """Web要素の属性を取得"""
    params = {
        "selector": selector if selector is not None else "",
        "attribute": attribute if attribute is not None else "value",
        "variable": variable if variable is not None else "属性値",
        "selector-type": selector_type if selector_type is not None else "css"
    }
    return create_step_from_template("get-web-element-attribute", params)

@mcp.tool()
def wait_for_web_element(
    selector: str = None,
    timeout: int = None,
    selector_type: str = None
) -> Dict[str, Any]:
    """Web要素の出現を待つ"""
    params = {
        "selector": selector if selector is not None else "",
        "timeout": timeout if timeout is not None else 10,
        "selector-type": selector_type if selector_type is not None else "css"
    }
    return create_step_from_template("wait-for-web-element", params)

@mcp.tool()
def select_dropdown_option(
    selector: str = None,
    option_value: str = None,
    selector_type: str = None
) -> Dict[str, Any]:
    """ドロップダウンのオプションを選択"""
    params = {
        "selector": selector if selector is not None else "",
        "option-value": option_value if option_value is not None else "",
        "selector-type": selector_type if selector_type is not None else "css"
    }
    return create_step_from_template("select-dropdown-option", params)

@mcp.tool()
def submit_web_form(selector: str = None, selector_type: str = None) -> Dict[str, Any]:
    """フォームを送信"""
    params = {
        "selector": selector if selector is not None else "",
        "selector-type": selector_type if selector_type is not None else "css"
    }
    return create_step_from_template("submit-web-form", params)

@mcp.tool()
def take_browser_screenshot(
    file_path: str = None,
    full_page: bool = None
) -> Dict[str, Any]:
    """ブラウザのスクリーンショットを取得"""
    params = {
        "file-path": file_path if file_path is not None else "",
        "full-page": full_page if full_page is not None else False
    }
    return create_step_from_template("take-browser-screenshot", params)

@mcp.tool()
def execute_javascript(
    script: str = None,
    variable: str = None
) -> Dict[str, Any]:
    """JavaScriptを実行"""
    params = {
        "script": script if script is not None else "",
        "variable": variable if variable is not None else "結果"
    }
    return create_step_from_template("execute-javascript", params)

@mcp.tool()
def switch_browser_tab(tab_index: int = None) -> Dict[str, Any]:
    """ブラウザのタブを切り替え"""
    params = {
        "tab-index": tab_index if tab_index is not None else 0
    }
    return create_step_from_template("switch-browser-tab", params)

@mcp.tool()
def open_new_browser_tab(url: str = None) -> Dict[str, Any]:
    """新しいブラウザタブを開く"""
    params = {
        "url": url if url is not None else ""
    }
    return create_step_from_template("open-new-browser-tab", params)

@mcp.tool()
def close_browser_tab(tab_index: int = None) -> Dict[str, Any]:
    """ブラウザタブを閉じる"""
    params = {
        "tab-index": tab_index if tab_index is not None else -1
    }
    return create_step_from_template("close-browser-tab", params)

# =================================================
# メール操作
# =================================================

@mcp.tool()
def send_email(
    to: str = None,
    subject: str = None,
    body: str = None,
    cc: str = None,
    bcc: str = None,
    attachments: str = None
) -> Dict[str, Any]:
    """メールを送信"""
    params = {
        "to": to if to is not None else "",
        "subject": subject if subject is not None else "",
        "body": body if body is not None else "",
        "cc": cc if cc is not None else "",
        "bcc": bcc if bcc is not None else "",
        "attachments": attachments if attachments is not None else ""
    }
    return create_step_from_template("send-email", params)

@mcp.tool()
def receive_emails(
    folder: str = None,
    filter: str = None,
    variable: str = None
) -> Dict[str, Any]:
    """メールを受信"""
    params = {
        "folder": folder if folder is not None else "INBOX",
        "filter": filter if filter is not None else "",
        "variable": variable if variable is not None else "メール"
    }
    return create_step_from_template("receive-emails", params)

@mcp.tool()
def read_email(
    email_id: str = None,
    variable: str = None
) -> Dict[str, Any]:
    """メールを読む"""
    params = {
        "email-id": email_id if email_id is not None else "",
        "variable": variable if variable is not None else "メール内容"
    }
    return create_step_from_template("read-email", params)

@mcp.tool()
def delete_email(email_id: str = None) -> Dict[str, Any]:
    """メールを削除"""
    params = {
        "email-id": email_id if email_id is not None else ""
    }
    return create_step_from_template("delete-email", params)

@mcp.tool()
def move_email(
    email_id: str = None,
    target_folder: str = None
) -> Dict[str, Any]:
    """メールを移動"""
    params = {
        "email-id": email_id if email_id is not None else "",
        "target-folder": target_folder if target_folder is not None else ""
    }
    return create_step_from_template("move-email", params)

@mcp.tool()
def mark_email_as_read(email_id: str = None) -> Dict[str, Any]:
    """メールを既読にする"""
    params = {
        "email-id": email_id if email_id is not None else ""
    }
    return create_step_from_template("mark-email-as-read", params)

@mcp.tool()
def mark_email_as_unread(email_id: str = None) -> Dict[str, Any]:
    """メールを未読にする"""
    params = {
        "email-id": email_id if email_id is not None else ""
    }
    return create_step_from_template("mark-email-as-unread", params)

@mcp.tool()
def reply_to_email(
    email_id: str = None,
    body: str = None,
    reply_all: bool = None
) -> Dict[str, Any]:
    """メールに返信"""
    params = {
        "email-id": email_id if email_id is not None else "",
        "body": body if body is not None else "",
        "reply-all": reply_all if reply_all is not None else False
    }
    return create_step_from_template("reply-to-email", params)

@mcp.tool()
def forward_email(
    email_id: str = None,
    to: str = None,
    message: str = None
) -> Dict[str, Any]:
    """メールを転送"""
    params = {
        "email-id": email_id if email_id is not None else "",
        "to": to if to is not None else "",
        "message": message if message is not None else ""
    }
    return create_step_from_template("forward-email", params)

@mcp.tool()
def search_emails(
    query: str = None,
    variable: str = None
) -> Dict[str, Any]:
    """メールを検索"""
    params = {
        "query": query if query is not None else "",
        "variable": variable if variable is not None else "検索結果"
    }
    return create_step_from_template("search-emails", params)

# =================================================
# その他のツール
# =================================================

@mcp.tool()
def http_request(
    method: str = None,
    url: str = None,
    headers: str = None,
    body: str = None,
    variable: str = None
) -> Dict[str, Any]:
    """HTTPリクエストを送信"""
    params = {
        "method": method if method is not None else "GET",
        "url": url if url is not None else "",
        "headers": headers if headers is not None else "",
        "body": body if body is not None else "",
        "variable": variable if variable is not None else "レスポンス"
    }
    return create_step_from_template("http-request", params)

@mcp.tool()
def parse_json(
    json_string: str = None,
    variable: str = None
) -> Dict[str, Any]:
    """JSON文字列をパース"""
    params = {
        "json-string": json_string if json_string is not None else "",
        "variable": variable if variable is not None else "JSONデータ"
    }
    return create_step_from_template("parse-json", params)

@mcp.tool()
def stringify_json(
    object: str = None,
    variable: str = None
) -> Dict[str, Any]:
    """オブジェクトをJSON文字列に変換"""
    params = {
        "object": object if object is not None else "",
        "variable": variable if variable is not None else "JSON文字列"
    }
    return create_step_from_template("stringify-json", params)

@mcp.tool()
def encode_base64(
    text: str = None,
    variable: str = None
) -> Dict[str, Any]:
    """Base64エンコード"""
    params = {
        "text": text if text is not None else "",
        "variable": variable if variable is not None else "エンコード結果"
    }
    return create_step_from_template("encode-base64", params)

@mcp.tool()
def decode_base64(
    encoded_text: str = None,
    variable: str = None
) -> Dict[str, Any]:
    """Base64デコード"""
    params = {
        "encoded-text": encoded_text if encoded_text is not None else "",
        "variable": variable if variable is not None else "デコード結果"
    }
    return create_step_from_template("decode-base64", params)

@mcp.tool()
def generate_uuid(variable: str = None) -> Dict[str, Any]:
    """UUIDを生成"""
    params = {
        "variable": variable if variable is not None else "UUID"
    }
    return create_step_from_template("generate-uuid", params)

@mcp.tool()
def system_command(
    command: str = None,
    arguments: str = None,
    variable: str = None
) -> Dict[str, Any]:
    """システムコマンドを実行"""
    params = {
        "command": command if command is not None else "",
        "arguments": arguments if arguments is not None else "",
        "variable": variable if variable is not None else "出力"
    }
    return create_step_from_template("system-command", params)

# =================================================
# 残りのツール（HTML操作、Excel詳細操作など）
# =================================================

@mcp.tool()
def add_memo() -> Dict[str, Any]:
    """メモを追加"""
    return create_step_from_template("add-memo", {})

@mcp.tool()
def api_web(
    method: str = None,
    services: str = None,
    url: str = None,
    queries: str = None,
    headers: str = None,
    body: str = None,
    form_data: str = None,
    raw: str = None,
    json: str = None,
    timeout: int = None,
    res_status: str = None,
    res_headers: str = None,
    res_data: str = None,
    res_content_type: str = None
) -> Dict[str, Any]:
    """Web APIを呼び出す"""
    params = {
        "method": method if method is not None else "GET",
        "services": services if services is not None else "",
        "url": url if url is not None else "",
        "queries": queries if queries is not None else "",
        "headers": headers if headers is not None else "",
        "body": body if body is not None else "",
        "form-data": form_data if form_data is not None else "",
        "raw": raw if raw is not None else "",
        "json": json if json is not None else "",
        "timeout": timeout if timeout is not None else 30,
        "res-status": res_status if res_status is not None else "",
        "res-headers": res_headers if res_headers is not None else "",
        "res-data": res_data if res_data is not None else "",
        "res-content-type": res_content_type if res_content_type is not None else ""
    }
    return create_step_from_template("api-web", params)

@mcp.tool()
def calculate_excel_column(
    base_column: str = None,
    operator: str = None,
    amount: int = None,
    variable: str = None
) -> Dict[str, Any]:
    """Excelの列を計算"""
    params = {
        "base-column": base_column if base_column is not None else "A",
        "operator": operator if operator is not None else "+",
        "amount": amount if amount is not None else 1,
        "variable": variable if variable is not None else "計算結果"
    }
    return create_step_from_template("calculate-excel-column", params)

@mcp.tool()
def check_html_checkbox_or_radiobutton(
    browser: str = None,
    selector_type: str = None,
    selector: str = None
) -> Dict[str, Any]:
    """HTMLチェックボックスまたはラジオボタンを確認"""
    params = {
        "browser": browser if browser is not None else "",
        "selector-type": selector_type if selector_type is not None else "css",
        "selector": selector if selector is not None else ""
    }
    return create_step_from_template("check-html-checkbox-or-radiobutton", params)

@mcp.tool()
def check_json_type(
    json_data: str = None,
    key: str = None,
    expected_type: str = None,
    variable: str = None
) -> Dict[str, Any]:
    """JSONの型をチェック"""
    params = {
        "json-data": json_data if json_data is not None else "",
        "key": key if key is not None else "",
        "expected-type": expected_type if expected_type is not None else "string",
        "variable": variable if variable is not None else "型チェック結果"
    }
    return create_step_from_template("check-json-type", params)

@mcp.tool()
def click_html_alert(browser: str = None) -> Dict[str, Any]:
    """HTMLアラートをクリック"""
    params = {
        "browser": browser if browser is not None else ""
    }
    return create_step_from_template("click-html-alert", params)

@mcp.tool()
def click_html_element(
    browser: str = None,
    selector_type: str = None,
    selector: str = None
) -> Dict[str, Any]:
    """HTML要素をクリック"""
    params = {
        "browser": browser if browser is not None else "",
        "selector-type": selector_type if selector_type is not None else "css",
        "selector": selector if selector is not None else ""
    }
    return create_step_from_template("click-html-element", params)

@mcp.tool()
def click_uia_element(
    element_name: str = None,
    element_type: str = None
) -> Dict[str, Any]:
    """UIA要素をクリック"""
    params = {
        "element-name": element_name if element_name is not None else "",
        "element-type": element_type if element_type is not None else ""
    }
    return create_step_from_template("click-uia-element", params)

@mcp.tool()
def close_excel_book(book_name: str = None) -> Dict[str, Any]:
    """Excelブックを閉じる"""
    params = {
        "book-name": book_name if book_name is not None else ""
    }
    return create_step_from_template("close-excel-book", params)

@mcp.tool()
def delete_excel_range(
    sheet_name: str = None,
    range: str = None
) -> Dict[str, Any]:
    """Excelの範囲を削除"""
    params = {
        "sheet-name": sheet_name if sheet_name is not None else "",
        "range": range if range is not None else ""
    }
    return create_step_from_template("delete-excel-range", params)

@mcp.tool()
def delete_spreadsheet(spreadsheet: str = None) -> Dict[str, Any]:
    """スプレッドシートを削除"""
    params = {
        "spreadsheet": spreadsheet if spreadsheet is not None else ""
    }
    return create_step_from_template("delete-spreadsheet", params)

@mcp.tool()
def download_html_csv(
    browser: str = None,
    url: str = None,
    file_path: str = None
) -> Dict[str, Any]:
    """HTMLからCSVをダウンロード"""
    params = {
        "browser": browser if browser is not None else "",
        "url": url if url is not None else "",
        "file-path": file_path if file_path is not None else ""
    }
    return create_step_from_template("download-html-csv", params)

@mcp.tool()
def download_html_element(
    browser: str = None,
    selector_type: str = None,
    selector: str = None,
    file_path: str = None
) -> Dict[str, Any]:
    """HTML要素をダウンロード"""
    params = {
        "browser": browser if browser is not None else "",
        "selector-type": selector_type if selector_type is not None else "css",
        "selector": selector if selector is not None else "",
        "file-path": file_path if file_path is not None else ""
    }
    return create_step_from_template("download-html-element", params)

@mcp.tool()
def escape_html_iframe(browser: str = None) -> Dict[str, Any]:
    """HTMLのiframeから脱出"""
    params = {
        "browser": browser if browser is not None else ""
    }
    return create_step_from_template("escape-html-iframe", params)

@mcp.tool()
def focus_html_element(
    browser: str = None,
    selector_type: str = None,
    selector: str = None
) -> Dict[str, Any]:
    """HTML要素にフォーカス"""
    params = {
        "browser": browser if browser is not None else "",
        "selector-type": selector_type if selector_type is not None else "css",
        "selector": selector if selector is not None else ""
    }
    return create_step_from_template("focus-html-element", params)

@mcp.tool()
def get_excel_address(
    row: int = None,
    column: str = None,
    variable: str = None
) -> Dict[str, Any]:
    """Excelのアドレスを取得"""
    params = {
        "row": row if row is not None else 1,
        "column": column if column is not None else "A",
        "variable": variable if variable is not None else "アドレス"
    }
    return create_step_from_template("get-excel-address", params)

@mcp.tool()
def get_excel_last_column(
    sheet_name: str = None,
    row: int = None,
    variable: str = None
) -> Dict[str, Any]:
    """Excelの最終列を取得"""
    params = {
        "sheet-name": sheet_name if sheet_name is not None else "",
        "row": row if row is not None else 1,
        "variable": variable if variable is not None else "最終列"
    }
    return create_step_from_template("get-excel-last-column", params)

@mcp.tool()
def get_excel_last_row(
    sheet_name: str = None,
    column: str = None,
    variable: str = None
) -> Dict[str, Any]:
    """Excelの最終行を取得"""
    params = {
        "sheet-name": sheet_name if sheet_name is not None else "",
        "column": column if column is not None else "A",
        "variable": variable if variable is not None else "最終行"
    }
    return create_step_from_template("get-excel-last-row", params)

@mcp.tool()
def get_excel_sheet_name(
    index: int = None,
    variable: str = None
) -> Dict[str, Any]:
    """Excelのシート名を取得"""
    params = {
        "index": index if index is not None else 0,
        "variable": variable if variable is not None else "シート名"
    }
    return create_step_from_template("get-excel-sheet-name", params)

@mcp.tool()
def get_excel_values(
    sheet_name: str = None,
    range: str = None,
    variable: str = None
) -> Dict[str, Any]:
    """Excelの値を取得"""
    params = {
        "sheet-name": sheet_name if sheet_name is not None else "",
        "range": range if range is not None else "",
        "variable": variable if variable is not None else "値"
    }
    return create_step_from_template("get-excel-values", params)

@mcp.tool()
def get_json_values(
    json_data: str = None,
    path: str = None,
    variable: str = None
) -> Dict[str, Any]:
    """JSONの値を取得"""
    params = {
        "json-data": json_data if json_data is not None else "",
        "path": path if path is not None else "",
        "variable": variable if variable is not None else "JSON値"
    }
    return create_step_from_template("get-json-values", params)

@mcp.tool()
def get_spreadsheet_last_row(
    spreadsheet: str = None,
    sheet_name: str = None,
    column: str = None,
    variable: str = None
) -> Dict[str, Any]:
    """スプレッドシートの最終行を取得"""
    params = {
        "spreadsheet": spreadsheet if spreadsheet is not None else "",
        "sheet-name": sheet_name if sheet_name is not None else "",
        "column": column if column is not None else "A",
        "variable": variable if variable is not None else "最終行"
    }
    return create_step_from_template("get-spreadsheet-last-row", params)

@mcp.tool()
def get_spreadsheet_url(
    spreadsheet: str = None,
    variable: str = None
) -> Dict[str, Any]:
    """スプレッドシートのURLを取得"""
    params = {
        "spreadsheet": spreadsheet if spreadsheet is not None else "",
        "variable": variable if variable is not None else "URL"
    }
    return create_step_from_template("get-spreadsheet-url", params)

@mcp.tool()
def get_text_from_uia_element(
    element_name: str = None,
    element_type: str = None,
    variable: str = None
) -> Dict[str, Any]:
    """UIA要素からテキストを取得"""
    params = {
        "element-name": element_name if element_name is not None else "",
        "element-type": element_type if element_type is not None else "",
        "variable": variable if variable is not None else "テキスト"
    }
    return create_step_from_template("get-text-from-uia-element", params)

@mcp.tool()
def get_uia_element_clickable_point(
    element_name: str = None,
    element_type: str = None,
    x_variable: str = None,
    y_variable: str = None
) -> Dict[str, Any]:
    """UIA要素のクリック可能ポイントを取得"""
    params = {
        "element-name": element_name if element_name is not None else "",
        "element-type": element_type if element_type is not None else "",
        "x-variable": x_variable if x_variable is not None else "X座標",
        "y-variable": y_variable if y_variable is not None else "Y座標"
    }
    return create_step_from_template("get-uia-element-clickable-point", params)

@mcp.tool()
def group_commands(commands: str = None) -> Dict[str, Any]:
    """コマンドをグループ化"""
    params = {
        "commands": commands if commands is not None else ""
    }
    return create_step_from_template("group-commands", params)

@mcp.tool()
def inherit_browsers() -> Dict[str, Any]:
    """ブラウザを継承"""
    return create_step_from_template("inherit-browsers", {})

@mcp.tool()
def inherit_excel() -> Dict[str, Any]:
    """Excelを継承"""
    return create_step_from_template("inherit-excel", {})

@mcp.tool()
def inherit_passwords() -> Dict[str, Any]:
    """パスワードを継承"""
    return create_step_from_template("inherit-passwords", {})

@mcp.tool()
def inherit_variables() -> Dict[str, Any]:
    """変数を継承"""
    return create_step_from_template("inherit-variables", {})

@mcp.tool()
def inherit_windows() -> Dict[str, Any]:
    """ウィンドウを継承"""
    return create_step_from_template("inherit-windows", {})

@mcp.tool()
def insert_excel_range(
    sheet_name: str = None,
    range: str = None,
    shift: str = None
) -> Dict[str, Any]:
    """Excelの範囲に挿入"""
    params = {
        "sheet-name": sheet_name if sheet_name is not None else "",
        "range": range if range is not None else "",
        "shift": shift if shift is not None else "down"
    }
    return create_step_from_template("insert-excel-range", params)

@mcp.tool()
def loop_csv(
    file_path: str = None,
    encoding: str = None,
    delimiter: str = None,
    variable: str = None
) -> Dict[str, Any]:
    """CSVファイルをループ処理"""
    params = {
        "file-path": file_path if file_path is not None else "",
        "encoding": encoding if encoding is not None else "utf-8",
        "delimiter": delimiter if delimiter is not None else ",",
        "variable": variable if variable is not None else "行データ"
    }
    return create_step_from_template("loop-csv", params)

@mcp.tool()
def loop_excel_col(
    sheet_name: str = None,
    start_column: str = None,
    end_column: str = None,
    row: int = None,
    variable: str = None
) -> Dict[str, Any]:
    """Excelの列をループ処理"""
    params = {
        "sheet-name": sheet_name if sheet_name is not None else "",
        "start-column": start_column if start_column is not None else "A",
        "end-column": end_column if end_column is not None else "Z",
        "row": row if row is not None else 1,
        "variable": variable if variable is not None else "列データ"
    }
    return create_step_from_template("loop-excel-col", params)

@mcp.tool()
def loop_excel_row(
    sheet_name: str = None,
    start_row: int = None,
    end_row: int = None,
    column: str = None,
    variable: str = None
) -> Dict[str, Any]:
    """Excelの行をループ処理"""
    params = {
        "sheet-name": sheet_name if sheet_name is not None else "",
        "start-row": start_row if start_row is not None else 1,
        "end-row": end_row if end_row is not None else 100,
        "column": column if column is not None else "A",
        "variable": variable if variable is not None else "行データ"
    }
    return create_step_from_template("loop-excel-row", params)

@mcp.tool()
def loop_spreadsheet_col(
    spreadsheet: str = None,
    sheet_name: str = None,
    start_column: str = None,
    end_column: str = None,
    row: int = None,
    variable: str = None
) -> Dict[str, Any]:
    """スプレッドシートの列をループ処理"""
    params = {
        "spreadsheet": spreadsheet if spreadsheet is not None else "",
        "sheet-name": sheet_name if sheet_name is not None else "",
        "start-column": start_column if start_column is not None else "A",
        "end-column": end_column if end_column is not None else "Z",
        "row": row if row is not None else 1,
        "variable": variable if variable is not None else "列データ"
    }
    return create_step_from_template("loop-spreadsheet-col", params)

@mcp.tool()
def loop_spreadsheet_row(
    spreadsheet: str = None,
    sheet_name: str = None,
    start_row: int = None,
    end_row: int = None,
    column: str = None,
    variable: str = None
) -> Dict[str, Any]:
    """スプレッドシートの行をループ処理"""
    params = {
        "spreadsheet": spreadsheet if spreadsheet is not None else "",
        "sheet-name": sheet_name if sheet_name is not None else "",
        "start-row": start_row if start_row is not None else 1,
        "end-row": end_row if end_row is not None else 100,
        "column": column if column is not None else "A",
        "variable": variable if variable is not None else "行データ"
    }
    return create_step_from_template("loop-spreadsheet-row", params)

@mcp.tool()
def move_excel_sheet(
    sheet_name: str = None,
    position: int = None
) -> Dict[str, Any]:
    """Excelのシートを移動"""
    params = {
        "sheet-name": sheet_name if sheet_name is not None else "",
        "position": position if position is not None else 0
    }
    return create_step_from_template("move-excel-sheet", params)

@mcp.tool()
def offset_excel_range(
    range: str = None,
    row_offset: int = None,
    column_offset: int = None,
    variable: str = None
) -> Dict[str, Any]:
    """Excelの範囲をオフセット"""
    params = {
        "range": range if range is not None else "",
        "row-offset": row_offset if row_offset is not None else 0,
        "column-offset": column_offset if column_offset is not None else 0,
        "variable": variable if variable is not None else "オフセット範囲"
    }
    return create_step_from_template("offset-excel-range", params)

@mcp.tool()
def play_sound(
    sound_file: str = None,
    volume: int = None
) -> Dict[str, Any]:
    """音声を再生"""
    params = {
        "sound-file": sound_file if sound_file is not None else "",
        "volume": volume if volume is not None else 100
    }
    return create_step_from_template("play-sound", params)

@mcp.tool()
def receive_emails_gmail(
    folder: str = None,
    filter: str = None,
    variable: str = None
) -> Dict[str, Any]:
    """Gmailからメールを受信"""
    params = {
        "folder": folder if folder is not None else "INBOX",
        "filter": filter if filter is not None else "",
        "variable": variable if variable is not None else "メール"
    }
    return create_step_from_template("receive-emails-gmail", params)

@mcp.tool()
def receive_emails_microsoft(
    folder: str = None,
    filter: str = None,
    variable: str = None
) -> Dict[str, Any]:
    """Microsoftからメールを受信"""
    params = {
        "folder": folder if folder is not None else "INBOX",
        "filter": filter if filter is not None else "",
        "variable": variable if variable is not None else "メール"
    }
    return create_step_from_template("receive-emails-microsoft", params)

@mcp.tool()
def remember_focused_browser_window(variable: str = None) -> Dict[str, Any]:
    """フォーカスされたブラウザウィンドウを記憶"""
    params = {
        "variable": variable if variable is not None else "ブラウザウィンドウ"
    }
    return create_step_from_template("remember-focused-browser-window", params)

@mcp.tool()
def remember_open_excel_book(variable: str = None) -> Dict[str, Any]:
    """開いているExcelブックを記憶"""
    params = {
        "variable": variable if variable is not None else "Excelブック"
    }
    return create_step_from_template("remember-open-excel-book", params)

@mcp.tool()
def remember_spreadsheet(
    spreadsheet: str = None,
    variable: str = None
) -> Dict[str, Any]:
    """スプレッドシートを記憶"""
    params = {
        "spreadsheet": spreadsheet if spreadsheet is not None else "",
        "variable": variable if variable is not None else "スプレッドシート"
    }
    return create_step_from_template("remember-spreadsheet", params)

@mcp.tool()
def rename_spreadsheet(
    spreadsheet: str = None,
    new_name: str = None
) -> Dict[str, Any]:
    """スプレッドシートの名前を変更"""
    params = {
        "spreadsheet": spreadsheet if spreadsheet is not None else "",
        "new-name": new_name if new_name is not None else ""
    }
    return create_step_from_template("rename-spreadsheet", params)

@mcp.tool()
def retrieve_attribute_of_html_element(
    browser: str = None,
    selector_type: str = None,
    selector: str = None,
    attribute: str = None,
    variable: str = None
) -> Dict[str, Any]:
    """HTML要素の属性を取得"""
    params = {
        "browser": browser if browser is not None else "",
        "selector-type": selector_type if selector_type is not None else "css",
        "selector": selector if selector is not None else "",
        "attribute": attribute if attribute is not None else "",
        "variable": variable if variable is not None else "属性値"
    }
    return create_step_from_template("retrieve-attribute-of-html-element", params)

@mcp.tool()
def retrieve_link_of_html_element(
    browser: str = None,
    selector_type: str = None,
    selector: str = None,
    variable: str = None
) -> Dict[str, Any]:
    """HTML要素のリンクを取得"""
    params = {
        "browser": browser if browser is not None else "",
        "selector-type": selector_type if selector_type is not None else "css",
        "selector": selector if selector is not None else "",
        "variable": variable if variable is not None else "リンク"
    }
    return create_step_from_template("retrieve-link-of-html-element", params)

@mcp.tool()
def retrieve_src_of_html_element(
    browser: str = None,
    selector_type: str = None,
    selector: str = None,
    variable: str = None
) -> Dict[str, Any]:
    """HTML要素のsrcを取得"""
    params = {
        "browser": browser if browser is not None else "",
        "selector-type": selector_type if selector_type is not None else "css",
        "selector": selector if selector is not None else "",
        "variable": variable if variable is not None else "src"
    }
    return create_step_from_template("retrieve-src-of-html-element", params)

@mcp.tool()
def retrieve_text_of_html_alert(
    browser: str = None,
    variable: str = None
) -> Dict[str, Any]:
    """HTMLアラートのテキストを取得"""
    params = {
        "browser": browser if browser is not None else "",
        "variable": variable if variable is not None else "アラートテキスト"
    }
    return create_step_from_template("retrieve-text-of-html-alert", params)

@mcp.tool()
def retrieve_text_of_html_element(
    browser: str = None,
    selector_type: str = None,
    selector: str = None,
    variable: str = None
) -> Dict[str, Any]:
    """HTML要素のテキストを取得"""
    params = {
        "browser": browser if browser is not None else "",
        "selector-type": selector_type if selector_type is not None else "css",
        "selector": selector if selector is not None else "",
        "variable": variable if variable is not None else "テキスト"
    }
    return create_step_from_template("retrieve-text-of-html-element", params)

@mcp.tool()
def run_browser(
    browser_type: str = None,
    url: str = None
) -> Dict[str, Any]:
    """ブラウザを起動"""
    params = {
        "browser-type": browser_type if browser_type is not None else "chrome",
        "url": url if url is not None else ""
    }
    return create_step_from_template("run-browser", params)

@mcp.tool()
def run_browser_with_profile(
    browser_type: str = None,
    profile_name: str = None,
    url: str = None
) -> Dict[str, Any]:
    """プロファイル付きでブラウザを起動"""
    params = {
        "browser-type": browser_type if browser_type is not None else "chrome",
        "profile-name": profile_name if profile_name is not None else "",
        "url": url if url is not None else ""
    }
    return create_step_from_template("run-browser-with-profile", params)

@mcp.tool()
def run_excel(file_path: str = None) -> Dict[str, Any]:
    """Excelを起動"""
    params = {
        "file-path": file_path if file_path is not None else ""
    }
    return create_step_from_template("run-excel", params)

@mcp.tool()
def run_excel_macro(
    macro_name: str = None,
    arguments: str = None
) -> Dict[str, Any]:
    """Excelマクロを実行"""
    params = {
        "macro-name": macro_name if macro_name is not None else "",
        "arguments": arguments if arguments is not None else ""
    }
    return create_step_from_template("run-excel-macro", params)

@mcp.tool()
def run_external_scenario_and_branch(
    scenario_path: str = None,
    parameters: str = None
) -> Dict[str, Any]:
    """外部シナリオを実行して分岐"""
    params = {
        "scenario-path": scenario_path if scenario_path is not None else "",
        "parameters": parameters if parameters is not None else ""
    }
    return create_step_from_template("run-external-scenario-and-branch", params)

@mcp.tool()
def run_javascript_in_browser(
    browser: str = None,
    script: str = None,
    variable: str = None
) -> Dict[str, Any]:
    """ブラウザでJavaScriptを実行"""
    params = {
        "browser": browser if browser is not None else "",
        "script": script if script is not None else "",
        "variable": variable if variable is not None else "実行結果"
    }
    return create_step_from_template("run-javascript-in-browser", params)

@mcp.tool()
def save_excel_book(
    file_path: str = None,
    format: str = None
) -> Dict[str, Any]:
    """Excelブックを保存"""
    params = {
        "file-path": file_path if file_path is not None else "",
        "format": format if format is not None else "xlsx"
    }
    return create_step_from_template("save-excel-book", params)

@mcp.tool()
def search_html_element_and_branch(
    browser: str = None,
    selector_type: str = None,
    selector: str = None
) -> Dict[str, Any]:
    """HTML要素を検索して分岐"""
    params = {
        "browser": browser if browser is not None else "",
        "selector-type": selector_type if selector_type is not None else "css",
        "selector": selector if selector is not None else ""
    }
    return create_step_from_template("search-html-element-and-branch", params)

@mcp.tool()
def select_excel_range(
    sheet_name: str = None,
    range: str = None
) -> Dict[str, Any]:
    """Excelの範囲を選択"""
    params = {
        "sheet-name": sheet_name if sheet_name is not None else "",
        "range": range if range is not None else ""
    }
    return create_step_from_template("select-excel-range", params)

@mcp.tool()
def send_email_gmail(
    to: str = None,
    subject: str = None,
    body: str = None,
    cc: str = None,
    bcc: str = None,
    attachments: str = None
) -> Dict[str, Any]:
    """Gmailでメールを送信"""
    params = {
        "to": to if to is not None else "",
        "subject": subject if subject is not None else "",
        "body": body if body is not None else "",
        "cc": cc if cc is not None else "",
        "bcc": bcc if bcc is not None else "",
        "attachments": attachments if attachments is not None else ""
    }
    return create_step_from_template("send-email-gmail", params)

@mcp.tool()
def send_email_microsoft(
    to: str = None,
    subject: str = None,
    body: str = None,
    cc: str = None,
    bcc: str = None,
    attachments: str = None
) -> Dict[str, Any]:
    """Microsoftでメールを送信"""
    params = {
        "to": to if to is not None else "",
        "subject": subject if subject is not None else "",
        "body": body if body is not None else "",
        "cc": cc if cc is not None else "",
        "bcc": bcc if bcc is not None else "",
        "attachments": attachments if attachments is not None else ""
    }
    return create_step_from_template("send-email-microsoft", params)

@mcp.tool()
def send_password_to_html_element(
    browser: str = None,
    selector_type: str = None,
    selector: str = None,
    password: str = None
) -> Dict[str, Any]:
    """HTML要素にパスワードを送信"""
    params = {
        "browser": browser if browser is not None else "",
        "selector-type": selector_type if selector_type is not None else "css",
        "selector": selector if selector is not None else "",
        "password": password if password is not None else ""
    }
    return create_step_from_template("send-password-to-html-element", params)

@mcp.tool()
def send_password_to_uia_element(
    element_name: str = None,
    element_type: str = None,
    password: str = None
) -> Dict[str, Any]:
    """UIA要素にパスワードを送信"""
    params = {
        "element-name": element_name if element_name is not None else "",
        "element-type": element_type if element_type is not None else "",
        "password": password if password is not None else ""
    }
    return create_step_from_template("send-password-to-uia-element", params)

@mcp.tool()
def send_text_to_html_element(
    browser: str = None,
    selector_type: str = None,
    selector: str = None,
    text: str = None
) -> Dict[str, Any]:
    """HTML要素にテキストを送信"""
    params = {
        "browser": browser if browser is not None else "",
        "selector-type": selector_type if selector_type is not None else "css",
        "selector": selector if selector is not None else "",
        "text": text if text is not None else ""
    }
    return create_step_from_template("send-text-to-html-element", params)

@mcp.tool()
def send_text_to_uia_element(
    element_name: str = None,
    element_type: str = None,
    text: str = None
) -> Dict[str, Any]:
    """UIA要素にテキストを送信"""
    params = {
        "element-name": element_name if element_name is not None else "",
        "element-type": element_type if element_type is not None else "",
        "text": text if text is not None else ""
    }
    return create_step_from_template("send-text-to-uia-element", params)

@mcp.tool()
def set_browser_cookie(
    browser: str = None,
    name: str = None,
    value: str = None,
    domain: str = None,
    path: str = None
) -> Dict[str, Any]:
    """ブラウザのクッキーを設定"""
    params = {
        "browser": browser if browser is not None else "",
        "name": name if name is not None else "",
        "value": value if value is not None else "",
        "domain": domain if domain is not None else "",
        "path": path if path is not None else "/"
    }
    return create_step_from_template("set-browser-cookie", params)

@mcp.tool()
def set_dropdown_html_element(
    browser: str = None,
    selector_type: str = None,
    selector: str = None,
    value: str = None
) -> Dict[str, Any]:
    """HTMLドロップダウンの値を設定"""
    params = {
        "browser": browser if browser is not None else "",
        "selector-type": selector_type if selector_type is not None else "css",
        "selector": selector if selector is not None else "",
        "value": value if value is not None else ""
    }
    return create_step_from_template("set-dropdown-html-element", params)

@mcp.tool()
def set_excel_values(
    sheet_name: str = None,
    range: str = None,
    values: str = None
) -> Dict[str, Any]:
    """Excelの値を設定"""
    params = {
        "sheet-name": sheet_name if sheet_name is not None else "",
        "range": range if range is not None else "",
        "values": values if values is not None else ""
    }
    return create_step_from_template("set-excel-values", params)

@mcp.tool()
def switch_excel_sheet(sheet_name: str = None) -> Dict[str, Any]:
    """Excelのシートを切り替え"""
    params = {
        "sheet-name": sheet_name if sheet_name is not None else ""
    }
    return create_step_from_template("switch-excel-sheet", params)

@mcp.tool()
def switch_html_iframe(
    browser: str = None,
    selector_type: str = None,
    selector: str = None
) -> Dict[str, Any]:
    """HTMLのiframeに切り替え"""
    params = {
        "browser": browser if browser is not None else "",
        "selector-type": selector_type if selector_type is not None else "css",
        "selector": selector if selector is not None else ""
    }
    return create_step_from_template("switch-html-iframe", params)

@mcp.tool()
def type_html_hotkeys(
    browser: str = None,
    keys: str = None
) -> Dict[str, Any]:
    """HTMLでホットキーを入力"""
    params = {
        "browser": browser if browser is not None else "",
        "keys": keys if keys is not None else ""
    }
    return create_step_from_template("type-html-hotkeys", params)

@mcp.tool()
def visit_url(
    browser: str = None,
    url: str = None
) -> Dict[str, Any]:
    """URLを訪問"""
    params = {
        "browser": browser if browser is not None else "",
        "url": url if url is not None else ""
    }
    return create_step_from_template("visit-url", params)

@mcp.tool()
def visit_url_with_basic_auth(
    browser: str = None,
    url: str = None,
    username: str = None,
    password: str = None
) -> Dict[str, Any]:
    """Basic認証付きでURLを訪問"""
    params = {
        "browser": browser if browser is not None else "",
        "url": url if url is not None else "",
        "username": username if username is not None else "",
        "password": password if password is not None else ""
    }
    return create_step_from_template("visit-url-with-basic-auth", params)

# FastMCPを実行
if __name__ == "__main__":
    import sys
    if "--http" in sys.argv:
        mcp.run(transport="http", port=8080)
    else:
        mcp.run(transport="stdio")