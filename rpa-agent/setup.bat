@echo off
echo 🐍 Setting up Python RPA Agent...

REM Python仮想環境を作成
if not exist "venv" (
    echo Creating virtual environment with Python 3.12...
    py -3.12 -m venv venv
    if errorlevel 1 (
        echo Python 3.12 not found, trying default python...
        python -m venv venv
    )
)

REM 仮想環境をアクティベート
call venv\Scripts\activate.bat

REM 依存関係をインストール
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo ✅ Setup complete!
echo.
echo To run the agent directly:
echo   venv\Scripts\activate.bat
echo   python rpa_agent.py
echo.
echo To build as executable:
echo   venv\Scripts\activate.bat
echo   pyinstaller --onefile --name rpa_agent rpa_agent.py
