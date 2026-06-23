<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white&labelColor=1a1a2e">
    <img alt="Python" src="https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white">
  </picture>
  <img alt="Bale API" src="https://img.shields.io/badge/Bale%20API-Compatible-34A853?style=for-the-badge&logo=telegram&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-F0DB4F?style=for-the-badge&logo=open-source-initiative&logoColor=black">
  <img alt="Status" src="https://img.shields.io/badge/Status-Active-00C853?style=for-the-badge">
  <img alt="Free" src="https://img.shields.io/badge/Free-No%20CC%20Required-FF6F00?style=for-the-badge">
</p>

<h1 align="center">🤖 Ashhcb Bot</h1>
<h3 align="center">AI Image Transformer for Bale Messenger</h3>
<p align="center"><b>txt2img</b> · <b>img2img</b> · <b>Vision</b><br><sub>Powered by Agnes AI — Free Tier, Unlimited Daily</sub></p>

<hr>

<br>

# 🇮🇷 فارسی

<p>
ربات <b>Ashhcb</b> یک دستیار هوشمند و کاملاً <b>رایگان</b> برای پیام‌رسان بله است.
با استفاده از قدرت <b>Agnes AI</b>، می‌توانید:
</p>

<ul dir="auto">
  <li><b>🖼️ عکس بسازید</b> — کافیست یک متن بنویسید، هوش مصنوعی تصویر 1024×1024 برایتان می‌سازد</li>
  <li><b>📷 عکس را تبدیل کنید</b> — یک عکس + پرامپت دلخواه بفرستید، نسخه ویرایش‌شده دریافت کنید</li>
  <li><b>🔍 تصاویر را تحلیل کنید</b> — هر عکسی بفرستید، توضیح کامل و دقیق به فارسی بگیرید</li>
</ul>

<p dir="auto">✅ بدون نیاز به کارت بانکی · ✅ بدون محدودیت روزانه · ✅ مبتنی بر هوش مصنوعی قدرتمند</p>

<details>
<summary><b>📋 راهنمای سریع</b></summary>

<br>

**۱. نصب:**

```bash
git clone https://github.com/SeniorAminam/Ashhcb.git
cd Ashhcb
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

**۲. تنظیم:**

```bash
cp .env.example .env
# فایل .env را ویرایش کنید:
#   BOT_TOKEN=توکن_ربات_بله
#   AGNES_API_KEY=کلید_API_Agnes
```

**۳. اجرا:**

```bash
python -m src.bot
```

یا با داکر:

```bash
docker compose up -d
```

</details>

<hr>

# 🇬🇧 English

**Ashhcb Bot** is a free, open-source AI assistant for Bale messenger.  
It leverages **Agnes AI** (free tier, no credit card required) to provide three core capabilities:

<div align="center">

| Icon | Capability | 🇮🇷 | 🇬🇧 |
|:---:|---|---|---|
| 🖼️ | **txt2img** | هر متنی بنویس → عکس بگیر | Type a prompt → get a 1024×1024 image |
| 📷 | **img2img** | عکس + متن بفرست → ویرایش کن | Send photo + prompt → get an AI edit |
| 🔍 | **Vision** | عکس بفرست → توضیح بگیر | Upload photo → get Persian analysis |

</div>

All operations are **completely free** — no daily cap, no hidden costs, no credit card required.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- A Bale bot token from [@botfather](https://ble.ir/botfather)
- A free Agnes AI API key from [apihub.agnes-ai.com](https://apihub.agnes-ai.com)

### Installation

```bash
# Clone the repository
git clone https://github.com/SeniorAminam/Ashhcb.git
cd Ashhcb

# Set up virtual environment (recommended)
python -m venv venv
source venv/bin/activate          # Linux/macOS
# .\venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your tokens:
#   BOT_TOKEN=your_bot_token
#   AGNES_API_KEY=sk-your-agnes-key
#   ADMIN_USER_IDS=your_user_id

# Run the bot
python -m src.bot
```

### Docker Deployment

```bash
# Build and start
docker compose up -d

# View logs
docker compose logs -f

# Update (after git pull)
docker compose build --no-cache && docker compose up -d
```

---

## ⚙️ Configuration

<table>
<tr>
  <th>Variable</th>
  <th>Description</th>
  <th>Required</th>
</tr>
<tr>
  <td><code>BOT_TOKEN</code></td>
  <td>Bale bot token from <a href="https://ble.ir/botfather">@botfather</a></td>
  <td>✅</td>
</tr>
<tr>
  <td><code>AGNES_API_KEY</code></td>
  <td>Free API key from Agnes AI console</td>
  <td>✅</td>
</tr>
<tr>
  <td><code>ADMIN_USER_IDS</code></td>
  <td>Comma-separated Bale user IDs with admin access</td>
  <td>Optional</td>
</tr>
<tr>
  <td><code>RATE_LIMIT_SECONDS</code></td>
  <td>Cooldown between API calls per user (default: 60)</td>
  <td>Optional</td>
</tr>
<tr>
  <td><code>MAX_PHOTO_SIZE_MB</code></td>
  <td>Maximum upload size in MB (default: 10)</td>
  <td>Optional</td>
</tr>
</table>

---

## 🏗️ Architecture

The system follows a clean layered architecture:

```
┌─────────────────────────────────────────────────────────┐
│                      Bale User                          │
└────────────────────┬────────────────────────────────────┘
                     │  Message / Photo
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Polling Bot (python-telegram-bot)           │
│  ┌─────────┐  ┌──────────┐  ┌────────┐  ┌───────────┐  │
│  │ start   │  │ photo    │  │admin   │  │ callback  │  │
│  │ handler │  │ handler  │  │handler │  │ handler   │  │
│  └────┬────┘  └────┬─────┘  └───┬────┘  └─────┬─────┘  │
│       │            │            │              │        │
│       └────────────┴────────────┴──────────────┘        │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   AIService (Orchestrator)                │
│  ┌──────────────────────────────────────────────────┐   │
│  │              AgnesService                         │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  │   │
│  │  │  txt2img   │  │  img2img   │  │  Vision    │  │   │
│  │  │  generate  │  │  transform │  │  analyze   │  │   │
│  │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  │   │
│  │        │               │               │         │   │
│  │        └───────────────┼───────────────┘         │   │
│  │                   ┌────┴────┐                    │   │
│  │                   │ Catbox  │                    │   │
│  │                   │ Upload  │                    │   │
│  │                   └─────────┘                    │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Agnes AI API (apihub.agnes-ai.com)          │
│         /v1/images/generations  ·  /v1/chat/completions │
└─────────────────────────────────────────────────────────┘
```

### Key Design Decisions

<table>
<tr>
  <th>Decision</th>
  <th>Rationale</th>
</tr>
<tr>
  <td><b>Single provider</b> (Agnes AI only)</td>
  <td>No fallback complexity; Agnes supports all three capabilities with generous free tier</td>
</tr>
<tr>
  <td><b>img2img via <code>/images/generations</code></b></td>
  <td>Upstream <code>/images/edits</code> has a UTF-8 decode bug on binary data — using <code>image_url</code> parameter instead</td>
</tr>
<tr>
  <td><b>Catbox.moe for temp hosting</b></td>
  <td>Free, no authentication, 72-hour expiry — used for both img2img and vision image URLs</td>
</tr>
<tr>
  <td><b>60s rate limit per user</b></td>
  <td>Ensures fair usage of the free API tier (20 req/min global limit)</td>
</tr>
</table>

---

## 📁 Project Structure

```
Ashhcb/
│
├── src/                          # Application source code
│   ├── bot.py                    # Entry point, handler registration
│   ├── config/
│   │   └── settings.py           # Environment variables, constants
│   ├── handlers/
│   │   ├── start.py              # /start, text routing, AI generation
│   │   ├── photo.py              # Photo receive + analysis routing
│   │   ├── callback.py           # Inline button callbacks
│   │   ├── admin.py              # Admin panel, stats, broadcast
│   │   ├── user_panel.py         # User history, statistics
│   │   └── error.py              # Global exception handler
│   ├── keyboards/
│   │   ├── reply.py              # Reply keyboards (main menu, panels)
│   │   └── inline.py             # Inline keyboards (model select)
│   ├── services/
│   │   ├── agnes_service.py      # Agnes AI API wrapper (core)
│   │   ├── ai_service.py         # Thin orchestrator layer
│   │   └── storage.py            # SQLite database operations
│   └── utils/
│       └── helpers.py            # Image resize, format, dimensions
│
├── tests/
│   └── test_agnes.py             # Agnes API integration tests
│
├── Dockerfile                    # Multi-stage Docker build
├── docker-compose.yml            # Docker Compose configuration
├── .env.example                  # Environment variable template
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
├── LICENSE                       # MIT License
└── README.md                     # This file
```

---

## 📊 Rate Limits

| Category | Limit |
|----------|-------|
| ⏱️ Per-user cooldown | **60 seconds** between requests |
| 🌐 Agnes AI global | ~20 requests per minute |
| 📤 Max upload size | **10 MB** per photo |
| 🖼️ Max resolution | 1024×1024 (supports up to 4K) |
| ⏳ Temp image hosting | **72 hours** on catbox.moe |

---

## 🛠️ Development

```bash
# Install dev dependencies
pip install ruff mypy pytest

# Lint
ruff check src/

# Type check
mypy src/

# Run tests
python -m pytest tests/ -v
```

---

## 🐳 Docker Reference

```bash
# Build
docker compose build --no-cache

# Start
docker compose up -d

# View logs
docker compose logs -f

# Stop
docker compose down

# Full rebuild after git pull
git pull
docker compose build --no-cache
docker compose up -d
```

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

```
MIT License
Copyright (c) 2026 Amin Davodian
Permission is hereby granted, free of charge, to any person obtaining a copy...
```

---

<p align="center">
  <b>Developed by <a href="https://senioramin.com">Amin Davodian</a></b>
  <br>
  <sub>
  <a href="https://ble.ir/SeniorAminBot">📱 @SeniorAminBot</a> ·
  <a href="https://github.com/SeniorAminam">🐙 GitHub</a> ·
  <a href="https://linkedin.com/in/SudoAmin">💼 LinkedIn</a>
  </sub>
</p>
