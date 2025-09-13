#!/bin/bash

# RPA Agent Setup Script

echo "🐍 Setting up Python RPA Agent..."

# Python仮想環境を作成
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# 仮想環境をアクティベート
source venv/bin/activate

# 依存関係をインストール
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Setup complete!"
echo ""
echo "To run the agent directly:"
echo "  source venv/bin/activate"
echo "  python rpa_agent.py"
echo ""
echo "To build as executable:"
echo "  source venv/bin/activate"
echo "  pyinstaller --onefile --name rpa_agent rpa_agent.py"
