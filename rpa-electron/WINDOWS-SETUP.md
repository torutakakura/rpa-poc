# 🪟 Windows開発環境セットアップガイド

## 問題と原因

Windows環境で`rpa-agent`との接続に失敗する主な原因：

1. **Pythonパスの問題**
   - `python3`コマンドが存在しない（Windowsは通常`python`）
   - Python Launcherの`py`コマンドが認識されない

2. **プロセス起動の問題**  
   - `spawn`にWindows固有の設定が必要
   - パス区切り文字の処理

3. **改行コードの問題**
   - Windows: `\r\n`
   - Unix: `\n`

## 🛠️ 解決方法

### 方法1: クイックフィックス（推奨）

`rpa-electron/electron/main/rpa-client.ts`を以下のように修正：

```typescript
// 78-79行目を以下に置き換え
this.process = spawn(this.options.pythonPath!, args, {
  stdio: ['pipe', 'pipe', 'pipe'],
  shell: process.platform === 'win32',  // Windows環境ではshell経由で実行
  windowsHide: true  // コンソールウィンドウを非表示
})
```

### 方法2: Windows対応版ファイルを使用

```bash
# Windows対応版に置き換え
cd rpa-electron/electron/main
mv rpa-client.ts rpa-client.ts.bak
mv rpa-client-windows-fix.ts rpa-client.ts
```

### 方法3: 環境変数でPythonパスを明示

```powershell
# PowerShellで環境変数を設定
$env:PYTHON_PATH = "C:\Python312\python.exe"
# または
$env:PYTHON_PATH = "py -3"
```

## 📋 Windows開発環境のセットアップ手順

### 1. Python環境の確認

```powershell
# コマンドプロンプトまたはPowerShellで実行

# オプション1: 通常のPython
python --version

# オプション2: Python Launcher（推奨）
py -3 --version

# オプション3: python3コマンドのエイリアス作成
# PowerShellの場合
Set-Alias python3 python
```

### 2. Python依存関係のインストール

```powershell
# rpa-agentディレクトリに移動
cd rpa-agent

# 仮想環境の作成（Windows）
python -m venv venv

# 仮想環境の有効化
.\venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt
```

### 3. Electronアプリの起動

```powershell
# rpa-electronディレクトリに移動
cd rpa-electron

# 依存関係のインストール
npm install
# または
pnpm install

# 開発モードで起動
npm run dev
# または
pnpm run dev
```

## 🔧 トラブルシューティング

### エラー: "python3 is not recognized"

**原因**: Windowsでは`python3`コマンドが存在しない

**解決策**:
```powershell
# オプション1: python3.batを作成
echo @python %* > C:\Windows\python3.bat

# オプション2: Python Launcherを使用
# rpa-bridge.tsの44行目を修正
pythonPath: isDev ? (process.platform === 'win32' ? 'py -3' : 'python3') : undefined
```

### エラー: "spawn python ENOENT"

**原因**: PythonがPATHに含まれていない

**解決策**:
```powershell
# Pythonのパスを確認
where python

# 環境変数PATHに追加
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Python312", [EnvironmentVariableTarget]::User)
```

### エラー: "Cannot find module"

**原因**: パス区切り文字の問題

**解決策**: `path.join()`を使用して自動的にOS別のパスを生成

```typescript
// 悪い例
const agentPath = __dirname + '/../../../rpa-agent/rpa_agent.py'

// 良い例
const agentPath = path.join(__dirname, '..', '..', '..', 'rpa-agent', 'rpa_agent.py')
```

## 📝 デバッグ方法

### 1. デベロッパーツールの使用

```
1. Electronアプリを起動
2. F12キーまたはCtrl+Shift+Iでデベロッパーツールを開く
3. Consoleタブでエラーメッセージを確認
```

### 2. ログの追加

`rpa-client.ts`にログを追加：

```typescript
console.log('Python command:', this.options.pythonPath)
console.log('Agent path:', this.options.agentPath)
console.log('Current directory:', process.cwd())
console.log('Platform:', process.platform)
```

### 3. 手動でPython Agentを起動してテスト

```powershell
# rpa-agentディレクトリで
python rpa_agent.py --debug

# 別のターミナルで以下を入力してテスト
{"jsonrpc":"2.0","method":"ping","id":1}
```

## ✅ 推奨される設定

### `package.json`に追加

```json
{
  "scripts": {
    "dev:win": "set NODE_ENV=development && electron .",
    "dev:unix": "NODE_ENV=development electron ."
  }
}
```

### `.env.development`ファイルを作成

```env
# Windows開発環境用設定
PYTHON_CMD=python
# または
PYTHON_CMD=py -3
```

## 🚀 ビルド済み配布版の作成

Windows環境で依存関係不要の配布版を作成：

```powershell
# rpa-agentディレクトリ
cd rpa-agent

# PyInstallerで実行ファイル作成
.\venv\Scripts\activate
pip install pyinstaller
pyinstaller --onefile --name rpa_agent.exe rpa_agent.py

# rpa-electronディレクトリ
cd ..\rpa-electron
npm run dist:win
```

これで、Windows環境でも正常に動作するようになります！
