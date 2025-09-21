#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RPA Agent - JSON-RPC over stdio server
Electronからの要求を受けて、Python側でRPA処理を実行

機能:
1. 接続 (agent.ready通知)
2. 接続の確認 (ping)
3. 操作の実行 (execute)
4. 操作可能一覧の取得 (listOperations)
"""

import asyncio
import json
import sys
import threading
import time
import traceback
from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional
import io
import os

# 標準出力のバッファリングを無効化（重要！）
# PyInstallerでビルドされたバイナリとElectronの通信を確実にするため
os.environ['PYTHONUNBUFFERED'] = '1'

# Windows環境での特別な処理
if sys.platform == "win32":
    # Windows環境でUTF-8を強制
    import locale
    locale.setlocale(locale.LC_ALL, '')
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    # PyInstallerでビルドされている場合の特別な処理
    if hasattr(sys, '_MEIPASS'):
        # 標準入出力を明示的にバイナリモードで再オープンし、UTF-8でラップ
        import msvcrt
        msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
        msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
        
        # UTF-8でラップ（行バッファリング有効）
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)
        sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
else:
    # Unix系の環境
    if hasattr(sys.stdout, 'fileno'):
        try:
            sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 1)  # line buffering
            sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 1)
        except:
            # fdopenが失敗した場合はflushを使用
            pass

from operation_manager import OperationManager


@dataclass
class JsonRpcRequest:
    """JSON-RPC 2.0 リクエスト"""

    jsonrpc: str = "2.0"
    method: str = ""
    params: Dict[str, Any] = None
    id: Optional[Any] = None


@dataclass
class JsonRpcResponse:
    """JSON-RPC 2.0 レスポンス"""

    jsonrpc: str = "2.0"
    result: Any = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[Any] = None


@dataclass
class JsonRpcNotification:
    """JSON-RPC 2.0 通知（レスポンス不要）"""

    jsonrpc: str = "2.0"
    method: str = ""
    params: Dict[str, Any] = None


class RPAAgent:
    """RPA処理を実行するエージェント"""

    def __init__(self):
        """初期化"""
        self.running = True
        self._operation_manager = None  # 遅延初期化

    def start(self):
        """エージェントを開始"""
        # デバッグ用: Windows環境でログファイルに出力
        if sys.platform == "win32" and hasattr(sys, '_MEIPASS'):
            import tempfile
            log_path = os.path.join(tempfile.gettempdir(), 'rpa_agent_debug.log')
            with open(log_path, 'a') as f:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Agent starting...\n")
                f.write(f"Python version: {sys.version}\n")
                f.write(f"Platform: {sys.platform}\n")
                f.write(f"_MEIPASS: {getattr(sys, '_MEIPASS', 'Not PyInstaller')}\n")
                f.write(f"stdout: {sys.stdout}\n")
                f.write(f"stdin: {sys.stdin}\n")
                f.flush()
        
        # 1. 接続: 初期化成功を通知（重い処理の前に送信）
        self.send_notification("agent.ready", {"status": "ready"})
        
        # デバッグ: Windows環境でログファイルに記録
        if sys.platform == "win32" and hasattr(sys, '_MEIPASS'):
            with open(log_path, 'a') as f:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] agent.ready sent\n")
                f.flush()
        
        # 必要になったら初期化（最初のリクエスト時）

        # メインループ
        while self.running:
            try:
                # 標準入力から1行読み込み
                line = sys.stdin.readline()
                if not line:
                    break

                # JSON-RPCリクエストをパース
                try:
                    data = json.loads(line.strip())
                    request = JsonRpcRequest(**data)
                except json.JSONDecodeError as e:
                    self.send_error_response(None, -32700, f"Parse error: {str(e)}")
                    continue
                except Exception as e:
                    self.send_error_response(None, -32600, f"Invalid Request: {str(e)}")
                    continue

                # リクエストを処理（非同期）
                threading.Thread(
                    target=self.handle_request, args=(request,), daemon=True
                ).start()

            except KeyboardInterrupt:
                break
            except Exception as e:
                self.send_notification(
                    "agent.error",
                    {"error": str(e), "traceback": traceback.format_exc()},
                )

    @property
    def operation_manager(self):
        """OperationManagerの遅延初期化"""
        if self._operation_manager is None:
            self._operation_manager = OperationManager()
        return self._operation_manager

    def handle_request(self, request: JsonRpcRequest):
        """リクエストを処理"""
        try:
            # メソッドに応じて処理を振り分け
            if request.method == "ping":
                # 2. 接続の確認
                self.handle_ping(request)
            elif request.method == "execute":
                # 3. 操作の実行
                self.handle_execute(request)
            elif request.method == "listOperations":
                # 4. 操作可能一覧の取得
                self.handle_list_operations(request)
            elif request.method == "getOperationTemplates":
                # 5. 操作テンプレートの取得
                self.handle_get_operation_templates(request)
            elif request.method == "executeOperations":
                # 6. 複数操作の一括実行（ワークフロー実行）
                self.handle_execute_operations(request)
            else:
                self.send_error_response(
                    request.id, -32601, f"Method not found: {request.method}"
                )
        except Exception as e:
            self.send_error_response(request.id, -32603, f"Internal error: {str(e)}")

    def handle_ping(self, request: JsonRpcRequest):
        """pingリクエストを処理 - 接続確認"""
        self.send_response(request.id, {"pong": True, "timestamp": time.time()})

    def handle_execute(self, request: JsonRpcRequest):
        """RPA操作を実行"""
        params = request.params or {}

        # 実行開始を通知
        self.send_notification(
            "task.started",
            {"operation": params.get("operation")},
        )

        try:
            # 非同期処理を同期的に実行
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # 操作を実行
            category = params.get("category")
            subcategory = params.get("subcategory")
            operation = params.get("operation")
            operation_params = params.get("params", {})

            result = loop.run_until_complete(
                self.operation_manager.execute_operation(
                    category, subcategory, operation, operation_params
                )
            )

            # 完了を通知
            self.send_notification("task.completed", {"result": result})

            # レスポンスを返す
            self.send_response(request.id, result)

        except Exception as e:
            # エラー処理
            error_info = {
                "error": str(e),
                "traceback": traceback.format_exc(),
            }

            self.send_notification("task.failed", {"error": error_info})

            self.send_error_response(request.id, -32000, f"Execution failed: {str(e)}")
        finally:
            # イベントループをクリーンアップ
            loop.close()

    def handle_list_operations(self, request: JsonRpcRequest):
        """利用可能な操作リストを返す"""
        operations = self.operation_manager.get_available_operations()
        self.send_response(request.id, {"operations": operations})

    def handle_get_operation_templates(self, request: JsonRpcRequest):
        """操作テンプレートを返す（rpa_operations.jsonの内容）"""
        import json
        import os
        import sys

        try:
            # PyInstallerでビルドされている場合は sys._MEIPASS を使用
            if hasattr(sys, '_MEIPASS'):
                json_path = os.path.join(sys._MEIPASS, "rpa_operations.json")
            else:
                # 開発環境ではファイルの相対パス
                json_path = os.path.join(os.path.dirname(__file__), "rpa_operations.json")
            
            with open(json_path, encoding="utf-8") as f:
                templates = json.load(f)
            self.send_response(request.id, templates)
        except Exception as e:
            self.send_error_response(
                request.id, -32000, f"Failed to load operation templates: {str(e)}"
            )

    def handle_execute_operations(self, request: JsonRpcRequest):
        """複数の操作を一括実行（ワークフロー実行）"""
        params = request.params or {}
        steps = params.get("steps", [])
        mode = params.get("mode", "sequential")  # sequential or parallel (将来対応)

        # ワークフロー開始を通知
        self.send_notification(
            "workflow.started",
            {"steps": len(steps), "mode": mode},
        )

        try:
            # 非同期処理を同期的に実行
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # ワークフローを実行
            results = loop.run_until_complete(
                self.operation_manager.execute_workflow_steps(steps)
            )

            # 完了を通知
            self.send_notification("workflow.completed", {"results": results})

            # レスポンスを返す
            self.send_response(
                request.id,
                {"success": True, "results": results, "stepsExecuted": len(results)},
            )

        except Exception as e:
            # エラー処理
            error_info = {
                "error": str(e),
                "traceback": traceback.format_exc(),
            }

            self.send_notification("workflow.failed", {"error": error_info})
            self.send_error_response(
                request.id, -32000, f"Workflow execution failed: {str(e)}"
            )
        finally:
            # イベントループをクリーンアップ
            loop.close()

    def send_response(self, request_id: Any, result: Any):
        """レスポンスを送信"""
        response = JsonRpcResponse(id=request_id, result=result)
        self.send_json(asdict(response))

    def send_error_response(
        self, request_id: Any, code: int, message: str, data: Any = None
    ):
        """エラーレスポンスを送信"""
        error = {"code": code, "message": message}
        if data:
            error["data"] = data
        response = JsonRpcResponse(id=request_id, error=error)
        self.send_json(asdict(response))

    def send_notification(self, method: str, params: Any = None):
        """通知を送信（レスポンス不要）"""
        notification = JsonRpcNotification(method=method, params=params)
        self.send_json(asdict(notification))

    def send_json(self, data: Dict[str, Any]):
        """JSONデータを標準出力に送信"""
        try:
            json_str = json.dumps(data, ensure_ascii=False)
            sys.stdout.write(json_str + "\n")
            sys.stdout.flush()
        except Exception as e:
            # エラーログ（通常は表示されない）
            sys.stderr.write(f"Failed to send JSON: {e}\n")
            sys.stderr.flush()


def main():
    """エントリーポイント"""
    # 標準エラー出力を無効化（JSONRPCの邪魔にならないように）
    sys.stderr = open("/dev/null", "w") if sys.platform != "win32" else open("nul", "w")

    agent = RPAAgent()
    agent.start()


if __name__ == "__main__":
    main()
