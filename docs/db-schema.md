# DB スキーマ（シナリオ管理）

本プロジェクトの Postgres 初期化 SQL は `db/init/001_init.sql` にあります。ここでは、主要テーブルと役割・主なカラムをまとめます。

## 概要
- シナリオ定義の「台帳」と、その版管理、実行履歴を管理します。
- 拡張: `pgcrypto`（`gen_random_uuid()` 利用）

## テーブル: `scenarios`
- 目的: シナリオの台帳（論理的なシナリオ単位）
- カラム
  - `id uuid primary key default gen_random_uuid()`
  - `name text not null` シナリオ名
  - `description text` 説明
  - `created_at timestamptz not null default now()`
  - `updated_at timestamptz not null default now()`

## テーブル: `scenario_versions`
- 目的: シナリオの版管理（steps のスナップショットを保持）
- カラム
  - `id uuid primary key default gen_random_uuid()`
  - `scenario_id uuid not null` → `scenarios(id)` 参照（ON DELETE CASCADE）
  - `version integer not null` 同一 `scenario_id` 内でユニーク
  - `steps_json jsonb not null` 実行用ステップ配列（App からそのまま保存）
  - `notes text` 変更ノートなど
  - `created_by text` 作成者（必要なら後でユーザ参照に変更）
  - `created_at timestamptz not null default now()`
- 制約
  - `unique (scenario_id, version)`

## テーブル: `runs`
- 目的: 実行履歴（各実行の状態・ログ・エラー）
- カラム
  - `id uuid primary key default gen_random_uuid()`
  - `scenario_version_id uuid not null` → `scenario_versions(id)` 参照（ON DELETE CASCADE）
  - `status text not null` 実行状態（例: `pending` / `running` / `success` / `failed`）
  - `started_at timestamptz default now()`
  - `finished_at timestamptz` 終了時刻
  - `logs_json jsonb` 実行ログ（配列）
  - `error text` エラーメッセージ


## 接続情報（docker-compose）
- host: `127.0.0.1`
- port: `55432`（ホスト側）
- user: `rpa`
- password: `rpa_password`
- db: `rpa`

## 今後の拡張案
- `run_artifacts`（スクショ/HTML/HAR の参照）
- `scenario_fragments`（共通ステップ断片の再利用）
- 監査列（`updated_by`、`deleted_at` など）
