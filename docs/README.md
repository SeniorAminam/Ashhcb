<!--
Project:         Ashhcb Bot - AI Image Transformer on Bale
File Path:       docs/README.md
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
Purpose:         Project documentation (Persian)
License:         MIT
Copyright:       (c) Amin Davodian
-->

# Ashhcb Bot — ربات هوش مصنوعی ساخت و تبدیل عکس در بله

**ربات رایگان و قدرتمند برای ساخت عکس از متن، تبدیل عکس، و تحلیل تصویر با Agnes AI**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Bale API](https://img.shields.io/badge/Bale%20API-Compatible-green.svg)](https://tapi.bale.ai)

---

## امکانات

| قابلیت | توضیحات |
|--------|---------|
| 🖼️ **ساخت عکس** | تولید تصویر 1024×1024 از هر متنی |
| 📷 **شروع تبدیل عکس** | ارسال عکس + پرامپت، دریافت نتیجه ویرایش شده |
| 🔍 **تحلیل تصویر** | آپلود عکس، دریافت توضیح کامل فارسی |

### ویژگی‌ها
- ✅ **کاملاً رایگان** — بدون نیاز به کارت بانکی
- ✅ **هوش مصنوعی Agnes AI** — قدرتمند و سریع
- ✅ **پشتیبانی از فارسی** — کاملاً فارسی و روان
- ✅ **محدودیت یک دقیقه** بین درخواست‌ها
- ✅ **بدون نیاز به GPU** — پردازش ابری

---

## نصب و اجرا

### روش ۱: اجرای مستقیم

```bash
git clone https://github.com/SeniorAminam/Ashhcb.git
cd Ashhcb
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# ویرایش .env با توکن‌ها
python -m src.bot
```

### روش ۲: اجرا با Docker

```bash
git clone https://github.com/SeniorAminam/Ashhcb.git
cd Ashhcb
cp .env.example .env
nano .env
docker compose up -d
```

---

## ساختار پروژه

```
src/
├── bot.py                 # نقطه ورودی، ثبت هندلرها، شروع polling
├── config/
│   └── settings.py        # تنظیمات و متغیرهای محیطی
├── handlers/
│   ├── start.py           # شروع، راهنما، درباره، مسیریابی متن
│   ├── photo.py           # دریافت و پردازش عکس
│   ├── callback.py        # دکمه‌های شیشه‌ای
│   ├── admin.py           # پنل مدیریت
│   ├── user_panel.py      # تاریخچه و آمار کاربر
│   └── error.py           # مدیریت خطاها
├── keyboards/
│   ├── reply.py           # کیبوردهای شیشه‌ای (منو اصلی، پنل‌ها)
│   └── inline.py          # کیبوردهای اینلاین (انتخاب مدل)
├── services/
│   ├── agnes_service.py   # سرویس اصلی Agnes AI
│   ├── ai_service.py      # لایه نازک wrapper
│   └── storage.py         # دیتابیس SQLite
└── utils/
    └── helpers.py         # توابع کمکی
```

---

## دریافت توکن‌ها

### توکن ربات بله
1. به @botfather در بله مراجعه کنید
2. دستور `/newbot` را بزنید
3. نام ربات را وارد کنید
4. توکن دریافتی را در `.env` قرار دهید

### کلید API Agnes AI
1. به [apihub.agnes-ai.com](https://apihub.agnes-ai.com) بروید
2. ثبت نام کنید (رایگان — بدون کارت بانکی)
3. یک کلید API جدید بسازید
4. کلید را در `.env` قرار دهید

---

## مجوز

این پروژه تحت مجوز **MIT** منتشر شده است.

---

## توسعه‌دهنده

**امین داودیان** (Mohammadamin Davodian)

- وبسایت: [senioramin.com](https://senioramin.com)
- گیت‌هاب: [github.com/SeniorAminam](https://github.com/SeniorAminam)
- ربات پشتیبانی: @SeniorAminBot

*Developed by Amin Davodian · @SeniorAminBot*
