#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows環境でのstdioテスト用スクリプト
PyInstallerでビルドして動作確認用
"""

import sys
import os
import json
import time

# 環境設定
os.environ['PYTHONUNBUFFERED'] = '1'
if sys.platform == "win32":
    os.environ['PYTHONIOENCODING'] = 'utf-8'

def main():
    # 起動メッセージを送信
    startup_msg = {"jsonrpc": "2.0", "method": "test.ready", "params": {"status": "ready"}}
    json_str = json.dumps(startup_msg, ensure_ascii=False)
    sys.stdout.write(json_str + "\n")
    sys.stdout.flush()
    
    # stderrにもデバッグ情報を出力
    sys.stderr.write("[TEST] Sent startup message\n")
    sys.stderr.flush()
    
    # 標準入力から読み取りループ
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            data = json.loads(line.strip())
            
            # pingリクエストに応答
            if data.get("method") == "ping":
                response = {
                    "jsonrpc": "2.0",
                    "result": {"pong": True, "timestamp": time.time()},
                    "id": data.get("id")
                }
                json_str = json.dumps(response, ensure_ascii=False)
                sys.stdout.write(json_str + "\n")
                sys.stdout.flush()
                
                sys.stderr.write(f"[TEST] Responded to ping {data.get('id')}\n")
                sys.stderr.flush()
                
        except Exception as e:
            sys.stderr.write(f"[TEST] Error: {e}\n")
            sys.stderr.flush()

if __name__ == "__main__":
    main()
