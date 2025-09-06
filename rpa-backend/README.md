# 起動方法（rpa-backend / FastAPI）

## 前提
- Python 3.12
- `uv` が利用可能であること
- 初回のみ Playwright のブラウザ（Chromium）をインストール

## 依存の同期（稼働環境）
```bash
cd rpa-backend
uv sync
```

## 仮想環境の有効化（.venv がある場合）
```bash
cd rpa-backend
source .venv/bin/activate
# 無効化する場合: deactivate
```

## セットアップと起動
```bash
cd rpa-backend

# API サーバー起動
uv run uvicorn main:app --reload --host 127.0.0.1 --port 8000
# → http://127.0.0.1:8000/healthz で疎通確認
```

## 主なエンドポイント
- GET /healthz : ヘルスチェック
- GET /steps : 利用可能なステップメタ一覧
- POST /run_scenario : ステップ配列でシナリオ実行
- GET /scenarios / PUT /scenarios/{id} / DELETE /scenarios/{id} : シナリオ一覧・編集・削除

## DB 接続（任意 / Postgres）
- デフォルト接続: host=127.0.0.1 port=55432 user=rpa password=rpa_password db=rpa
- 環境変数で上書き可能: PGHOST / PGPORT / PGUSER / PGPASSWORD / PGDATABASE
