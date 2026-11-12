# Project: Ashhcb Bot - Mazandaran Skills University AI Assistant
# File Path: src/handlers/menu.py
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
# Purpose: Menu-driven interface handlers
# License: MIT
# Copyright: (c) Amin Davodian

"""
Menu Handler for menu-driven interface.

Handles:
- Main menu display
- Settings (language selection)
- User panel
- Admin panel entry
- Quick actions
"""

import logging
from typing import List

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from src.services.i18n_service import I18nService, SUPPORTED_LANGUAGES
from src.services.storage import UserStorage
from src.utils.helpers import escape_markdown

logger = logging.getLogger(__name__)

# Conversation states for settings
SETTINGS_LANGUAGE = 0


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command - show welcome and main menu."""
    user = update.effective_user
    user_id = user.id

    # Get or create user
    UserStorage.get_or_create_user(
        user_id=user_id,
        username=user.username,
        first_name=user.first_name,
    )

    language = UserStorage.get_user_language(user_id)

    welcome_text = (
        f"{I18nService.t('welcome', language)}\n\n"
        f"{I18nService.t('welcome_subtitle', language)}"
    )

    await update.message.reply_text(
        escape_markdown(welcome_text),
        parse_mode="MarkdownV2",
        reply_markup=_get_main_menu_keyboard(language),
    )


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle main menu callbacks."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    language = UserStorage.get_user_language(user_id)
    data = query.data

    if data == "main_menu":
        welcome_text = (
            f"{I18nService.t('welcome', language)}\n\n"
            f"{I18nService.t('welcome_subtitle', language)}"
        )
        await query.edit_message_text(
            escape_markdown(welcome_text),
            parse_mode="MarkdownV2",
            reply_markup=_get_main_menu_keyboard(language),
        )
    elif data == "menu_settings":
        await _show_settings(query, language)
    elif data == "menu_user_panel":
        await _show_user_panel(query, language)
    elif data == "menu_admin":
        await _show_admin_panel(query, language)
    elif data == "menu_help":
        await _show_help(query, language)


async def settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle settings callbacks."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    language = UserStorage.get_user_language(user_id)
    data = query.data

    if data == "settings_language":
        await query.edit_message_text(
            f"{I18nService.t('settings.language', language)}\n\n"
            "زبان مورد نظر را انتخاب کنید:",
            reply_markup=_get_language_keyboard(language),
        )
        return SETTINGS_LANGUAGE
    elif data == "settings_back":
        await menu_callback(update, context)
        return ConversationHandler.END

    return SETTINGS_LANGUAGE


async def language_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle language selection."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    if data.startswith("lang_"):
        new_lang = data.replace("lang_", "")
        if new_lang in SUPPORTED_LANGUAGES:
            UserStorage.set_user_language(user_id, new_lang)
            language = new_lang
            await query.edit_message_text(
                I18nService.t("settings.language_changed", language).format(
                    language=I18nService.get_language_name(language)
                ),
                reply_markup=_get_main_menu_keyboard(language),
            )
        else:
            await query.edit_message_text("زبان نامعتبر است.")
    else:
        await query.edit_message_text("انتخاب نامعتبر.")

    return ConversationHandler.END


async def _show_settings(query, language: str) -> None:
    """Show settings menu."""
    await query.edit_message_text(
        "⚙️ تنظیمات",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(I18nService.t("settings.language", language), callback_data="settings_language")],
            [InlineKeyboardButton(I18nService.t("common.back", language), callback_data="main_menu")],
        ]),
    )


async def _show_user_panel(query, language: str) -> None:
    """Show user panel with stats."""
    user_id = query.from_user.id
    stats = UserStorage.get_user_stats(user_id)

    if not stats:
        await query.edit_message_text(
            "اطلاعات کاربری یافت نشد.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(I18nService.t("common.back", language), callback_data="main_menu")
            ]]),
        )
        return

    user = stats.get("user", {})
    style_counts = stats.get("style_counts", [])
    today_count = stats.get("today_count", 0)

    text_lines = [
        f"👤 {I18nService.t('user_panel.title', language)}",
        f"نام: {user.get('first_name', 'نامشخص')}",
        f"نام کاربری: @{user.get('username', 'ندارد')}",
        f"{I18nService.t('user_panel.joined', language).format(date=user.get('join_date', '').split('T')[0])}",
        "",
        f"{I18nService.t('user_panel.total_queries', language).format(count=user.get('total_transforms', 0))}",
        f"{I18nService.t('user_panel.today_queries', language).format(count=today_count)}",
    ]

    if style_counts:
        text_lines.append("\n📊 آمار استفاده:")
        for sc in style_counts[:5]:
            text_lines.append(f"  • {sc['style_label']}: {sc['count']}")

    await query.edit_message_text(
        escape_markdown("\n".join(text_lines)),
        parse_mode="MarkdownV2",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(I18nService.t("user_panel.history", language), callback_data="user_history")],
            [InlineKeyboardButton(I18nService.t("user_panel.language", language), callback_data="settings_language")],
            [InlineKeyboardButton(I18nService.t("common.back", language), callback_data="main_menu")],
        ]),
    )


async def _show_admin_panel(query, language: str) -> None:
    """Show admin panel (only for admins)."""
    user_id = query.from_user.id
    user = UserStorage.get_or_create_user(user_id)

    if not user.get("is_admin"):
        await query.answer("شما دسترسی ادمین ندارید.", show_alert=True)
        return

    stats = UserStorage.get_total_stats()

    text_lines = [
        f"👑 {I18nService.t('admin.panel', language)}",
        f"👥 کاربران: {stats['total_users']}",
        f"🔄 کل تبدیل‌ها: {stats['total_transforms']}",
        f"📅 امروز: {stats['today_transforms']}",
    ]

    await query.edit_message_text(
        escape_markdown("\n".join(text_lines)),
        parse_mode="MarkdownV2",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(I18nService.t("admin.stats", language), callback_data="admin_stats")],
            [InlineKeyboardButton(I18nService.t("admin.users", language), callback_data="admin_users")],
            [InlineKeyboardButton(I18nService.t("admin.knowledge", language), callback_data="admin_knowledge")],
            [InlineKeyboardButton(I18nService.t("admin.scrapers", language), callback_data="admin_scrapers")],
            [InlineKeyboardButton(I18nService.t("common.back", language), callback_data="main_menu")],
        ]),
    )


async def _show_help(query, language: str) -> None:
    """Show help message."""
    help_text = (
        f"📖 راهنما\n\n"
        f"این ربات دستیار هوشمند دانشگاه ملی مهارت مازندران است.\n\n"
        f"🔍 جستجو: در پایگاه دانش، مهارت‌ها و اطلاعیه‌ها جستجو کنید\n"
        f"💬 چت آزاد: سوالات خود را به زبان طبیعی بپرسید\n"
        f"🎓 مهارت‌ها: دوره‌ها و وورشاپ‌ها را 발견 کنید\n"
        f"📝 پذیرش: اطلاعات ثبت‌نام و شرایط پذیرش\n"
        f"💼 مشاوره شغلی: مسیر شغلی و مهارت‌های مورد نیاز\n"
        f"📢 اطلاعیه‌ها: آخرین اخبار و اعلان‌ها\n"
        f"🖼️ تولید تصویر: ابزارهای هوش مصنوعی تصویر\n"
        f"⚙️ تنظیمات: تغییر زبان و تنظیمات حساب\n\n"
        f"برای شروع، یکی از گزینه‌های منو را انتخاب کنید."
    )

    await query.edit_message_text(
        escape_markdown(help_text),
        parse_mode="MarkdownV2",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(I18nService.t("common.back", language), callback_data="main_menu")
        ]]),
    )


def _get_main_menu_keyboard(language: str) -> InlineKeyboardMarkup:
    """Get main menu keyboard."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(I18nService.t("menu.search", language), callback_data="menu_search"),
            InlineKeyboardButton(I18nService.t("menu.chat", language), callback_data="menu_chat"),
        ],
        [
            InlineKeyboardButton(I18nService.t("menu.skills", language), callback_data="menu_skills"),
            InlineKeyboardButton(I18nService.t("menu.admissions", language), callback_data="menu_admissions"),
        ],
        [
            InlineKeyboardButton(I18nService.t("menu.career", language), callback_data="menu_career"),
            InlineKeyboardButton(I18nService.t("menu.announcements", language), callback_data="menu_announcements"),
        ],
        [
            InlineKeyboardButton(I18nService.t("menu.settings", language), callback_data="menu_settings"),
        ],
        [
            InlineKeyboardButton(I18nService.t("menu.user_panel", language), callback_data="menu_user_panel"),
        ],
    ])


def _get_language_keyboard(current_language: str) -> InlineKeyboardMarkup:
    """Get language selection keyboard."""
    flags = {"fa": "🇮🇷", "en": "🇬🇧", "ar": "🇸🇦"}
    buttons = []
    for lang in SUPPORTED_LANGUAGES:
        name = I18nService.get_language_name(lang)
        flag = flags.get(lang, "")
        marker = " ✅" if lang == current_language else ""
        buttons.append([InlineKeyboardButton(f"{flag} {name}{marker}", callback_data=f"lang_{lang}")])
    buttons.append([InlineKeyboardButton(I18nService.t("common.back", current_language), callback_data="settings_back")])
    return InlineKeyboardMarkup(buttons)


def get_menu_conversation_handler() -> ConversationHandler:
    """Get settings conversation handler."""
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(settings_callback, pattern=r"^menu_settings$")],
        states={
            SETTINGS_LANGUAGE: [
                CallbackQueryHandler(language_selected, pattern=r"^lang_"),
                CallbackQueryHandler(settings_callback, pattern=r"^settings_back$"),
            ],
        },
        fallbacks=[CallbackQueryHandler(settings_callback, pattern=r"^settings_back$")],
        per_user=True,
        per_chat=True,
    )


def get_menu_handlers() -> List:
    """Get all menu handlers."""
    return [
        CommandHandler("start", start_command),
        CommandHandler("menu", start_command),
        CallbackQueryHandler(menu_callback, pattern=r"^main_menu$"),
        CallbackQueryHandler(menu_callback, pattern=r"^menu_(settings|user_panel|admin|help)$"),
        get_menu_conversation_handler(),
    ]