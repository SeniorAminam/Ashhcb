<div align="center">

# 🤖 Ashhcb Bot
### AI Image Transformer on Bale Messenger
**txt2img · img2img · Vision** — powered by Agnes AI (free tier)

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Bale API](https://img.shields.io/badge/Bale%20API-Compatible-34A853?style=flat-square&logo=telegram&logoColor=white)](https://tapi.bale.ai)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-00C853?style=flat-square)]()
[![Free](https://img.shields.io/badge/Free-No%20CC%20Required-FF6F00?style=flat-square)]()

</div>

---

<br>

> **🇮🇷 Ashhcb Bot** یک ربات هوشمند و کاملاً رایگان برای پیام‌رسان **بله** است.  
> با قدرت **Agnes AI** می‌توانید عکس بسازید، عکس را با پرامپت دلخواه تبدیل کنید، و تصاویر را تحلیل کنید.  
> بدون نیاز به کارت بانکی، بدون محدودیت روزانه. فقط یک توکن ربات بله + کلید API رایگان Agnes AI.

<br>

---

## 🚀 Quick Start

```bash
git clone https://github.com/SeniorAminam/Ashhcb.git
cd Ashhcb
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env → BOT_TOKEN + AGNES_API_KEY
python -m src.bot
```

Or with **Docker**:

```bash
docker compose up -d
```

---

## ✨ Features

| | 🇮🇷 فارسی | 🇬🇧 English |
|---|---|---|
| 🖼️ | **ساخت عکس** — هر متنی بنویس، عکس 1024×1024 دریافت کن | **txt2img** — type any prompt, get a 1024×1024 image |
| 📷 | **تبدیل عکس** — عکس + متن بفرست، نسخه ویرایش شده بگیر | **img2img** — send photo + prompt, get AI-edited result |
| 🔍 | **تحلیل تصویر** — عکس بفرست، توضیح کامل فارسی بگیر | **Vision** — upload photo, get detailed Persian analysis |

**All capabilities are free. Zero daily limit. Zero credit card required.**

---

## 🔧 Configuration

```ini
BOT_TOKEN=123456789:abc...        # From @botfather (ble.ir/botfather)
AGNES_API_KEY=sk-...              # From apihub.agnes-ai.com (free)
ADMIN_USER_IDS=1040785496         # Comma-separated admin IDs
RATE_LIMIT_SECONDS=60             # 60s cooldown between requests
```

---

## 🏗️ Architecture

```
┌──────────┐     ┌──────────────┐     ┌──────────────────┐
│   Bale   │────▶│  AIService   │────▶│  Agnes AI API    │
│   User   │◀────│  (Wrapper)   │◀────│  (Free Tier)     │
└──────────┘     └──────┬───────┘     └──────────────────┘
                        │
                 ┌──────┴───────┐
                 │ AgnesService │
                 │  ├─ txt2img  │
                 │  ├─ img2img  │
                 │  └─ vision   │
                 │  └─ catbox   │
                 │     uploader  │
                 └──────────────┘
```

**Key decisions:**
- Single provider (Agnes AI) — no fallback chain, minimal complexity
- img2img uses `/images/generations` + `image_url` (NOT `/images/edits` — upstream bug)
- Catbox.moe for temp image hosting (free, 72h, no auth)
- 60s rate limit per user (fair usage of free tier)

---

## 📁 Project Structure

```
src/
├── bot.py              # Entry point, handler registration
├── config/settings.py  # Env vars & constants
├── handlers/           # start, photo, callback, admin, user_panel, error
├── keyboards/          # reply (menu), inline (model select)
├── services/           # agnes_service, ai_service, storage (SQLite)
└── utils/helpers.py    # resize, format, dimensions
```

---

## 📊 Rate Limits

| Limit | Value |
|-------|-------|
| Per-user cooldown | 60 seconds |
| Agnes API global | ~20 req/min |
| Max image size | 10 MB |
| Max resolution | 1024×1024 (4K capable) |
| Temp image hosting | 72 hours (catbox.moe) |

---

## 🐳 Docker Deployment

```bash
docker compose build --no-cache
docker compose up -d
docker compose logs -f
```

**Update:**
```bash
git pull && docker compose build --no-cache && docker compose up -d
```

---

## 📄 License

**MIT** — see [LICENSE](LICENSE)  
Free to use, modify, and distribute.

---

<div align="center">

**Developed by [Amin Davodian](https://senioramin.com)**  
[📱 @SeniorAminBot](https://ble.ir/SeniorAminBot) · [🐙 GitHub](https://github.com/SeniorAminam) · [💼 LinkedIn](https://linkedin.com/in/SudoAmin)

</div>
