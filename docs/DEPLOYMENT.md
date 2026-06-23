<!--
Project:         Ashhcb Bot - AI Image Transformer on Bale
File Path:       docs/DEPLOYMENT.md
Author:          Amin Davodian
Full Name:       Mohammadamin Davodian
Website:         https://senioramin.com
GitHub:          https://github.com/SeniorAminam
LinkedIn:        https://linkedin.com/in/SudoAmin
Developer:       @SeniorAminBot 
Brand:           SeniorAmin
Created Date:    2026-06-23
Modified Date:   2026-06-23
Version:         1.0.0
Purpose:         Deployment instructions for production (systemd + Docker)
License:         MIT
Copyright:       (c) Amin Davodian
-->

# Deployment

## Production Server (Ubuntu 22.04+)

### Option 1: Direct (venv)

```bash
# 1. System dependencies
sudo apt update && sudo apt install -y python3 python3-venv git

# 2. Clone and setup
git clone https://github.com/SeniorAminam/Ashhcb.git /opt/Ashhcb
cd /opt/Ashhcb
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env                    # Fill in tokens

# 3. Test the bot
python -m src.bot
```

### Option 2: Docker

```bash
# 1. Clone
git clone https://github.com/SeniorAminam/Ashhcb.git /opt/Ashhcb
cd /opt/Ashhcb

# 2. Configure
cp .env.example .env
nano .env

# 3. Build and run
docker compose up -d
docker compose logs -f
```

## Systemd Service

```ini
# /etc/systemd/system/ashhc-bot.service
[Unit]
Description=Ashhcb Bot — AI Image Transformer on Bale
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/Ashhcb
ExecStart=/opt/Ashhcb/venv/bin/python -m src.bot
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now ashhc-bot
sudo systemctl status ashhc-bot
```

## Health Check

The bot runs a health check on startup. Watch logs with:

```bash
# systemd
journalctl -u ashhc-bot -f

# Docker
docker compose logs -f
```

## Updating

```bash
cd /opt/Ashhcb

# Direct
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart ashhc-bot

# Docker
git pull
docker compose build --no-cache
docker compose up -d
```
