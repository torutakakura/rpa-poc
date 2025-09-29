# RPA MCP Server

RPAツールをMCP (Model Context Protocol) サーバーとして提供するプロジェクトです。

## 環境要件

- Python 3.12 以上

## 環境構築

### 1. Python仮想環境の作成

プロジェクトのルートディレクトリで以下のコマンドを実行して、Python仮想環境を作成します：

```bash
python -m venv venv
```

### 2. 仮想環境の有効化

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 3. 依存パッケージのインストール

仮想環境を有効化した状態で、必要なパッケージをインストールします：

```bash
pip install -r requirements.txt
```

## サーバーの起動

環境構築が完了したら、以下のコマンドでMCPサーバーを起動します：

```bash
python main.py --http
```

サーバーが正常に起動すると、HTTPモードでMCPサーバーが利用可能になります。

## トラブルシューティング

- Pythonのバージョンが3.12以上であることを確認してください：
  ```bash
  python --version
  ```

- 仮想環境が正しく有効化されているか確認してください。プロンプトに`(venv)`が表示されているはずです。

- 依存パッケージのインストールでエラーが発生した場合は、pipを最新版にアップグレードしてください：
  ```bash
  pip install --upgrade pip
  ```