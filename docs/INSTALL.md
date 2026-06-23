<!--
Project:         Ashhcb Bot - AI Image Transformer on Bale
File Path:       docs/INSTALL.md
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
Purpose:         Installation guide (venv + Docker)
License:         MIT
Copyright:       (c) Amin Davodian
-->

# Installation

## Prerequisites

- Python 3.10+
- A Bale bot token ([@botfather](https://ble.ir/botfather))
- A free Agnes AI API key ([agnes-ai.com](https://agnes-ai.com))
- Docker (optional, for containerized deployment)

## Steps

### Option 1: Direct (venv)

```bash
# 1. Clone
git clone https://github.com/SeniorAminam/Ashhcb.git
cd Ashhcb

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure
cp .env.example .env
nano .env
```

### Option 2: Docker

```bash
# 1. Clone
git clone https://github.com/SeniorAminam/Ashhcb.git
cd Ashhcb

# 2. Configure
cp .env.example .env
nano .env

# 3. Build and run
docker compose up -d
docker compose logs -f
```

### .env Configuration

```ini
BOT_TOKEN=123456789:abc...        # From @botfather
AGNES_API_KEY=sk-...              # From Agnes AI console
ADMIN_USER_IDS=1040785496         # Your Bale user ID
RATE_LIMIT_SECONDS=60             # Cooldown between API requests
```

## Verify Installation

```bash
python -c "import sys; sys.path.insert(0, '.'); from src.services.agnes_service import AgnesService; print('OK')"
```
