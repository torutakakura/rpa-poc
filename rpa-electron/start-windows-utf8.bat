@echo off
REM Windows環境でUTF-8エンコーディングを有効にして起動

echo ====================================
echo RPA Electron App (Windows UTF-8)
echo ====================================
echo.

REM UTF-8環境変数を設定
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

REM コードページをUTF-8に変更（オプション）
chcp 65001 >nul 2>&1

echo 環境設定完了:
echo   - Python I/O: UTF-8
echo   - コードページ: 65001 (UTF-8)
echo.

echo 開発サーバーを起動中...
npm run dev

pause
