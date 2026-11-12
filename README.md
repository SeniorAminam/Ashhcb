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

<h1 align="center">🤖 Ashhcb Bot — MSU AI Assistant</h1>
<h3 align="center">Mazandaran National Skills University AI Assistant for Bale Messenger</h3>
<p align="center"><b>RAG Chat</b> · <b>Academic Advising</b> · <b>Career Guidance</b> · <b>Skill Discovery</b> · <b>Web Search</b> · <b>Scraping</b><br><sub>Powered by Gemma 4 (OpenAI-compatible) · Text-First Architecture · Multilingual (fa/en/ar)</sub></p>

<hr>

<br>

# 🇮🇷 فارسی

<p>
ربات <b>Ashhcb</b> دستیار هوشمند <b>دانشگاه ملی مهارت مازندران (MSU)</b> برای پیام‌رسان بله است.
این ربات به عنوان یک دستیار متنی (Text-First) با قابلیت‌های زیر طراحی شده است:
</p>

<ul dir="auto">
  <li><b>💬 چت آزاد (RAG)</b> — سوالات خود را به زبان طبیعی بپرسید، پاسخ بر اساس پایگاه دانش دانشگاه</li>
  <li><b>🎓 مشاوره تحصیلی</b> — برنامه‌ریزی تحصیلی، پیشنهاد دوره‌ها، مسیر پیشرفت بر اساس پروفایل شما</li>
  <li><b>💼 مشاوره شغلی</b> — مسیرهای شغلی، مهارت‌های مورد نیاز بازار کار، نقشه‌راه یادگیری</li>
  <li><b>🎯 کشف مهارت‌ها</b> — جستجوی دوره‌ها و وورشاپ‌ها با فیلتر دسته‌بندی و سطح</li>
  <li><b>📝 اطلاعات پذیرش</b> — شرایط ثبت‌نام، مدارک، مهلت‌ها، هزینه‌ها و مراحل پذیرش</li>
  <li><b>📢 خلاصه اطلاعیه‌ها</b> — آخرین اخبار و اعلان‌های دانشگاه (از پایگاه دانش و اسکرپینگ)</li>
  <li><b>🔍 جستجوی ترکیبی</b> — جستجو در پایگاه دانش محلی + وب (داکداک‌گو، سایت دانشگاه، کانال‌های ایتا)</li>
  <li><b>🌐 چندزبانه</b> — فارسی (RTL)، انگلیسی، عربی با فرمت‌دهی عدد و راست‌چین</li>
  <li><b>⚙️ پنل ادمین</b> — مدیریت دانش، کنترل اسکریپرها، آمار کاربران، پیام همگانی</li>
</ul>

<p dir="auto">✅ متنی (بدون تولید عکس) · ✅ چندزبانه (fa/en/ar) · ✅ RAG + وب‌اسکرپینگ · ✅ متن‌باز (MIT)</p>

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
#   AI_API_KEY=کلید_API_هوش_مصنوعی
#   AI_BASE_URL=آدرس_API
#   AI_MODEL_CHAT=نام_مدل_چت
#   ADMIN_USER_IDS=شناسه_کاربری_ادمین
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

**Ashhcb Bot** is the official AI assistant for **Mazandaran National Skills University (MSU)** on Bale messenger.  
It is a **text-first** assistant powered by **Gemma 4** (via OpenAI-compatible API) with the following capabilities:

<div align="center">

| Icon | Capability | 🇮🇷 | 🇬🇧 |
|:---:|---|---|---|
| 💬 | **RAG Chat** | چت آزاد با پایگاه دانش | Free-form chat with KB context |
| 🎓 | **Academic Advising** | مشاوره تحصیلی و برنامه‌ریزی | Personalized study planning |
| 💼 | **Career Guidance** | مشاوره شغلی و بازار کار | Career paths & skill roadmaps |
| 🎯 | **Skill Discovery** | جستجوی مهارت‌ها و دوره‌ها | Course/workshop search |
| 📝 | **Admissions Info** | اطلاعات پذیرش و ثبت‌نام | Registration requirements |
| 📢 | **Announcements** | خلاصه اطلاعیه‌ها | University news summary |
| 🔍 | **Hybrid Search** | جستجوی محلی + وب | Local KB + web search |
| 🌐 | **Multilingual** | فارسی/انگلیسی/عربی (RTL) | fa/en/ar with RTL support |

</div>

All operations are **text-based** (no image generation), **multilingual**, and **open-source** (MIT).

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- A Bale bot token from [@botfather](https://ble.ir/botfather)
- An OpenAI-compatible AI API endpoint (e.g., Gemma 4) with API key

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
#   AI_API_KEY=sk-your-ai-key
#   AI_BASE_URL=https://your-endpoint/v1
#   AI_MODEL_CHAT=Iag4a/Gemma-4-26B-A4B-it
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
  <td><code>AI_API_KEY</code></td>
  <td>API key for OpenAI-compatible endpoint</td>
  <td>✅</td>
</tr>
<tr>
  <td><code>AI_BASE_URL</code></td>
  <td>Base URL of AI API (e.g., http://193.93.169.247:20128/v1)</td>
  <td>✅</td>
</tr>
<tr>
  <td><code>AI_MODEL_CHAT</code></td>
  <td>Chat model name (e.g., Iag4a/Gemma-4-26B-A4B-it)</td>
  <td>✅</td>
</tr>
<tr>
  <td><code>AI_MODEL_VISION</code></td>
  <td>Vision model name (for future image analysis)</td>
  <td>Optional</td>
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
<tr>
  <td><code>DOWNLOAD_TIMEOUT</code></td>
  <td>Download timeout in seconds (default: 60)</td>
  <td>Optional</td>
</tr>
<tr>
  <td><code>API_TIMEOUT</code></td>
  <td>AI API request timeout (default: 120)</td>
  <td>Optional</td>
</tr>
<tr>
  <td><code>ENABLE_WEB_SEARCH</code></td>
  <td>Enable DuckDuckGo web search (default: true)</td>
  <td>Optional</td>
</tr>
<tr>
  <td><code>ENABLE_SCRAPERS</code></td>
  <td>Enable scheduled web scraping (default: true)</td>
  <td>Optional</td>
</tr>
<tr>
  <td><code>DEFAULT_LANGUAGE</code></td>
  <td>Default language: fa, en, ar (default: fa)</td>
  <td>Optional</td>
</tr>
<tr>
  <td><code>LOG_LEVEL</code></td>
  <td>Logging level: DEBUG, INFO, WARNING, ERROR (default: INFO)</td>
  <td>Optional</td>
</tr>
<tr>
  <td><code>LOG_DIR</code></td>
  <td>Log directory (default: logs)</td>
  <td>Optional</td>
</tr>
<tr>
  <td><code>LOG_JSON</code></td>
  <td>JSON format for log files (default: false)</td>
  <td>Optional</td>
</tr>
</table>

---

## 🏗️ Architecture

The system follows a clean layered architecture with modular services:

```
┌─────────────────────────────────────────────────────────┐
│                      Bale User                          │
└────────────────────┬────────────────────────────────────┘
                     │  Message / Callback
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Polling Bot (python-telegram-bot 21.x)      │
│  ┌─────────┐ ┌────────┐ ┌─────────┐ ┌──────────┐        │
│  │ menu    │ │ chat   │ │ search  │ │ advisory │        │
│  │ handler │ │ handler│ │ handler │ │ handlers │        │
│  └────┬────┘ └────┬───┘ └────┬────┘ └────┬─────┘        │
└───────┼────────────┼──────────┼──────────┼───────────────┘
        │            │          │          │
        ▼            ▼          ▼          ▼
┌─────────────────────────────────────────────────────────┐
│                    Service Layer                         │
│  ┌──────────────┐ ┌──────────────┐ ┌────────────────┐  │
│  │ AIService    │ │ KnowledgeSvc │ │ SearchService  │  │
│  │ (RAG, LLM)   │ │ (ingest,     │ │ (local + web)  │  │
│  │              │ │  search)     │ │                │  │
│  └──────────────┘ └──────────────┘ └────────────────┘  │
│  ┌──────────────┐ ┌──────────────┐ ┌────────────────┐  │
│  │ ScraperSvc   │ │ I18nService  │ │ Storage        │  │
│  │ (web, eitaa) │ │ (fa/en/ar,   │ │ (SQLite WAL)   │  │
│  │              │ │  RTL, nums)  │ │                │  │
│  └──────────────┘ └──────────────┘ └────────────────┘  │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              External Services                           │
│  ┌──────────────────┐  ┌──────────────┐  ┌───────────┐  │
│  │ AI API (Gemma 4) │  │ University   │  │ Eitaa /   │  │
│  │ /v1/chat/        │  │ Website /    │  │ RSS Feeds │  │
│  │ completions      │  │ DuckDuckGo   │  │           │  │
│  └──────────────────┘  └──────────────┘  └───────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Key Design Decisions

<table>
<tr>
  <th>Decision</th>
  <th>Rationale</th>
</tr>
<tr>
  <td><b>Text-first (no image gen)</b></td>
  <td>Focus on RAG, advising, search; vision kept for future file/image reading</td>
</tr>
<tr>
  <td><b>OpenAI-compatible API</b></td>
  <td>Vendor-agnostic; swap Gemma 4 for any compatible model</td>
</tr>
<tr>
  <td><b>RAG with keyword search</b></td>
  <td>Simple, fast, no embedding dependency; upgradable to FTS5/vector</td>
</tr>
<tr>
  <td><b>Async httpx + connection pooling</b></td>
  <td>No blocking calls; 120s timeout freeze fixed</td>
</tr>
<tr>
  <td><b>Multilingual (fa/en/ar) + RTL</b></td>
  <td>Native Persian/Arabic support with numeral conversion</td>
</tr>
<tr>
  <td><b>Hybrid search (local + web)</b></td>
  <td>Covers KB gaps via DuckDuckGo + university site scraping</td>
</tr>
<tr>
  <td><b>APScheduler for scrapers</b></td>
  <td>Cron-like jobs for announcements, Eitaa channels</td>
</tr>
<tr>
  <td><b>Rotating file logs</b></td>
  <td>Separate bot/error/debug/ai/scraper logs with 10MB rotation</td>
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
│   │   ├── settings.py           # Environment variables, constants
│   │   └── logging_config.py     # File-based rotating log setup
│   ├── handlers/
│   │   ├── menu.py               # Main menu, settings, user/admin panels
│   │   ├── chat.py               # Free-form RAG chat with history
│   │   ├── search.py             # General/skills/announcements search
│   │   ├── advisory.py           # Academic advising, career guidance (multi-step)
│   │   ├── admin.py              # Admin: stats, users, knowledge, scrapers, broadcast
│   │   └── error.py              # Global exception handler
│   ├── keyboards/
│   │   └── builders.py           # Dynamic i18n keyboard builders
│   ├── services/
│   │   ├── agnes_service.py      # AI client (OpenAI-compat, Gemma 4)
│   │   ├── ai_service.py         # RAG orchestrator (chat, advising, career, skills)
│   │   ├── knowledge_service.py  # RAG pipeline: ingest, chunk, search, context
│   │   ├── search_service.py     # Hybrid search: local KB + web
│   │   ├── web_scraper_service.py# Async scraping: university, Eitaa, RSS, DDG
│   │   ├── i18n_service.py       # i18n: translations, RTL, numerals, detection
│   │   └── storage.py            # SQLite WAL: users, knowledge_chunks, scrape_jobs
│   ├── locales/
│   │   ├── fa.json               # Persian translations (200+ keys)
│   │   ├── en.json               # English translations
│   │   └── ar.json               # Arabic translations
│   └── utils/
│       └── helpers.py            # MarkdownV2 escape, formatting helpers
│
├── scripts/
│   └── seed_data.py              # Populate KB with MSU data (fa/en/ar)
│
├── tests/                        # Test suite (to be expanded)
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

## 📊 Core Features Detail

### RAG Chat (`handlers/chat.py` + `services/ai_service.py`)
- Conversation history (last 6 messages)
- Context from knowledge base (top 3 chunks, 2500 chars)
- Modes: general, admissions, career, skills
- Source citations in responses

### Academic Advising (`handlers/advisory.py`)
- 5-step conversation: interests → skills → education → goals → fields
- Personalized program recommendations
- Course prerequisites, duration, certificates

### Career Guidance (`handlers/advisory.py`)
- 6-step conversation: interests → skills → experience → education → industries → location
- Market-aware skill roadmaps
- Learning path suggestions

### Skill Discovery (`handlers/search.py`)
- Category filter: admission, courses, announcements, skills, regulations, career
- Level filter: beginner, intermediate, advanced
- Paginated results with inline keyboards

### Hybrid Search (`services/search_service.py`)
- Local KB search (keyword-based, multi-language)
- Web search via DuckDuckGo HTML scraping
- Combined ranking with source priority

### Web Scraping (`services/web_scraper_service.py`)
- University website (announcements, admissions, courses)
- Eitaa channel messages (public)
- RSS/Atom feeds
- APScheduler cron jobs (configurable intervals)
- Selectolax (lexbor) for fast HTML parsing

### Multilingual (`services/i18n_service.py`)
- JSON translation files (200+ keys each)
- Language detection from text
- RTL formatting for fa/ar
- Numeral conversion: Western → Persian/Arabic-Indic

### Logging (`config/logging_config.py`)
- Rotating files: `bot_YYYYMMDD.log`, `error_YYYYMMDD.log`, `debug_YYYYMMDD.log`
- Specialized: `ai_calls_YYYYMMDD.log`, `scraper_YYYYMMDD.log`
- 10MB max, 5 backups, UTF-8
- Colored console output

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

# Seed knowledge base (after .env configured)
python scripts/seed_data.py
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