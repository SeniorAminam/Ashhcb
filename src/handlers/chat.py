# Project: Ashhcb Bot - Mazandaran Skills University AI Assistant
# File Path: src/handlers/chat.py
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
# Purpose: Free-form RAG chat handler
# License: MIT
# Copyright: (c) Amin Davodian

"""
Chat Handler for free-form conversation with RAG.

Handles:
- Natural language questions
- Context-aware responses using knowledge base
- Multi-language support
- Conversation history
"""

import logging
from typing import Dict, List, Optional

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from src.services.ai_service import AIService
from src.services.i18n_service import I18nService
from src.services.storage import UserStorage
from src.utils.helpers import escape_markdown

logger = logging.getLogger(__name__)

# In-memory conversation history (per user)
_conversation_history: Dict[int, List[Dict[str, str]]] = {}
MAX_HISTORY = 10

# AI Service instance
_ai_service = AIService()


async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle free-form text messages as chat queries."""
    if not update.message or not update.message.text:
        return

    user_id = update.effective_user.id
    text = update.message.text.strip()

    # Skip commands
    if text.startswith("/"):
        return

    # Get user language
    language = UserStorage.get_user_language(user_id)

    # Send "thinking" indicator
    thinking_msg = await update.message.reply_text(
        I18nService.t("chat.thinking", language)
    )

    # Get conversation history
    history = _conversation_history.get(user_id, [])

    # Process with RAG
    response, sources = await _ai_service.chat_with_rag(
        user_message=text,
        language=language,
        mode="chat",
        conversation_history=history,
    )

    # Update history
    history.append({"role": "user", "content": text})
    history.append({"role": "assistant", "content": response})
    if len(history) > MAX_HISTORY * 2:
        history = history[-MAX_HISTORY * 2:]
    _conversation_history[user_id] = history

    # Format response with sources
    formatted_response = response
    if sources:
        source_lines = [I18nService.t("chat.sources", language)]
        for src in sources:
            source_lines.append(f"  {src['index']}. {src['title']}")
        formatted_response += "\n\n" + "\n".join(source_lines)

    # Edit thinking message with response
    try:
        await thinking_msg.edit_text(
            escape_markdown(formatted_response),
            parse_mode="MarkdownV2",
            reply_markup=_get_chat_keyboard(language),
        )
    except Exception as e:
        logger.warning("Failed to edit thinking message: %s", e)
        await update.message.reply_text(
            escape_markdown(formatted_response),
            parse_mode="MarkdownV2",
            reply_markup=_get_chat_keyboard(language),
        )


async def chat_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle chat-related callback queries."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    language = UserStorage.get_user_language(user_id)
    data = query.data

    if data == "chat_clear_history":
        _conversation_history.pop(user_id, None)
        await query.edit_message_text(
            I18nService.t("common.try_again", language),
            reply_markup=_get_chat_keyboard(language),
        )
    elif data == "chat_switch_mode":
        # Show mode selection
        await query.edit_message_text(
            "حالت چت را انتخاب کنید:",
            reply_markup=_get_mode_keyboard(language),
        )
    elif data.startswith("chat_mode_"):
        mode = data.replace("chat_mode_", "")
        context.user_data["chat_mode"] = mode
        mode_names = {
            "chat": "چت عمومی",
            "admissions": "مشاوره پذیرش",
            "career": "مشاوره شغلی",
            "skills": "مهارت‌ها و دوره‌ها",
        }
        await query.edit_message_text(
            f"حالت چت به «{mode_names.get(mode, mode)}» تغییر کرد.",
            reply_markup=_get_chat_keyboard(language),
        )


def _get_chat_keyboard(language: str) -> InlineKeyboardMarkup:
    """Get chat action keyboard."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                I18nService.t("menu.search", language),
                callback_data="menu_search",
            ),
            InlineKeyboardButton(
                "🧹 پاک کردن تاریخچه",
                callback_data="chat_clear_history",
            ),
        ],
        [
            InlineKeyboardButton(
                "🔄 تغییر حالت",
                callback_data="chat_switch_mode",
            ),
            InlineKeyboardButton(
                I18nService.t("common.back", language),
                callback_data="main_menu",
            ),
        ],
    ])


def _get_mode_keyboard(language: str) -> InlineKeyboardMarkup:
    """Get chat mode selection keyboard."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💬 چت عمومی", callback_data="chat_mode_chat"),
            InlineKeyboardButton("📝 مشاوره پذیرش", callback_data="chat_mode_admissions"),
        ],
        [
            InlineKeyboardButton("💼 مشاوره شغلی", callback_data="chat_mode_career"),
            InlineKeyboardButton("🎓 مهارت‌ها", callback_data="chat_mode_skills"),
        ],
        [
            InlineKeyboardButton(I18nService.t("common.back", language), callback_data="chat_switch_mode"),
        ],
    ])


def get_chat_handlers() -> List:
    """Get all chat handlers."""
    return [
        MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler),
        CallbackQueryHandler(chat_callback, pattern=r"^chat_"),
    ]


# Export for backward compatibility
chat_handler.__doc__ = "Handle free-form chat messages with RAG"
chat_callback.__doc__ = "Handle chat callback queries"