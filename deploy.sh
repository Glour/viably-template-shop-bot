#!/bin/bash
set -e

echo "🚀 Deploying Shop Bot..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Copy .env.example to .env and configure it."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Create systemd service
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/shop-bot.service > /dev/null <<EOF
[Unit]
Description=Telegram Shop Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(which python3) $(pwd)/bot.py
Restart=always
RestartSec=10
Environment="PATH=/usr/local/bin:/usr/bin:/bin"

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and start service
echo "▶️ Starting service..."
sudo systemctl daemon-reload
sudo systemctl enable shop-bot
sudo systemctl restart shop-bot

echo "✅ Shop Bot deployed successfully!"
echo "📊 Check status: sudo systemctl status shop-bot"
echo "📜 View logs: sudo journalctl -u shop-bot -f"
