from fastmcp import FastMCP
import json
from typing import Optional, Dict, Any, List
import uuid
from datetime import datetime
import os
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
    for subcat, operations in category_data.items():
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
            # 空文字列やFalse、0以外の値のみ上書き
            if value != "" and value is not False and value != 0:
                template_params[key] = value
            elif key in template_params and (value == "" or value is False or value == 0):
                # 明示的にデフォルト値が指定された場合も設定
                template_params[key] = value
        
        params = template_params
    
    return create_rpa_step(
        category=category,
        operation=operation,
        params=params,
        step_id=step_id,
        description=description
    )

# A_アプリ・画面 カテゴリ
@mcp.tool()
def app_launch(
    app_name: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None,
    wait_time: Optional[int] = None,
    maximize_window: Optional[bool] = None,
    arguments: Optional[str] = None,
    working_directory: Optional[str] = None
) -> Dict[str, Any]:
    """アプリケーションを起動"""
    params = {"app_path": app_name}
    
    # オプションパラメータを追加
    if wait_time is not None:
        params["wait_time"] = wait_time
    if maximize_window is not None:
        params["maximize_window"] = maximize_window
    if arguments is not None:
        params["arguments"] = arguments
    if working_directory is not None:
        params["working_directory"] = working_directory
    
    return create_rpa_step_from_template(
        category="A_アプリ・画面",
        operation="起動",
        params=params,
        subcategory="アプリ",
        step_id=step_id,
        description=description or f"{app_name}を起動"
    )

@mcp.tool()
def app_launch_wait(
    app_name: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None,
    maximize_window: Optional[bool] = None,
    arguments: Optional[str] = None,
    working_directory: Optional[str] = None
) -> Dict[str, Any]:
    """アプリケーションを起動して終了を待つ"""
    params = {"app_path": app_name}
    
    if maximize_window is not None:
        params["maximize_window"] = maximize_window
    if arguments is not None:
        params["arguments"] = arguments
    if working_directory is not None:
        params["working_directory"] = working_directory
    
    return create_rpa_step_from_template(
        category="A_アプリ・画面",
        operation="起動（終了待ち）",
        params=params,
        subcategory="アプリ",
        step_id=step_id,
        description=description or f"{app_name}を起動して終了を待つ"
    )

@mcp.tool()
def window_remember_active(
    reference_id: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """最前面のウィンドウを記憶"""
    return create_rpa_step(
        category="A_アプリ・画面",
        operation="最前画面を覚える",
        params={"reference_id": reference_id},
        step_id=step_id,
        description=description or "最前面のウィンドウを記憶"
    )

@mcp.tool()
def window_remember_by_name(
    window_name: str,
    reference_id: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None,
    partial_match: bool = False
) -> Dict[str, Any]:
    """ウィンドウ名でウィンドウを記憶"""
    return create_rpa_step(
        category="A_アプリ・画面",
        operation="画面を覚える（名前）",
        params={
            "window_name": window_name,
            "reference_id": reference_id,
            "partial_match": partial_match
        },
        step_id=step_id,
        description=description or f"{window_name}を記憶"
    )

@mcp.tool()
def window_switch_by_ref(
    reference_id: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """参照IDでウィンドウを切り替え"""
    return create_rpa_step(
        category="A_アプリ・画面",
        operation="切り替え（参照ID）",
        params={"reference_id": reference_id},
        step_id=step_id,
        description=description or f"ウィンドウ{reference_id}に切り替え"
    )

@mcp.tool()
def window_switch_by_name(
    window_name: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None,
    partial_match: bool = False
) -> Dict[str, Any]:
    """ウィンドウ名でウィンドウを切り替え"""
    return create_rpa_step(
        category="A_アプリ・画面",
        operation="切り替え（名前）",
        params={
            "window_name": window_name,
            "partial_match": partial_match
        },
        step_id=step_id,
        description=description or f"{window_name}に切り替え"
    )

@mcp.tool()
def window_get_name(
    storage_key: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ウィンドウ名を取得"""
    return create_rpa_step(
        category="A_アプリ・画面",
        operation="画面の名前を取得",
        params={"storage_key": storage_key},
        step_id=step_id,
        description=description or "ウィンドウ名を取得"
    )

@mcp.tool()
def window_move(
    x: int,
    y: int,
    width: int,
    height: int,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ウィンドウを移動・リサイズ"""
    return create_rpa_step(
        category="A_アプリ・画面",
        operation="移動",
        params={
            "x": x,
            "y": y,
            "width": width,
            "height": height
        },
        step_id=step_id,
        description=description or f"ウィンドウを({x}, {y})に移動"
    )

@mcp.tool()
def window_maximize_minimize(
    action: str = "maximize",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ウィンドウを最大化/最小化"""
    return create_rpa_step(
        category="A_アプリ・画面",
        operation="最大化/最小化",
        params={"action": action},
        step_id=step_id,
        description=description or f"ウィンドウを{action}"
    )

@mcp.tool()
def screenshot(
    save_path: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None,
    capture_area: str = "full_screen",
    x: int = 0,
    y: int = 0,
    width: int = 0,
    height: int = 0
) -> Dict[str, Any]:
    """スクリーンショットを撮る"""
    params = {
        "save_path": save_path,
        "capture_area": capture_area
    }
    if capture_area == "coordinates":
        params["coordinates"] = {
            "x": x,
            "y": y,
            "width": width,
            "height": height
        }
    
    return create_rpa_step(
        category="A_アプリ・画面",
        operation="スクリーンショットを撮る",
        params=params,
        step_id=step_id,
        description=description or "スクリーンショットを撮る"
    )

# B_待機・終了・エラー カテゴリ
@mcp.tool()
def wait_seconds(
    seconds: int,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """指定秒数待機"""
    return create_rpa_step_from_template(
        category="B_待機・終了・エラー",
        operation="秒",
        params={"wait_seconds": seconds},
        step_id=step_id,
        description=description or f"{seconds}秒待機"
    )

@mcp.tool()
def wait_for_image(
    image_path: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None,
    accuracy: float = 0.8,
    search_area: str = "full_screen",
    x: int = 0,
    y: int = 0,
    width: int = 0,
    height: int = 0
) -> Dict[str, Any]:
    """画像が表示されるまで待機"""
    params = {
        "image_path": image_path,
        "accuracy": accuracy,
        "search_area": search_area
    }
    if search_area == "coordinates":
        params["coordinates"] = {
            "x": x,
            "y": y,
            "width": width,
            "height": height
        }
    
    return create_rpa_step(
        category="B_待機・終了・エラー",
        operation="画像出現を待つ",
        params=params,
        step_id=step_id,
        description=description or "画像出現を待つ"
    )

@mcp.tool()
def continue_confirm(
    message: str,
    title: str = "続行確認",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """続行確認ダイアログを表示"""
    return create_rpa_step(
        category="B_待機・終了・エラー",
        operation="続行確認",
        params={
            "message": message,
            "title": title
        },
        step_id=step_id,
        description=description or "続行確認"
    )

@mcp.tool()
def continue_confirm_timer(
    message: str,
    countdown_seconds: int = 10,
    title: str = "続行確認",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """タイマー付き続行確認ダイアログを表示"""
    return create_rpa_step(
        category="B_待機・終了・エラー",
        operation="タイマー付き続行確認（秒）",
        params={
            "message": message,
            "title": title,
            "countdown_seconds": countdown_seconds
        },
        step_id=step_id,
        description=description or f"{countdown_seconds}秒後に自動続行"
    )

@mcp.tool()
def change_command_interval(
    interval_ms: int,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """コマンド間の待機時間を変更"""
    return create_rpa_step(
        category="B_待機・終了・エラー",
        operation="コマンド間待機時間を変更",
        params={"interval_ms": interval_ms},
        step_id=step_id,
        description=description or f"コマンド間隔を{interval_ms}msに変更"
    )

@mcp.tool()
def force_exit(
    exit_code: int = 0,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """作業を強制終了"""
    return create_rpa_step(
        category="B_待機・終了・エラー",
        operation="作業強制終了",
        params={"exit_code": exit_code},
        step_id=step_id,
        description=description or "作業を強制終了"
    )

@mcp.tool()
def raise_error(
    error_message: str,
    error_code: str = "",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """エラーを発生させる"""
    return create_rpa_step(
        category="B_待機・終了・エラー",
        operation="エラー発生",
        params={
            "error_message": error_message,
            "error_code": error_code
        },
        step_id=step_id,
        description=description or "エラーを発生"
    )

# C_マウス カテゴリ
@mcp.tool()
def mouse_move_to(
    x: int,
    y: int,
    step_id: Optional[str] = None,
    description: Optional[str] = None,
    move_speed: str = "normal"
) -> Dict[str, Any]:
    """マウスを座標に移動"""
    return create_rpa_step(
        category="C_マウス",
        operation="移動（座標）",
        params={
            "x": x,
            "y": y,
            "move_speed": move_speed
        },
        step_id=step_id,
        description=description or f"マウスを({x}, {y})に移動"
    )

@mcp.tool()
def mouse_move_by(
    dx: int,
    dy: int,
    step_id: Optional[str] = None,
    description: Optional[str] = None,
    move_speed: str = "normal"
) -> Dict[str, Any]:
    """マウスを相対移動"""
    return create_rpa_step(
        category="C_マウス",
        operation="移動（距離）",
        params={
            "dx": dx,
            "dy": dy,
            "move_speed": move_speed
        },
        step_id=step_id,
        description=description or f"マウスを({dx}, {dy})相対移動"
    )

@mcp.tool()
def mouse_move_to_image(
    image_path: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None,
    accuracy: float = 0.8,
    click_position: str = "center",
    offset_x: int = 0,
    offset_y: int = 0
) -> Dict[str, Any]:
    """画像を認識してマウスを移動"""
    return create_rpa_step(
        category="C_マウス",
        operation="移動（画像認識）",
        params={
            "image_path": image_path,
            "accuracy": accuracy,
            "click_position": click_position,
            "offset_x": offset_x,
            "offset_y": offset_y
        },
        step_id=step_id,
        description=description or "画像にマウスを移動"
    )

@mcp.tool()
def mouse_drag_drop_coords(
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    step_id: Optional[str] = None,
    description: Optional[str] = None,
    drag_speed: str = "normal"
) -> Dict[str, Any]:
    """座標間でドラッグ＆ドロップ"""
    return create_rpa_step(
        category="C_マウス",
        operation="ドラッグ＆ドロップ（座標）",
        params={
            "start_x": start_x,
            "start_y": start_y,
            "end_x": end_x,
            "end_y": end_y,
            "drag_speed": drag_speed
        },
        step_id=step_id,
        description=description or "ドラッグ＆ドロップ"
    )

@mcp.tool()
def mouse_drag_drop_distance(
    dx: int,
    dy: int,
    step_id: Optional[str] = None,
    description: Optional[str] = None,
    drag_speed: str = "normal"
) -> Dict[str, Any]:
    """距離でドラッグ＆ドロップ"""
    return create_rpa_step(
        category="C_マウス",
        operation="ドラッグ＆ドロップ（距離）",
        params={
            "dx": dx,
            "dy": dy,
            "drag_speed": drag_speed
        },
        step_id=step_id,
        description=description or f"({dx}, {dy})ドラッグ"
    )

@mcp.tool()
def mouse_drag_drop_images(
    start_image_path: str,
    end_image_path: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None,
    accuracy: float = 0.8,
    drag_speed: str = "normal"
) -> Dict[str, Any]:
    """画像間でドラッグ＆ドロップ"""
    return create_rpa_step(
        category="C_マウス",
        operation="ドラッグ＆ドロップ（画像認識）",
        params={
            "start_image_path": start_image_path,
            "end_image_path": end_image_path,
            "accuracy": accuracy,
            "drag_speed": drag_speed
        },
        step_id=step_id,
        description=description or "画像間でドラッグ＆ドロップ"
    )

@mcp.tool()
def mouse_click(
    button: str = "left",
    click_type: str = "single",
    x: Optional[int] = None,
    y: Optional[int] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """マウスクリック"""
    params = {
        "button": button,
        "click_type": click_type
    }
    if x is not None:
        params["x"] = x
    if y is not None:
        params["y"] = y
    
    return create_rpa_step(
        category="C_マウス",
        operation="マウスクリック",
        params=params,
        step_id=step_id,
        description=description or f"{button}クリック"
    )

@mcp.tool()
def mouse_scroll(
    direction: str = "down",
    amount: int = 3,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """マウススクロール"""
    return create_rpa_step(
        category="C_マウス",
        operation="スクロール",
        params={
            "direction": direction,
            "amount": amount
        },
        step_id=step_id,
        description=description or f"{direction}に{amount}スクロール"
    )

# D_キーボード カテゴリ
@mcp.tool()
def keyboard_type_text(
    text: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None,
    typing_speed: Optional[str] = None,
    clear_before: Optional[bool] = None
) -> Dict[str, Any]:
    """文字を入力"""
    params = {"text": text}
    
    if typing_speed is not None:
        params["typing_speed"] = typing_speed
    if clear_before is not None:
        params["clear_before"] = clear_before
    
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
    text: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None,
    clear_before: bool = False
) -> Dict[str, Any]:
    """文字を貼り付け"""
    return create_rpa_step(
        category="D_キーボード",
        operation="文字（貼り付け）",
        params={
            "text": text,
            "clear_before": clear_before
        },
        step_id=step_id,
        description=description or "テキストを貼り付け"
    )

@mcp.tool()
def keyboard_type_password(
    password_key: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None,
    clear_before: bool = False,
    encrypted: bool = True
) -> Dict[str, Any]:
    """パスワードを入力"""
    return create_rpa_step(
        category="D_キーボード",
        operation="パスワード",
        params={
            "password_key": password_key,
            "clear_before": clear_before,
            "encrypted": encrypted
        },
        step_id=step_id,
        description=description or "パスワードを入力"
    )

@mcp.tool()
def keyboard_shortcut(
    keys: List[str],
    step_id: Optional[str] = None,
    description: Optional[str] = None,
    hold_duration: int = 0
) -> Dict[str, Any]:
    """ショートカットキーを押す"""
    return create_rpa_step(
        category="D_キーボード",
        operation="ショートカットキー",
        params={
            "keys": keys,
            "hold_duration": hold_duration
        },
        step_id=step_id,
        description=description or f"{'+'.join(keys)}を押す"
    )

@mcp.tool()
def keyboard_press_key(
    key: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """キーを押す"""
    # ショートカットキーとして処理
    return create_rpa_step_from_template(
        category="D_キーボード",
        operation="ショートカットキー",
        params={"keys": [key], "hold_duration": 0},
        subcategory="入力",
        step_id=step_id,
        description=description or f"{key}キーを押す"
    )

# E_記憶 カテゴリ
@mcp.tool()
def memory_store_text(
    storage_key: str,
    value: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """文字を記憶"""
    return create_rpa_step(
        category="E_記憶",
        operation="文字",
        params={
            "storage_key": storage_key,
            "value": value
        },
        step_id=step_id,
        description=description or f"{storage_key}に文字を記憶"
    )

@mcp.tool()
def memory_store_password(
    storage_key: str,
    value: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None,
    encrypted: bool = True
) -> Dict[str, Any]:
    """パスワードを記憶"""
    return create_rpa_step(
        category="E_記憶",
        operation="パスワード",
        params={
            "storage_key": storage_key,
            "value": value,
            "encrypted": encrypted
        },
        step_id=step_id,
        description=description or f"{storage_key}にパスワードを記憶"
    )

@mcp.tool()
def memory_store_env_info(
    storage_key: str,
    info_type: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """環境情報を記憶"""
    return create_rpa_step(
        category="E_記憶",
        operation="環境情報",
        params={
            "storage_key": storage_key,
            "info_type": info_type
        },
        step_id=step_id,
        description=description or f"{info_type}を記憶"
    )

@mcp.tool()
def memory_store_date(
    storage_key: str,
    date_type: str = "today",
    date_format: str = "yyyy/MM/dd",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """日付を記憶"""
    return create_rpa_step(
        category="E_記憶",
        operation="日付",
        params={
            "storage_key": storage_key,
            "date_type": date_type,
            "format": date_format
        },
        step_id=step_id,
        description=description or f"{date_type}を記憶"
    )

@mcp.tool()
def memory_store_time(
    storage_key: str,
    time_format: str = "HH:mm:ss",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """時刻を記憶"""
    return create_rpa_step(
        category="E_記憶",
        operation="時刻",
        params={
            "storage_key": storage_key,
            "format": time_format
        },
        step_id=step_id,
        description=description or "現在時刻を記憶"
    )

@mcp.tool()
def memory_calculate(
    storage_key: str,
    expression: str,
    decimal_places: int = 2,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """計算結果を記憶"""
    return create_rpa_step(
        category="E_記憶",
        operation="計算",
        params={
            "storage_key": storage_key,
            "expression": expression,
            "decimal_places": decimal_places
        },
        step_id=step_id,
        description=description or "計算結果を記憶"
    )

@mcp.tool()
def memory_random_number(
    storage_key: str,
    min_value: int = 0,
    max_value: int = 100,
    number_type: str = "integer",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """乱数を記憶"""
    return create_rpa_step(
        category="E_記憶",
        operation="乱数",
        params={
            "storage_key": storage_key,
            "min": min_value,
            "max": max_value,
            "type": number_type
        },
        step_id=step_id,
        description=description or f"{min_value}〜{max_value}の乱数を記憶"
    )

@mcp.tool()
def memory_clipboard_content(
    storage_key: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """クリップボードの内容を記憶"""
    return create_rpa_step(
        category="E_記憶",
        operation="コピー内容",
        params={"storage_key": storage_key},
        step_id=step_id,
        description=description or "クリップボード内容を記憶"
    )

@mcp.tool()
def memory_copy_to_clipboard(
    value: str,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """クリップボードにコピー"""
    return create_rpa_step(
        category="E_記憶",
        operation="クリップボードへコピー",
        params={"value": value},
        step_id=step_id,
        description=description or "クリップボードにコピー"
    )

@mcp.tool()
def memory_user_input(
    storage_key: str,
    prompt: str,
    input_type: str = "text",
    default_value: str = "",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """実行中にユーザー入力を取得"""
    return create_rpa_step(
        category="E_記憶",
        operation="実行中に入力",
        params={
            "storage_key": storage_key,
            "prompt": prompt,
            "input_type": input_type,
            "default_value": default_value
        },
        step_id=step_id,
        description=description or "ユーザー入力を取得"
    )

# F_文字抽出 カテゴリ
@mcp.tool()
def text_extract_brackets(
    storage_key: str,
    source_text: str,
    bracket_type: str = "parentheses",
    occurrence: int = 1,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """括弧内の文字を抽出"""
    return create_rpa_step(
        category="F_文字抽出",
        operation="括弧・引用符号から",
        params={
            "storage_key": storage_key,
            "source_text": source_text,
            "bracket_type": bracket_type,
            "occurrence": occurrence
        },
        step_id=step_id,
        description=description or "括弧内文字を抽出"
    )

@mcp.tool()
def text_extract_delimiter(
    storage_key: str,
    source_text: str,
    delimiter: str = ",",
    position: int = 1,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """区切り文字で分割して抽出"""
    return create_rpa_step(
        category="F_文字抽出",
        operation="区切り文字から",
        params={
            "storage_key": storage_key,
            "source_text": source_text,
            "delimiter": delimiter,
            "position": position
        },
        step_id=step_id,
        description=description or "区切り文字で抽出"
    )

@mcp.tool()
def text_remove_whitespace(
    storage_key: str,
    source_text: str,
    remove_newlines: bool = True,
    remove_spaces: bool = True,
    remove_tabs: bool = True,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """改行・空白を削除"""
    return create_rpa_step(
        category="F_文字抽出",
        operation="改行・空白を削除",
        params={
            "storage_key": storage_key,
            "source_text": source_text,
            "remove_newlines": remove_newlines,
            "remove_spaces": remove_spaces,
            "remove_tabs": remove_tabs
        },
        step_id=step_id,
        description=description or "空白文字を削除"
    )

@mcp.tool()
def text_extract_from_path(
    storage_key: str,
    file_path: str,
    extract_type: str = "filename",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ファイルパスから情報を抽出"""
    return create_rpa_step(
        category="F_文字抽出",
        operation="ファイルパスから",
        params={
            "storage_key": storage_key,
            "file_path": file_path,
            "extract_type": extract_type
        },
        step_id=step_id,
        description=description or f"パスから{extract_type}を抽出"
    )

@mcp.tool()
def text_match_pattern(
    storage_key: str,
    source_text: str,
    pattern: str,
    regex: bool = False,
    occurrence: int = 1,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """パターンにマッチする文字を抽出"""
    return create_rpa_step(
        category="F_文字抽出",
        operation="ルールにマッチ",
        params={
            "storage_key": storage_key,
            "source_text": source_text,
            "pattern": pattern,
            "regex": regex,
            "occurrence": occurrence
        },
        step_id=step_id,
        description=description or "パターンマッチで抽出"
    )

@mcp.tool()
def text_replace(
    storage_key: str,
    source_text: str,
    find: str,
    replace: str,
    replace_all: bool = True,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """文字を置換"""
    return create_rpa_step(
        category="F_文字抽出",
        operation="置換",
        params={
            "storage_key": storage_key,
            "source_text": source_text,
            "find": find,
            "replace": replace,
            "replace_all": replace_all
        },
        step_id=step_id,
        description=description or "文字を置換"
    )

@mcp.tool()
def text_convert_case(
    storage_key: str,
    source_text: str,
    conversion_type: str = "uppercase",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """文字変換（大文字/小文字等）"""
    return create_rpa_step(
        category="F_文字抽出",
        operation="文字変換",
        params={
            "storage_key": storage_key,
            "source_text": source_text,
            "conversion_type": conversion_type
        },
        step_id=step_id,
        description=description or f"{conversion_type}に変換"
    )

# G_分岐 カテゴリ
@mcp.tool()
def branch_string(
    left_value: str,
    operator: str,
    right_value: str,
    true_steps: List[Dict] = None,
    false_steps: List[Dict] = None,
    case_sensitive: bool = True,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """文字列条件で分岐"""
    return create_rpa_step(
        category="G_分岐",
        operation="文字列",
        params={
            "left_value": left_value,
            "operator": operator,
            "right_value": right_value,
            "case_sensitive": case_sensitive,
            "true_steps": true_steps or [],
            "false_steps": false_steps or []
        },
        step_id=step_id,
        description=description or "文字列条件で分岐"
    )

@mcp.tool()
def branch_number(
    left_value: float,
    operator: str,
    right_value: float,
    true_steps: List[Dict] = None,
    false_steps: List[Dict] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """数値条件で分岐"""
    return create_rpa_step(
        category="G_分岐",
        operation="数値",
        params={
            "left_value": left_value,
            "operator": operator,
            "right_value": right_value,
            "true_steps": true_steps or [],
            "false_steps": false_steps or []
        },
        step_id=step_id,
        description=description or "数値条件で分岐"
    )

@mcp.tool()
def branch_file_exists(
    path: str,
    check_type: str = "exists",
    true_steps: List[Dict] = None,
    false_steps: List[Dict] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ファイル/フォルダの存在で分岐"""
    return create_rpa_step(
        category="G_分岐",
        operation="ファイル・フォルダの有/無を確認",
        params={
            "path": path,
            "check_type": check_type,
            "true_steps": true_steps or [],
            "false_steps": false_steps or []
        },
        step_id=step_id,
        description=description or "ファイル存在確認で分岐"
    )

@mcp.tool()
def branch_image(
    image_path: str,
    accuracy: float = 0.8,
    search_area: str = "full_screen",
    found_steps: List[Dict] = None,
    not_found_steps: List[Dict] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """画像検出で分岐"""
    return create_rpa_step(
        category="G_分岐",
        operation="画像",
        params={
            "image_path": image_path,
            "accuracy": accuracy,
            "search_area": search_area,
            "found_steps": found_steps or [],
            "not_found_steps": not_found_steps or []
        },
        step_id=step_id,
        description=description or "画像検出で分岐"
    )

# H_繰り返し カテゴリ
@mcp.tool()
def loop_repeat(
    loop_type: str = "count",
    count: int = 10,
    condition: str = "",
    max_iterations: int = 1000,
    index_storage_key: str = "",
    loop_steps: List[Dict] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """繰り返し処理"""
    return create_rpa_step(
        category="H_繰り返し",
        operation="繰り返し",
        params={
            "loop_type": loop_type,
            "count": count,
            "condition": condition,
            "max_iterations": max_iterations,
            "index_storage_key": index_storage_key,
            "loop_steps": loop_steps or []
        },
        step_id=step_id,
        description=description or f"{count}回繰り返し"
    )

@mcp.tool()
def loop_break(
    condition: str = "",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """繰り返しを抜ける"""
    return create_rpa_step(
        category="H_繰り返し",
        operation="繰り返しを抜ける",
        params={"condition": condition},
        step_id=step_id,
        description=description or "繰り返しを抜ける"
    )

@mcp.tool()
def loop_continue(
    condition: str = "",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """繰り返しの最初に戻る"""
    return create_rpa_step(
        category="H_繰り返し",
        operation="繰り返しの最初に戻る",
        params={"condition": condition},
        step_id=step_id,
        description=description or "繰り返しの最初に戻る"
    )

# I_ファイル・フォルダ カテゴリ
@mcp.tool()
def file_open(
    file_path: str,
    application: str = "default",
    wait_for_open: bool = True,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ファイルを開く"""
    return create_rpa_step(
        category="I_ファイル・フォルダ",
        operation="ファイル開く",
        params={
            "file_path": file_path,
            "application": application,
            "wait_for_open": wait_for_open
        },
        step_id=step_id,
        description=description or f"{file_path}を開く"
    )

@mcp.tool()
def file_move(
    source_path: str,
    destination_path: str,
    overwrite: bool = False,
    create_directory: bool = True,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ファイルを移動"""
    return create_rpa_step(
        category="I_ファイル・フォルダ",
        operation="ファイル移動",
        params={
            "source_path": source_path,
            "destination_path": destination_path,
            "overwrite": overwrite,
            "create_directory": create_directory
        },
        step_id=step_id,
        description=description or "ファイルを移動"
    )

@mcp.tool()
def file_read(
    file_path: str,
    storage_key: str,
    encoding: str = "utf-8",
    read_mode: str = "text",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ファイルを読み込む"""
    return create_rpa_step(
        category="I_ファイル・フォルダ",
        operation="ファイル読み込む",
        params={
            "file_path": file_path,
            "storage_key": storage_key,
            "encoding": encoding,
            "read_mode": read_mode
        },
        step_id=step_id,
        description=description or f"{file_path}を読み込む"
    )

@mcp.tool()
def file_write(
    file_path: str,
    content: str,
    encoding: str = "utf-8",
    write_mode: str = "overwrite",
    create_directory: bool = True,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ファイルに書き込む"""
    return create_rpa_step(
        category="I_ファイル・フォルダ",
        operation="ファイル書き込む",
        params={
            "file_path": file_path,
            "content": content,
            "encoding": encoding,
            "write_mode": write_mode,
            "create_directory": create_directory
        },
        step_id=step_id,
        description=description or f"{file_path}に書き込む"
    )

@mcp.tool()
def folder_open(
    folder_path: str,
    explorer_window: bool = True,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """フォルダを開く"""
    return create_rpa_step(
        category="I_ファイル・フォルダ",
        operation="フォルダ開く",
        params={
            "folder_path": folder_path,
            "explorer_window": explorer_window
        },
        step_id=step_id,
        description=description or f"{folder_path}を開く"
    )

@mcp.tool()
def folder_create(
    folder_path: str,
    create_parents: bool = True,
    exist_ok: bool = True,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """フォルダを作成"""
    return create_rpa_step(
        category="I_ファイル・フォルダ",
        operation="フォルダ作成",
        params={
            "folder_path": folder_path,
            "create_parents": create_parents,
            "exist_ok": exist_ok
        },
        step_id=step_id,
        description=description or f"{folder_path}を作成"
    )

@mcp.tool()
def file_rename(
    target_path: str,
    new_name: str,
    keep_extension: bool = True,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ファイル・フォルダ名を変更"""
    return create_rpa_step(
        category="I_ファイル・フォルダ",
        operation="ファイル・フォルダ名の変更",
        params={
            "target_path": target_path,
            "new_name": new_name,
            "keep_extension": keep_extension
        },
        step_id=step_id,
        description=description or "名前を変更"
    )

@mcp.tool()
def file_copy(
    source_path: str,
    destination_path: str,
    overwrite: bool = False,
    copy_permissions: bool = True,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ファイル・フォルダをコピー"""
    return create_rpa_step(
        category="I_ファイル・フォルダ",
        operation="ファイル・フォルダをコピー",
        params={
            "source_path": source_path,
            "destination_path": destination_path,
            "overwrite": overwrite,
            "copy_permissions": copy_permissions
        },
        step_id=step_id,
        description=description or "コピー"
    )

@mcp.tool()
def file_delete(
    target_path: str,
    move_to_trash: bool = True,
    confirm: bool = True,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ファイル・フォルダを削除"""
    return create_rpa_step(
        category="I_ファイル・フォルダ",
        operation="ファイル・フォルダを削除",
        params={
            "target_path": target_path,
            "move_to_trash": move_to_trash,
            "confirm": confirm
        },
        step_id=step_id,
        description=description or f"{target_path}を削除"
    )

# J_エクセル・CSV カテゴリ
@mcp.tool()
def excel_open_book(
    file_path: str,
    reference_id: str,
    read_only: bool = False,
    password: str = "",
    update_links: bool = False,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """Excelブックを開く"""
    return create_rpa_step(
        category="J_エクセル・CSV",
        operation="ブックを開く",
        params={
            "file_path": file_path,
            "reference_id": reference_id,
            "read_only": read_only,
            "password": password,
            "update_links": update_links
        },
        step_id=step_id,
        description=description or f"{file_path}を開く"
    )

@mcp.tool()
def excel_save_book(
    reference_id: str,
    save_as: bool = False,
    file_path: str = "",
    file_format: str = "xlsx",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """Excelブックを保存"""
    params = {
        "reference_id": reference_id,
        "save_as": save_as,
        "file_format": file_format
    }
    if file_path:
        params["file_path"] = file_path
    
    return create_rpa_step(
        category="J_エクセル・CSV",
        operation="ブックを保存",
        params=params,
        step_id=step_id,
        description=description or "ブックを保存"
    )

@mcp.tool()
def excel_close_book(
    reference_id: str,
    save_changes: bool = True,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """Excelブックを閉じる"""
    return create_rpa_step(
        category="J_エクセル・CSV",
        operation="ブックを閉じる",
        params={
            "reference_id": reference_id,
            "save_changes": save_changes
        },
        step_id=step_id,
        description=description or "ブックを閉じる"
    )

@mcp.tool()
def excel_get_cell(
    reference_id: str,
    range: str,
    storage_key: str,
    value_type: str = "value",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """セルの値を取得"""
    return create_rpa_step(
        category="J_エクセル・CSV",
        operation="値を取得",
        params={
            "reference_id": reference_id,
            "range": range,
            "storage_key": storage_key,
            "value_type": value_type
        },
        step_id=step_id,
        description=description or f"{range}の値を取得"
    )

@mcp.tool()
def excel_set_cell(
    reference_id: str,
    range: str,
    value: str,
    value_type: str = "value",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """セルに値を入力"""
    return create_rpa_step(
        category="J_エクセル・CSV",
        operation="値を入力",
        params={
            "reference_id": reference_id,
            "range": range,
            "value": value,
            "value_type": value_type
        },
        step_id=step_id,
        description=description or f"{range}に値を入力"
    )

# L_ウェブブラウザ カテゴリ
@mcp.tool()
def browser_open(
    url: str,
    browser: Optional[str] = None,
    incognito: Optional[bool] = None,
    maximize: Optional[bool] = None,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ブラウザを開く"""
    params = {"url": url}
    
    if browser is not None:
        params["browser"] = browser
    if incognito is not None:
        params["incognito"] = incognito
    if maximize is not None:
        params["maximize"] = maximize
    
    return create_rpa_step_from_template(
        category="L_ウェブブラウザ",
        operation="ブラウザを開く",
        params=params,
        step_id=step_id,
        description=description or f"{url}を開く"
    )

@mcp.tool()
def browser_close(
    target: str = "current",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ブラウザを閉じる"""
    return create_rpa_step(
        category="L_ウェブブラウザ",
        operation="ブラウザを閉じる",
        params={"target": target},
        step_id=step_id,
        description=description or "ブラウザを閉じる"
    )

@mcp.tool()
def browser_navigate(
    url: str,
    wait_for_load: bool = True,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ページ移動"""
    return create_rpa_step(
        category="L_ウェブブラウザ",
        operation="ページ移動",
        params={
            "url": url,
            "wait_for_load": wait_for_load
        },
        step_id=step_id,
        description=description or f"{url}へ移動"
    )

@mcp.tool()
def browser_click(
    selector: str,
    selector_type: str = "css",
    wait_before: int = 0,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ブラウザ要素をクリック"""
    return create_rpa_step(
        category="L_ウェブブラウザ",
        operation="クリック",
        params={
            "selector": selector,
            "selector_type": selector_type,
            "wait_before": wait_before
        },
        step_id=step_id,
        description=description or "要素をクリック"
    )

@mcp.tool()
def browser_input(
    selector: str,
    text: str,
    selector_type: str = "css",
    clear_before: bool = True,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ブラウザ要素に入力"""
    return create_rpa_step(
        category="L_ウェブブラウザ",
        operation="入力",
        params={
            "selector": selector,
            "selector_type": selector_type,
            "text": text,
            "clear_before": clear_before
        },
        step_id=step_id,
        description=description or "テキストを入力"
    )

@mcp.tool()
def browser_select(
    selector: str,
    value: str,
    selector_type: str = "css",
    by: str = "value",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ブラウザ要素を選択"""
    return create_rpa_step(
        category="L_ウェブブラウザ",
        operation="選択",
        params={
            "selector": selector,
            "selector_type": selector_type,
            "value": value,
            "by": by
        },
        step_id=step_id,
        description=description or "要素を選択"
    )

@mcp.tool()
def browser_read(
    selector: str,
    storage_key: str,
    selector_type: str = "css",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ブラウザ要素を読み取り"""
    return create_rpa_step(
        category="L_ウェブブラウザ",
        operation="読み取り",
        params={
            "selector": selector,
            "selector_type": selector_type,
            "storage_key": storage_key
        },
        step_id=step_id,
        description=description or "要素を読み取り"
    )

@mcp.tool()
def browser_wait(
    selector: str,
    selector_type: str = "css",
    timeout: int = 30,
    condition: str = "visible",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ブラウザ要素を待機"""
    return create_rpa_step(
        category="L_ウェブブラウザ",
        operation="待機",
        params={
            "selector": selector,
            "selector_type": selector_type,
            "timeout": timeout,
            "condition": condition
        },
        step_id=step_id,
        description=description or "要素を待機"
    )

@mcp.tool()
def browser_scroll(
    direction: str = "down",
    amount: int = 300,
    element_selector: str = "",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ブラウザをスクロール"""
    params = {
        "direction": direction,
        "amount": amount
    }
    if element_selector:
        params["element_selector"] = element_selector
    
    return create_rpa_step(
        category="L_ウェブブラウザ",
        operation="スクロール",
        params=params,
        step_id=step_id,
        description=description or f"{direction}に{amount}スクロール"
    )

@mcp.tool()
def browser_screenshot(
    save_path: str,
    full_page: bool = False,
    element_selector: str = "",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ブラウザのスクリーンショット"""
    params = {
        "save_path": save_path,
        "full_page": full_page
    }
    if element_selector:
        params["element_selector"] = element_selector
    
    return create_rpa_step(
        category="L_ウェブブラウザ",
        operation="スクリーンショット",
        params=params,
        step_id=step_id,
        description=description or "スクリーンショットを撮る"
    )

@mcp.tool()
def browser_execute_js(
    script: str,
    return_value: bool = False,
    storage_key: str = "",
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """JavaScriptを実行"""
    params = {
        "script": script,
        "return_value": return_value
    }
    if storage_key:
        params["storage_key"] = storage_key
    
    return create_rpa_step(
        category="L_ウェブブラウザ",
        operation="JavaScript実行",
        params=params,
        step_id=step_id,
        description=description or "JavaScriptを実行"
    )

@mcp.tool()
def browser_refresh(
    wait_for_load: bool = True,
    hard_refresh: bool = False,
    step_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """ブラウザを更新"""
    return create_rpa_step(
        category="L_ウェブブラウザ",
        operation="更新",
        params={
            "wait_for_load": wait_for_load,
            "hard_refresh": hard_refresh
        },
        step_id=step_id,
        description=description or "ページを更新"
    )

if __name__ == "__main__":
    import sys
    if "--http" in sys.argv:
        mcp.run(transport="http", port=8080)
    else:
        mcp.run(transport="stdio")