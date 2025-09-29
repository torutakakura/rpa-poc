# RPA Electron

RPA自動化ツール - Electronベースのデスクトップアプリケーション

## 📋 必要要件

- Node.js (v23.5.0以降)
- pnpm (パッケージマネージャー)

## 🚀 環境構築手順

### 1. pnpmのインストール

```bash
# pnpmをグローバルインストール
npm install -g pnpm
```

### 2. 依存関係のインストール

```bash
# プロジェクトルートで実行
pnpm install
```

## 📦 利用可能なコマンド

### 開発環境の起動

```bash
pnpm dev
```
開発モードでアプリケーションを起動します。以下の処理が並行して実行されます：
- Viteの開発サーバー起動（ホットリロード対応）
- Electronのコード監視とトランスパイル
- Electronアプリケーションの起動

### 個別の開発コマンド

```bash
# Vite開発サーバーのみ起動
pnpm dev:vite

# Electronコードの監視・トランスパイル
pnpm dev:electron-watch

# Electronアプリケーションの起動
pnpm dev:electron
```

### ビルド

```bash
# プロジェクト全体のビルド
pnpm build
```
TypeScriptのトランスパイルとViteビルド、Electronコードのビルドを実行します。

### プレビュー

```bash
# ビルドしたアプリケーションのプレビュー
pnpm preview
```

### ディストリビューション作成

```bash
# Windows向けインストーラー作成（デフォルト）
pnpm dist

# Windows向けインストーラー作成（明示的）
pnpm dist:win

# macOS向けインストーラー作成
pnpm dist:mac

# Electronのみのビルド
pnpm dist:electron-only
```

## 🛠️ 技術スタック

### フレームワーク・ツール
- **Electron** (v38.1.0) - デスクトップアプリケーションフレームワーク
- **React** (v19.1.1) - UIライブラリ
- **TypeScript** (v5.9.2) - 型付きJavaScript
- **Vite** (v7.1.5) - ビルドツール・開発サーバー
- **Tailwind CSS** (v4.1.13) - ユーティリティファーストCSSフレームワーク

### UIコンポーネント
- **Radix UI** - アクセシブルなReactコンポーネント群
  - Accordion, Checkbox, Dialog, Label, Progress
  - ScrollArea, Select, Separator, Slot, Switch
  - Tabs, Tooltip
- **Lucide React** - アイコンライブラリ

### ユーティリティ
- **React Router DOM** (v7.9.1) - ルーティング
- **Axios** (v1.12.2) - HTTPクライアント
- **clsx** - クラス名結合ユーティリティ
- **tailwind-merge** - Tailwindクラスのマージユーティリティ
- **class-variance-authority** - バリアントベースのスタイリング

### 開発ツール
- **concurrently** - 複数のコマンドを並行実行
- **cross-env** - クロスプラットフォーム環境変数設定
- **wait-on** - リソースの待機処理
- **electron-builder** - Electronアプリのパッケージング

## 📁 プロジェクト構造

```
rpa-electron/
├── src/              # フロントエンドソースコード
├── electron/         # Electronメインプロセス・プリロードコード
├── dist/            # Viteビルド出力
├── dist-electron/   # Electronビルド出力
├── release/         # パッケージングされたアプリケーション
├── scripts/         # ビルドスクリプト
└── build/           # アプリケーションアイコン等のリソース
```

## 🔧 ビルド設定

### アプリケーション情報
- **App ID**: com.devote.rpa
- **Product Name**: RPA Tool

### 対応プラットフォーム
- **Windows**: NSIS インストーラー (x64)
- **macOS**: DMG イメージ (x64, arm64)

### 追加リソース
ビルド時に `../rpa-agent/dist/` のファイルが `rpa-agent/` として含まれます。

## 🤝 開発チーム

Devote RPA Team

## 📄 ライセンス

ISC License