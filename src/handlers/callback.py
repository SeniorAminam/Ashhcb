# Project: Ashhcb Bot - Image to Trend Transform
# File Path: src/handlers/callback.py
# Author: Amin Davodian
# Full Name: Mohammadamin Davodian
# Website: https://senioramin.com
# GitHub: https://github.com/SeniorAminam
# LinkedIn: https://linkedin.com/in/SudoAmin
# Developer: @SeniorAminBot
# Brand: SeniorAmin
# Created Date: 2026-06-23
# Modified Date: 2026-06-23
# Version: 2.0.0
# Purpose: Handles inline keyboard callback queries
# License: MIT
# Copyright: (c) Amin Davodian

import logging

from telegram import Update
from telegram.ext import ContextTypes

from src.config.settings import BOT_VERSION, SUPPORT_LINK
from src.keyboards.inline import get_start_keyboard, get_back_keyboard
from src.services.agnes_service import AGNES_MODELS

logger = logging.getLogger(__name__)


def _find_model_by_id(model_id: str) -> dict:
    for m in AGNES_MODELS:
        if m["id"] == model_id:
            return m
    return AGNES_MODELS[0]


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.data:
        return

    await query.answer()

    data = query.data

    if data == "start_transform":
        await _safe_edit(
            query,
            text="📷 خوب، یه عکس برام بفرست تا شروع کنیم!\n\n"
            "بعد از ارسال عکس، پرامپت مورد نظرت رو بنویس\n"
            "تا عکست رو پردازش کنم ✨",
            reply_markup=get_back_keyboard(),
        )

    elif data.startswith("model_"):
        model_id = data.replace("model_", "", 1)
        model = _find_model_by_id(model_id)
        context.user_data["selected_model"] = model_id

        text = (
            f"✅ مدل انتخاب شد: {model['label']}\n"
            f"   کیفیت: {model.get('quality', 'N/A')} | هزینه: {model.get('cost', 'N/A')}\n\n"
            "📷 حالا عکست رو بفرست!\n"
            "بعدش پرامپت مورد نظرت رو بنویس."
        )
        await _safe_edit(query, text=text, reply_markup=get_back_keyboard())

    elif data == "about":
        about_text = (
            "🤖 درباره ربات\n\n"
            "ربات هوشمند تبدیل عکس\n"
            "عکس‌های شما رو با پرامپت دلخواه خودتون\n"
            "به سبک‌های هنری مختلف تبدیل می‌کنه.\n\n"
            "🎨 با قدرت Agnes AI:\n"
            "• تولید تصویر از متن\n"
            "• ویرایش و تبدیل عکس\n"
            "• تحلیل هوشمند تصاویر\n\n"
            "✍️ کافیه پرامپت مورد نظرت رو بنویسی!\n\n"
            f"💬 پشتیبانی: {SUPPORT_LINK}\n"
            f"📌 نسخه: {BOT_VERSION}\n\n"
            "🌐 توسعه‌دهنده: @SeniorAminBot\n"
            "📄 کاملاً رایگان - بدون محدودیت 🎉"
        )
        await _safe_edit(query, text=about_text, reply_markup=get_back_keyboard())

    elif data == "back_to_menu":
        await _safe_edit(
            query,
            text=(
                "👋 به منوی اصلی خوش آمدی!\n\n"
                "📷 کافیه یه عکس بفرستی تا شروع کنیم!\n\n"
                "💡 از دکمه‌های زیر استفاده کن 👇"
            ),
            reply_markup=get_start_keyboard(),
        )


async def _safe_edit(query, text: str, reply_markup=None) -> bool:
    try:
        await query.message.edit_text(text=text, reply_markup=reply_markup)
        return True
    except Exception as e:
        logger.debug("Safe edit failed: %s", str(e)[:80])
        return False
