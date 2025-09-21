# RPA Agent - Python JSON-RPC Server

Electron アプリケーションと JSON-RPC over stdio で通信する Python エージェント。

## 🚀 セットアップ

### 1. Python 環境の準備

**必要な環境**: Python 3.12 以上

```bash
# セットアップスクリプトを実行
./setup.sh                # macOS/Linux
setup.bat                 # Windows

# または手動でセットアップ
python3.12 -m venv venv   # macOS/Linux
py -3.12 -m venv venv     # Windows
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate.bat # Windows
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

### Excel 操作

- ✅ excel_read - Excel ファイルの読み込み
- ✅ excel_write - Excel ファイルの書き込み

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
  "result": { "status": "pong", "timestamp": 1234567890 },
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

### PyInstaller で単一実行ファイル化

```bash
source venv/bin/activate
pyinstaller --onefile --name rpa_agent rpa_agent.py
```

生成されたファイル：

- `dist/rpa_agent` - 実行ファイル（依存関係すべて含む）

### Electron アプリへの組み込み

1. ビルドした実行ファイルを Electron の resources ディレクトリにコピー
2. Electron 側から child_process.spawn で起動

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

### Python が見つからない

- Python 3.12 がインストールされているか確認: `py -3.12 --version` (Windows) または `python3.12 --version` (macOS/Linux)
- `py -0` コマンドでインストール済みバージョンを確認 (Windows)
- 仮想環境がアクティブか確認

### openpyxl エラー

- `pip install openpyxl` で手動インストール
- Excel 機能が不要な場合は無視可能

### Permission denied

- `chmod +x setup.sh` で実行権限を付与
- `chmod +x dist/rpa_agent` でビルド後のファイルに実行権限を付与
