# Project: Ashhcb Bot - Mazandaran Skills University AI Assistant
# File Path: src/handlers/advisory.py
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
# Purpose: Academic advising and career guidance handlers
# License: MIT
# Copyright: (c) Amin Davodian

"""
Advisory Handlers for academic advising and career guidance.

Handles:
- Academic advising conversation flow
- Career guidance conversation flow
- Profile collection
- Personalized recommendations
"""

import logging
from typing import List, Dict, Any, Optional

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    CommandHandler,
)

from src.services.ai_service import AIService
from src.services.i18n_service import I18nService
from src.services.storage import UserStorage
from src.utils.helpers import escape_markdown

logger = logging.getLogger(__name__)

# Conversation states for academic advising
ADV_INTERESTS, ADV_SKILLS, ADV_EDUCATION, ADV_GOALS, ADV_FIELDS = range(5)

# Conversation states for career guidance
CAR_INTERESTS, CAR_SKILLS, CAR_EXPERIENCE, CAR_EDUCATION, CAR_INDUSTRIES, CAR_LOCATION = range(6)

_ai_service = AIService()


# =============================================================================
# Academic Advising
# =============================================================================

async def academic_advice_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry point for academic advising."""
    query = update.callback_query
    if query:
        await query.answer()

    user_id = update.effective_user.id
    language = UserStorage.get_user_language(user_id)

    await query.edit_message_text(
        "🎓 مشاوره تحصیلی\n\n"
        "برای ارائه برنامه تحصیلی شخصی‌سازی شده، لطفاً به سوالات زیر پاسخ دهید.\n\n"
        "مرحله ۱ از ۵: علایق و علاقه‌مندی‌های شما چیست؟\n"
        "(مثال: برنامه‌نویسی، طراحی، تحلیل داده، مدیریت پروژه)",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(I18nService.t("common.cancel", language), callback_data="adv_cancel")
        ]]),
    )
    context.user_data["adv_profile"] = {}
    return ADV_INTERESTS


async def adv_interests_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    language = UserStorage.get_user_language(user_id)
    text = update.message.text.strip()

    if not text:
        await update.message.reply_text("لطفاً علایق خود را وارد کنید.")
        return ADV_INTERESTS

    context.user_data["adv_profile"]["interests"] = [i.strip() for i in text.split("،") if i.strip()]

    await update.message.reply_text(
        "مرحله ۲ از ۵: مهارت‌های فعلی شما چیست؟\n"
        "(مثال: Python، Excel، ارتباطات، حل مسئله)",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(I18nService.t("common.cancel", language), callback_data="adv_cancel")
        ]]),
    )
    return ADV_SKILLS


async def adv_skills_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    language = UserStorage.get_user_language(user_id)
    text = update.message.text.strip()

    context.user_data["adv_profile"]["skills"] = [s.strip() for s in text.split("،") if s.strip()]

    await update.message.reply_text(
        "مرحله ۳ از ۵: سطح تحصیلات فعلی شما چیست؟\n"
        "(مثال: دیپلم، لیسانس، فوق‌لیسانس، دانش‌آموز)",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(I18nService.t("common.cancel", language), callback_data="adv_cancel")
        ]]),
    )
    return ADV_EDUCATION


async def adv_education_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    language = UserStorage.get_user_language(user_id)
    text = update.message.text.strip()

    context.user_data["adv_profile"]["education_level"] = text

    await update.message.reply_text(
        "مرحله ۴ از ۵: اهداف تحصیلی و شغلی شما چیست؟\n"
        "(مثال: یافتن کار در حوزه IT، ادامه تحصیل، تغییر مسیر شغلی)",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(I18nService.t("common.cancel", language), callback_data="adv_cancel")
        ]]),
    )
    return ADV_GOALS


async def adv_goals_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    language = UserStorage.get_user_language(user_id)
    text = update.message.text.strip()

    context.user_data["adv_profile"]["goals"] = text

    await update.message.reply_text(
        "مرحله ۵ از ۵: رشته‌ها یا حوزه‌های ترجیحی شما چیست؟\n"
        "(مثال: علوم کامپیوتر، مهندسی، مدیریت، هنر)",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(I18nService.t("common.cancel", language), callback_data="adv_cancel")
        ]]),
    )
    return ADV_FIELDS


async def adv_fields_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    language = UserStorage.get_user_language(user_id)
    text = update.message.text.strip()

    context.user_data["adv_profile"]["preferred_fields"] = [f.strip() for f in text.split("،") if f.strip()]

    # Show processing
    processing_msg = await update.message.reply_text(I18nService.t("common.loading", language))

    # Get academic advice
    profile = context.user_data["adv_profile"]
    advice, sources = await _ai_service.academic_advice(profile, language)

    # Format response
    response = f"🎓 برنامه تحصیلی پیشنهادی\n\n{advice}"

    if sources:
        response += "\n\n" + I18nService.t("chat.sources", language)
        for src in sources:
            response += f"\n  {src['index']}. {src['title']}"

    await processing_msg.edit_text(
        escape_markdown(response),
        parse_mode="MarkdownV2",
        reply_markup=_get_advice_action_keyboard(language),
    )

    context.user_data.clear()
    return ConversationHandler.END


# =============================================================================
# Career Guidance
# =============================================================================

async def career_guidance_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry point for career guidance."""
    query = update.callback_query
    if query:
        await query.answer()

    user_id = update.effective_user.id
    language = UserStorage.get_user_language(user_id)

    await query.edit_message_text(
        "💼 مشاوره شغلی و مهارتی\n\n"
        "برای ارائه مسیر شغلی مناسب، لطفاً به سوالات زیر پاسخ دهید.\n\n"
        "مرحله ۱ از ۶: علایق و علاقه‌مندی‌های شما چیست؟",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(I18nService.t("common.cancel", language), callback_data="car_cancel")
        ]]),
    )
    context.user_data["car_profile"] = {}
    return CAR_INTERESTS


async def car_interests_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    language = UserStorage.get_user_language(user_id)
    text = update.message.text.strip()

    context.user_data["car_profile"]["interests"] = [i.strip() for i in text.split("،") if i.strip()]

    await update.message.reply_text(
        "مرحله ۲ از ۶: مهارت‌های شما چیست؟\n"
        "(مهارت‌های فنی، نرم، زبان‌ها، ابزارها)",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(I18nService.t("common.cancel", language), callback_data="car_cancel")
        ]]),
    )
    return CAR_SKILLS


async def car_skills_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    language = UserStorage.get_user_language(user_id)
    text = update.message.text.strip()

    context.user_data["car_profile"]["skills"] = [s.strip() for s in text.split("،") if s.strip()]

    await update.message.reply_text(
        "مرحله ۳ از ۶: تجربه کاری شما چقدر است؟\n"
        "(مثال: ۲ سال برنامه‌نویسی، تازه فارغ‌التحصیل، ۵ سال مدیریت پروژه)",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(I18nService.t("common.cancel", language), callback_data="car_cancel")
        ]]),
    )
    return CAR_EXPERIENCE


async def car_experience_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    language = UserStorage.get_user_language(user_id)
    text = update.message.text.strip()

    context.user_data["car_profile"]["experience"] = text

    await update.message.reply_text(
        "مرحله ۴ از ۶: آخرین مدرک تحصیلی شما چیست؟",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(I18nService.t("common.cancel", language), callback_data="car_cancel")
        ]]),
    )
    return CAR_EDUCATION


async def car_education_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    language = UserStorage.get_user_language(user_id)
    text = update.message.text.strip()

    context.user_data["car_profile"]["education"] = text

    await update.message.reply_text(
        "مرحله ۵ از ۶: صنایع یا حوزه‌های کاری ترجیحی شما چیست؟\n"
        "(مثال: فناوری اطلاعات، آموزش، بانکداری، استارتاپ)",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(I18nService.t("common.cancel", language), callback_data="car_cancel")
        ]]),
    )
    return CAR_INDUSTRIES


async def car_industries_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    language = UserStorage.get_user_language(user_id)
    text = update.message.text.strip()

    context.user_data["car_profile"]["preferred_industries"] = [i.strip() for i in text.split("،") if i.strip()]

    await update.message.reply_text(
        "مرحله ۶ از ۶: ترجیح مکان کار شما کجاست؟\n"
        "(مثال: مازندران، تهران، راه دور، هیچ ترجیحات)",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(I18nService.t("common.cancel", language), callback_data="car_cancel")
        ]]),
    )
    return CAR_LOCATION


async def car_location_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    language = UserStorage.get_user_language(user_id)
    text = update.message.text.strip()

    context.user_data["car_profile"]["location_preference"] = text

    processing_msg = await update.message.reply_text(I18nService.t("common.loading", language))

    profile = context.user_data["car_profile"]
    guidance, sources = await _ai_service.career_guidance(profile, language)

    response = f"💼 راهنمای شغلی پیشنهادی\n\n{guidance}"

    if sources:
        response += "\n\n" + I18nService.t("chat.sources", language)
        for src in sources:
            response += f"\n  {src['index']}. {src['title']}"

    await processing_msg.edit_text(
        escape_markdown(response),
        parse_mode="MarkdownV2",
        reply_markup=_get_advice_action_keyboard(language),
    )

    context.user_data.clear()
    return ConversationHandler.END


# =============================================================================
# Cancel handlers
# =============================================================================

async def adv_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    if query:
        await query.answer()
    user_id = update.effective_user.id
    language = UserStorage.get_user_language(user_id)
    await (query.edit_message_text if query else update.message.reply_text)(
        I18nService.t("common.cancel", language),
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(I18nService.t("common.back", language), callback_data="main_menu")
        ]]),
    )
    context.user_data.clear()
    return ConversationHandler.END


async def car_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await adv_cancel(update, context)


# =============================================================================
# Keyboards
# =============================================================================

def _get_advice_action_keyboard(language: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 درخواست مجدد", callback_data="menu_admissions")],
        [InlineKeyboardButton("💼 مشاوره شغلی", callback_data="menu_career")],
        [InlineKeyboardButton(I18nService.t("common.back", language), callback_data="main_menu")],
    ])


# =============================================================================
# Conversation Handlers
# =============================================================================

def get_academic_advice_conversation() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(academic_advice_entry, pattern=r"^menu_admissions$")],
        states={
            ADV_INTERESTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, adv_interests_received)],
            ADV_SKILLS: [MessageHandler(filters.TEXT & ~filters.COMMAND, adv_skills_received)],
            ADV_EDUCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, adv_education_received)],
            ADV_GOALS: [MessageHandler(filters.TEXT & ~filters.COMMAND, adv_goals_received)],
            ADV_FIELDS: [MessageHandler(filters.TEXT & ~filters.COMMAND, adv_fields_received)],
        },
        fallbacks=[CallbackQueryHandler(adv_cancel, pattern=r"^adv_cancel$")],
        per_user=True,
        per_chat=True,
    )


def get_career_guidance_conversation() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(career_guidance_entry, pattern=r"^menu_career$")],
        states={
            CAR_INTERESTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, car_interests_received)],
            CAR_SKILLS: [MessageHandler(filters.TEXT & ~filters.COMMAND, car_skills_received)],
            CAR_EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, car_experience_received)],
            CAR_EDUCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, car_education_received)],
            CAR_INDUSTRIES: [MessageHandler(filters.TEXT & ~filters.COMMAND, car_industries_received)],
            CAR_LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, car_location_received)],
        },
        fallbacks=[CallbackQueryHandler(car_cancel, pattern=r"^car_cancel$")],
        per_user=True,
        per_chat=True,
    )


def get_advisory_handlers() -> List:
    return [
        get_academic_advice_conversation(),
        get_career_guidance_conversation(),
    ]