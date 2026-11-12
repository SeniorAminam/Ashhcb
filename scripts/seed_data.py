#!/usr/bin/env python3
# Project: Ashhcb Bot - Mazandaran Skills University AI Assistant
# File Path: scripts/seed_data.py
# Author: Amin Davodian
# Full Name: Mohammadamin Davodian
# Website: https://senioramin.com
# GitHub: https://github.com/SeniorAminam
# LinkedIn: https://linkedin.com/in/SudoAmin
# Developer: @SeniorAminBot
# Brand: SeniorAmin
# Created Date: 2026-11-12
# Modified Date: 2026-11-12
# Version: 1.0.0
# Purpose: Seed initial knowledge base data for MSU AI Assistant
# License: MIT
# Copyright: (c) Amin Davodian

"""
Seed Script for initial knowledge base population.

Run this script to populate the knowledge base with initial data:
- University information
- Admission requirements
- Course/skill catalog
- Announcements
- Career guidance content
"""

import sys
import os
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.storage import init_db, UserStorage
from src.services.knowledge_service import KnowledgeService
from src.services.i18n_service import I18nService
from src.services.web_scraper_service import WebScraperService, DEFAULT_SCRAPER_CONFIGS


def seed_knowledge_base():
    """Seed initial knowledge base with university data."""
    print("🌱 Seeding knowledge base...")

    # Initialize DB
    init_db()
    I18nService.load_translations()

    # Persian content
    fa_content = [
        {
            "content": """دانشگاه ملی مهارت مازندران (MSU) یکی از مراکز برتر آموزش مهارت‌های تخصصی در ایران است.
این دانشگاه با هدف توانمندسازی نیروی انسانی و پاسخگویی به نیازهای بازار کار تأسیس شده است.
دانشگاه در شهر ساری، استان مازندران قرار دارد و زیر نظر وزارت علوم، تحقیقات و فناوری فعالیت می‌کند.

مهم‌ترین ویژگی‌ها:
- آموزش مبتنی بر مهارت و شغلی
- همکاری با صنعت و بازار کار
- امکانات آموزشی پیشرفته
- اساتید مجرب و متخصص""",
            "source_type": "manual",
            "language": "fa",
            "category": "general",
            "tags": ["دانشگاه", "معرفی", "مازندران"],
            "source_title": "معرفی دانشگاه",
        },
        {
            "content": """شرایط پذیرش در دانشگاه ملی مهارت مازندران:

1. داشتن مدرک دیپلم یا معادل (برای دوره‌های فنی و مهارتی)
2. حدود سنی: معمولاً ۱۸ تا ۳۵ سال
3. عدم иметь سابقه انضباطی در موسسات آموزشی
4. عبور از آزمون‌های مهارتی (در صورت نیاز)
5. ارائه مدارک مورد نیاز در مهلت مقرر

مدارک مورد نیاز:
- اصل و کپی شناسنامه و کارت ملی
- مدرک دیپلم یا پیشدیپلم (اصل و کپی)
- ۴ قطعه عکس ۳×۴ پس‌زمینه آبی
- گواهی خدمت سربازی (برای آقایان)
- فرم ثبت‌نام تکمیل‌شده

مهلت ثبت‌نام: معمولاً از اول مرداد تا آخر شهریور هر سال
برای اطلاعات دقیق به سامانه پذیرش مراجعه کنید: pzh.msu.ac.ir""",
            "source_type": "manual",
            "language": "fa",
            "category": "admission",
            "tags": ["پذیرش", "ثبت‌نام", "شرایط", "مدارک"],
            "source_title": "راهنمای پذیرش و ثبت‌نام",
        },
        {
            "content": """دوره‌های مهارتی و آموزشی دانشگاه ملی مهارت مازندران:

دوره‌های فنی و مهندسی:
- برنامه‌نویسی پایتون (پیشرفته، ۱۲۰ ساعت، گواهی فنی‌وحرفه‌ای)
- برنامه‌نویسی جاوا اسکریپت و React (پیشرفته، ۱۰۰ ساعت)
- تحلیل داده با Python و Power BI (میان‌پیشرفته، ۸۰ ساعت)
- شبکه و امنیت سایبری (پیشرفته، ۱۵۰ ساعت)
- تعمیرات موبایل و لپ‌تاپ (فنی، ۲۰۰ ساعت)

دوره‌های مهارت‌های دیجیتال:
- طراحی گرافیک با Illustrator و Photoshop (مبتدی تا پیشرفته، ۹۰ ساعت)
- ویرایش ویدیو با Premiere و After Effects (میان‌پیشرفته، ۸۰ ساعت)
- بازاریابی دیجیتال و SEO (مبتدی، ۶۰ ساعت)
- مدیریت شبکه‌های اجتماعی (مبتدی، ۴۰ ساعت)

دوره‌های مهارت‌های نرم:
- ارتباطات موثر و مهارت‌های عرضه (مبتدی، ۳۰ ساعت)
- مدیریت زمان و بهره‌وری (مبتدی، ۲۰ ساعت)
- کار تیمی و رهبری (میان‌پیشرفته، ۴۰ ساعت)
- زبان انگلیسی تخصصی (آکادمیک و شغلی، ۱۰۰ ساعت)

دوره‌های کسب‌وکار:
- راه‌اندازی استارتاپ (پیشرفته، ۸۰ ساعت)
- مدیریت پروژه با PMP (پیشرفته، ۶۰ ساعت)
- حسابداری و مالی برای غیرمتخصصان (مبتدی، ۵۰ ساعت)

همه دوره‌ها شامل:
- آموزش تئوری و عملی
- پروژه‌های واقعی
- گواهی‌نامه معتبر وزارت علوم
- مشاوره شغلی پس از دوره""",
            "source_type": "manual",
            "language": "fa",
            "category": "courses",
            "tags": ["دوره‌ها", "مهارت‌ها", "برنامه‌نویسی", "طراحی", "بازاریابی"],
            "source_title": "کاتالוג کامل دوره‌ها و مهارت‌ها",
        },
        {
            "content": """مشاوره تحصیلی و انتخاب رشته در دانشگاه ملی مهارت مازندران:

مراحل انتخاب مسیر تحصیلی:
1. شناسایی علایق و استعدادها (آزمون‌های مشاوره)
2. بررسی بازار کار و تقاضا
3. انتخاب دسته‌بندی مهارت (فنی، دیجیتال، نرم، کسب‌وکار)
4. تعیین سطح مهارت (مبتدی، میان‌پیشرفته، پیشرفته)
5. برنامه‌ریزی یادگیری و گواهی‌گیری

راهنمای انتخاب بر اساس علایق:
- اگر به کدنویسی و منطق علاقه دارید: برنامه‌نویسی، تحلیل داده، امنیت سایبری
- اگر خلاقیت بصری دارید: طراحی گرافیک، ویرایش ویدیو، UI/UX
- اگر به ارتباطات و مدیریت علاقه دارید: بازاریابی دیجیتال، مدیریت پروژه، مهارت‌های نرم
- اگر می‌خواهید کسب‌وکار راه‌اندازی کنید: استارتاپ، حسابداری، حقوق کسب‌وکار

پیش‌نیازهای رایج:
- سطح مبتدی: هیچ پیش‌نیازی نیاز نیست
- سطح میان‌پیشرفته: تسلط بر مبنای دوره قبلی
- سطح پیشرفته: تجربه عملی یا گواهی دوره‌های پایه""",
            "source_type": "manual",
            "language": "fa",
            "category": "skills",
            "tags": ["مشاوره", "انتخاب رشته", "مسیر شغلی", "پیش‌نیازها"],
            "source_title": "راهنمای مشاوره تحصیلی و انتخاب مهارت",
        },
        {
            "content": """راهنمای شغلی و بازار کار برای فارغ‌التحصیلان مهارت:

شغل‌های پرطلب در مازندران و ایران (۲۰۲۴-۲۰۲۵):
1. برنامه‌نویس 백‌اند (Python, Node.js) - حقوق ۱۵-۴۰ میلیون تومان
2. برنامه‌نویس فرانت‌اند (React, Vue) - حقوق ۱۲-۳۵ میلیون تومان
3. تحلیل‌گر داده (Python, SQL, Power BI) - حقوق ۱۸-۴۵ میلیون تومان
4. متخصص امنیت سایبری - حقوق ۲۰-۵۰ میلیون تومان
5. طراح گرافیک و UI/UX - حقوق ۱۰-۳۰ میلیون تومان
6. متخصص بازاریابی دیجیتال - حقوق ۱۲-۳۵ میلیون تومان
7. مدیر پروژه - حقوق ۱۵-۴۰ میلیون تومان
8. ویرایش‌گر ویدیو - حقوق ۸-۲۵ میلیون تومان

مهارت‌های تکمیلی پیشنهادی:
- زبان انگلیسی (حداقل B2)
- کنترل نسخه Git
- داکر و کانتینرها
- روش‌های Agile/Scrum
- پورتفولیو پروژه‌های واقعی

مراحل ورود به بازار کار:
1. تکمیل پورتفولیو (۳-۵ پروژه)
2. بهینه‌سازی لینکدین و رزومه
3. شرکت در هکاتون‌ها و چالش‌های کدنویسی
4. شبکه‌سازی در جمعیت‌های فنی
5. درخواست کار در سایت‌های کاریابی (ج‌بین،Lnkdn،ایرانی‌تاللنت)""",
            "source_type": "manual",
            "language": "fa",
            "category": "career",
            "tags": ["بازار کار", "حقوق", "شغل", "رزومه", "پورتفولیو"],
            "source_title": "راهنمای بازار کار و استخدام",
        },
        {
            "content": """مقررات آموزشی دانشگاه ملی مهارت مازندران:

حضور و غیاب:
- حداقل ۷۵٪ حضور در جلسات الزامی است
- غیاب بیش از ۲۵٪ مانع از دریافت گواهی می‌شود
- مرخصی‌ها باید به صورت کتبی و با مستندات ارائه شود

ارزیابی:
- پروژه‌های عملی (۴۰٪ نمره)
- آزمون‌های میان‌ترم و پایان‌ترم (۴۰٪)
- شرکت در کلاس و تمرینات (۲۰٪)
- نمره قبولی: ۱۰ از ۲۰

گواهی‌نامه:
- گواهی‌نامه فنی‌وحرفه‌ای وزارت علوم، تحقیقات و فناوری
- معتبر برای استخدام در секتور دولتی و خصوصی
- قابل تأیید در سامانه ملی مهارت‌ها

انصراف و مرخصی:
- انصراف تا ۱ هفته قبل از شروع: استرداد ۱۰۰٪ شهریه
- انصراف تا شروع کلاس: استرداد ۵۰٪ شهریه
- بعد از شروع کلاس: عدم استرداد شهریه
- مرخصی تحصیلی: حداکثر ۱ ترم با حفظ سمت""",
            "source_type": "manual",
            "language": "fa",
            "category": "regulations",
            "tags": ["مقررات", "حضور", "ارزیابی", "گواهی", "انصراف"],
            "source_title": "مقررات آموزشی و آزمایشی",
        },
        {
            "content": """اطلاعیه‌های مهم دانشگاه ملی مهارت مازندران (نمونه):

۱. آغاز ثبت‌نام دوره‌های بهار ۱۴۰۴
مهلت: ۱ فروردین تا ۱۵ فروردین
دوره‌های جدید: هوش مصنوعی، بلاکچین، واقعیت مجازی
مراجعه: سامانه پذیرش pzh.msu.ac.ir

۲. برگزاری کارگاه رایگان مهارت‌های دیجیتال
تاریخ: ۱۰ فروردین ۱۴۰۴
موضوع: مقدمه برنامه‌نویسی پایتون
مکان: سالن کنفرانس‌های دانشگاه
ثبت‌نام: رایگان، محدود به ۵۰ نفر

۳. جشنواره کارآفرینی و استارتاپ
تاریخ: ۲۰ تا ۲۲ فروردین ۱۴۰۴
جوایز: سرمایه‌گذاری، مشاوره، فضای کار
شرایط: داشتن ایده یا تیم استارتاپ

۴. تغییر ساعات اداری در ماه رمضان
ساعات جدید: ۸ تا ۱۴
مدت: تا پایان ماه رمضان

۵. نتیجه آزمون‌های مهارتی دوره‌های زمستانی
منتشر شده در سامانه آموزشی
تظلم تا ۵ روز کاری

برای اطلاع از جدیدترین اخبار کانال ایتا دانشگاه را دنبال کنید: @msu_skills""",
            "source_type": "manual",
            "language": "fa",
            "category": "announcements",
            "tags": ["اطلاعیه", "ثبت‌نام", "کارگاه", "جشنواره", "رامضان"],
            "source_title": "اطلاعیه‌های اخیر دانشگاه",
        },
    ]

    # English content
    en_content = [
        {
            "content": """Mazandaran National Skills University (MSU) is one of Iran's leading centers for specialized skills education.
Established to empower human resources and meet labor market needs.
Located in Sari, Mazandaran Province, operating under the Ministry of Science, Research and Technology.

Key Features:
- Skill-based and job-oriented education
- Industry and labor market collaboration
- Advanced educational facilities
- Experienced and specialized faculty""",
            "source_type": "manual",
            "language": "en",
            "category": "general",
            "tags": ["university", "introduction", "mazandaran"],
            "source_title": "University Introduction",
        },
        {
            "content": """Admission Requirements for Mazandaran National Skills University:

1. High school diploma or equivalent (for technical and skill programs)
2. Age range: typically 18-35 years
3. No disciplinary record in educational institutions
4. Passing skill assessments (if required)
5. Submission of required documents within deadline

Required Documents:
- Original and copy of ID card and national ID
- High school diploma or pre-diploma (original and copy)
- 4 passport photos (3x4, blue background)
- Military service completion certificate (for males)
- Completed registration form

Registration Period: Typically from early August to late September each year
For exact information, visit the admission portal: pzh.msu.ac.ir""",
            "source_type": "manual",
            "language": "en",
            "category": "admission",
            "tags": ["admission", "registration", "requirements", "documents"],
            "source_title": "Admission and Registration Guide",
        },
        {
            "content": """Skill Courses and Programs at Mazandaran National Skills University:

Technical & Engineering Programs:
- Python Programming (Advanced, 120 hours, Technical Vocational Certificate)
- JavaScript & React Development (Advanced, 100 hours)
- Data Analysis with Python & Power BI (Intermediate, 80 hours)
- Network & Cybersecurity (Advanced, 150 hours)
- Mobile & Laptop Repair (Technical, 200 hours)

Digital Skills Programs:
- Graphic Design with Illustrator & Photoshop (Beginner to Advanced, 90 hours)
- Video Editing with Premiere & After Effects (Intermediate, 80 hours)
- Digital Marketing & SEO (Beginner, 60 hours)
- Social Media Management (Beginner, 40 hours)

Soft Skills Programs:
- Effective Communication & Presentation (Beginner, 30 hours)
- Time Management & Productivity (Beginner, 20 hours)
- Teamwork & Leadership (Intermediate, 40 hours)
- Professional English (Academic & Business, 100 hours)

Business Programs:
- Startup Launch (Advanced, 80 hours)
- Project Management with PMP (Advanced, 60 hours)
- Accounting & Finance for Non-Specialists (Beginner, 50 hours)

All programs include:
- Theoretical and practical training
- Real-world projects
- Ministry of Science accredited certificates
- Post-program career counseling""",
            "source_type": "manual",
            "language": "en",
            "category": "courses",
            "tags": ["courses", "skills", "programming", "design", "marketing"],
            "source_title": "Complete Course & Skills Catalog",
        },
    ]

    # Arabic content
    ar_content = [
        {
            "content": """جامعة مهارات مازندران الوطنية (MSU) هي أحد المراكز الرائدة في إيران للتعليم المهني المتخصص.
تأسست لتمكين الموارد البشرية وتلبية احتياجات سوق العمل.
تقع في مدينة ساري، محافظة مازندران، وتعمل تحت إشراف وزارة العلوم والبحوث والتكنولوجيا.

أهم الميزات:
- تعليم قائم على المهارات وموجه نحو سوق العمل
- التعاون مع الصناعة وسوق العمل
- مرافق تعليمية متقدمة
- هيئة تدريس ذات خبرة وتخصص""",
            "source_type": "manual",
            "language": "ar",
            "category": "general",
            "tags": ["جامعة", "مقدمة", "مازندران"],
            "source_title": "مقدمة عن الجامعة",
        },
        {
            "content": """شروط القبول في جامعة مهارات مازندران الوطنية:

1. الحصول على شهادة الثانوية العامة أو ما يعادلها (للبرامج التقنية والمهنية)
2. الفئة العمرية: عادة ١٨-٣٥ سنة
3. عدم وجود سجل تأديبي في المؤسسات التعليمية
4. اجتياز اختبارات المهارات (إذا لزم الأمر)
5. تقديم المستندات المطلوبة في الموعد المحدد

المستندات المطلوبة:
- أصل وصورة بطاقة الهوية والبطاقة الوطنية
- شهادة الثانوية العامة أو ما قبل الثانوية (أصل وصورة)
- ٤ صور شخصية (٣×٤، خلفية زرقاء)
- شهادة إتمام الخدمة العسكرية (للذكور)
- استمارة التسجيل المكتملة

فترة التسجيل: عادة من أوائل أغسطس إلى أواخر سبتمبر من كل عام
للحصول على معلومات دقيقة، يرجى زيارة بوابة القبول: pzh.msu.ac.ir""",
            "source_type": "manual",
            "language": "ar",
            "category": "admission",
            "tags": ["قبول", "تسجيل", "شروط", "مستندات"],
            "source_title": "دليل القبول والتسجيل",
        },
    ]

    all_content = fa_content + en_content + ar_content

    for item in all_content:
        chunk_ids = KnowledgeService.ingest_text(
            content=item["content"],
            source_type=item["source_type"],
            language=item["language"],
            category=item["category"],
            tags=item["tags"],
            source_title=item["source_title"],
        )
        if chunk_ids:
            print(f"  ✅ Added {len(chunk_ids)} chunks: {item['source_title']} ({item['language']})")
        else:
            print(f"  ⚠️ Duplicate skipped: {item['source_title']} ({item['language']})")

    # Initialize scraper jobs
    print("\n🕷️ Initializing scraper jobs...")
    for job_name, config in DEFAULT_SCRAPER_CONFIGS.items():
        UserStorage.upsert_scrape_job(
            name=config["name"],
            url_pattern=config.get("base_url", ""),
            selector_config={
                "list_selector": config.get("list_selector"),
                "title_selector": config.get("title_selector"),
                "link_selector": config.get("link_selector"),
                "content_selector": config.get("content_selector"),
                "date_selector": config.get("date_selector"),
                "pagination": config.get("pagination"),
                "max_pages": config.get("max_pages", 1),
            },
            schedule_cron=config.get("schedule_cron"),
            is_active=0,  # Disabled by default, enable manually
        )
        print(f"  ✅ Scraper job registered: {config['name']} (disabled)")

    # Show final stats
    stats = KnowledgeService.get_stats()
    print(f"\n📊 Seeding complete!")
    print(f"   Total chunks: {stats.get('total_chunks', 0)}")
    for lang_stat in stats.get("by_language", []):
        print(f"   {lang_stat['language']}: {lang_stat['count']} chunks")
    for cat_stat in stats.get("by_category", []):
        cat = cat_stat['category'] or 'general'
        print(f"   {cat}: {cat_stat['count']} chunks")


if __name__ == "__main__":
    seed_knowledge_base()