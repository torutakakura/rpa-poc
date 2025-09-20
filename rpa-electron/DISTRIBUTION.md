# 📦 Electron配布ガイド

## 概要

このガイドでは、RPA ElectronアプリケーションをWindows、macOS、Linux向けに配布する方法を説明します。

## 🛠️ セットアップ

### 1. 依存関係のインストール

```bash
cd rpa-electron
pnpm install  # または npm install
```

### 2. Python Agentの準備

Python Agentをバンドルする場合：

```bash
cd ../rpa-agent
./setup.sh
source venv/bin/activate
pyinstaller --onefile --name rpa_agent rpa_agent.py
```

## 📦 ビルド方法

### 自動ビルドスクリプト

```bash
./build.sh
```

このスクリプトは以下を自動で実行します：
1. Python Agentのビルド
2. 依存関係のインストール
3. Electronアプリのビルド
4. プラットフォーム別パッケージの作成

### 手動ビルド

#### 現在のプラットフォーム用
```bash
pnpm run dist
```

#### プラットフォーム別
```bash
pnpm run dist:mac    # macOS (.dmg, .zip)
pnpm run dist:win    # Windows (.exe installer)
pnpm run dist:linux  # Linux (.AppImage, .deb, .rpm)
```

## 🎨 アイコンの準備

### 必要なファイル

1. **macOS**: `build/icon.icns` (1024x1024px)
2. **Windows**: `build/icon.ico` (256x256px, 複数サイズ推奨)
3. **Linux**: `build/icon.png` (512x512px)

### アイコン作成コマンド

#### macOS用 .icns
```bash
# PNGから.icnsを作成
mkdir icon.iconset
# 各サイズのPNGを用意（icon_16x16.png ... icon_512x512@2x.png）
iconutil -c icns icon.iconset -o build/icon.icns
```

#### Windows用 .ico (ImageMagick使用)
```bash
convert icon.png -define icon:auto-resize=256,128,64,48,32,16 build/icon.ico
```

## 🔐 コード署名

### macOS

1. **Developer ID証明書の取得**
   - Apple Developer Programへの登録が必要
   - Xcode > Preferences > Accounts で証明書を管理

2. **署名の設定**
   ```json
   // package.jsonまたはelectron-builder.yml
   "mac": {
     "identity": "Developer ID Application: Your Name (TEAMID)",
     "hardenedRuntime": true,
     "gatekeeperAssess": false
   }
   ```

3. **ノータライズ**
   ```bash
   # .envファイルを作成
   APPLE_ID=your-apple-id@example.com
   APPLE_ID_PASSWORD=app-specific-password
   TEAM_ID=YOUR_TEAM_ID
   ```

### Windows

1. **コード署名証明書の取得**
   - 認証局から証明書を購入（DigiCert、Sectigo等）

2. **署名の設定**
   ```json
   "win": {
     "certificateFile": "path/to/certificate.pfx",
     "certificatePassword": "password"
   }
   ```

## 🚀 配布

### 配布ファイルの場所

ビルド完了後、配布ファイルは `release/` ディレクトリに作成されます：

- **macOS**: 
  - `RPA Tool-1.0.0.dmg` - インストーラー
  - `RPA Tool-1.0.0-mac.zip` - ポータブル版

- **Windows**:
  - `RPA Tool Setup 1.0.0.exe` - インストーラー
  - `RPA Tool 1.0.0.exe` - ポータブル版

- **Linux**:
  - `RPA-Tool-1.0.0.AppImage` - ポータブル版
  - `rpa-tool_1.0.0_amd64.deb` - Debian/Ubuntu用
  - `rpa-tool-1.0.0.x86_64.rpm` - RedHat/Fedora用

### 自動更新の設定

1. **GitHub Releases**を使用する場合：
   ```yml
   # electron-builder.yml
   publish:
     provider: github
     owner: your-username
     repo: your-repo
   ```

2. **リリース作成**:
   ```bash
   # package.jsonのバージョンを更新後
   git tag v1.0.0
   git push origin v1.0.0
   pnpm run dist -- --publish always
   ```

## 🧪 テスト

### ローカルテスト
```bash
# ビルドしたアプリを直接実行
./release/mac/RPA Tool.app/Contents/MacOS/RPA Tool  # macOS
./release/win-unpacked/RPA Tool.exe                   # Windows
./release/linux-unpacked/rpa-tool                     # Linux
```

### インストーラーテスト
各プラットフォームの配布ファイルを実際にインストールして動作確認

## ⚠️ トラブルシューティング

### macOSで「開発元が未確認」エラー
```bash
# アプリを右クリック > 開く
# または System Preferences > Security & Privacy で許可
```

### Windowsで「SmartScreen」警告
- 「詳細情報」をクリック > 「実行」を選択

### Linuxで実行権限エラー
```bash
chmod +x RPA-Tool-1.0.0.AppImage
./RPA-Tool-1.0.0.AppImage
```

### Python Agentが見つからない
- `extraResources`の設定を確認
- Python Agentが正しくビルドされているか確認

## 📝 チェックリスト

配布前の確認事項：

- [ ] アプリのバージョン番号を更新
- [ ] アイコンファイルを配置
- [ ] Python Agentをビルド
- [ ] 各プラットフォームでテスト
- [ ] コード署名（可能な場合）
- [ ] ライセンスファイルを更新
- [ ] READMEを更新
- [ ] リリースノートを作成

## 🔗 参考リンク

- [Electron Builder Documentation](https://www.electron.build/)
- [Apple Developer - Notarizing macOS Software](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)
- [Microsoft - Code Signing](https://docs.microsoft.com/en-us/windows-hardware/drivers/dashboard/get-a-code-signing-certificate)
