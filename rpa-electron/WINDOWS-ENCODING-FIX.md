# 🔧 Windows文字エンコーディング問題の解決

## 問題の詳細

Windows環境で以下のエラーが発生：
```
SyntaxError: Unexpected token '�', ..."�/�����i�\��t���j", "... is not valid JSON
```

日本語文字が文字化けして、JSONパースエラーが発生しています。

## 原因

1. **文字エンコーディングの不一致**
   - Python側: Windows標準のCP932（Shift-JIS）で出力
   - Node.js側: UTF-8として受信を期待

2. **標準入出力のデフォルトエンコーディング**
   - Windows: CP932（日本語版）
   - macOS/Linux: UTF-8

## ✅ 解決策（適用済み）

### 1. **Python Agent側の修正**

`rpa-agent/rpa_agent.py`の先頭に以下を追加：

```python
# -*- coding: utf-8 -*-
import io
import os

# Windows環境での文字エンコーディングを修正
if sys.platform == "win32":
    # 標準入出力をUTF-8に設定
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    # 環境変数でもUTF-8を指定
    os.environ['PYTHONIOENCODING'] = 'utf-8'
```

### 2. **Electron側の修正**

`rpa-electron/electron/main/rpa-client.ts`に環境変数を追加：

```typescript
// Windows環境では環境変数でUTF-8を指定
if (process.platform === 'win32') {
  spawnOptions.env = {
    ...process.env,
    PYTHONIOENCODING: 'utf-8',
    PYTHONUTF8: '1'
  }
}
```

## 🚀 修正後の動作確認

### 1. 開発環境の再起動

```powershell
# Ctrl+C で停止後
npm run dev
```

### 2. テストコマンド

```powershell
# PowerShellで実行
cd rpa-agent
$env:PYTHONIOENCODING = "utf-8"
python rpa_agent.py --debug
```

別のターミナルで：
```json
{"jsonrpc":"2.0","method":"listOperations","id":1}
```

## 📝 追加の対策（必要に応じて）

### オプション1: システム全体のUTF-8化

Windows 10 バージョン 1903以降：
1. 設定 → 時刻と言語 → 言語 → 管理用の言語の設定
2. 「システムロケールの変更」
3. 「ベータ：ワールドワイド言語サポートでUnicode UTF-8を使用」にチェック
4. 再起動

### オプション2: Python起動オプション

```powershell
# Python 3.7+
python -X utf8 rpa_agent.py
```

### オプション3: package.jsonスクリプト追加

```json
{
  "scripts": {
    "dev:win": "set PYTHONIOENCODING=utf-8 && electron .",
    "dev:win:ps": "powershell -Command \"$env:PYTHONIOENCODING='utf-8'; electron .\""
  }
}
```

## 🎯 確認ポイント

修正が正しく適用されたかの確認：

1. **Python側の確認**
   ```python
   import sys
   print(sys.stdout.encoding)  # 'utf-8' と表示されればOK
   ```

2. **データの確認**
   - 日本語が正しく表示される
   - JSONパースエラーが発生しない
   - 「アプリ・画面」などの日本語カテゴリが正しく表示される

## ⚠️ 注意事項

1. **既存のファイル**
   - CP932で保存されたファイルを読み込む場合は、明示的にエンコーディングを指定
   ```python
   with open('file.txt', 'r', encoding='cp932') as f:
       content = f.read()
   ```

2. **外部プロセス**
   - 他のWindowsプログラムとの連携時は、エンコーディングに注意

3. **配布版**
   - PyInstallerでビルドする際も同じ設定が必要
   ```python
   # spec ファイルに追加
   runtime_hooks=['encoding_fix.py']
   ```

## ✅ まとめ

これらの修正により：
- Windows環境でも日本語が正しく処理される
- クロスプラットフォーム対応が改善
- JSONパースエラーが解消

修正は既に適用済みなので、アプリケーションを再起動すれば問題が解決するはずです。
