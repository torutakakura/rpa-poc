#!/usr/bin/env python3
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
        self.operation_manager = OperationManager()

    def start(self):
        """エージェントを開始"""
        # 1. 接続: 初期化成功を通知
        self.send_notification("agent.ready", {"status": "ready"})

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

        try:
            # rpa_operations.jsonを読み込む
            json_path = os.path.join(os.path.dirname(__file__), 'rpa_operations.json')
            with open(json_path, encoding='utf-8') as f:
                templates = json.load(f)
            self.send_response(request.id, templates)
        except Exception as e:
            self.send_error_response(request.id, -32000, f"Failed to load operation templates: {str(e)}")

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
            self.send_response(request.id, {
                "success": True,
                "results": results,
                "stepsExecuted": len(results)
            })

        except Exception as e:
            # エラー処理
            error_info = {
                "error": str(e),
                "traceback": traceback.format_exc(),
            }

            self.send_notification("workflow.failed", {"error": error_info})
            self.send_error_response(request.id, -32000, f"Workflow execution failed: {str(e)}")
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
