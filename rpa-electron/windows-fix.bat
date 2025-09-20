@echo off
REM Windows環境の文字エンコーディング問題修正スクリプト

echo ====================================
echo Windows文字エンコーディング問題修正
echo ====================================
echo.

REM 1. Python側の修正を適用
echo [1] Python Agentに修正を適用中...
cd ..\rpa-agent

REM rpa_agent.pyのバックアップ
copy rpa_agent.py rpa_agent.py.bak

REM Windowsテスト
echo [2] 修正版のテスト実行...
echo    UTF-8エンコーディングでPython Agentを起動
echo.

REM UTF-8モードで実行
set PYTHONIOENCODING=utf-8
chcp 65001 >nul
python rpa_agent_windows_fix.py --debug

cd ..\rpa-electron
