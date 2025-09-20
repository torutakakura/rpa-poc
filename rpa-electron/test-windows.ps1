# Windows環境でのRPA Agent接続テストスクリプト (PowerShell版)

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "RPA Agent Windows接続テストスクリプト" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# 1. Pythonの確認
Write-Host "[1] Python環境の確認..." -ForegroundColor Yellow

$pythonCommands = @("python", "python3", "py", "py -3")
$pythonFound = $false
$workingCommand = ""

foreach ($cmd in $pythonCommands) {
    try {
        $output = & cmd /c "$cmd --version 2>&1"
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✓ '$cmd' コマンドが使用可能: $output" -ForegroundColor Green
            if (-not $pythonFound) {
                $pythonFound = $true
                $workingCommand = $cmd
            }
        }
    } catch {
        Write-Host "   × '$cmd' コマンドが見つかりません" -ForegroundColor Gray
    }
}

if (-not $pythonFound) {
    Write-Host "   ERROR: Pythonが見つかりません" -ForegroundColor Red
    Write-Host "   Python 3.8以上をインストールしてください" -ForegroundColor Red
    Write-Host "   https://www.python.org/downloads/" -ForegroundColor Blue
    exit 1
}

Write-Host ""
Write-Host "   推奨: '$workingCommand' を使用します" -ForegroundColor Green
Write-Host ""

# 2. 環境変数PATHの確認
Write-Host "[2] Python PATH確認..." -ForegroundColor Yellow
$pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Path
if ($pythonPath) {
    Write-Host "   Pythonパス: $pythonPath" -ForegroundColor Green
} else {
    Write-Host "   警告: PythonがPATHに含まれていない可能性があります" -ForegroundColor Yellow
}
Write-Host ""

# 3. rpa-agentディレクトリの確認
Write-Host "[3] RPA Agentディレクトリ確認..." -ForegroundColor Yellow
$agentPath = Join-Path $PSScriptRoot "..\rpa-agent"
if (Test-Path $agentPath) {
    Write-Host "   ✓ RPA Agentディレクトリが存在: $agentPath" -ForegroundColor Green
} else {
    Write-Host "   ERROR: RPA Agentディレクトリが見つかりません" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 4. 必要なファイルの確認
Write-Host "[4] 必要なファイルの確認..." -ForegroundColor Yellow
$requiredFiles = @(
    "rpa_agent.py",
    "operation_manager.py",
    "requirements.txt"
)

foreach ($file in $requiredFiles) {
    $filePath = Join-Path $agentPath $file
    if (Test-Path $filePath) {
        Write-Host "   ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "   × $file が見つかりません" -ForegroundColor Red
    }
}
Write-Host ""

# 5. package.jsonの設定提案
Write-Host "[5] 推奨設定..." -ForegroundColor Yellow
Write-Host "   rpa-bridge.ts の44行目を以下のように修正:" -ForegroundColor White
Write-Host "   pythonPath: isDev ? (process.platform === 'win32' ? '$workingCommand' : 'python3') : undefined" -ForegroundColor Cyan
Write-Host ""

# 6. テスト起動
Write-Host "[6] Agent起動テスト準備..." -ForegroundColor Yellow
Write-Host "   以下のコマンドでAgentをテスト起動できます:" -ForegroundColor White
Write-Host ""
Write-Host "   cd $agentPath" -ForegroundColor Cyan
Write-Host "   $workingCommand rpa_agent.py --debug" -ForegroundColor Cyan
Write-Host ""
Write-Host "   別のターミナルで以下を送信してテスト:" -ForegroundColor White
Write-Host '   {"jsonrpc":"2.0","method":"ping","id":1}' -ForegroundColor Cyan
Write-Host ""

Write-Host "====================================" -ForegroundColor Green
Write-Host "テスト完了" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
