<!--
Project:         Ashhcb Bot - AI Image Transformer on Bale
File Path:       README.md
Author:          Amin Davodian
Full Name:       Mohammadamin Davodian
Website:         https://senioramin.com
GitHub:          https://github.com/SeniorAminam
LinkedIn:        https://linkedin.com/in/SudoAmin
Developer:       @SeniorAminBot
Brand:           SeniorAmin
Created Date:    2026-06-23
Modified Date:   2026-06-23
Version:         4.0.2
Purpose:         Project README (Persian + English)
License:         MIT
Copyright:       (c) Amin Davodian
-->

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Bale%20API-Compatible-34A853?style=for-the-badge&logo=telegram&logoColor=white" alt="Bale API">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="MIT">
  <img src="https://img.shields.io/badge/Status-Active-00C853?style=for-the-badge" alt="Status">
  <img src="https://img.shields.io/badge/Free-No%20CC%20Required-FF6F00?style=for-the-badge" alt="Free">
</p>

<h1 align="center">🤖 Ashhcb Bot</h1>
<h3 align="center">AI Image Transformer on Bale Messenger</h3>
<p align="center"><b>txt2img · img2img · Vision</b> — powered by Agnes AI</p>

<br>

<div dir="rtl" align="right">

---

# 🇮🇷 فارسی

## 🤖 ربات Ashhcb

**ربات هوشمند و رایگان بله** برای ساخت عکس از متن، تبدیل عکس با پرامپت، و تحلیل تصاویر — با قدرت هوش مصنوعی **Agnes AI**.

### ✨ قابلیت‌ها

| | قابلیت | توضیح |
|---|---|---|
| 🖼️ | **ساخت عکس** (txt2img) | هر متنی بنویس → عکس 1024×1024 در ~۲۵ ثانیه |
| 📷 | **شروع تبدیل عکس** (img2img) | عکس + متن بفرست → نسخه ویرایش شده دریافت کن |
| 🔍 | **تحلیل تصویر** (Vision) | عکس بفرست → توضیح کامل فارسی دریافت کن |

**کاملاً رایگان** — بدون نیاز به کارت بانکی، بدون محدودیت روزانه.

### 🚀 شروع سریع

```bash
git clone https://github.com/SeniorAminam/Ashhcb.git
cd Ashhcb
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# ویرایش .env — BOT_TOKEN و AGNES_API_KEY رو وارد کن
python -m src.bot
```

یا با داکر:

```bash
docker compose up -d
```

### 🏗️ معماری

```
کاربر بله → Polling Bot → AIService → AgnesService → Agnes AI API → نتیجه
                                        │
                                   txt2img | img2img | vision
                                        │
                                   Catbox.moe (آپلود موقت عکس)
```

### 📁 ساختار پروژه

```
src/
├── bot.py              # نقطه ورودی، ثبت هندلرها
├── config/settings.py  # تنظیمات و متغیرهای محیطی
├── handlers/           # start, photo, callback, admin, user_panel, error
├── keyboards/          # reply (منو), inline (مدل‌ها)
├── services/           # agnes_service, ai_service, storage (SQLite)
└── utils/helpers.py    # resize, format, dimensions
```

### ⚙️ تنظیمات

```ini
BOT_TOKEN=123456789:abc...        # از @botfather در بله (ble.ir/botfather)
AGNES_API_KEY=sk-...              # از apihub.agnes-ai.com (ثبت‌نام رایگان)
ADMIN_USER_IDS=1040785496         # آیدی عددی ادمین‌ها
RATE_LIMIT_SECONDS=60             # فاصله یک دقیقه‌ای بین درخواست‌ها
```

### 🔐 محدودیت‌ها

- **یک دقیقه** فاصله بین درخواست‌ها (به ازای هر کاربر)
- حداکثر حجم عکس: **۱۰ مگابایت**
- رزولوشن: تا **1024×1024** (قابلیت 4K)
- هاستینگ موقت عکس: **۷۲ ساعت** (catbox.moe)

### 🐳 استقرار با داکر

```bash
docker compose build --no-cache
docker compose up -d
docker compose logs -f
git pull && docker compose build --no-cache && docker compose up -d
```

### 📄 مجوز

**MIT** — [LICENSE](LICENSE)

---

</div>

---

# 🇬🇧 English

## 🤖 Ashhcb Bot

A **zero-cost** Bale messenger bot for AI-powered image generation, transformation, and analysis — powered by **Agnes AI** free tier.

### ✨ Capabilities

| | Feature | How it Works |
|---|---|---|
| 🖼️ | **txt2img** | Type any prompt → get a 1024×1024 image in ~25s |
| 📷 | **img2img** | Send photo + prompt → get an AI-edited version |
| 🔍 | **Vision** | Upload a photo → get a detailed Persian description |

**100% free** — no credit card, no daily limits, no hidden costs.

### 🚀 Quick Start

```bash
git clone https://github.com/SeniorAminam/Ashhcb.git
cd Ashhcb
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env with your BOT_TOKEN + AGNES_API_KEY
python -m src.bot
```

Or with Docker:

```bash
docker compose up -d
```

### 🏗️ Architecture

```
Bale User → Polling Bot → AIService → AgnesService → Agnes AI API → Result
                                       │
                                  txt2img | img2img | vision
                                       │
                                  Catbox.moe (temp image upload)
```

### 📁 Project Structure

```
src/
├── bot.py              # Entry point, handler registration
├── config/settings.py  # Environment variables, constants
├── handlers/           # start, photo, callback, admin, user_panel, error
├── keyboards/          # reply (menu), inline (model selection)
├── services/           # agnes_service, ai_service, storage (SQLite)
└── utils/helpers.py    # resize, format, dimensions
```

### ⚙️ Configuration

```ini
BOT_TOKEN=123456789:abc...        # From @botfather on Bale (ble.ir/botfather)
AGNES_API_KEY=sk-...              # From apihub.agnes-ai.com (free signup)
ADMIN_USER_IDS=1040785496         # Comma-separated admin user IDs
RATE_LIMIT_SECONDS=60             # Cooldown between API calls per user
```

### 🔐 Rate Limits

| Limit | Value |
|-------|-------|
| Per-user cooldown | 60 seconds |
| Agnes API global | ~20 req/min |
| Max image size | 10 MB |
| Image resolution | Up to 1024×1024 (4K capable) |
| Temp hosting | 72 hours (catbox.moe) |

### 🐳 Docker Deployment

```bash
docker compose build --no-cache
docker compose up -d
docker compose logs -f
git pull && docker compose build --no-cache && docker compose up -d
```

### 📄 License

**MIT** — see [LICENSE](LICENSE).

---

<p align="center">
  <b>Developed with ❤️ by <a href="https://senioramin.com">Amin Davodian</a></b><br>
  <a href="https://ble.ir/SeniorAminBot">📱 @SeniorAminBot on Bale</a> ·
  <a href="https://github.com/SeniorAminam">🐙 GitHub</a> ·
  <a href="https://linkedin.com/in/SudoAmin">💼 LinkedIn</a>
</p>

