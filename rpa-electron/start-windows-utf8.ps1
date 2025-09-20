# Windows環境でUTF-8エンコーディングを有効にして起動

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "RPA Electron App (Windows UTF-8)" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# UTF-8環境変数を設定
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

# PowerShellの出力エンコーディングをUTF-8に設定
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "✅ 環境設定完了:" -ForegroundColor Green
Write-Host "   - Python I/O: UTF-8" -ForegroundColor White
Write-Host "   - PowerShell出力: UTF-8" -ForegroundColor White
Write-Host ""

Write-Host "📦 開発サーバーを起動中..." -ForegroundColor Yellow
npm run dev
