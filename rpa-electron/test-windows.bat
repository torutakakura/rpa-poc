@echo off
REM Windows環境でのRPA Agent接続テストスクリプト

echo ====================================
echo RPA Agent Windows接続テストスクリプト
echo ====================================
echo.

REM Pythonの確認
echo [1] Pythonバージョン確認...
python --version 2>nul
if %errorlevel% neq 0 (
    echo    ERROR: Pythonが見つかりません
    echo    Python 3.8以上をインストールしてください
    echo    https://www.python.org/downloads/
    exit /b 1
) else (
    echo    OK: Pythonが見つかりました
)
echo.

REM Python Agentのテスト起動
echo [2] Python Agentのテスト起動...
cd ..\rpa-agent
echo    現在のディレクトリ: %cd%

REM 仮想環境の確認
if exist venv\Scripts\activate.bat (
    echo    仮想環境をアクティベート中...
    call venv\Scripts\activate.bat
) else (
    echo    仮想環境が見つかりません
    echo    以下を実行してください:
    echo    python -m venv venv
    echo    venv\Scripts\activate.bat
    echo    pip install -r requirements.txt
)
echo.

REM Agentの直接起動テスト
echo [3] Agent起動テスト（Ctrl+Cで停止）...
echo    以下のコマンドを別のコマンドプロンプトで実行:
echo    {"jsonrpc":"2.0","method":"ping","id":1}
echo.
python rpa_agent.py --debug

cd ..\rpa-electron
