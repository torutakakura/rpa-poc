# RPA Backend

RPAバックエンドアプリケーションの環境構築と起動方法について説明します。

## 必要要件

- Python 3.12以上
- pip（Pythonパッケージマネージャー）

## 環境構築

### 1. Pythonバージョンの確認

まず、Python 3.12以上がインストールされていることを確認してください。

```bash
python --version
# または
python3 --version
```

### 2. 仮想環境の作成

プロジェクトのルートディレクトリで以下のコマンドを実行して、仮想環境を作成します。

```bash
python -m venv venv
```

### 3. 仮想環境の有効化

作成した仮想環境を有効化します。

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 4. 依存パッケージのインストール

仮想環境が有効化された状態で、必要なパッケージをインストールします。

```bash
pip install -r requirements.txt
```

## 環境変数の設定

### 1. .envファイルの作成

プロジェクトのルートディレクトリに`.env`ファイルを作成し、以下の環境変数を設定してください。

```env
OPENAI_API_KEY=
DB_HOST=localhost
DB_PORT=55432
DB_NAME=rpa
DB_USER=rpa
DB_PASSWORD=rpa_password
```

### 2. OpenAI APIキーの取得

`OPENAI_API_KEY`には、OpenAIのAPIキーを設定する必要があります。

1. [OpenAI公式サイト](https://platform.openai.com/)にアクセス
2. アカウントを作成またはログイン
3. [APIキーページ](https://platform.openai.com/api-keys)でAPIキーを生成
4. 生成されたAPIキーを`.env`ファイルの`OPENAI_API_KEY=`の後に貼り付け

**注意:** APIキーは秘密情報です。Gitにコミットしないよう、`.gitignore`に`.env`が含まれていることを確認してください。

## アプリケーションの起動

環境構築が完了したら、以下のコマンドでアプリケーションを起動します。

```bash
uvicorn main:app --reload --port 8000
```

起動後、ブラウザで以下のURLにアクセスできます。

- アプリケーション: http://localhost:8000
- APIドキュメント: http://localhost:8000/docs

## トラブルシューティング

### ポートが使用中の場合

ポート8000が既に使用されている場合は、別のポート番号を指定してください。

```bash
uvicorn main:app --reload --port 8001
```

### データベース接続エラーの場合

`.env`ファイルのデータベース設定が正しいことを確認してください。特に以下の項目を確認：

- `DB_HOST`: データベースのホスト名（通常は`localhost`）
- `DB_PORT`: データベースのポート番号（デフォルトは`55432`）
- `DB_NAME`: データベース名
- `DB_USER`: データベースユーザー名
- `DB_PASSWORD`: データベースパスワード

## 開発時の注意事項

- `--reload`オプションは開発時のみ使用してください。本番環境では使用しないでください。
- 環境変数を変更した場合は、アプリケーションを再起動する必要があります。

## ファイル構造

```
rpa-backend/
├── main.py                    # FastAPIアプリケーションのメインファイル
├── builder.py                 # RPAワークフロービルダーのロジック
├── tool_mapping.py            # MCPツール名のマッピング定義
├── requirements.txt           # Python依存パッケージ一覧
├── .env                       # 環境変数設定（Git管理外）
├── .env.example              # 環境変数のサンプル
├── generated_step_list.json   # 生成されたステップリスト（自動生成）
│
├── schema/                    # ステップ定義スキーマ
│   ├── __init__.py
│   ├── base.py               # 基本クラス定義
│   ├── step_factory.py       # ステップファクトリパターン実装
│   ├── step_descriptions.py  # ステップの説明文定義
│   ├── step_tags.py          # ステップのタグ定義
│   ├── basic_steps.py        # 基本的なステップ定義
│   ├── mouse_steps.py        # マウス操作関連のステップ
│   ├── keyboard_steps.py     # キーボード操作関連のステップ
│   ├── window_steps.py       # ウィンドウ操作関連のステップ
│   ├── file_steps.py         # ファイル操作関連のステップ
│   ├── excel_steps.py        # Excel操作関連のステップ
│   ├── variable_steps.py     # 変数操作関連のステップ
│   ├── branching_steps.py    # 条件分岐関連のステップ
│   └── looping_steps.py      # ループ処理関連のステップ
│
├── scripts/                   # ユーティリティスクリプト
│   ├── generate_step_list.py # ステップリスト生成スクリプト
│   └── seed_step_embedding.py # ステップのエンベディング生成
│
└── venv/                      # Python仮想環境（Git管理外）
```

### 主要コンポーネント

#### APIエンドポイント（main.py）
- `/api/workflow/generate` - AIを使用してワークフローを生成
- `/api/workflow/save` - 生成されたワークフローを保存
- `/api/step-list/latest` - 最新のステップリストを取得
- `/health` - ヘルスチェック

#### ワークフロービルダー（builder.py）
- MCPツールを使用したワークフロー構築
- ユーザーのヒアリングに基づくステップ生成
- JSON形式でのワークフロー出力

#### ステップ定義（schema/）
各ステップタイプごとにモジュール化された定義：
- **基本操作**: クリック、入力、待機などの基本的な操作
- **マウス/キーボード**: 詳細な入力デバイス操作
- **ファイル/Excel**: ファイルシステムとExcel操作
- **制御構造**: 条件分岐、ループ、変数管理