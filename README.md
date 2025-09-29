# RPA POC (Proof of Concept)

RPAツールの自動化機能のPOCプロジェクト


## 構成

```
rpa-poc/
├── rpa-backend/      # FastAPI バックエンドサーバー
├── rpa-electron/     # Electron デスクトップアプリケーション
├── rpa-agent/        # Python JSON-RPCエージェント
├── rpa-mcp/          # MCP (Model Context Protocol) サーバー
├── db/               # PostgreSQL データベース設定
└── docker-compose.yaml
```

## クイックスタート

### 前提条件

- Docker & Docker Compose
- Python 3.12+
- Node.js 23.5.0+ (Electron開発時)
- pnpm (Electron開発時)

### データベースの起動

```bash
# PostgreSQLデータベースの起動
docker-compose up -d postgres

# 起動確認
docker-compose ps

# 接続テスト
docker-compose exec postgres pg_isready -U rpa -d rpa
```

データベースは以下の設定で起動します：
- ホスト: localhost
- ポート: 55432
- データベース名: rpa
- ユーザー: rpa
- パスワード: rpa_password

### 各サービスの起動

#### 1. バックエンドサーバー

```bash
cd rpa-backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# .envファイルにOpenAI APIキーを設定
echo "OPENAI_API_KEY=your_api_key_here" >> .env

# サーバー起動
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

詳細は [rpa-backend/README.md](rpa-backend/README.md) を参照してください。

#### 2. Electronアプリケーション

```bash
cd rpa-electron
pnpm install
pnpm dev
```

詳細は [rpa-electron/README.md](rpa-electron/README.md) を参照してください。

#### 3. Pythonエージェント

```bash
cd rpa-agent
./setup.sh  # または setup.bat (Windows)
python rpa_agent.py
```

詳細は [rpa-agent/README.md](rpa-agent/README.md) を参照してください。

#### 4. MCPサーバー

```bash
cd rpa-mcp
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py --http
```

詳細は [rpa-mcp/README.md](rpa-mcp/README.md) を参照してください。

## アクセスURL

- **バックエンドAPI**: http://localhost:8000
- **API ドキュメント**: http://localhost:8000/docs
- **MCPサーバー**: (HTTPモードで起動)

## 技術スタック

### バックエンド
- **FastAPI**: REST API フレームワーク
- **PostgreSQL**: ベクトルデータベース (pgvector)
- **SQLAlchemy**: ORM
- **Playwright**: 自動化実行
- **Pydantic**: データバリデーション

### デスクトップアプリケーション
- **Electron**: クロスプラットフォーム対応
- **React 19**: UIフレームワーク
- **TypeScript**: 型安全性
- **Vite**: ビルドツール
- **Tailwind CSS**: スタイリング

### エージェント
- **Python**: JSON-RPC over stdio通信
- **pandas**: Excel操作
- **asyncio**: 非同期処理

### MCPサーバー
- **fastmcp**: MCP実装フレームワーク
- **Playwright**: ブラウザ自動化
- **BeautifulSoup**: HTML解析

## Docker操作

```bash
# ログ確認
docker-compose logs -f postgres

# データベース接続
docker-compose exec postgres psql -U rpa -d rpa

# 完全な再起動
docker-compose down
docker-compose up -d
```

## 開発規約（未導入）

- コードフォーマット: `black` (Python), `prettier` (TypeScript/JavaScript)
- 型チェック: `mypy` (Python), `tsc` (TypeScript)
- リンター: `ruff` (Python), `eslint` (TypeScript/JavaScript)
