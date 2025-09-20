# 📦 RPA Tool ポータブル配布ガイド

## 概要

このガイドでは、Windows/Mac両方で動作するRPA Toolのポータブル配布パッケージの作成方法を説明します。

## 🎯 配布方式の比較

| 方式 | メリット | デメリット | 推奨用途 |
|------|--------|----------|----------|
| **ポータブル版** | クロスプラットフォーム対応<br>軽量（〜100MB） | Python要（配布先） | 技術者向け<br>社内配布 |
| **スタンドアロン版** | Python不要<br>1ファイルで完結 | プラットフォーム別ビルド要<br>大容量（〜200MB） | 一般ユーザー向け |

## 🚀 ポータブル版の作成

### 必要な環境

- Node.js 18以上
- pnpm または npm
- Python 3.8以上（ローカルテスト用）

### ビルド手順

```bash
# 1. ポータブルビルドスクリプトを実行
cd rpa-electron
./build-portable.sh

# 実行後、以下のZIPファイルが作成されます：
# - release/RPA-Tool-Windows-Portable.zip
# - release/RPA-Tool-macOS-Portable.zip
```

### 生成されるファイル

```
release/
├── RPA-Tool-Windows-Portable.zip
│   ├── RPA Tool Setup 1.0.0.exe  # Windowsインストーラー
│   └── README-Windows.txt         # インストール手順書
└── RPA-Tool-macOS-Portable.zip
    ├── RPA Tool-1.0.0.dmg        # macOSインストーラー
    └── README-macOS.txt           # インストール手順書
```

## 📝 配布先での設定

### Windows環境

1. **Python 3.8以上をインストール**
   - [Python公式サイト](https://www.python.org/downloads/)からダウンロード
   - インストール時に「Add Python to PATH」にチェック

2. **RPA Toolをインストール**
   - `RPA Tool Setup 1.0.0.exe`を実行

3. **Python依存関係をインストール**
   ```cmd
   cd "C:\Program Files\RPA Tool\resources\rpa-agent"
   pip install -r requirements.txt
   ```

### macOS環境

1. **Python確認**（通常はプリインストール済み）
   ```bash
   python3 --version
   # Python 3.8未満の場合：
   brew install python3
   ```

2. **RPA Toolをインストール**
   - `RPA Tool-1.0.0.dmg`をマウント
   - RPA Tool.appをApplicationsにドラッグ

3. **Python依存関係をインストール**
   ```bash
   cd "/Applications/RPA Tool.app/Contents/Resources/rpa-agent"
   pip3 install -r requirements.txt
   ```

## 🔧 技術詳細

### アーキテクチャ

```
Electron App
    ↓
[開発環境] → Python script (rpa_agent.py)
[本番環境] → 以下を順に試行：
    1. PyInstaller実行ファイル（rpa_agent.exe/.app）
    2. バンドルPythonスクリプト + システムPython
    3. フォールバックパス
```

### ファイル配置

```
配布パッケージ構造：
RPA Tool.app/Contents/Resources/  (macOS)
C:\Program Files\RPA Tool\resources\  (Windows)
└── rpa-agent/
    ├── rpa_agent.py          # メインスクリプト
    ├── operations/           # 操作モジュール
    ├── schemas/             # スキーマ定義
    ├── requirements.txt     # Python依存関係
    └── run-agent.sh/.bat    # 起動スクリプト
```

### ブリッジ設定の自動検出

`rpa-bridge-portable.ts`は以下の順序でPython Agentを検出：

1. **PyInstaller実行ファイル**（最優先）
2. **バンドルPythonスクリプト** + システムPython
3. **アプリディレクトリ内スクリプト**

Python検出順序（OS別）：
- Windows: `python` → `python3` → `py`
- macOS/Linux: `python3` → `python`

## ⚠️ トラブルシューティング

### 「Python Agentが見つかりません」エラー

**原因と対策：**
1. **Pythonがインストールされていない**
   - Python 3.8以上をインストール
   - PATHに追加されているか確認

2. **依存関係が不足**
   ```bash
   pip install -r requirements.txt
   ```

3. **権限の問題**（macOS）
   ```bash
   chmod +x "/Applications/RPA Tool.app/Contents/Resources/rpa-agent/rpa_agent.py"
   ```

### Windows Defenderの警告

初回起動時：
1. 「詳細情報」をクリック
2. 「実行」を選択

### macOS「開発元が未確認」警告

1. Finderでアプリを右クリック
2. 「開く」を選択
3. または：システム環境設定 → セキュリティとプライバシー → 「このまま開く」

### デバッグモード

開発者ツールを開いてログを確認：
- Windows: `Ctrl + Shift + I`
- macOS: `Cmd + Option + I`

コンソールで確認するポイント：
- Agent path
- Python command
- エラーメッセージ

## 📊 配布チェックリスト

配布前の確認事項：

- [ ] Python 3.8以上の要件を文書化
- [ ] インストール手順書を同梱
- [ ] 依存関係リスト（requirements.txt）を含める
- [ ] テスト環境での動作確認
- [ ] エラーメッセージが分かりやすいか確認
- [ ] サポート連絡先を記載

## 🆚 従来版との違い

| 項目 | 従来版 | ポータブル版 |
|------|--------|------------|
| Python Agent | バイナリ化（〜50MB） | ソースコード（〜1MB） |
| Python要件 | 不要 | 必要（3.8以上） |
| 配布サイズ | 200MB+ | 100MB以下 |
| クロスプラットフォーム | ビルド別 | 共通化可能 |
| 更新容易性 | 再ビルド要 | スクリプト差替可 |

## 💡 推奨事項

### 社内配布の場合

1. **Python環境を標準化**
   - 企業標準のPythonバージョンを決定
   - 必要なパッケージを事前インストール

2. **自動セットアップスクリプトを作成**
   ```bash
   # setup-rpa.sh
   #!/bin/bash
   python3 -m pip install --user -r requirements.txt
   ```

### 外部配布の場合

1. **Python同梱版を検討**
   - Portable Python
   - Anaconda/Miniconda

2. **Dockerコンテナ化**
   - 完全な環境分離
   - 依存関係の固定

## 📞 サポート

問題が発生した場合：
1. デベロッパーツールのコンソールログを確認
2. Python環境を確認（`python --version`）
3. requirements.txtの依存関係を再インストール
