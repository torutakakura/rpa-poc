from fastmcp import FastMCP
import json
from typing import Optional, Dict, Any, List
import uuid
from pathlib import Path

mcp = FastMCP("RPA Operations Tool")

# rpa_operations.jsonのパスを設定
RPA_OPERATIONS_PATH = Path(__file__).parent.parent / "rpa-agent" / "rpa_operations.json"

# 起動時にJSONファイルを読み込み
def load_rpa_operations():
    """rpa_operations.jsonを読み込む"""
    try:
        with open(RPA_OPERATIONS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {RPA_OPERATIONS_PATH} not found")
        return {"operation_templates": {}}
    except Exception as e:
        print(f"Error loading rpa_operations.json: {e}")
        return {"operation_templates": {}}

# グローバル変数として操作定義を保持
RPA_OPERATIONS = load_rpa_operations()

# RPAステップのベースモデル
def create_rpa_step(
    category: str,
    operation: str,
    params: Dict[str, Any],
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """RPAステップの共通フォーマットを生成"""
    if not step_id:
        step_id = f"step-{uuid.uuid4().hex[:8]}"

    return {
        "id": step_id,
        "category": category,
        "operation": operation,
        "params": params,
        "description": description or f"{operation}を実行"
    }

def get_operation_template(category: str, subcategory: str, operation: str) -> Dict[str, Any]:
    """rpa_operations.jsonから操作テンプレートを取得"""
    templates = RPA_OPERATIONS.get("operation_templates", {})

    # カテゴリをチェック
    if category not in templates:
        return None

    category_data = templates[category]

    # サブカテゴリがある場合
    if subcategory and subcategory in category_data:
        if operation in category_data[subcategory]:
            return category_data[subcategory][operation]

    # サブカテゴリがない場合、直接操作を探す
    if operation in category_data:
        return category_data[operation]

    # すべてのサブカテゴリを検索
    for _, operations in category_data.items():
        if isinstance(operations, dict) and operation in operations:
            return operations[operation]

    return None

def merge_params_with_template(template_params: Dict, provided_params: Dict) -> Dict[str, Any]:
    """テンプレートのパラメータと提供されたパラメータをマージ"""
    result = {}

    # common_paramsをマージ
    if "common_params" in template_params:
        result.update(template_params["common_params"])

    # specific_paramsをマージ
    if "specific_params" in template_params:
        result.update(template_params["specific_params"])

    # 提供されたパラメータで上書き
    result.update(provided_params)

    return result

def create_rpa_step_from_template(
    category: str,
    operation: str,
    params: Dict[str, Any],
    subcategory: str = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """テンプレートを使用してRPAステップを生成"""
    # テンプレートを取得
    template = get_operation_template(category, subcategory, operation)

    if template:
        # テンプレートのパラメータをコピー
        template_params = {}
        if "specific_params" in template:
            template_params = template["specific_params"].copy()

        # 提供されたパラメータで上書き
        for key, value in params.items():
            template_params[key] = value

        params = template_params

    return create_rpa_step(
        category=category,
        operation=operation,
        params=params,
        step_id=step_id,
        description=description
    )

# ====================
# A_アプリ・画面
# ====================

# アプリ
@mcp.tool()
def app_launch(
    path: str,
    arguments: Optional[str] = None,
    interval: Optional[int] = None,
    maximized: Optional[bool] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """アプリケーションを起動"""
    params = {"path": path}
    if arguments is not None:
        params["arguments"] = arguments
    if interval is not None:
        params["interval"] = interval
    if maximized is not None:
        params["maximized"] = maximized

    return create_rpa_step_from_template(
        category="A_アプリ・画面",
        operation="起動",
        params=params,
        subcategory="アプリ",
        step_id=step_id,
        description=description or f"{path}を起動"
    )

@mcp.tool()
def app_launch_wait(
    path: str,
    arguments: Optional[str] = None,
    timeout: Optional[int] = None,
    output_variable: Optional[str] = None,
    error_variable: Optional[str] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """アプリケーションを起動して終了を待つ"""
    params = {"path": path}
    if arguments is not None:
        params["arguments"] = arguments
    if timeout is not None:
        params["timeout"] = timeout
    if output_variable is not None:
        params["output_variable"] = output_variable
    if error_variable is not None:
        params["error_variable"] = error_variable

    return create_rpa_step_from_template(
        category="A_アプリ・画面",
        operation="起動（終了待ち）",
        params=params,
        subcategory="アプリ",
        step_id=step_id,
        description=description or f"{path}を起動して終了を待つ"
    )

# 画面
@mcp.tool()
def window_remember_active(
    variable: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """最前面のウィンドウを記憶"""
    return create_rpa_step_from_template(
        category="A_アプリ・画面",
        operation="最前画面を覚える",
        params={"variable": variable},
        subcategory="画面",
        step_id=step_id,
        description=description or "最前面のウィンドウを記憶"
    )

@mcp.tool()
def window_remember_by_name(
    window_name: str,
    variable: str,
    match_type: Optional[str] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ウィンドウ名でウィンドウを記憶"""
    params = {
        "window_name": window_name,
        "variable": variable
    }
    if match_type is not None:
        params["match_type"] = match_type

    return create_rpa_step_from_template(
        category="A_アプリ・画面",
        operation="画面を覚える（名前）",
        params=params,
        subcategory="画面",
        step_id=step_id,
        description=description or f"{window_name}を記憶"
    )

@mcp.tool()
def window_switch_by_ref(
    variable: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """参照IDでウィンドウを切り替え"""
    return create_rpa_step_from_template(
        category="A_アプリ・画面",
        operation="切り替え（参照ID）",
        params={"variable": variable},
        subcategory="画面",
        step_id=step_id,
        description=description or f"ウィンドウ{variable}に切り替え"
    )

@mcp.tool()
def window_switch_by_name(
    string: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ウィンドウ名でウィンドウを切り替え"""
    return create_rpa_step_from_template(
        category="A_アプリ・画面",
        operation="切り替え（名前）",
        params={"string": string},
        subcategory="画面",
        step_id=step_id,
        description=description or f"{string}に切り替え"
    )

@mcp.tool()
def window_get_name(
    variable: str,
    window: Optional[str] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ウィンドウ名を取得"""
    params = {"variable": variable}
    if window is not None:
        params["window"] = window

    return create_rpa_step_from_template(
        category="A_アプリ・画面",
        operation="画面の名前を取得",
        params=params,
        subcategory="画面",
        step_id=step_id,
        description=description or "ウィンドウ名を取得"
    )

@mcp.tool()
def window_move(
    x: int,
    y: int,
    width: int,
    height: int,
    window: Optional[str] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ウィンドウを移動・リサイズ"""
    params = {
        "x": x,
        "y": y,
        "width": width,
        "height": height
    }
    if window is not None:
        params["window"] = window

    return create_rpa_step_from_template(
        category="A_アプリ・画面",
        operation="移動",
        params=params,
        subcategory="画面",
        step_id=step_id,
        description=description or f"ウィンドウを({x}, {y})に移動"
    )

@mcp.tool()
def window_maximize_minimize(
    action: str,
    window: Optional[str] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ウィンドウを最大化/最小化"""
    params = {"action": action}
    if window is not None:
        params["window"] = window

    return create_rpa_step_from_template(
        category="A_アプリ・画面",
        operation="最大化/最小化",
        params=params,
        subcategory="画面",
        step_id=step_id,
        description=description or f"ウィンドウを{action}"
    )

@mcp.tool()
def screenshot(
    path: str,
    window: Optional[str] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """スクリーンショットを撮る"""
    params = {"path": path}
    if window is not None:
        params["window"] = window

    return create_rpa_step_from_template(
        category="A_アプリ・画面",
        operation="スクリーンショットを撮る",
        params=params,
        subcategory="画面",
        step_id=step_id,
        description=description or "スクリーンショットを撮る"
    )

# ====================
# B_待機・終了・エラー
# ====================

@mcp.tool()
def wait_seconds(
    interval: int,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """指定秒数待機"""
    return create_rpa_step_from_template(
        category="B_待機・終了・エラー",
        operation="秒",
        params={"interval": interval},
        step_id=step_id,
        description=description or f"{interval}秒待機"
    )

@mcp.tool()
def wait_for_image(
    path: str,
    accuracy: Optional[float] = None,
    timeout: Optional[int] = None,
    window: Optional[str] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """画像が表示されるまで待機"""
    params = {"path": path}
    if accuracy is not None:
        params["accuracy"] = accuracy
    if timeout is not None:
        params["timeout"] = timeout
    if window is not None:
        params["window"] = window

    return create_rpa_step_from_template(
        category="B_待機・終了・エラー",
        operation="画像出現を待つ",
        params=params,
        step_id=step_id,
        description=description or "画像出現を待つ"
    )

@mcp.tool()
def continue_confirm(
    string: str,
    title: Optional[str] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """続行確認ダイアログを表示"""
    params = {"string": string}
    if title is not None:
        params["title"] = title

    return create_rpa_step_from_template(
        category="B_待機・終了・エラー",
        operation="続行確認",
        params=params,
        step_id=step_id,
        description=description or "続行確認"
    )

@mcp.tool()
def continue_confirm_timer(
    string: str,
    timeout: int,
    title: Optional[str] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """タイマー付き続行確認ダイアログを表示"""
    params = {
        "string": string,
        "timeout": timeout
    }
    if title is not None:
        params["title"] = title

    return create_rpa_step_from_template(
        category="B_待機・終了・エラー",
        operation="タイマー付き続行確認（秒）",
        params=params,
        step_id=step_id,
        description=description or f"{timeout}秒後に自動続行"
    )

@mcp.tool()
def change_command_interval(
    interval: int,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """コマンド間の待機時間を変更"""
    return create_rpa_step_from_template(
        category="B_待機・終了・エラー",
        operation="コマンド間待機時間を変更",
        params={"interval": interval},
        step_id=step_id,
        description=description or f"コマンド間隔を{interval}msに変更"
    )

@mcp.tool()
def force_exit(
    exit_code: Optional[int] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """作業を強制終了"""
    params = {}
    if exit_code is not None:
        params["exit_code"] = exit_code

    return create_rpa_step_from_template(
        category="B_待機・終了・エラー",
        operation="作業強制終了",
        params=params,
        step_id=step_id,
        description=description or "作業を強制終了"
    )

@mcp.tool()
def raise_error(
    string: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """エラーを発生させる"""
    return create_rpa_step_from_template(
        category="B_待機・終了・エラー",
        operation="エラー発生",
        params={"string": string},
        step_id=step_id,
        description=description or "エラーを発生"
    )

@mcp.tool()
def error_check(
    variable: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """エラー確認・処理"""
    return create_rpa_step_from_template(
        category="B_待機・終了・エラー",
        operation="エラー確認・処理",
        params={"variable": variable},
        step_id=step_id,
        description=description or "エラー確認・処理"
    )

@mcp.tool()
def error_check_retry(
    variable: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """エラー確認・処理（リトライ前処理）"""
    return create_rpa_step_from_template(
        category="B_待機・終了・エラー",
        operation="エラー確認・処理（リトライ前処理）",
        params={"variable": variable},
        step_id=step_id,
        description=description or "エラー確認・処理（リトライ前）"
    )

# ====================
# C_マウス
# ====================

# 移動
@mcp.tool()
def mouse_move_to(
    x: int,
    y: int,
    interval: Optional[int] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """マウスを座標に移動"""
    params = {"x": x, "y": y}
    if interval is not None:
        params["interval"] = interval

    return create_rpa_step_from_template(
        category="C_マウス",
        operation="座標",
        params=params,
        subcategory="移動",
        step_id=step_id,
        description=description or f"マウスを({x}, {y})に移動"
    )

@mcp.tool()
def mouse_move_by(
    x: int,
    y: int,
    interval: Optional[int] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """マウスを相対移動"""
    params = {"x": x, "y": y}
    if interval is not None:
        params["interval"] = interval

    return create_rpa_step_from_template(
        category="C_マウス",
        operation="距離",
        params=params,
        subcategory="移動",
        step_id=step_id,
        description=description or f"マウスを({x}, {y})相対移動"
    )

@mcp.tool()
def mouse_move_to_image(
    path: str,
    accuracy: Optional[float] = None,
    timeout: Optional[int] = None,
    window: Optional[str] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """画像を認識してマウスを移動"""
    params = {"path": path}
    if accuracy is not None:
        params["accuracy"] = accuracy
    if timeout is not None:
        params["timeout"] = timeout
    if window is not None:
        params["window"] = window

    return create_rpa_step_from_template(
        category="C_マウス",
        operation="画像認識",
        params=params,
        subcategory="移動",
        step_id=step_id,
        description=description or "画像にマウスを移動"
    )

# ドラッグ＆ドロップ
@mcp.tool()
def mouse_drag_drop_coords(
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    interval: Optional[int] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """座標間でドラッグ＆ドロップ"""
    params = {
        "start_x": start_x,
        "start_y": start_y,
        "end_x": end_x,
        "end_y": end_y
    }
    if interval is not None:
        params["interval"] = interval

    return create_rpa_step_from_template(
        category="C_マウス",
        operation="座標（D&D）",
        params=params,
        subcategory="ドラッグ＆ドロップ",
        step_id=step_id,
        description=description or "ドラッグ＆ドロップ"
    )

@mcp.tool()
def mouse_drag_drop_distance(
    x: int,
    y: int,
    interval: Optional[int] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """距離でドラッグ＆ドロップ"""
    params = {"x": x, "y": y}
    if interval is not None:
        params["interval"] = interval

    return create_rpa_step_from_template(
        category="C_マウス",
        operation="距離（D&D）",
        params=params,
        subcategory="ドラッグ＆ドロップ",
        step_id=step_id,
        description=description or f"({x}, {y})ドラッグ"
    )

@mcp.tool()
def mouse_drag_drop_images(
    start_image: str,
    end_image: str,
    accuracy: Optional[float] = None,
    timeout: Optional[int] = None,
    window: Optional[str] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """画像間でドラッグ＆ドロップ"""
    params = {
        "start_image": start_image,
        "end_image": end_image
    }
    if accuracy is not None:
        params["accuracy"] = accuracy
    if timeout is not None:
        params["timeout"] = timeout
    if window is not None:
        params["window"] = window

    return create_rpa_step_from_template(
        category="C_マウス",
        operation="画像認識（D&D）",
        params=params,
        subcategory="ドラッグ＆ドロップ",
        step_id=step_id,
        description=description or "画像間でドラッグ＆ドロップ"
    )

@mcp.tool()
def mouse_click(
    button: str = "left",
    click_count: int = 1,
    x: Optional[int] = None,
    y: Optional[int] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """マウスクリック"""
    params = {
        "button": button,
        "click_count": click_count
    }
    if x is not None:
        params["x"] = x
    if y is not None:
        params["y"] = y

    return create_rpa_step_from_template(
        category="C_マウス",
        operation="マウスクリック",
        params=params,
        step_id=step_id,
        description=description or f"{button}クリック"
    )

@mcp.tool()
def mouse_scroll(
    direction: str,
    amount: int,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """マウススクロール"""
    return create_rpa_step_from_template(
        category="C_マウス",
        operation="スクロール",
        params={
            "direction": direction,
            "amount": amount
        },
        step_id=step_id,
        description=description or f"{direction}に{amount}スクロール"
    )

# ====================
# D_キーボード
# ====================

@mcp.tool()
def keyboard_type_text(
    string: str,
    interval: Optional[int] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """文字を入力"""
    params = {"string": string}
    if interval is not None:
        params["interval"] = interval

    return create_rpa_step_from_template(
        category="D_キーボード",
        operation="文字",
        params=params,
        subcategory="入力",
        step_id=step_id,
        description=description or "テキストを入力"
    )

@mcp.tool()
def keyboard_paste_text(
    string: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """文字を貼り付け"""
    return create_rpa_step_from_template(
        category="D_キーボード",
        operation="文字（貼り付け）",
        params={"string": string},
        subcategory="入力",
        step_id=step_id,
        description=description or "テキストを貼り付け"
    )

@mcp.tool()
def keyboard_type_password(
    password_type: str,
    password: Optional[str] = None,
    password_id: Optional[str] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """パスワードを入力"""
    params = {"password_type": password_type}
    if password is not None:
        params["password"] = password
    if password_id is not None:
        params["password_id"] = password_id

    return create_rpa_step_from_template(
        category="D_キーボード",
        operation="パスワード",
        params=params,
        subcategory="入力",
        step_id=step_id,
        description=description or "パスワードを入力"
    )

@mcp.tool()
def keyboard_shortcut(
    keys: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ショートカットキーを押す"""
    return create_rpa_step_from_template(
        category="D_キーボード",
        operation="ショートカットキー",
        params={"keys": keys},
        subcategory="入力",
        step_id=step_id,
        description=description or f"{keys}を押す"
    )

# ====================
# E_記憶
# ====================

@mcp.tool()
def memory_store_text(
    variable: str,
    string: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """文字を記憶"""
    return create_rpa_step_from_template(
        category="E_記憶",
        operation="文字",
        params={
            "variable": variable,
            "string": string
        },
        step_id=step_id,
        description=description or f"{variable}に文字を記憶"
    )

@mcp.tool()
def memory_store_password(
    password_type: str,
    password: Optional[str] = None,
    password_id: Optional[str] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """パスワードを記憶"""
    params = {"password_type": password_type}
    if password is not None:
        params["password"] = password
    if password_id is not None:
        params["password_id"] = password_id

    return create_rpa_step_from_template(
        category="E_記憶",
        operation="パスワード",
        params=params,
        step_id=step_id,
        description=description or "パスワードを記憶"
    )

@mcp.tool()
def memory_store_env_info(
    variable: str,
    environment: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """環境情報を記憶"""
    return create_rpa_step_from_template(
        category="E_記憶",
        operation="環境情報",
        params={
            "variable": variable,
            "environment": environment
        },
        step_id=step_id,
        description=description or f"{environment}を記憶"
    )

@mcp.tool()
def memory_store_date(
    variable: str,
    offset: int = 0,
    format: str = "yyyy/MM/dd",
    zero_option: Optional[str] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """日付を記憶"""
    params = {
        "variable": variable,
        "offset": offset,
        "format": format
    }
    if zero_option is not None:
        params["0_option"] = zero_option

    return create_rpa_step_from_template(
        category="E_記憶",
        operation="日付",
        params=params,
        step_id=step_id,
        description=description or "日付を記憶"
    )

@mcp.tool()
def memory_store_business_date(
    variable: str,
    offset: int = 0,
    busidays: str = "",
    format: str = "yyyy/MM/dd",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """営業日を記憶"""
    return create_rpa_step_from_template(
        category="E_記憶",
        operation="日付（営業日）",
        params={
            "variable": variable,
            "offset": offset,
            "busidays": busidays,
            "format": format
        },
        step_id=step_id,
        description=description or "営業日を記憶"
    )

@mcp.tool()
def memory_store_weekday_date(
    variable: str,
    offset: int = 0,
    weekday: str = "",
    format: str = "yyyy/MM/dd",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """曜日指定で日付を記憶"""
    return create_rpa_step_from_template(
        category="E_記憶",
        operation="日付（曜日）",
        params={
            "variable": variable,
            "offset": offset,
            "weekday": weekday,
            "format": format
        },
        step_id=step_id,
        description=description or "曜日指定で日付を記憶"
    )

@mcp.tool()
def memory_calculate_date(
    variable: str,
    date: str,
    offset: int,
    format: str = "yyyy/MM/dd",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """日付計算"""
    return create_rpa_step_from_template(
        category="E_記憶",
        operation="日付計算",
        params={
            "variable": variable,
            "date": date,
            "offset": offset,
            "format": format
        },
        step_id=step_id,
        description=description or "日付計算"
    )

@mcp.tool()
def memory_store_weekday(
    variable: str,
    date: Optional[str] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """曜日を記憶"""
    params = {"variable": variable}
    if date is not None:
        params["date"] = date

    return create_rpa_step_from_template(
        category="E_記憶",
        operation="曜日",
        params=params,
        step_id=step_id,
        description=description or "曜日を記憶"
    )

@mcp.tool()
def memory_store_time(
    variable: str,
    format: str = "HH:mm:ss",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """時刻を記憶"""
    return create_rpa_step_from_template(
        category="E_記憶",
        operation="時刻",
        params={
            "variable": variable,
            "format": format
        },
        step_id=step_id,
        description=description or "現在時刻を記憶"
    )

@mcp.tool()
def memory_calculate_time(
    variable: str,
    time: str,
    offset: int,
    format: str = "HH:mm:ss",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """時刻計算"""
    return create_rpa_step_from_template(
        category="E_記憶",
        operation="時刻計算",
        params={
            "variable": variable,
            "time": time,
            "offset": offset,
            "format": format
        },
        step_id=step_id,
        description=description or "時刻計算"
    )

@mcp.tool()
def memory_calculate(
    variable: str,
    expression: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """計算結果を記憶"""
    return create_rpa_step_from_template(
        category="E_記憶",
        operation="計算",
        params={
            "variable": variable,
            "expression": expression
        },
        step_id=step_id,
        description=description or "計算結果を記憶"
    )

@mcp.tool()
def memory_random_number(
    variable: str,
    min_value: int = 0,
    max_value: int = 100,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """乱数を記憶"""
    return create_rpa_step_from_template(
        category="E_記憶",
        operation="乱数",
        params={
            "variable": variable,
            "min": min_value,
            "max": max_value
        },
        step_id=step_id,
        description=description or f"{min_value}〜{max_value}の乱数を記憶"
    )

@mcp.tool()
def memory_clipboard_content(
    variable: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """クリップボードの内容を記憶"""
    return create_rpa_step_from_template(
        category="E_記憶",
        operation="コピー内容",
        params={"variable": variable},
        step_id=step_id,
        description=description or "クリップボード内容を記憶"
    )

@mcp.tool()
def memory_copy_to_clipboard(
    string: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """クリップボードにコピー"""
    return create_rpa_step_from_template(
        category="E_記憶",
        operation="クリップボードへコピー",
        params={"string": string},
        step_id=step_id,
        description=description or "クリップボードにコピー"
    )

@mcp.tool()
def memory_user_input(
    variable: str,
    string: str,
    title: Optional[str] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """実行中にユーザー入力を取得"""
    params = {
        "variable": variable,
        "string": string
    }
    if title is not None:
        params["title"] = title

    return create_rpa_step_from_template(
        category="E_記憶",
        operation="実行中に入力",
        params=params,
        step_id=step_id,
        description=description or "ユーザー入力を取得"
    )

@mcp.tool()
def memory_file_modified_date(
    variable: str,
    path: str,
    format: str = "yyyy/MM/dd HH:mm:ss",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ファイル更新日時を記憶"""
    return create_rpa_step_from_template(
        category="E_記憶",
        operation="ファイル更新日時",
        params={
            "variable": variable,
            "path": path,
            "format": format
        },
        step_id=step_id,
        description=description or "ファイル更新日時を記憶"
    )

@mcp.tool()
def memory_file_size(
    variable: str,
    path: str,
    unit: str = "KB",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ファイルサイズを記憶"""
    return create_rpa_step_from_template(
        category="E_記憶",
        operation="ファイルサイズ",
        params={
            "variable": variable,
            "path": path,
            "unit": unit
        },
        step_id=step_id,
        description=description or "ファイルサイズを記憶"
    )

@mcp.tool()
def memory_latest_file(
    variable: str,
    folder: str,
    pattern: Optional[str] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """最新ファイル・フォルダを記憶"""
    params = {
        "variable": variable,
        "folder": folder
    }
    if pattern is not None:
        params["pattern"] = pattern

    return create_rpa_step_from_template(
        category="E_記憶",
        operation="最新ファイル・フォルダ",
        params=params,
        step_id=step_id,
        description=description or "最新ファイル・フォルダを記憶"
    )

# ====================
# F_文字抽出
# ====================

@mcp.tool()
def text_extract_brackets(
    variable: str,
    string: str,
    bracket_type: str,
    position: int = 1,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """括弧内の文字を抽出"""
    return create_rpa_step_from_template(
        category="F_文字抽出",
        operation="括弧・引用符号から",
        params={
            "variable": variable,
            "string": string,
            "bracket_type": bracket_type,
            "position": position
        },
        step_id=step_id,
        description=description or "括弧内文字を抽出"
    )

@mcp.tool()
def text_extract_delimiter(
    variable: str,
    string: str,
    delimiter: str,
    position: int = 1,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """区切り文字で分割して抽出"""
    return create_rpa_step_from_template(
        category="F_文字抽出",
        operation="区切り文字から",
        params={
            "variable": variable,
            "string": string,
            "delimiter": delimiter,
            "position": position
        },
        step_id=step_id,
        description=description or "区切り文字で抽出"
    )

@mcp.tool()
def text_remove_whitespace(
    variable: str,
    string: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """改行・空白を削除"""
    return create_rpa_step_from_template(
        category="F_文字抽出",
        operation="改行・空白を削除",
        params={
            "variable": variable,
            "string": string
        },
        step_id=step_id,
        description=description or "空白文字を削除"
    )

@mcp.tool()
def text_extract_from_path(
    variable: str,
    path: str,
    extract_type: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ファイルパスから情報を抽出"""
    return create_rpa_step_from_template(
        category="F_文字抽出",
        operation="ファイルパスから",
        params={
            "variable": variable,
            "path": path,
            "extract_type": extract_type
        },
        step_id=step_id,
        description=description or f"パスから{extract_type}を抽出"
    )

@mcp.tool()
def text_match_pattern(
    variable: str,
    string: str,
    pattern: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """パターンにマッチする文字を抽出"""
    return create_rpa_step_from_template(
        category="F_文字抽出",
        operation="ルールにマッチ",
        params={
            "variable": variable,
            "string": string,
            "pattern": pattern
        },
        step_id=step_id,
        description=description or "パターンマッチで抽出"
    )

@mcp.tool()
def text_replace(
    variable: str,
    string: str,
    find: str,
    replace: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """文字を置換"""
    return create_rpa_step_from_template(
        category="F_文字抽出",
        operation="置換",
        params={
            "variable": variable,
            "string": string,
            "find": find,
            "replace": replace
        },
        step_id=step_id,
        description=description or "文字を置換"
    )

@mcp.tool()
def text_convert_case(
    variable: str,
    string: str,
    conversion_type: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """文字変換（大文字/小文字等）"""
    return create_rpa_step_from_template(
        category="F_文字抽出",
        operation="文字変換",
        params={
            "variable": variable,
            "string": string,
            "conversion_type": conversion_type
        },
        step_id=step_id,
        description=description or f"{conversion_type}に変換"
    )

@mcp.tool()
def text_convert_date_format(
    variable: str,
    date: str,
    from_format: str,
    to_format: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """日付形式変換"""
    return create_rpa_step_from_template(
        category="F_文字抽出",
        operation="日付形式変換",
        params={
            "variable": variable,
            "date": date,
            "from_format": from_format,
            "to_format": to_format
        },
        step_id=step_id,
        description=description or "日付形式を変換"
    )

@mcp.tool()
def text_loop_lines(
    string: str,
    variable: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """1行ずつループ"""
    return create_rpa_step_from_template(
        category="F_文字抽出",
        operation="1行ずつループ",
        params={
            "string": string,
            "variable": variable
        },
        step_id=step_id,
        description=description or "1行ずつループ処理"
    )

# ====================
# G_分岐
# ====================

@mcp.tool()
def branch_string(
    left: str,
    operator: str,
    right: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """文字列条件で分岐"""
    return create_rpa_step_from_template(
        category="G_分岐",
        operation="文字列",
        params={
            "left": left,
            "operator": operator,
            "right": right
        },
        step_id=step_id,
        description=description or "文字列条件で分岐"
    )

@mcp.tool()
def branch_number(
    left: float,
    operator: str,
    right: float,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """数値条件で分岐"""
    return create_rpa_step_from_template(
        category="G_分岐",
        operation="数値",
        params={
            "left": left,
            "operator": operator,
            "right": right
        },
        step_id=step_id,
        description=description or "数値条件で分岐"
    )

@mcp.tool()
def branch_date(
    left: str,
    operator: str,
    right: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """日付条件で分岐"""
    return create_rpa_step_from_template(
        category="G_分岐",
        operation="日付",
        params={
            "left": left,
            "operator": operator,
            "right": right
        },
        step_id=step_id,
        description=description or "日付条件で分岐"
    )

@mcp.tool()
def branch_file_exists(
    path: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ファイル/フォルダの存在で分岐"""
    return create_rpa_step_from_template(
        category="G_分岐",
        operation="ファイル・フォルダの有/無を確認",
        params={"path": path},
        step_id=step_id,
        description=description or "ファイル存在確認で分岐"
    )

@mcp.tool()
def branch_image(
    path: str,
    accuracy: Optional[float] = None,
    timeout: Optional[int] = None,
    window: Optional[str] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """画像検出で分岐"""
    params = {"path": path}
    if accuracy is not None:
        params["accuracy"] = accuracy
    if timeout is not None:
        params["timeout"] = timeout
    if window is not None:
        params["window"] = window

    return create_rpa_step_from_template(
        category="G_分岐",
        operation="画像",
        params=params,
        step_id=step_id,
        description=description or "画像検出で分岐"
    )

# ====================
# H_繰り返し
# ====================

@mcp.tool()
def loop_repeat(
    count: int,
    variable: Optional[str] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """繰り返し処理"""
    params = {"count": count}
    if variable is not None:
        params["variable"] = variable

    return create_rpa_step_from_template(
        category="H_繰り返し",
        operation="繰り返し",
        params=params,
        step_id=step_id,
        description=description or f"{count}回繰り返し"
    )

@mcp.tool()
def loop_break(
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """繰り返しを抜ける"""
    return create_rpa_step_from_template(
        category="H_繰り返し",
        operation="繰り返しを抜ける",
        params={},
        step_id=step_id,
        description=description or "繰り返しを抜ける"
    )

@mcp.tool()
def loop_continue(
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """繰り返しの最初に戻る"""
    return create_rpa_step_from_template(
        category="H_繰り返し",
        operation="繰り返しの最初に戻る",
        params={},
        step_id=step_id,
        description=description or "繰り返しの最初に戻る"
    )

# ====================
# I_ファイル・フォルダ
# ====================

# ファイル
@mcp.tool()
def file_open(
    path: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ファイルを開く"""
    return create_rpa_step_from_template(
        category="I_ファイル・フォルダ",
        operation="開く",
        params={"path": path},
        subcategory="ファイル",
        step_id=step_id,
        description=description or f"{path}を開く"
    )

@mcp.tool()
def file_move(
    source: str,
    destination: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ファイルを移動"""
    return create_rpa_step_from_template(
        category="I_ファイル・フォルダ",
        operation="移動",
        params={
            "source": source,
            "destination": destination
        },
        subcategory="ファイル",
        step_id=step_id,
        description=description or "ファイルを移動"
    )

@mcp.tool()
def file_read(
    path: str,
    variable: str,
    encoding: str = "utf-8",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ファイルを読み込む"""
    return create_rpa_step_from_template(
        category="I_ファイル・フォルダ",
        operation="読み込む",
        params={
            "path": path,
            "variable": variable,
            "encoding": encoding
        },
        subcategory="ファイル",
        step_id=step_id,
        description=description or f"{path}を読み込む"
    )

@mcp.tool()
def file_write(
    path: str,
    content: str,
    encoding: str = "utf-8",
    mode: str = "overwrite",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ファイルに書き込む"""
    return create_rpa_step_from_template(
        category="I_ファイル・フォルダ",
        operation="書き込む",
        params={
            "path": path,
            "content": content,
            "encoding": encoding,
            "mode": mode
        },
        subcategory="ファイル",
        step_id=step_id,
        description=description or f"{path}に書き込む"
    )

# フォルダ
@mcp.tool()
def folder_open(
    path: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """フォルダを開く"""
    return create_rpa_step_from_template(
        category="I_ファイル・フォルダ",
        operation="開く",
        params={"path": path},
        subcategory="フォルダ",
        step_id=step_id,
        description=description or f"{path}を開く"
    )

@mcp.tool()
def folder_create(
    path: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """フォルダを作成"""
    return create_rpa_step_from_template(
        category="I_ファイル・フォルダ",
        operation="作成",
        params={"path": path},
        subcategory="フォルダ",
        step_id=step_id,
        description=description or f"{path}を作成"
    )

@mcp.tool()
def folder_loop(
    path: str,
    variable: str,
    pattern: Optional[str] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """フォルダ内をループ"""
    params = {
        "path": path,
        "variable": variable
    }
    if pattern is not None:
        params["pattern"] = pattern

    return create_rpa_step_from_template(
        category="I_ファイル・フォルダ",
        operation="ループ",
        params=params,
        subcategory="フォルダ",
        step_id=step_id,
        description=description or "フォルダ内をループ"
    )

# 共通
@mcp.tool()
def file_rename(
    old_name: str,
    new_name: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ファイル・フォルダ名を変更"""
    return create_rpa_step_from_template(
        category="I_ファイル・フォルダ",
        operation="ファイル・フォルダ名の変更",
        params={
            "old_name": old_name,
            "new_name": new_name
        },
        step_id=step_id,
        description=description or "名前を変更"
    )

@mcp.tool()
def file_copy(
    source: str,
    destination: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ファイル・フォルダをコピー"""
    return create_rpa_step_from_template(
        category="I_ファイル・フォルダ",
        operation="ファイル・フォルダをコピー",
        params={
            "source": source,
            "destination": destination
        },
        step_id=step_id,
        description=description or "コピー"
    )

@mcp.tool()
def file_delete(
    path: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ファイル・フォルダを削除"""
    return create_rpa_step_from_template(
        category="I_ファイル・フォルダ",
        operation="ファイル・フォルダを削除",
        params={"path": path},
        step_id=step_id,
        description=description or f"{path}を削除"
    )

# 圧縮・解凍
@mcp.tool()
def file_compress(
    source: str,
    destination: str,
    format: str = "zip",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ファイル・フォルダを圧縮"""
    return create_rpa_step_from_template(
        category="I_ファイル・フォルダ",
        operation="ファイル・フォルダを圧縮",
        params={
            "source": source,
            "destination": destination,
            "format": format
        },
        subcategory="圧縮・解凍",
        step_id=step_id,
        description=description or "圧縮"
    )

@mcp.tool()
def file_decompress(
    source: str,
    destination: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ファイル・フォルダに解凍"""
    return create_rpa_step_from_template(
        category="I_ファイル・フォルダ",
        operation="ファイル・フォルダに解凍",
        params={
            "source": source,
            "destination": destination
        },
        subcategory="圧縮・解凍",
        step_id=step_id,
        description=description or "解凍"
    )

# ファイル名変更（挿入）
@mcp.tool()
def file_rename_insert_text(
    path: str,
    text: str,
    position: str = "prefix",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ファイル名に文字を挿入"""
    return create_rpa_step_from_template(
        category="I_ファイル・フォルダ",
        operation="文字",
        params={
            "path": path,
            "text": text,
            "position": position
        },
        subcategory="ファイル名変更（挿入）",
        step_id=step_id,
        description=description or "ファイル名に文字を挿入"
    )

@mcp.tool()
def file_rename_insert_date(
    path: str,
    format: str = "yyyyMMdd",
    position: str = "prefix",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ファイル名に日付を挿入"""
    return create_rpa_step_from_template(
        category="I_ファイル・フォルダ",
        operation="日付",
        params={
            "path": path,
            "format": format,
            "position": position
        },
        subcategory="ファイル名変更（挿入）",
        step_id=step_id,
        description=description or "ファイル名に日付を挿入"
    )

@mcp.tool()
def file_rename_insert_ref(
    path: str,
    variable: str,
    position: str = "prefix",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ファイル名に参照IDを挿入"""
    return create_rpa_step_from_template(
        category="I_ファイル・フォルダ",
        operation="参照ID",
        params={
            "path": path,
            "variable": variable,
            "position": position
        },
        subcategory="ファイル名変更（挿入）",
        step_id=step_id,
        description=description or "ファイル名に参照IDを挿入"
    )

# ====================
# J_エクセル・CSV（続き）
# ====================

# ブック
@mcp.tool()
def excel_open_book(
    path: str,
    variable: str,
    password: Optional[str] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """Excelブックを開く"""
    params = {
        "path": path,
        "variable": variable
    }
    if password is not None:
        params["password"] = password

    return create_rpa_step_from_template(
        category="J_エクセル・CSV",
        operation="ブックを開く",
        params=params,
        subcategory="ブック",
        step_id=step_id,
        description=description or f"{path}を開く"
    )

@mcp.tool()
def excel_remember_book(
    variable: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """Excelブックを覚える"""
    return create_rpa_step_from_template(
        category="J_エクセル・CSV",
        operation="ブックを覚える",
        params={"variable": variable},
        subcategory="ブック",
        step_id=step_id,
        description=description or "ブックを覚える"
    )

@mcp.tool()
def excel_save_book(
    variable: str,
    path: Optional[str] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """Excelブックを保存"""
    params = {"variable": variable}
    if path is not None:
        params["path"] = path

    return create_rpa_step_from_template(
        category="J_エクセル・CSV",
        operation="ブックを保存",
        params=params,
        subcategory="ブック",
        step_id=step_id,
        description=description or "ブックを保存"
    )

@mcp.tool()
def excel_close_book(
    variable: str,
    save: bool = True,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """Excelブックを閉じる"""
    return create_rpa_step_from_template(
        category="J_エクセル・CSV",
        operation="ブックを閉じる",
        params={
            "variable": variable,
            "save": save
        },
        subcategory="ブック",
        step_id=step_id,
        description=description or "ブックを閉じる"
    )

# シート操作
@mcp.tool()
def excel_sheet_create(
    book: str,
    name: str,
    position: Optional[int] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """シートを新規作成"""
    params = {
        "book": book,
        "name": name
    }
    if position is not None:
        params["position"] = position

    return create_rpa_step_from_template(
        category="J_エクセル・CSV",
        operation="新規作成",
        params=params,
        subcategory="シート操作",
        step_id=step_id,
        description=description or f"シート{name}を作成"
    )

@mcp.tool()
def excel_sheet_delete(
    book: str,
    name: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """シートを削除"""
    return create_rpa_step_from_template(
        category="J_エクセル・CSV",
        operation="削除",
        params={
            "book": book,
            "name": name
        },
        subcategory="シート操作",
        step_id=step_id,
        description=description or f"シート{name}を削除"
    )

@mcp.tool()
def excel_sheet_switch(
    book: str,
    name: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """シートを切り替え"""
    return create_rpa_step_from_template(
        category="J_エクセル・CSV",
        operation="切り替え",
        params={
            "book": book,
            "name": name
        },
        subcategory="シート操作",
        step_id=step_id,
        description=description or f"シート{name}に切り替え"
    )

@mcp.tool()
def excel_sheet_move_copy(
    book: str,
    source: str,
    destination: str,
    action: str = "move",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """シートを移動・コピー"""
    return create_rpa_step_from_template(
        category="J_エクセル・CSV",
        operation="移動・コピー",
        params={
            "book": book,
            "source": source,
            "destination": destination,
            "action": action
        },
        subcategory="シート操作",
        step_id=step_id,
        description=description or "シートを移動・コピー"
    )

@mcp.tool()
def excel_sheet_get_name(
    book: str,
    variable: str,
    index: Optional[int] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """シート名を取得"""
    params = {
        "book": book,
        "variable": variable
    }
    if index is not None:
        params["index"] = index

    return create_rpa_step_from_template(
        category="J_エクセル・CSV",
        operation="名前取得",
        params=params,
        subcategory="シート操作",
        step_id=step_id,
        description=description or "シート名を取得"
    )

@mcp.tool()
def excel_sheet_rename(
    book: str,
    old_name: str,
    new_name: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """シート名を変更"""
    return create_rpa_step_from_template(
        category="J_エクセル・CSV",
        operation="名前変更",
        params={
            "book": book,
            "old_name": old_name,
            "new_name": new_name
        },
        subcategory="シート操作",
        step_id=step_id,
        description=description or "シート名を変更"
    )

# セル操作
@mcp.tool()
def excel_cell_range(
    book: str,
    sheet: str,
    range: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """範囲指定"""
    return create_rpa_step_from_template(
        category="J_エクセル・CSV",
        operation="範囲指定",
        params={
            "book": book,
            "sheet": sheet,
            "range": range
        },
        subcategory="セル操作",
        step_id=step_id,
        description=description or f"範囲{range}を指定"
    )

@mcp.tool()
def excel_cell_move_range(
    book: str,
    sheet: str,
    source: str,
    destination: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """指定範囲の移動"""
    return create_rpa_step_from_template(
        category="J_エクセル・CSV",
        operation="指定範囲の移動",
        params={
            "book": book,
            "sheet": sheet,
            "source": source,
            "destination": destination
        },
        subcategory="セル操作",
        step_id=step_id,
        description=description or "範囲を移動"
    )

@mcp.tool()
def excel_cell_delete_range(
    book: str,
    sheet: str,
    range: str,
    shift: str = "up",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """指定範囲の削除"""
    return create_rpa_step_from_template(
        category="J_エクセル・CSV",
        operation="指定範囲の削除",
        params={
            "book": book,
            "sheet": sheet,
            "range": range,
            "shift": shift
        },
        subcategory="セル操作",
        step_id=step_id,
        description=description or "範囲を削除"
    )

@mcp.tool()
def excel_cell_insert_range(
    book: str,
    sheet: str,
    range: str,
    shift: str = "down",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """指定範囲にセルを挿入"""
    return create_rpa_step_from_template(
        category="J_エクセル・CSV",
        operation="指定範囲にセルを挿入",
        params={
            "book": book,
            "sheet": sheet,
            "range": range,
            "shift": shift
        },
        subcategory="セル操作",
        step_id=step_id,
        description=description or "セルを挿入"
    )

@mcp.tool()
def excel_cell_get_value(
    book: str,
    sheet: str,
    range: str,
    variable: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """値を取得"""
    return create_rpa_step_from_template(
        category="J_エクセル・CSV",
        operation="値を取得",
        params={
            "book": book,
            "sheet": sheet,
            "range": range,
            "variable": variable
        },
        subcategory="セル操作",
        step_id=step_id,
        description=description or f"{range}の値を取得"
    )

@mcp.tool()
def excel_cell_set_value(
    book: str,
    sheet: str,
    range: str,
    value: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """値を入力"""
    return create_rpa_step_from_template(
        category="J_エクセル・CSV",
        operation="値を入力",
        params={
            "book": book,
            "sheet": sheet,
            "range": range,
            "value": value
        },
        subcategory="セル操作",
        step_id=step_id,
        description=description or f"{range}に値を入力"
    )

@mcp.tool()
def excel_cell_copy(
    book: str,
    sheet: str,
    range: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """セルをコピー"""
    return create_rpa_step_from_template(
        category="J_エクセル・CSV",
        operation="セルをコピー",
        params={
            "book": book,
            "sheet": sheet,
            "range": range
        },
        subcategory="セル操作",
        step_id=step_id,
        description=description or "セルをコピー"
    )

@mcp.tool()
def excel_cell_paste(
    book: str,
    sheet: str,
    range: str,
    paste_type: str = "all",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """セルを貼り付け"""
    return create_rpa_step_from_template(
        category="J_エクセル・CSV",
        operation="セルを貼り付け",
        params={
            "book": book,
            "sheet": sheet,
            "range": range,
            "paste_type": paste_type
        },
        subcategory="セル操作",
        step_id=step_id,
        description=description or "セルを貼り付け"
    )

@mcp.tool()
def excel_cell_get_position(
    book: str,
    sheet: str,
    value: str,
    variable: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """位置を取得"""
    return create_rpa_step_from_template(
        category="J_エクセル・CSV",
        operation="位置を取得",
        params={
            "book": book,
            "sheet": sheet,
            "value": value,
            "variable": variable
        },
        subcategory="セル操作",
        step_id=step_id,
        description=description or "位置を取得"
    )

@mcp.tool()
def excel_cell_get_last_row(
    book: str,
    sheet: str,
    variable: str,
    column: Optional[str] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """最終行を取得"""
    params = {
        "book": book,
        "sheet": sheet,
        "variable": variable
    }
    if column is not None:
        params["column"] = column

    return create_rpa_step_from_template(
        category="J_エクセル・CSV",
        operation="最終行取得",
        params=params,
        subcategory="セル操作",
        step_id=step_id,
        description=description or "最終行を取得"
    )

@mcp.tool()
def excel_cell_get_last_column(
    book: str,
    sheet: str,
    variable: str,
    row: Optional[int] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """最終列を取得"""
    params = {
        "book": book,
        "sheet": sheet,
        "variable": variable
    }
    if row is not None:
        params["row"] = row

    return create_rpa_step_from_template(
        category="J_エクセル・CSV",
        operation="最終列取得",
        params=params,
        subcategory="セル操作",
        step_id=step_id,
        description=description or "最終列を取得"
    )

@mcp.tool()
def excel_cell_calculate_column(
    book: str,
    sheet: str,
    column: str,
    formula: str,
    start_row: int,
    end_row: int,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """列計算"""
    return create_rpa_step_from_template(
        category="J_エクセル・CSV",
        operation="列計算",
        params={
            "book": book,
            "sheet": sheet,
            "column": column,
            "formula": formula,
            "start_row": start_row,
            "end_row": end_row
        },
        subcategory="セル操作",
        step_id=step_id,
        description=description or "列計算"
    )

@mcp.tool()
def excel_run_macro(
    book: str,
    macro_name: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """マクロ実行"""
    return create_rpa_step_from_template(
        category="J_エクセル・CSV",
        operation="マクロ実行",
        params={
            "book": book,
            "macro_name": macro_name
        },
        subcategory="セル操作",
        step_id=step_id,
        description=description or f"マクロ{macro_name}を実行"
    )

@mcp.tool()
def excel_row_loop(
    book: str,
    sheet: str,
    start_row: int,
    variable: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """行ループ"""
    return create_rpa_step_from_template(
        category="J_エクセル・CSV",
        operation="行ループ",
        params={
            "book": book,
            "sheet": sheet,
            "start_row": start_row,
            "variable": variable
        },
        subcategory="セル操作",
        step_id=step_id,
        description=description or "行ループ処理"
    )

@mcp.tool()
def excel_column_loop(
    book: str,
    sheet: str,
    start_column: str,
    variable: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """列ループ"""
    return create_rpa_step_from_template(
        category="J_エクセル・CSV",
        operation="列ループ",
        params={
            "book": book,
            "sheet": sheet,
            "start_column": start_column,
            "variable": variable
        },
        subcategory="セル操作",
        step_id=step_id,
        description=description or "列ループ処理"
    )

@mcp.tool()
def csv_read_loop(
    path: str,
    variable: str,
    encoding: str = "utf-8",
    delimiter: str = ",",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """CSV読込ループ"""
    return create_rpa_step_from_template(
        category="J_エクセル・CSV",
        operation="CSV読込ループ",
        params={
            "path": path,
            "variable": variable,
            "encoding": encoding,
            "delimiter": delimiter
        },
        subcategory="セル操作",
        step_id=step_id,
        description=description or "CSV読込ループ"
    )

# K〜Qは既に定義済みなので、残りのLカテゴリを追加

# ====================
# L_ウェブブラウザ
# ====================

@mcp.tool()
def browser_open(
    url: str,
    browser: str = "chrome",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ブラウザを開く"""
    return create_rpa_step_from_template(
        category="L_ウェブブラウザ",
        operation="ブラウザを開く",
        params={
            "url": url,
            "browser": browser
        },
        step_id=step_id,
        description=description or f"{url}を開く"
    )

@mcp.tool()
def browser_close(
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ブラウザを閉じる"""
    return create_rpa_step_from_template(
        category="L_ウェブブラウザ",
        operation="ブラウザを閉じる",
        params={},
        step_id=step_id,
        description=description or "ブラウザを閉じる"
    )

@mcp.tool()
def browser_navigate(
    url: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ページ移動"""
    return create_rpa_step_from_template(
        category="L_ウェブブラウザ",
        operation="ページ移動",
        params={"url": url},
        step_id=step_id,
        description=description or f"{url}へ移動"
    )

@mcp.tool()
def browser_click(
    selector: str,
    selector_type: str = "css",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ブラウザ要素をクリック"""
    return create_rpa_step_from_template(
        category="L_ウェブブラウザ",
        operation="クリック",
        params={
            "selector": selector,
            "selector_type": selector_type
        },
        step_id=step_id,
        description=description or "要素をクリック"
    )

@mcp.tool()
def browser_input(
    selector: str,
    text: str,
    selector_type: str = "css",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ブラウザ要素に入力"""
    return create_rpa_step_from_template(
        category="L_ウェブブラウザ",
        operation="入力",
        params={
            "selector": selector,
            "text": text,
            "selector_type": selector_type
        },
        step_id=step_id,
        description=description or "テキストを入力"
    )

@mcp.tool()
def browser_select(
    selector: str,
    value: str,
    selector_type: str = "css",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ブラウザ要素を選択"""
    return create_rpa_step_from_template(
        category="L_ウェブブラウザ",
        operation="選択",
        params={
            "selector": selector,
            "value": value,
            "selector_type": selector_type
        },
        step_id=step_id,
        description=description or "要素を選択"
    )

@mcp.tool()
def browser_read(
    selector: str,
    variable: str,
    selector_type: str = "css",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ブラウザ要素を読み取り"""
    return create_rpa_step_from_template(
        category="L_ウェブブラウザ",
        operation="読み取り",
        params={
            "selector": selector,
            "variable": variable,
            "selector_type": selector_type
        },
        step_id=step_id,
        description=description or "要素を読み取り"
    )

@mcp.tool()
def browser_wait(
    selector: str,
    selector_type: str = "css",
    timeout: int = 30,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ブラウザ要素を待機"""
    return create_rpa_step_from_template(
        category="L_ウェブブラウザ",
        operation="待機",
        params={
            "selector": selector,
            "selector_type": selector_type,
            "timeout": timeout
        },
        step_id=step_id,
        description=description or "要素を待機"
    )

@mcp.tool()
def browser_scroll(
    direction: str = "down",
    amount: int = 300,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ブラウザをスクロール"""
    return create_rpa_step_from_template(
        category="L_ウェブブラウザ",
        operation="スクロール",
        params={
            "direction": direction,
            "amount": amount
        },
        step_id=step_id,
        description=description or f"{direction}に{amount}スクロール"
    )

@mcp.tool()
def browser_screenshot(
    path: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ブラウザのスクリーンショット"""
    return create_rpa_step_from_template(
        category="L_ウェブブラウザ",
        operation="スクリーンショット",
        params={"path": path},
        step_id=step_id,
        description=description or "スクリーンショットを撮る"
    )

@mcp.tool()
def browser_execute_js(
    script: str,
    variable: Optional[str] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """JavaScriptを実行"""
    params = {"script": script}
    if variable is not None:
        params["variable"] = variable

    return create_rpa_step_from_template(
        category="L_ウェブブラウザ",
        operation="JavaScript実行",
        params=params,
        step_id=step_id,
        description=description or "JavaScriptを実行"
    )

@mcp.tool()
def browser_switch_tab(
    index: int,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """タブ切り替え"""
    return create_rpa_step_from_template(
        category="L_ウェブブラウザ",
        operation="タブ切り替え",
        params={"index": index},
        step_id=step_id,
        description=description or f"タブ{index}に切り替え"
    )

@mcp.tool()
def browser_refresh(
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ブラウザを更新"""
    return create_rpa_step_from_template(
        category="L_ウェブブラウザ",
        operation="更新",
        params={},
        step_id=step_id,
        description=description or "ページを更新"
    )

@mcp.tool()
def browser_remember_popup(
    variable: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """派生ブラウザ画面を記憶"""
    return create_rpa_step_from_template(
        category="L_ウェブブラウザ",
        subcategory="派生ブラウザ画面記憶",
        operation="派生ブラウザ画面記憶",
        params={"variable": variable},
        step_id=step_id,
        description=description or "派生ブラウザ画面を記憶"
    )

@mcp.tool()
def browser_navigate_basic_auth(
    url: str,
    username: str,
    password: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """Basic認証付きでURL移動"""
    return create_rpa_step_from_template(
        category="L_ウェブブラウザ",
        subcategory="URL移動（Basic認証）",
        operation="URL移動（Basic認証）",
        params={"url": url, "username": username, "password": password},
        step_id=step_id,
        description=description or "Basic認証でURL移動"
    )

@mcp.tool()
def browser_add_cookie(
    name: str,
    value: str,
    domain: Optional[str] = None,
    path: Optional[str] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """Cookieを追加"""
    params = {"name": name, "value": value}
    if domain:
        params["domain"] = domain
    if path:
        params["path"] = path

    return create_rpa_step_from_template(
        category="L_ウェブブラウザ",
        subcategory="Cookie追加",
        operation="Cookie追加",
        params=params,
        step_id=step_id,
        description=description or "Cookieを追加"
    )

@mcp.tool()
def browser_wait_element(
    selector: str,
    timeout: int = 30,
    selector_type: str = "css",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """HTML要素の出現を待つ"""
    return create_rpa_step_from_template(
        category="L_ウェブブラウザ",
        subcategory="ページ操作",
        operation="HTMLエレメント出現を待つ",
        params={
            "selector": selector,
            "timeout": timeout,
            "selector_type": selector_type
        },
        step_id=step_id,
        description=description or "要素の出現を待つ"
    )

@mcp.tool()
def browser_enter_iframe(
    iframe_selector: str,
    selector_type: str = "css",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """IFrameに入る"""
    return create_rpa_step_from_template(
        category="L_ウェブブラウザ",
        subcategory="IFrame移動",
        operation="IFrameに入る",
        params={
            "iframe_selector": iframe_selector,
            "selector_type": selector_type
        },
        step_id=step_id,
        description=description or "IFrameに入る"
    )

@mcp.tool()
def browser_exit_iframe(
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """IFrameから出る"""
    return create_rpa_step_from_template(
        category="L_ウェブブラウザ",
        subcategory="IFrame移動",
        operation="IFrameから出る",
        params={},
        step_id=step_id,
        description=description or "IFrameから出る"
    )

# K_スプレッドシート
# ====================

@mcp.tool()
def spreadsheet_create(
    name: str,
    folder: Optional[str] = None,
    variable: Optional[str] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """新規スプレッドシートを作成"""
    params = {"name": name}
    if folder:
        params["folder"] = folder
    if variable:
        params["variable"] = variable

    return create_rpa_step_from_template(
        category="K_スプレッドシート",
        subcategory="スプレッドシート",
        operation="作成",
        params=params,
        step_id=step_id,
        description=description or "スプレッドシートを作成"
    )

@mcp.tool()
def spreadsheet_load(
    url: str,
    variable: Optional[str] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """スプレッドシートを読み込む"""
    params = {"url": url}
    if variable:
        params["variable"] = variable

    return create_rpa_step_from_template(
        category="K_スプレッドシート",
        subcategory="スプレッドシート",
        operation="読み込む",
        params=params,
        step_id=step_id,
        description=description or "スプレッドシートを読み込み"
    )

@mcp.tool()
def spreadsheet_delete(
    spreadsheet: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """スプレッドシートを削除"""
    return create_rpa_step_from_template(
        category="K_スプレッドシート",
        subcategory="スプレッドシート",
        operation="削除",
        params={"spreadsheet": spreadsheet},
        step_id=step_id,
        description=description or "スプレッドシートを削除"
    )

@mcp.tool()
def spreadsheet_rename(
    spreadsheet: str,
    name: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """スプレッドシートの名前を変更"""
    return create_rpa_step_from_template(
        category="K_スプレッドシート",
        subcategory="スプレッドシート",
        operation="名前変更",
        params={"spreadsheet": spreadsheet, "name": name},
        step_id=step_id,
        description=description or "スプレッドシート名を変更"
    )

@mcp.tool()
def spreadsheet_get_url(
    spreadsheet: str,
    variable: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """スプレッドシートのURLを取得"""
    return create_rpa_step_from_template(
        category="K_スプレッドシート",
        subcategory="スプレッドシート",
        operation="URL取得",
        params={"spreadsheet": spreadsheet, "variable": variable},
        step_id=step_id,
        description=description or "スプレッドシートURLを取得"
    )

@mcp.tool()
def sheet_create(
    spreadsheet: str,
    name: str,
    position: Optional[int] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """新規シートを作成"""
    params = {"spreadsheet": spreadsheet, "name": name}
    if position is not None:
        params["position"] = position

    return create_rpa_step_from_template(
        category="K_スプレッドシート",
        subcategory="シート",
        operation="新規作成",
        params=params,
        step_id=step_id,
        description=description or "シートを作成"
    )

@mcp.tool()
def sheet_delete(
    spreadsheet: str,
    sheet: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """シートを削除"""
    return create_rpa_step_from_template(
        category="K_スプレッドシート",
        subcategory="シート",
        operation="削除",
        params={"spreadsheet": spreadsheet, "sheet": sheet},
        step_id=step_id,
        description=description or "シートを削除"
    )

@mcp.tool()
def sheet_move(
    spreadsheet: str,
    sheet: str,
    position: int,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """シートを移動"""
    return create_rpa_step_from_template(
        category="K_スプレッドシート",
        subcategory="シート",
        operation="移動",
        params={"spreadsheet": spreadsheet, "sheet": sheet, "position": position},
        step_id=step_id,
        description=description or "シートを移動"
    )

@mcp.tool()
def sheet_copy(
    spreadsheet: str,
    sheet: str,
    new_name: str,
    position: Optional[int] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """シートをコピー"""
    params = {"spreadsheet": spreadsheet, "sheet": sheet, "new_name": new_name}
    if position is not None:
        params["position"] = position

    return create_rpa_step_from_template(
        category="K_スプレッドシート",
        subcategory="シート",
        operation="コピー",
        params=params,
        step_id=step_id,
        description=description or "シートをコピー"
    )

@mcp.tool()
def sheet_get_name(
    spreadsheet: str,
    index: int,
    variable: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """シート名を取得"""
    return create_rpa_step_from_template(
        category="K_スプレッドシート",
        subcategory="シート",
        operation="名前取得",
        params={"spreadsheet": spreadsheet, "index": index, "variable": variable},
        step_id=step_id,
        description=description or "シート名を取得"
    )

@mcp.tool()
def sheet_rename(
    spreadsheet: str,
    sheet: str,
    new_name: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """シート名を変更"""
    return create_rpa_step_from_template(
        category="K_スプレッドシート",
        subcategory="シート",
        operation="名前変更",
        params={"spreadsheet": spreadsheet, "sheet": sheet, "new_name": new_name},
        step_id=step_id,
        description=description or "シート名を変更"
    )

@mcp.tool()
def spreadsheet_delete_range(
    spreadsheet: str,
    sheet: str,
    range: str,
    shift: str = "up",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """指定範囲のセルを削除"""
    return create_rpa_step_from_template(
        category="K_スプレッドシート",
        subcategory="セル操作",
        operation="指定範囲の削除",
        params={"spreadsheet": spreadsheet, "sheet": sheet, "range": range, "shift": shift},
        step_id=step_id,
        description=description or "セル範囲を削除"
    )

@mcp.tool()
def spreadsheet_insert_cells(
    spreadsheet: str,
    sheet: str,
    range: str,
    shift: str = "down",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """指定範囲にセルを挿入"""
    return create_rpa_step_from_template(
        category="K_スプレッドシート",
        subcategory="セル操作",
        operation="指定範囲にセルを挿入",
        params={"spreadsheet": spreadsheet, "sheet": sheet, "range": range, "shift": shift},
        step_id=step_id,
        description=description or "セルを挿入"
    )

@mcp.tool()
def spreadsheet_get_value(
    spreadsheet: str,
    sheet: str,
    cell: str,
    variable: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """セルの値を取得"""
    return create_rpa_step_from_template(
        category="K_スプレッドシート",
        subcategory="セル操作",
        operation="値を取得",
        params={"spreadsheet": spreadsheet, "sheet": sheet, "cell": cell, "variable": variable},
        step_id=step_id,
        description=description or "セル値を取得"
    )

@mcp.tool()
def spreadsheet_set_value(
    spreadsheet: str,
    sheet: str,
    cell: str,
    value: Any,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """セルに値を入力"""
    return create_rpa_step_from_template(
        category="K_スプレッドシート",
        subcategory="セル操作",
        operation="値を入力",
        params={"spreadsheet": spreadsheet, "sheet": sheet, "cell": cell, "value": value},
        step_id=step_id,
        description=description or "セルに値を入力"
    )

@mcp.tool()
def spreadsheet_copy_paste(
    spreadsheet: str,
    source_sheet: str,
    source_range: str,
    dest_sheet: str,
    dest_cell: str,
    paste_type: str = "values",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """セルをコピー・貼り付け"""
    return create_rpa_step_from_template(
        category="K_スプレッドシート",
        subcategory="セル操作",
        operation="セルをコピー・貼り付け",
        params={
            "spreadsheet": spreadsheet,
            "source_sheet": source_sheet,
            "source_range": source_range,
            "dest_sheet": dest_sheet,
            "dest_cell": dest_cell,
            "paste_type": paste_type
        },
        step_id=step_id,
        description=description or "セルをコピー貼り付け"
    )

@mcp.tool()
def spreadsheet_get_last_row(
    spreadsheet: str,
    sheet: str,
    column: str,
    variable: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """最終行を取得"""
    return create_rpa_step_from_template(
        category="K_スプレッドシート",
        subcategory="セル操作",
        operation="最終行取得",
        params={"spreadsheet": spreadsheet, "sheet": sheet, "column": column, "variable": variable},
        step_id=step_id,
        description=description or "最終行を取得"
    )

@mcp.tool()
def spreadsheet_loop_rows(
    spreadsheet: str,
    sheet: str,
    start_row: int,
    end_row: Optional[int] = None,
    variable: str = "行データ",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """行単位でループ"""
    params = {"spreadsheet": spreadsheet, "sheet": sheet, "start_row": start_row, "variable": variable}
    if end_row is not None:
        params["end_row"] = end_row

    return create_rpa_step_from_template(
        category="K_スプレッドシート",
        subcategory="セル操作",
        operation="行ループ",
        params=params,
        step_id=step_id,
        description=description or "行をループ処理"
    )

@mcp.tool()
def spreadsheet_loop_columns(
    spreadsheet: str,
    sheet: str,
    start_column: str,
    end_column: Optional[str] = None,
    variable: str = "列データ",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """列単位でループ"""
    params = {"spreadsheet": spreadsheet, "sheet": sheet, "start_column": start_column, "variable": variable}
    if end_column is not None:
        params["end_column"] = end_column

    return create_rpa_step_from_template(
        category="K_スプレッドシート",
        subcategory="セル操作",
        operation="列ループ",
        params=params,
        step_id=step_id,
        description=description or "列をループ処理"
    )

# M_メール
# ====================

@mcp.tool()
def mail_send(
    to: str,
    subject: str,
    body: str,
    cc: Optional[str] = None,
    bcc: Optional[str] = None,
    attachments: Optional[List[str]] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """メールを送信"""
    params = {"to": to, "subject": subject, "body": body}
    if cc:
        params["cc"] = cc
    if bcc:
        params["bcc"] = bcc
    if attachments:
        params["attachments"] = attachments

    return create_rpa_step_from_template(
        category="M_メール",
        operation="メール送信",
        params=params,
        step_id=step_id,
        description=description or "メールを送信"
    )

@mcp.tool()
def mail_receive(
    folder: str = "INBOX",
    unread_only: bool = True,
    variable: str = "メール一覧",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """メールを受信"""
    return create_rpa_step_from_template(
        category="M_メール",
        operation="メール受信",
        params={"folder": folder, "unread_only": unread_only, "variable": variable},
        step_id=step_id,
        description=description or "メールを受信"
    )

@mcp.tool()
def mail_get_attachments(
    mail_id: str,
    save_path: str,
    variable: Optional[str] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """添付ファイルを取得"""
    params = {"mail_id": mail_id, "save_path": save_path}
    if variable:
        params["variable"] = variable

    return create_rpa_step_from_template(
        category="M_メール",
        operation="添付ファイル取得",
        params=params,
        step_id=step_id,
        description=description or "添付ファイルを取得"
    )

@mcp.tool()
def mail_move(
    mail_id: str,
    destination_folder: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """メールを移動"""
    return create_rpa_step_from_template(
        category="M_メール",
        operation="メール移動",
        params={"mail_id": mail_id, "destination_folder": destination_folder},
        step_id=step_id,
        description=description or "メールを移動"
    )

@mcp.tool()
def mail_delete(
    mail_id: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """メールを削除"""
    return create_rpa_step_from_template(
        category="M_メール",
        operation="メール削除",
        params={"mail_id": mail_id},
        step_id=step_id,
        description=description or "メールを削除"
    )

@mcp.tool()
def mail_mark_as_read(
    mail_id: str,
    mark_as_read: bool = True,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """メールを既読/未読にする"""
    return create_rpa_step_from_template(
        category="M_メール",
        operation="既読/未読設定",
        params={"mail_id": mail_id, "mark_as_read": mark_as_read},
        step_id=step_id,
        description=description or "メールの既読/未読を設定"
    )

@mcp.tool()
def mail_send_gmail(
    to: str,
    subject: str,
    body: str,
    cc: Optional[str] = None,
    bcc: Optional[str] = None,
    attachments: Optional[List[str]] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """Gmail経由でメールを送信"""
    params = {"to": to, "subject": subject, "body": body}
    if cc:
        params["cc"] = cc
    if bcc:
        params["bcc"] = bcc
    if attachments:
        params["attachments"] = attachments

    return create_rpa_step_from_template(
        category="M_メール",
        subcategory="送信（Gmail）",
        operation="送信（Gmail）",
        params=params,
        step_id=step_id,
        description=description or "Gmail経由でメールを送信"
    )

@mcp.tool()
def mail_receive_gmail(
    folder: str = "INBOX",
    unread_only: bool = True,
    variable: str = "メール一覧",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """Gmailからメールを受信"""
    return create_rpa_step_from_template(
        category="M_メール",
        subcategory="受信（Gmail）",
        operation="受信（Gmail）",
        params={"folder": folder, "unread_only": unread_only, "variable": variable},
        step_id=step_id,
        description=description or "Gmailからメールを受信"
    )

@mcp.tool()
def mail_send_microsoft(
    to: str,
    subject: str,
    body: str,
    cc: Optional[str] = None,
    bcc: Optional[str] = None,
    attachments: Optional[List[str]] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """Microsoft Outlook経由でメールを送信"""
    params = {"to": to, "subject": subject, "body": body}
    if cc:
        params["cc"] = cc
    if bcc:
        params["bcc"] = bcc
    if attachments:
        params["attachments"] = attachments

    return create_rpa_step_from_template(
        category="M_メール",
        subcategory="送信（Microsoft）",
        operation="送信（Microsoft）",
        params=params,
        step_id=step_id,
        description=description or "Outlook経由でメールを送信"
    )

@mcp.tool()
def mail_receive_microsoft(
    folder: str = "INBOX",
    unread_only: bool = True,
    variable: str = "メール一覧",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """Microsoft Outlookからメールを受信"""
    return create_rpa_step_from_template(
        category="M_メール",
        subcategory="受信（Microsoft）",
        operation="受信（Microsoft）",
        params={"folder": folder, "unread_only": unread_only, "variable": variable},
        step_id=step_id,
        description=description or "Outlookからメールを受信"
    )

# N_特殊アプリ操作
# ====================

@mcp.tool()
def special_app_teams(
    action: str,
    params: Optional[Dict[str, Any]] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """Microsoft Teams操作"""
    return create_rpa_step_from_template(
        category="N_特殊アプリ操作",
        operation="Teams",
        params={"action": action, "params": params or {}},
        step_id=step_id,
        description=description or "Teams操作"
    )

@mcp.tool()
def special_app_slack(
    action: str,
    params: Optional[Dict[str, Any]] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """Slack操作"""
    return create_rpa_step_from_template(
        category="N_特殊アプリ操作",
        operation="Slack",
        params={"action": action, "params": params or {}},
        step_id=step_id,
        description=description or "Slack操作"
    )

@mcp.tool()
def special_app_zoom(
    action: str,
    params: Optional[Dict[str, Any]] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """Zoom操作"""
    return create_rpa_step_from_template(
        category="N_特殊アプリ操作",
        operation="Zoom",
        params={"action": action, "params": params or {}},
        step_id=step_id,
        description=description or "Zoom操作"
    )

@mcp.tool()
def special_app_line(
    action: str,
    params: Optional[Dict[str, Any]] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """LINE操作"""
    return create_rpa_step_from_template(
        category="N_特殊アプリ操作",
        operation="LINE",
        params={"action": action, "params": params or {}},
        step_id=step_id,
        description=description or "LINE操作"
    )

@mcp.tool()
def special_app_salesforce(
    action: str,
    params: Optional[Dict[str, Any]] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """Salesforce操作"""
    return create_rpa_step_from_template(
        category="N_特殊アプリ操作",
        operation="Salesforce",
        params={"action": action, "params": params or {}},
        step_id=step_id,
        description=description or "Salesforce操作"
    )

# O_API
# ====================

@mcp.tool()
def api_request(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    body: Optional[Any] = None,
    variable: Optional[str] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """APIリクエストを送信"""
    params = {"url": url, "method": method}
    if headers:
        params["headers"] = headers
    if body is not None:
        params["body"] = body
    if variable:
        params["variable"] = variable

    return create_rpa_step_from_template(
        category="O_API",
        operation="APIリクエスト",
        params=params,
        step_id=step_id,
        description=description or "APIリクエスト送信"
    )

@mcp.tool()
def api_parse_response(
    response: str,
    parse_type: str = "json",
    variable: Optional[str] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """APIレスポンスを解析"""
    params = {"response": response, "parse_type": parse_type}
    if variable:
        params["variable"] = variable

    return create_rpa_step_from_template(
        category="O_API",
        operation="レスポンス解析",
        params=params,
        step_id=step_id,
        description=description or "レスポンスを解析"
    )

@mcp.tool()
def json_get_value(
    json_data: str,
    path: str,
    variable: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """JSON値を取得"""
    return create_rpa_step_from_template(
        category="O_API",
        subcategory="JSON",
        operation="JSON値取得",
        params={"json_data": json_data, "path": path, "variable": variable},
        step_id=step_id,
        description=description or "JSON値を取得"
    )

@mcp.tool()
def json_check_type(
    json_data: str,
    path: str,
    expected_type: str,
    variable: Optional[str] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """JSON型を確認"""
    params = {"json_data": json_data, "path": path, "expected_type": expected_type}
    if variable:
        params["variable"] = variable

    return create_rpa_step_from_template(
        category="O_API",
        subcategory="JSON",
        operation="JSON型確認",
        params=params,
        step_id=step_id,
        description=description or "JSON型を確認"
    )

# P_シナリオ整理
# ====================

@mcp.tool()
def scenario_comment(
    comment: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """コメントを追加"""
    return create_rpa_step_from_template(
        category="P_シナリオ整理",
        operation="コメント",
        params={"comment": comment},
        step_id=step_id,
        description=description or "コメント"
    )

@mcp.tool()
def scenario_group(
    name: str,
    steps: List[Dict[str, Any]],
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ステップをグループ化"""
    return create_rpa_step_from_template(
        category="P_シナリオ整理",
        operation="グループ",
        params={"name": name, "steps": steps},
        step_id=step_id,
        description=description or f"グループ: {name}"
    )

@mcp.tool()
def scenario_try_catch(
    try_steps: List[Dict[str, Any]],
    catch_steps: Optional[List[Dict[str, Any]]] = None,
    finally_steps: Optional[List[Dict[str, Any]]] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """エラーハンドリング"""
    params = {"try_steps": try_steps}
    if catch_steps:
        params["catch_steps"] = catch_steps
    if finally_steps:
        params["finally_steps"] = finally_steps

    return create_rpa_step_from_template(
        category="P_シナリオ整理",
        operation="Try-Catch",
        params=params,
        step_id=step_id,
        description=description or "エラーハンドリング"
    )

# Q_別シナリオ実行・継承
# ====================

@mcp.tool()
def external_run_scenario(
    scenario_name: str,
    uuid: Optional[str] = None,
    wait_for_completion: bool = True,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """別シナリオを実行"""
    params = {"scenario_name": scenario_name, "wait_for_completion": wait_for_completion}
    if uuid:
        params["uuid"] = uuid

    return create_rpa_step_from_template(
        category="Q_別シナリオ実行・継承",
        operation="別シナリオ実行",
        params=params,
        step_id=step_id,
        description=description or f"シナリオ実行: {scenario_name}"
    )

@mcp.tool()
def external_inherit_variables(
    variables: List[str],
    scenario_name: Optional[str] = None,
    uuid: Optional[str] = None,
    overwrite: bool = True,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """親シナリオから変数を継承"""
    params = {"variables": variables, "overwrite": overwrite}
    if scenario_name:
        params["scenario_name"] = scenario_name
    if uuid:
        params["uuid"] = uuid

    return create_rpa_step_from_template(
        category="Q_別シナリオ実行・継承",
        operation="変数継承",
        params=params,
        step_id=step_id,
        description=description or "変数を継承"
    )

@mcp.tool()
def external_inherit_passwords(
    password_ids: List[str],
    scenario_name: Optional[str] = None,
    uuid: Optional[str] = None,
    overwrite: bool = True,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """親シナリオからパスワードを継承"""
    params = {"password_ids": password_ids, "overwrite": overwrite}
    if scenario_name:
        params["scenario_name"] = scenario_name
    if uuid:
        params["uuid"] = uuid

    return create_rpa_step_from_template(
        category="Q_別シナリオ実行・継承",
        operation="パスワード継承",
        params=params,
        step_id=step_id,
        description=description or "パスワードを継承"
    )

@mcp.tool()
def external_inherit_windows(
    windows: List[str],
    scenario_name: Optional[str] = None,
    uuid: Optional[str] = None,
    overwrite: bool = True,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """親シナリオからウィンドウを継承"""
    params = {"windows": windows, "overwrite": overwrite}
    if scenario_name:
        params["scenario_name"] = scenario_name
    if uuid:
        params["uuid"] = uuid

    return create_rpa_step_from_template(
        category="Q_別シナリオ実行・継承",
        operation="ウィンドウ継承",
        params=params,
        step_id=step_id,
        description=description or "ウィンドウを継承"
    )

@mcp.tool()
def external_inherit_excel(
    excel_names: List[str],
    scenario_name: Optional[str] = None,
    uuid: Optional[str] = None,
    overwrite: bool = True,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """親シナリオからエクセルを継承"""
    params = {"excel_names": excel_names, "overwrite": overwrite}
    if scenario_name:
        params["scenario_name"] = scenario_name
    if uuid:
        params["uuid"] = uuid

    return create_rpa_step_from_template(
        category="Q_別シナリオ実行・継承",
        operation="エクセル継承",
        params=params,
        step_id=step_id,
        description=description or "エクセルを継承"
    )

@mcp.tool()
def external_inherit_browsers(
    browsers: List[str],
    scenario_name: Optional[str] = None,
    uuid: Optional[str] = None,
    overwrite: bool = True,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """親シナリオからブラウザを継承"""
    params = {"browsers": browsers, "overwrite": overwrite}
    if scenario_name:
        params["scenario_name"] = scenario_name
    if uuid:
        params["uuid"] = uuid

    return create_rpa_step_from_template(
        category="Q_別シナリオ実行・継承",
        operation="ブラウザ継承",
        params=params,
        step_id=step_id,
        description=description or "ブラウザを継承"
    )

if __name__ == "__main__":
    import sys
    if "--http" in sys.argv:
        mcp.run(transport="http", port=8080)
    else:
        mcp.run(transport="stdio")