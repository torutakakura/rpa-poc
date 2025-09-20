#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RPA Agent - Windows対応版
文字エンコーディング問題を修正
"""

import asyncio
import json
import sys
import io
import threading
import time
import traceback
from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional
import os

# Windows環境での文字エンコーディングを修正
if sys.platform == "win32":
    # 標準入出力をUTF-8に設定
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    # 環境変数でもUTF-8を指定
    os.environ['PYTHONIOENCODING'] = 'utf-8'

from operation_manager import OperationManager


@dataclass
class JsonRpcRequest:
    """JSON-RPC 2.0 リクエスト"""
    jsonrpc: str = "2.0"
    method: str = ""
    params: Optional[Dict[str, Any]] = None
    id: Optional[Any] = None


@dataclass
class JsonRpcResponse:
    """JSON-RPC 2.0 レスポンス"""
    jsonrpc: str = "2.0"
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[Any] = None


@dataclass
class JsonRpcNotification:
    """JSON-RPC 2.0 通知"""
    jsonrpc: str = "2.0"
    method: str = ""
    params: Optional[Dict[str, Any]] = None


class RPAAgent:
    """JSON-RPC over stdio で通信するRPAエージェント"""

    def __init__(self, debug=False):
        self.debug = debug
        self.manager = OperationManager()
        self.running = True
        self.tasks = {}
        self.task_counter = 0

    def log(self, message):
        """デバッグログ出力"""
        if self.debug:
            self.send_notification("log", {"message": message, "timestamp": time.time()})

    def send_response(self, id, result=None, error=None):
        """レスポンスを送信"""
        response = JsonRpcResponse(id=id, result=result, error=error)
        response_dict = {k: v for k, v in asdict(response).items() if v is not None}
        # ensure_ascii=Falseで日本語を正しく出力
        print(json.dumps(response_dict, ensure_ascii=False), flush=True)

    def send_notification(self, method, params=None):
        """通知を送信"""
        notification = JsonRpcNotification(method=method, params=params)
        notification_dict = {k: v for k, v in asdict(notification).items() if v is not None}
        # ensure_ascii=Falseで日本語を正しく出力
        print(json.dumps(notification_dict, ensure_ascii=False), flush=True)

    def handle_request(self, request_dict):
        """リクエストを処理"""
        try:
            request = JsonRpcRequest(**request_dict)
            method = request.method
            params = request.params or {}
            id = request.id

            if method == "ping":
                result = {"status": "pong", "timestamp": time.time()}

            elif method == "listOperations":
                operations = self.manager.get_operations_dict()
                result = {"operations": operations, "error": None}

            elif method == "execute":
                category = params.get("category")
                operation = params.get("operation")
                operation_params = params.get("params", {})

                self.log(f"Executing: {category}.{operation}")
                result_data = self.manager.execute_operation(category, operation, operation_params)
                result = asdict(result_data)

            elif method == "run_task":
                task_name = params.get("name", "unnamed_task")
                task_params = params.get("params", {})
                task_id = f"task-{self.task_counter}"
                self.task_counter += 1

                def run_task():
                    self.send_notification("task_started", {"task_id": task_id, "name": task_name})
                    time.sleep(2)  # シミュレート処理
                    self.send_notification("task_completed", {
                        "task_id": task_id,
                        "result": {"status": "success", "data": task_params}
                    })

                thread = threading.Thread(target=run_task)
                self.tasks[task_id] = thread
                thread.start()

                result = {"task_id": task_id, "status": "started"}

            elif method == "cancel_task":
                task_id = params.get("task_id")
                result = {"task_id": task_id, "status": "cancelled"}

            elif method == "get_capabilities":
                result = {
                    "version": "1.0.0",
                    "excel": True,
                    "features": ["file_operations", "excel_operations", "keyboard", "mouse"]
                }

            else:
                # 未知のメソッド
                if id is not None:
                    self.send_response(
                        id,
                        error={
                            "code": -32601,
                            "message": f"Method not found: {method}"
                        }
                    )
                return

            # IDがある場合はレスポンスを返す
            if id is not None:
                self.send_response(id, result=result)

        except Exception as e:
            self.log(f"Error handling request: {e}")
            if "id" in request_dict:
                self.send_response(
                    request_dict["id"],
                    error={
                        "code": -32603,
                        "message": str(e),
                        "data": traceback.format_exc()
                    }
                )

    def run(self):
        """メインループ"""
        # 起動通知
        self.send_notification("agent.ready", {"status": "ready"})

        # メインループ
        while self.running:
            try:
                # 標準入力から読み込み（UTF-8）
                line = sys.stdin.readline()
                if not line:
                    break  # EOF

                line = line.strip()
                if not line:
                    continue

                if self.debug:
                    self.log(f"Received: {line}")

                # JSONパース
                try:
                    request_dict = json.loads(line)
                except json.JSONDecodeError as e:
                    self.send_response(
                        None,
                        error={
                            "code": -32700,
                            "message": f"Parse error: {e}"
                        }
                    )
                    continue

                # リクエスト処理
                self.handle_request(request_dict)

            except KeyboardInterrupt:
                self.running = False
                break
            except Exception as e:
                self.log(f"Unexpected error: {e}")
                continue

        self.log("Agent shutting down")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='RPA Agent - JSON-RPC over stdio server')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()

    agent = RPAAgent(debug=args.debug)
    agent.run()


if __name__ == "__main__":
    main()
