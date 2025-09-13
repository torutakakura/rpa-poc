#!/usr/bin/env python3
"""
RPA Agent - JSON-RPC over stdio server
Electronからの要求を受けて、Python側でRPA処理を実行
"""

import sys
import json
import time
import traceback
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict
import threading
import uuid

# Excel操作用（オプション）
try:
    import openpyxl
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False


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
        self.running_tasks = {}
        self.debug_mode = False
        
    def send_response(self, response: JsonRpcResponse):
        """レスポンスを標準出力に送信"""
        response_json = json.dumps(asdict(response))
        sys.stdout.write(response_json + "\n")
        sys.stdout.flush()
        
    def send_notification(self, method: str, params: Dict[str, Any]):
        """通知を送信（進捗報告など）"""
        notification = JsonRpcNotification(method=method, params=params)
        notification_json = json.dumps(asdict(notification))
        sys.stdout.write(notification_json + "\n")
        sys.stdout.flush()
        
    def log(self, message: str, level: str = "info"):
        """ログを通知として送信"""
        self.send_notification("log", {
            "level": level,
            "message": message,
            "timestamp": time.time()
        })
        
    # ===========================================
    # RPC メソッド実装
    # ===========================================
    
    def method_ping(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """接続確認用"""
        return {"status": "pong", "timestamp": time.time()}
    
    def method_get_capabilities(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """利用可能な機能を返す"""
        return {
            "excel": EXCEL_AVAILABLE,
            "version": "1.0.0",
            "methods": [
                "ping",
                "get_capabilities",
                "run_task",
                "cancel_task",
                "excel_read",
                "excel_write"
            ]
        }
    
    def method_run_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """非同期タスクを開始"""
        task_id = str(uuid.uuid4())
        task_name = params.get("name", "unknown")
        task_params = params.get("params", {})
        
        # 非同期でタスクを実行
        def run_async():
            try:
                self.send_notification("task_started", {
                    "task_id": task_id,
                    "name": task_name
                })
                
                # サンプル：進捗を送信しながら処理
                for i in range(5):
                    time.sleep(1)
                    self.send_notification("task_progress", {
                        "task_id": task_id,
                        "progress": (i + 1) * 20,
                        "message": f"Processing step {i + 1}/5"
                    })
                
                self.send_notification("task_completed", {
                    "task_id": task_id,
                    "result": {"status": "success", "data": task_params}
                })
                
            except Exception as e:
                self.send_notification("task_failed", {
                    "task_id": task_id,
                    "error": str(e)
                })
            finally:
                if task_id in self.running_tasks:
                    del self.running_tasks[task_id]
        
        thread = threading.Thread(target=run_async)
        thread.daemon = True
        self.running_tasks[task_id] = thread
        thread.start()
        
        return {"task_id": task_id, "status": "started"}
    
    def method_cancel_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """タスクをキャンセル"""
        task_id = params.get("task_id")
        if task_id in self.running_tasks:
            # 実際のキャンセル処理は実装が必要
            del self.running_tasks[task_id]
            return {"status": "cancelled", "task_id": task_id}
        return {"status": "not_found", "task_id": task_id}
    
    def method_excel_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Excelファイルを読み込む"""
        if not EXCEL_AVAILABLE:
            raise Exception("Excel support not available. Install openpyxl.")
        
        file_path = params.get("file_path")
        sheet_name = params.get("sheet_name", None)
        range_spec = params.get("range", None)
        
        try:
            workbook = openpyxl.load_workbook(file_path, read_only=True)
            sheet = workbook[sheet_name] if sheet_name else workbook.active
            
            data = []
            for row in sheet.iter_rows(values_only=True):
                data.append(list(row))
            
            workbook.close()
            
            return {
                "file_path": file_path,
                "sheet_name": sheet.title,
                "data": data,
                "rows": len(data),
                "columns": len(data[0]) if data else 0
            }
        except Exception as e:
            raise Exception(f"Excel read error: {str(e)}")
    
    def method_excel_write(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Excelファイルに書き込む"""
        if not EXCEL_AVAILABLE:
            raise Exception("Excel support not available. Install openpyxl.")
        
        file_path = params.get("file_path")
        sheet_name = params.get("sheet_name", "Sheet1")
        data = params.get("data", [])
        
        try:
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.title = sheet_name
            
            for row_idx, row_data in enumerate(data, 1):
                for col_idx, value in enumerate(row_data, 1):
                    sheet.cell(row=row_idx, column=col_idx, value=value)
            
            workbook.save(file_path)
            workbook.close()
            
            return {
                "file_path": file_path,
                "sheet_name": sheet_name,
                "rows_written": len(data),
                "status": "success"
            }
        except Exception as e:
            raise Exception(f"Excel write error: {str(e)}")
    
    def handle_request(self, request_json: str):
        """JSON-RPCリクエストを処理"""
        try:
            # JSONパース
            request_data = json.loads(request_json)
            request = JsonRpcRequest(**request_data)
            
            # デバッグログ
            if self.debug_mode:
                self.log(f"Received request: {request.method}", "debug")
            
            # メソッド名から実際のメソッドを取得
            method_name = f"method_{request.method.replace('.', '_')}"
            if not hasattr(self, method_name):
                raise AttributeError(f"Method not found: {request.method}")
            
            method = getattr(self, method_name)
            result = method(request.params or {})
            
            # レスポンスを送信
            if request.id is not None:  # 通知でない場合のみレスポンスを返す
                response = JsonRpcResponse(id=request.id, result=result)
                self.send_response(response)
                
        except json.JSONDecodeError as e:
            error_response = JsonRpcResponse(
                id=None,
                error={"code": -32700, "message": "Parse error", "data": str(e)}
            )
            self.send_response(error_response)
            
        except AttributeError as e:
            if hasattr(request, 'id'):
                error_response = JsonRpcResponse(
                    id=request.id,
                    error={"code": -32601, "message": "Method not found", "data": str(e)}
                )
                self.send_response(error_response)
                
        except Exception as e:
            if hasattr(request, 'id'):
                error_response = JsonRpcResponse(
                    id=request.id,
                    error={"code": -32603, "message": "Internal error", "data": str(e)}
                )
                self.send_response(error_response)
            self.log(f"Error: {traceback.format_exc()}", "error")
    
    def run(self):
        """メインループ：標準入力からリクエストを読み取る"""
        self.log("RPA Agent started", "info")
        self.send_notification("agent_ready", {"version": "1.0.0"})
        
        try:
            for line in sys.stdin:
                line = line.strip()
                if line:
                    self.handle_request(line)
        except KeyboardInterrupt:
            self.log("Agent interrupted", "info")
        except Exception as e:
            self.log(f"Fatal error: {str(e)}", "error")
        finally:
            self.log("Agent stopped", "info")


def main():
    """エントリーポイント"""
    # 標準エラー出力を無効化（JSONRPCの邪魔にならないように）
    sys.stderr = open('/dev/null', 'w') if sys.platform != 'win32' else open('nul', 'w')
    
    agent = RPAAgent()
    
    # コマンドライン引数でデバッグモード
    if "--debug" in sys.argv:
        agent.debug_mode = True
    
    agent.run()


if __name__ == "__main__":
    main()
