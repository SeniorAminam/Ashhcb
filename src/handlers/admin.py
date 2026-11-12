# Project: Ashhcb Bot - Mazandaran Skills University AI Assistant
# File Path: src/handlers/admin.py
# Author: Amin Davodian
# Full Name: Mohammadamin Davodian
# Website: https://senioramin.com
# GitHub: https://github.com/SeniorAminam
# LinkedIn: https://linkedin.com/in/SudoAmin
# Developer: @SeniorAminBot
# Brand: SeniorAmin
# Created Date: 2026-06-21
# Modified Date: 2026-11-12
# Version: 4.0.0
# Purpose: Admin panel handlers - stats, users, broadcast, knowledge management, scrapers
# License: MIT
# Copyright: (c) Amin Davodian

import logging
import json
from typing import List, Dict, Any

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    CommandHandler,
)

from src.config.settings import ADMIN_USER_IDS, BOT_USERNAME
from src.services.storage import UserStorage
from src.services.knowledge_service import KnowledgeService
from src.services.web_scraper_service import WebScraperService, DEFAULT_SCRAPER_CONFIGS
from src.services.i18n_service import I18nService
from src.utils.helpers import escape_markdown, format_number

logger = logging.getLogger(__name__)

# Conversation states
ADMIN_KNOWLEDGE_TEXT, ADMIN_KNOWLEDGE_CATEGORY, ADMIN_KNOWLEDGE_TAGS, ADMIN_KNOWLEDGE_LANG = range(4)
ADMIN_SCRAPER_SELECT, ADMIN_SCRAPER_RUN = range(4, 6)

BROADCAST_TEXT = 1


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_USER_IDS


# =============================================================================
# Admin Panel Entry
# =============================================================================

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle admin panel callbacks from inline keyboards."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("⛔ شما دسترسی ادمین ندارید!", show_alert=True)
        return

    language = UserStorage.get_user_language(user_id)
    data = query.data

    if data == "admin_stats":
        await _show_admin_stats(query, language)
    elif data == "admin_users":
        await _show_users_list(query, language)
    elif data == "admin_knowledge":
        await _show_knowledge_menu(query, language)
    elif data == "admin_scrapers":
        await _show_scrapers_menu(query, language)
    elif data == "admin_broadcast":
        await _start_broadcast_callback(query, language)
    elif data == "admin_back":
        await _show_admin_main(query, language)


async def _show_admin_main(query, language: str) -> None:
    """Show main admin panel."""
    await query.edit_message_text(
        f"👑 {I18nService.t('admin.panel', language)}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(I18nService.t("admin.stats", language), callback_data="admin_stats")],
            [InlineKeyboardButton(I18nService.t("admin.users", language), callback_data="admin_users")],
            [InlineKeyboardButton(I18nService.t("admin.knowledge", language), callback_data="admin_knowledge")],
            [InlineKeyboardButton(I18nService.t("admin.scrapers", language), callback_data="admin_scrapers")],
            [InlineKeyboardButton(I18nService.t("admin.broadcast", language), callback_data="admin_broadcast")],
            [InlineKeyboardButton(I18nService.t("common.back", language), callback_data="main_menu")],
        ]),
    )


# =============================================================================
# Stats
# =============================================================================

async def _show_admin_stats(query, language: str) -> None:
    stats = UserStorage.get_total_stats()
    kb_stats = KnowledgeService.get_stats()

    text_lines = [
        f"📊 {I18nService.t('admin.stats', language)}",
        "",
        f"👥 کاربران: {format_number(stats['total_users'])}",
        f"💬 کل پرسش‌ها: {format_number(stats['total_transforms'])}",
        f"📅 امروز: {format_number(stats['today_transforms'])}",
        "",
        f"📚 پایگاه دانش:",
        f"  قطعات (chunks): {format_number(kb_stats.get('total_chunks', 0))}",
    ]

    for lang_stat in kb_stats.get("by_language", []):
        text_lines.append(f"    {lang_stat['language']}: {format_number(lang_stat['count'])}")

    for cat_stat in kb_stats.get("by_category", []):
        cat = cat_stat['category'] or 'general'
        text_lines.append(f"    {cat}: {format_number(cat_stat['count'])}")

    await query.edit_message_text(
        escape_markdown("\n".join(text_lines)),
        parse_mode="MarkdownV2",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(I18nService.t("common.back", language), callback_data="admin_back")
        ]]),
    )


async def _show_users_list(query, language: str) -> None:
    users = UserStorage.get_all_users()

    if not users:
        text = "📭 هنوز کاربری ثبت نشده است."
    else:
        text_lines = [f"👥 {I18nService.t('admin.users', language)} ({len(users)} نفر)\n"]
        for i, user in enumerate(users[:20], 1):
            name = user["first_name"] or f"کاربر {user['user_id']}"
            username = f"@{user['username']}" if user["username"] else ""
            lang = user.get("language", "fa")
            lang_flag = I18nService.get_language_flag(lang)
            join_date = user["join_date"][:10] if user["join_date"] else "نامشخص"
            text_lines.append(
                f"{i}. {name} {username} {lang_flag}\n"
                f"   🆔 {user['user_id']} | 💬 {user['total_transforms']}\n"
                f"   📅 {join_date}\n"
            )
        if len(users) > 20:
            text_lines.append(f"\n... و {len(users) - 20} کاربر دیگر")
        text = "\n".join(text_lines)

    await query.edit_message_text(
        escape_markdown(text),
        parse_mode="MarkdownV2",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(I18nService.t("common.back", language), callback_data="admin_back")
        ]]),
    )


# =============================================================================
# Knowledge Management
# =============================================================================

async def _show_knowledge_menu(query, language: str) -> None:
    """Show knowledge management menu."""
    await query.edit_message_text(
        f"📥 {I18nService.t('admin.knowledge', language)}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(I18nService.t("admin.add_knowledge", language), callback_data="knowledge_add")],
            [InlineKeyboardButton("📊 آمار پایگاه دانش", callback_data="knowledge_stats")],
            [InlineKeyboardButton("🗑️ پاک‌سازی دسته‌بندی", callback_data="knowledge_cleanup")],
            [InlineKeyboardButton(I18nService.t("common.back", language), callback_data="admin_back")],
        ]),
    )


async def knowledge_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle knowledge management callbacks."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("⛔ دسترسی ادمین نیست!", show_alert=True)
        return ConversationHandler.END

    language = UserStorage.get_user_language(user_id)
    data = query.data

    if data == "knowledge_add":
        await query.edit_message_text(
            "📝 افزودن دانش جدید\n\n"
            "متن یا محتوای مورد نظر را ارسال کنید:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(I18nService.t("common.cancel", language), callback_data="knowledge_cancel")
            ]]),
        )
        return ADMIN_KNOWLEDGE_TEXT

    elif data == "knowledge_stats":
        kb_stats = KnowledgeService.get_stats()
        text = f"📊 آمار پایگاه دانش\n\nکل قطعات: {kb_stats.get('total_chunks', 0)}\n\n"
        text += "بر اساس زبان:\n"
        for ls in kb_stats.get("by_language", []):
            text += f"  {ls['language']}: {ls['count']}\n"
        text += "\nبر اساس دسته‌بندی:\n"
        for cs in kb_stats.get("by_category", []):
            cat = cs['category'] or 'general'
            text += f"  {cat}: {cs['count']}\n"
        text += "\nبر اساس منبع:\n"
        for ss in kb_stats.get("by_source_type", []):
            text += f"  {ss['source_type']}: {ss['count']}\n"

        await query.edit_message_text(
            escape_markdown(text),
            parse_mode="MarkdownV2",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(I18nService.t("common.back", language), callback_data="admin_knowledge")
            ]]),
        )
        return ConversationHandler.END

    elif data == "knowledge_cleanup":
        await query.edit_message_text(
            "⚠️ پاک‌سازی دسته‌بندی\n\n"
            "این عملیات تمام قطعات یک دسته‌بندی را حذف می‌کند.\n"
            "آیا مطمئن هستید؟\n\n"
            "دستور: /cleanup_category <category> <language>",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(I18nService.t("common.back", language), callback_data="admin_knowledge")
            ]]),
        )
        return ConversationHandler.END

    elif data == "knowledge_cancel":
        await _show_knowledge_menu(query, language)
        return ConversationHandler.END

    return ConversationHandler.END


async def knowledge_text_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive knowledge text content."""
    user_id = update.effective_user.id
    language = UserStorage.get_user_language(user_id)
    text = update.message.text.strip()

    if not text or len(text) < 10:
        await update.message.reply_text("محتوای کوتاه است. حداقل ۱۰ کاراکتر وارد کنید.")
        return ADMIN_KNOWLEDGE_TEXT

    context.user_data["knowledge_content"] = text
    context.user_data["knowledge_source_type"] = "manual"

    await update.message.reply_text(
        "دسته‌بندی را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📝 پذیرش", callback_data="kn_cat_admission"),
                InlineKeyboardButton("🎓 دوره‌ها", callback_data="kn_cat_courses"),
            ],
            [
                InlineKeyboardButton("📢 اطلاعیه‌ها", callback_data="kn_cat_announcements"),
                InlineKeyboardButton("🎯 مهارت‌ها", callback_data="kn_cat_skills"),
            ],
            [
                InlineKeyboardButton("📜 مقررات", callback_data="kn_cat_regulations"),
                InlineKeyboardButton("💼 شغلی", callback_data="kn_cat_career"),
            ],
            [InlineKeyboardButton("⏭️ رد کردن", callback_data="kn_cat_skip")],
            [InlineKeyboardButton(I18nService.t("common.cancel", language), callback_data="knowledge_cancel")],
        ]),
    )
    return ADMIN_KNOWLEDGE_CATEGORY


async def knowledge_category_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle category selection."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    language = UserStorage.get_user_language(user_id)
    data = query.data

    if data == "kn_cat_skip":
        context.user_data["knowledge_category"] = None
    elif data.startswith("kn_cat_"):
        context.user_data["knowledge_category"] = data.replace("kn_cat_", "")
    else:
        await query.edit_message_text("انتخاب نامعتبر.")
        return ADMIN_KNOWLEDGE_CATEGORY

    await query.edit_message_text(
        "برچسب‌ها (Tags) را وارد کنید (با کاما جدا کنید):\n"
        "مثال: برنامه‌نویسی، پایتون، مقدماتی",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("⏭️ رد کردن", callback_data="kn_tags_skip"),
            InlineKeyboardButton(I18nService.t("common.cancel", language), callback_data="knowledge_cancel")
        ]]),
    )
    return ADMIN_KNOWLEDGE_TAGS


async def knowledge_tags_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive tags."""
    user_id = update.effective_user.id
    language = UserStorage.get_user_language(user_id)
    text = update.message.text.strip()

    if text and text != "⏭️ رد کردن":
        tags = [t.strip() for t in text.split("،") if t.strip()]
    else:
        tags = []

    context.user_data["knowledge_tags"] = tags

    await update.message.reply_text(
        "زبان محتوا را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🇮🇷 فارسی", callback_data="kn_lang_fa"),
                InlineKeyboardButton("🇬🇧 English", callback_data="kn_lang_en"),
            ],
            [
                InlineKeyboardButton("🇸🇦 العربية", callback_data="kn_lang_ar"),
            ],
            [InlineKeyboardButton(I18nService.t("common.cancel", language), callback_data="knowledge_cancel")],
        ]),
    )
    return ADMIN_KNOWLEDGE_LANG


async def knowledge_language_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle language selection and save knowledge."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    language = UserStorage.get_user_language(user_id)
    data = query.data

    lang_map = {"kn_lang_fa": "fa", "kn_lang_en": "en", "kn_lang_ar": "ar"}
    content_lang = lang_map.get(data, "fa")

    content = context.user_data.get("knowledge_content", "")
    category = context.user_data.get("knowledge_category")
    tags = context.user_data.get("knowledge_tags", [])
    source_type = context.user_data.get("knowledge_source_type", "manual")

    # Ingest to knowledge base
    chunk_ids = KnowledgeService.ingest_text(
        content=content,
        source_type=source_type,
        language=content_lang,
        category=category,
        tags=tags,
        source_title="افزوده شده توسط ادمین",
    )

    if chunk_ids:
        await query.edit_message_text(
            f"✅ {I18nService.t('admin.knowledge_added', language)}\n"
            f"تعداد قطعات: {len(chunk_ids)}\n"
            f"دسته‌بندی: {category or 'general'}\n"
            f"زبان: {content_lang}\n"
            f"برچسب‌ها: {', '.join(tags) if tags else 'ندارد'}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(I18nService.t("common.back", language), callback_data="admin_knowledge")
            ]]),
        )
    else:
        await query.edit_message_text(
            "❌ خطا در افزودن دانش (احتمالا تکراری است).",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(I18nService.t("common.back", language), callback_data="admin_knowledge")
            ]]),
        )

    context.user_data.clear()
    return ConversationHandler.END


def get_knowledge_conversation() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(knowledge_callback, pattern=r"^admin_knowledge$")],
        states={
            ADMIN_KNOWLEDGE_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, knowledge_text_received)],
            ADMIN_KNOWLEDGE_CATEGORY: [CallbackQueryHandler(knowledge_category_selected, pattern=r"^kn_cat_")],
            ADMIN_KNOWLEDGE_TAGS: [MessageHandler(filters.TEXT & ~filters.COMMAND, knowledge_tags_received)],
            ADMIN_KNOWLEDGE_LANG: [CallbackQueryHandler(knowledge_language_selected, pattern=r"^kn_lang_")],
        },
        fallbacks=[CallbackQueryHandler(knowledge_callback, pattern=r"^knowledge_cancel$")],
        per_user=True,
        per_chat=True,
    )


# =============================================================================
# Scraper Management
# =============================================================================

async def _show_scrapers_menu(query, language: str) -> None:
    """Show scrapers management menu."""
    jobs = UserStorage.get_active_scrape_jobs()

    text = f"🕷️ {I18nService.t('admin.scrapers', language)}\n\n"
    if jobs:
        for job in jobs:
            status = job.get("last_status", "unknown")
            last_run = job.get("last_run_at", "never")[:19] if job.get("last_run_at") else "never"
            text += f"• {job['name']} ({job.get('category', 'general')})\n  وضعیت: {status} | آخرین اجرا: {last_run}\n\n"
    else:
        text += "هیچ اسکریپری تعریف نشده.\n"

    await query.edit_message_text(
        escape_markdown(text),
        parse_mode="MarkdownV2",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(I18nService.t("admin.trigger_scrape", language), callback_data="scraper_run_all")],
            [InlineKeyboardButton("▶️ اجرای همه", callback_data="scraper_run_all")],
            [InlineKeyboardButton("📋 مشاهده لاگ‌ها", callback_data="scraper_logs")],
            [InlineKeyboardButton(I18nService.t("common.back", language), callback_data="admin_back")],
        ]),
    )


async def scraper_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle scraper callbacks."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("⛔ دسترسی ادمین نیست!", show_alert=True)
        return ConversationHandler.END

    language = UserStorage.get_user_language(user_id)
    data = query.data

    if data == "scraper_run_all":
        await query.edit_message_text(I18nService.t("common.loading", language))
        # Run scrapers in background
        context.application.create_task(_run_all_scrapers_background(query, language))
        return ConversationHandler.END

    elif data == "scraper_logs":
        jobs = UserStorage.get_active_scrape_jobs()
        text = "📋 لاگ‌های اسکریپرها:\n\n"
        for job in jobs:
            text += f"• {job['name']}\n  وضعیت: {job.get('last_status', 'unknown')}\n  خطا: {job.get('last_error', 'ندارد')[:100]}\n\n"

        await query.edit_message_text(
            escape_markdown(text),
            parse_mode="MarkdownV2",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(I18nService.t("common.back", language), callback_data="admin_scrapers")
            ]]),
        )
        return ConversationHandler.END

    return ConversationHandler.END


async def _run_all_scrapers_background(query, language: str):
    """Run all scrapers in background and update message."""
    try:
        async with WebScraperService() as scraper:
            results = await scraper.run_all_jobs()

        text = f"✅ {I18nService.t('admin.scrape_triggered', language)}\n\n"
        for r in results:
            text += f"• {r['job_name']}: {r['new_chunks']} قطعه جدید، {r['pages_fetched']} صفحه\n"

        await query.edit_message_text(
            escape_markdown(text),
            parse_mode="MarkdownV2",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(I18nService.t("common.back", language), callback_data="admin_scrapers")
            ]]),
        )
    except Exception as e:
        logger.error("Background scraper run failed: %s", e)
        await query.edit_message_text(
            f"❌ خطا در اجرای اسکریپرها: {str(e)[:100]}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(I18nService.t("common.back", language), callback_data="admin_scrapers")
            ]]),
        )


def get_scraper_conversation() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(scraper_callback, pattern=r"^admin_scrapers$")],
        states={
            ADMIN_SCRAPER_RUN: [CallbackQueryHandler(scraper_callback, pattern=r"^scraper_")],
        },
        fallbacks=[],
        per_user=True,
        per_chat=True,
    )


# =============================================================================
# Broadcast
# =============================================================================

async def _start_broadcast_callback(query, language: str) -> int:
    await query.edit_message_text(
        "📢 ارسال پیام همگانی\n\n"
        "متن پیام را بنویسید. برای لغو /cancel بفرستید.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(I18nService.t("common.cancel", language), callback_data="broadcast_cancel")
        ]]),
    )
    return BROADCAST_TEXT


async def receive_broadcast_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message:
        return ConversationHandler.END

    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("⛔ شما دسترسی ادمین ندارید!")
        return ConversationHandler.END

    text = update.message.text
    users = UserStorage.get_all_users()

    await update.message.reply_text(
        f"📤 در حال ارسال پیام به {len(users)} کاربر... لطفاً صبر کنید.",
    )

    success = 0
    failed = 0

    for user in users:
        try:
            await context.bot.send_message(
                chat_id=user["user_id"],
                text=(
                    "📢 پیام همگانی از طرف مدیریت:\n\n"
                    f"{text}\n\n"
                    f"---\nربات {BOT_USERNAME}"
                ),
            )
            success += 1
        except Exception as e:
            logger.warning("Broadcast failed for user %d: %s", user["user_id"], str(e))
            failed += 1

    await update.message.reply_text(
        f"✅ پیام همگانی ارسال شد!\n\n"
        f"✓ موفق: {success}\n"
        f"✗ ناموفق: {failed}\n"
        f"👥 کل: {len(users)}",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("👑 پنل ادمین", callback_data="admin_back")
        ]]),
    )

    return ConversationHandler.END


async def cancel_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "❌ ارسال پیام همگانی لغو شد.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("👑 پنل ادمین", callback_data="admin_back")
        ]]),
    )
    return ConversationHandler.END


def get_broadcast_conversation() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(_start_broadcast_callback, pattern=r"^admin_broadcast$")],
        states={
            BROADCAST_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_broadcast_text)],
        },
        fallbacks=[CommandHandler("cancel", cancel_broadcast)],
        per_user=True,
        per_chat=True,
    )


# =============================================================================
# Exported handlers
# =============================================================================

def get_admin_handlers() -> List:
    """Get all admin handlers."""
    return [
        CallbackQueryHandler(admin_callback, pattern=r"^admin_"),
        CallbackQueryHandler(knowledge_callback, pattern=r"^(knowledge_|kn_)"),
        CallbackQueryHandler(scraper_callback, pattern=r"^scraper_"),
        get_knowledge_conversation(),
        get_scraper_conversation(),
        get_broadcast_conversation(),
    ]