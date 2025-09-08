# RPA POC (Proof of Concept)

RPAツールの自動化機能のPOCプロジェクト

## 特徴

- **ビジュアルエディタ**: ドラッグ&ドロップでRPA作成可能
- **AI支援機能**: 操作の自動認識と最適化
- **自動化実行**: Playwright使用でWeb自動化対応
- **柔軟性**: カスタムステップの作成と共有が可能

## 構成

```
rpa-poc/
├── rpa-backend/      # FastAPI バックエンドサーバー
├── rpa-front/        # Next.js フロントエンドアプリケーション
├── db/              # PostgreSQL データベース
└── docker-compose.yaml
```

## セットアップ

### 前提条件

- Docker & Docker Compose
- Node.js 18+ (フロントエンド開発時)
- Python 3.12+ (バックエンド開発時)

### インストール手順

#### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd rpa-poc
```

#### 2. Dockerコンテナの起動

```bash
# 全サービスの起動
docker-compose up -d

# 個別起動も可能
docker-compose up -d db        # PostgreSQLのみ
docker-compose up -d backend   # バックエンドのみ
docker-compose up -d frontend  # フロントエンドのみ
```

#### 3. データベースの初期化

```bash
# データベースマイグレーションの実行
docker-compose exec backend python -m alembic upgrade head

# 初期データのシード（オプション）
docker-compose exec backend python scripts/seed_data.py
```

### 開発

#### バックエンド開発

```bash
cd rpa-backend

# 仮想環境の作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt

# 開発サーバーの起動
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### フロントエンド開発

```bash
cd rpa-front

# 依存関係のインストール
npm install

# 開発サーバーの起動
npm run dev
```

### アクセスURL

- **フロントエンド**: http://localhost:3000
- **バックエンドAPI**: http://localhost:8000
- **API ドキュメント**: http://localhost:8000/docs

## 技術スタック

### バックエンド
- **FastAPI**: REST API フレームワーク
- **PostgreSQL**: データベース
- **SQLAlchemy**: ORM
- **Playwright**: 自動化実行
- **Pydantic**: データバリデーション

### フロントエンド
- **Next.js 15**: Reactフレームワーク
- **TypeScript**: 型安全性
- **Tailwind CSS**: スタイリング
- **shadcn/ui**: UIコンポーネント


### Dockerコンテナの再起動

```bash
# ログ確認
docker-compose logs -f [service-name]

# 完全な再構築
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### データベース接続

```bash
# PostgreSQLコンテナの確認
docker-compose ps db

# データベース接続
docker-compose exec db psql -U postgres -d rpa_db
```


## 開発規約（未導入）

- コードフォーマット: `black` (Python), `prettier` (TypeScript/JavaScript)
- 型チェック: `mypy` (Python), `tsc` (TypeScript)
- リンター: `ruff` (Python), `eslint` (TypeScript/JavaScript)
