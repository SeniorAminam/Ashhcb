# Project: Ashhcb Bot - Mazandaran Skills University AI Assistant
# File Path: src/handlers/search.py
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
# Purpose: Search handlers for knowledge base, skills, announcements, web search
# License: MIT
# Copyright: (c) Amin Davodian

"""
Search Handlers for hybrid search functionality.

Handles:
- General knowledge base search
- Skills/courses search with filters
- Announcements search
- Web search integration
- Category-based search
"""

import logging
from typing import List, Optional

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from src.services.search_service import SearchService
from src.services.i18n_service import I18nService
from src.services.storage import UserStorage
from src.utils.helpers import escape_markdown

logger = logging.getLogger(__name__)

# Conversation states
SEARCH_QUERY, SEARCH_CATEGORY, SKILLS_QUERY, SKILLS_CATEGORY, SKILLS_LEVEL = range(5)

# Category mappings
SEARCH_CATEGORIES = {
    "all": "همه",
    "admission": "پذیرش",
    "courses": "دوره‌ها",
    "announcements": "اطلاعیه‌ها",
    "skills": "مهارت‌ها",
    "regulations": "مقررات",
    "career": "شغلی",
}

SKILL_CATEGORIES = {
    "digital": "دیجیتال",
    "technical": "فنی",
    "soft": "نرم",
    "language": "زبان",
    "business": "کسب‌وکار",
}

SKILL_LEVELS = {
    "beginner": "مبتدی",
    "intermediate": "میان‌پیشرفته",
    "advanced": "پیشرفته",
}


async def search_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry point for search conversation."""
    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text(
            I18nService.t("search.prompt", UserStorage.get_user_language(query.from_user.id)),
            reply_markup=_get_search_category_keyboard(UserStorage.get_user_language(query.from_user.id)),
        )
    else:
        await update.message.reply_text(
            I18nService.t("search.prompt", UserStorage.get_user_language(update.effective_user.id)),
            reply_markup=_get_search_category_keyboard(UserStorage.get_user_language(update.effective_user.id)),
        )
    return SEARCH_CATEGORY


async def search_category_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle category selection."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    language = UserStorage.get_user_language(user_id)
    data = query.data

    if data == "search_cat_all":
        context.user_data["search_category"] = None
    elif data.startswith("search_cat_"):
        context.user_data["search_category"] = data.replace("search_cat_", "")
    else:
        await query.edit_message_text(I18nService.t("errors.invalid_input", language))
        return SEARCH_CATEGORY

    await query.edit_message_text(
        I18nService.t("search.prompt", language),
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(I18nService.t("common.cancel", language), callback_data="search_cancel")
        ]]),
    )
    return SEARCH_QUERY


async def search_query_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process search query and show results."""
    user_id = update.effective_user.id
    language = UserStorage.get_user_language(user_id)
    query_text = update.message.text.strip()
    category = context.user_data.get("search_category")

    if not query_text:
        await update.message.reply_text(I18nService.t("errors.invalid_input", language))
        return SEARCH_QUERY

    # Show loading
    loading_msg = await update.message.reply_text(I18nService.t("common.loading", language))

    # Perform hybrid search
    async with SearchService() as service:
        results = await service.search(
            query=query_text,
            language=language,
            category=category,
            include_web=True,
        )

    # Format and send results
    formatted = service.format_results_for_display(results, language, max_items=5)

    await loading_msg.edit_text(
        escape_markdown(formatted),
        parse_mode="MarkdownV2",
        reply_markup=_get_search_results_keyboard(language, query_text, category),
    )

    # Clear conversation data
    context.user_data.clear()
    return ConversationHandler.END


# Skills search conversation
async def skills_search_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry point for skills search."""
    query = update.callback_query
    if query:
        await query.answer()

    user_id = query.from_user.id
    language = UserStorage.get_user_language(user_id)

    await query.edit_message_text(
        I18nService.t("skills.search_prompt", language),
        reply_markup=_get_skills_category_keyboard(language),
    )
    return SKILLS_CATEGORY


async def skills_category_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle skills category selection."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    language = UserStorage.get_user_language(user_id)
    data = query.data

    if data == "skills_cat_all":
        context.user_data["skills_category"] = None
    elif data.startswith("skills_cat_"):
        context.user_data["skills_category"] = data.replace("skills_cat_", "")
    else:
        await query.edit_message_text(I18nService.t("errors.invalid_input", language))
        return SKILLS_CATEGORY

    await query.edit_message_text(
        "سطح مهارت را انتخاب کنید:",
        reply_markup=_get_skills_level_keyboard(language),
    )
    return SKILLS_LEVEL


async def skills_level_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle skills level selection."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    language = UserStorage.get_user_language(user_id)
    data = query.data

    if data == "skills_level_all":
        context.user_data["skills_level"] = None
    elif data.startswith("skills_level_"):
        context.user_data["skills_level"] = data.replace("skills_level_", "")
    else:
        await query.edit_message_text(I18nService.t("errors.invalid_input", language))
        return SKILLS_LEVEL

    await query.edit_message_text(
        I18nService.t("skills.search_prompt", language),
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(I18nService.t("common.cancel", language), callback_data="search_cancel")
        ]]),
    )
    return SKILLS_QUERY


async def skills_query_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process skills search query."""
    user_id = update.effective_user.id
    language = UserStorage.get_user_language(user_id)
    query_text = update.message.text.strip()
    category = context.user_data.get("skills_category")
    level = context.user_data.get("skills_level")

    if not query_text:
        await update.message.reply_text(I18nService.t("errors.invalid_input", language))
        return SKILLS_QUERY

    loading_msg = await update.message.reply_text(I18nService.t("common.loading", language))

    async with SearchService() as service:
        results = await service.search_skills(
            query=query_text,
            language=language,
            skill_category=category,
            level=level,
        )

    formatted = service.format_results_for_display(results, language, max_items=5)

    await loading_msg.edit_text(
        escape_markdown(formatted),
        parse_mode="MarkdownV2",
        reply_markup=_get_search_results_keyboard(language, query_text, f"skills:{category}" if category else "skills"),
    )

    context.user_data.clear()
    return ConversationHandler.END


# Announcements search
async def announcements_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show recent announcements."""
    query = update.callback_query
    if query:
        await query.answer()
        user_id = query.from_user.id
    else:
        user_id = update.effective_user.id

    language = UserStorage.get_user_language(user_id)

    loading_msg = None
    if query:
        loading_msg = await query.edit_message_text(I18nService.t("common.loading", language))
    else:
        loading_msg = await update.message.reply_text(I18nService.t("common.loading", language))

    async with SearchService() as service:
        results = await service.search_announcements(language=language)

    formatted = service.format_results_for_display(results, language, max_items=5)

    target = query.edit_message_text if query else update.message.reply_text
    await target(
        escape_markdown(formatted),
        parse_mode="MarkdownV2",
        reply_markup=_get_search_results_keyboard(language, "", "announcements"),
    )


# Callback handlers
async def search_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle search-related callbacks."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    language = UserStorage.get_user_language(user_id)
    data = query.data

    if data == "search_cancel":
        await query.edit_message_text(
            I18nService.t("common.cancel", language),
            reply_markup=_get_main_menu_keyboard(language),
        )
    elif data == "search_again":
        await search_entry(update, context)
    elif data == "skills_search":
        await skills_search_entry(update, context)
    elif data == "announcements_search":
        await announcements_search(update, context)


def _get_search_category_keyboard(language: str) -> InlineKeyboardMarkup:
    """Get search category selection keyboard."""
    buttons = []
    row = []
    for key, label in SEARCH_CATEGORIES.items():
        row.append(InlineKeyboardButton(label, callback_data=f"search_cat_{key}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(I18nService.t("common.cancel", language), callback_data="search_cancel")])
    return InlineKeyboardMarkup(buttons)


def _get_skills_category_keyboard(language: str) -> InlineKeyboardMarkup:
    """Get skills category keyboard."""
    buttons = []
    row = []
    for key, label in SKILL_CATEGORIES.items():
        row.append(InlineKeyboardButton(label, callback_data=f"skills_cat_{key}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("همه", callback_data="skills_cat_all")])
    buttons.append([InlineKeyboardButton(I18nService.t("common.cancel", language), callback_data="search_cancel")])
    return InlineKeyboardMarkup(buttons)


def _get_skills_level_keyboard(language: str) -> InlineKeyboardMarkup:
    """Get skills level keyboard."""
    buttons = []
    row = []
    for key, label in SKILL_LEVELS.items():
        row.append(InlineKeyboardButton(label, callback_data=f"skills_level_{key}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("همه", callback_data="skills_level_all")])
    buttons.append([InlineKeyboardButton(I18nService.t("common.cancel", language), callback_data="search_cancel")])
    return InlineKeyboardMarkup(buttons)


def _get_search_results_keyboard(language: str, query: str, category: str) -> InlineKeyboardMarkup:
    """Get keyboard for search results."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔍 جستجوی مجدد", callback_data="search_again"),
            InlineKeyboardButton("🎓 جستجوی مهارت‌ها", callback_data="skills_search"),
        ],
        [
            InlineKeyboardButton("📢 اطلاعیه‌ها", callback_data="announcements_search"),
            InlineKeyboardButton(I18nService.t("common.back", language), callback_data="main_menu"),
        ],
    ])


def _get_main_menu_keyboard(language: str) -> InlineKeyboardMarkup:
    """Get main menu keyboard."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(I18nService.t("menu.search", language), callback_data="menu_search"),
            InlineKeyboardButton(I18nService.t("menu.chat", language), callback_data="menu_chat"),
        ],
        [
            InlineKeyboardButton(I18nService.t("menu.skills", language), callback_data="skills_search"),
            InlineKeyboardButton(I18nService.t("menu.announcements", language), callback_data="announcements_search"),
        ],
    ])


def get_search_conversation_handler() -> ConversationHandler:
    """Get general search conversation handler."""
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(search_entry, pattern=r"^menu_search$")],
        states={
            SEARCH_CATEGORY: [CallbackQueryHandler(search_category_selected, pattern=r"^search_cat_")],
            SEARCH_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, search_query_received)],
        },
        fallbacks=[CallbackQueryHandler(search_callback, pattern=r"^search_cancel$")],
        per_user=True,
        per_chat=True,
    )


def get_skills_search_conversation_handler() -> ConversationHandler:
    """Get skills search conversation handler."""
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(skills_search_entry, pattern=r"^(menu_skills|skills_search)$")],
        states={
            SKILLS_CATEGORY: [CallbackQueryHandler(skills_category_selected, pattern=r"^skills_cat_")],
            SKILLS_LEVEL: [CallbackQueryHandler(skills_level_selected, pattern=r"^skills_level_")],
            SKILLS_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, skills_query_received)],
        },
        fallbacks=[CallbackQueryHandler(search_callback, pattern=r"^search_cancel$")],
        per_user=True,
        per_chat=True,
    )


def get_search_callback_handlers() -> List:
    """Get search callback handlers."""
    return [
        CallbackQueryHandler(announcements_search, pattern=r"^(menu_announcements|announcements_search)$"),
        CallbackQueryHandler(search_callback, pattern=r"^(search_again|skills_search|announcements_search|search_cancel)$"),
    ]


# Export all handlers
def get_all_search_handlers() -> List:
    """Get all search-related handlers."""
    return [
        get_search_conversation_handler(),
        get_skills_search_conversation_handler(),
        *get_search_callback_handlers(),
    ]