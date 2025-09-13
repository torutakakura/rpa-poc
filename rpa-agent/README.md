# RPA Agent - Python JSON-RPC Server

Electron アプリケーションと JSON-RPC over stdio で通信する Python エージェント。

## 🚀 セットアップ

### 1. Python環境の準備

```bash
# セットアップスクリプトを実行
./setup.sh

# または手動でセットアップ
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. 動作確認

```bash
# エージェントを直接実行
python rpa_agent.py

# デバッグモードで実行
python rpa_agent.py --debug
```

## 📋 機能

### 基本機能
- ✅ ping - 接続確認
- ✅ get_capabilities - 利用可能な機能の取得
- ✅ run_task - 非同期タスクの実行
- ✅ cancel_task - タスクのキャンセル

### Excel操作
- ✅ excel_read - Excelファイルの読み込み
- ✅ excel_write - Excelファイルの書き込み

### 通知イベント
- log - ログメッセージ
- task_started - タスク開始
- task_progress - タスク進捗
- task_completed - タスク完了
- task_failed - タスク失敗

## 🔧 JSON-RPC プロトコル

### リクエスト形式
```json
{
  "jsonrpc": "2.0",
  "method": "ping",
  "params": {},
  "id": 1
}
```

### レスポンス形式
```json
{
  "jsonrpc": "2.0",
  "result": {"status": "pong", "timestamp": 1234567890},
  "id": 1
}
```

### 通知形式（レスポンス不要）
```json
{
  "jsonrpc": "2.0",
  "method": "task_progress",
  "params": {
    "task_id": "uuid",
    "progress": 50,
    "message": "Processing..."
  }
}
```

## 📦 ビルド（配布用）

### PyInstallerで単一実行ファイル化

```bash
source venv/bin/activate
pyinstaller --onefile --name rpa_agent rpa_agent.py
```

生成されたファイル：
- `dist/rpa_agent` - 実行ファイル（依存関係すべて含む）

### Electronアプリへの組み込み

1. ビルドした実行ファイルを Electron の resources ディレクトリにコピー
2. Electron側から child_process.spawn で起動

## 🧪 テスト用コマンド

### 手動テスト（echo & cat）

```bash
# ping テスト
echo '{"jsonrpc":"2.0","method":"ping","params":{},"id":1}' | python rpa_agent.py

# 機能取得
echo '{"jsonrpc":"2.0","method":"get_capabilities","params":{},"id":2}' | python rpa_agent.py

# タスク実行
echo '{"jsonrpc":"2.0","method":"run_task","params":{"name":"test","params":{}},"id":3}' | python rpa_agent.py
```

## 📝 拡張方法

### 新しいメソッドの追加

`rpa_agent.py` に以下の形式でメソッドを追加：

```python
def method_your_method_name(self, params: Dict[str, Any]) -> Dict[str, Any]:
    """メソッドの説明"""
    # 処理実装
    return {"result": "success"}
```

メソッド名の規則：
- `method_` プレフィックスが必要
- ドット記法は アンダースコアに変換（例：`file.read` → `method_file_read`）

## 🔍 トラブルシューティング

### Pythonが見つからない
- `python3` コマンドが利用可能か確認
- 仮想環境がアクティブか確認

### openpyxlエラー
- `pip install openpyxl` で手動インストール
- Excel機能が不要な場合は無視可能

### Permission denied
- `chmod +x setup.sh` で実行権限を付与
- `chmod +x dist/rpa_agent` でビルド後のファイルに実行権限を付与
