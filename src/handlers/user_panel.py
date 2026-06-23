# Project: Ashhcb Bot - Image to Trend Transform
# File Path: src/handlers/user_panel.py
# Author: Amin Davodian
# Full Name: Mohammadamin Davodian
# Website: https://senioramin.com
# GitHub: https://github.com/SeniorAminam
# LinkedIn: https://linkedin.com/in/SudoAmin
# Developer: @SeniorAminBot
# Brand: SeniorAmin
# Created Date: 2026-06-21
# Modified Date: 2026-06-21
# Version: 2.2.0
# Purpose: User panel handlers — history and statistics for end users
# License: MIT
# Copyright: (c) Amin Davodian

import logging

from telegram import Update
from telegram.ext import ContextTypes

from src.config.settings import BOT_USERNAME
from src.services.storage import UserStorage
from src.keyboards.reply import get_user_panel_keyboard, get_main_keyboard
from src.handlers.admin import is_admin

logger = logging.getLogger(__name__)


def _fmt_num(num: int) -> str:
    """Format large numbers with commas or shorthand."""
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num:,}"
    else:
        return str(num)





# Known old AI model labels that were incorrectly stored as styles
_AI_STYLE_FILTER = {"Together AI (FLUX.1 Schnell)", "Gemini 2.5 Flash (رایگان)", "Gemini 2.5 Flash", "Replicate (FLUX.1 Schnell)", "FLUX.1 Schnell", "پرامپت سفارشی (AI)"}


async def user_panel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    user_id = update.effective_user.id

    if text == "📜 تاریخچه تبدیل‌ها":
        await _show_history(update, context, user_id)
    elif text == "📊 آمار کاربری":
        await _show_user_stats(update, context, user_id)
    elif text == "🔙 بازگشت به منوی اصلی":
        await _back_to_main(update, context)


async def _show_history(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
    history = UserStorage.get_user_history(user_id, limit=15)

    if not history:
        await update.message.reply_text(
            "📭 تاریخچه تبدیلی وجود ندارد!\n\n"
            "هنوز هیچ عکسی تبدیل نکردی!\n"
            "📷 یه عکس بفرست تا شروع کنیم 🎨",
            reply_markup=get_user_panel_keyboard(),
        )
        return

    text = f"📜 تاریخچه تبدیل‌های شما (آخرین {len(history)} تا)\n\n"

    for i, record in enumerate(history, 1):
        style = record["style_label"]
        model_used = record.get("model_used", "") or ""
        ts = record["timestamp"][:19].replace("T", " ")
        image_size = record["image_size"]

        size_str = ""
        if image_size:
            if image_size < 1024:
                size_str = f"({image_size} B)"
            elif image_size < 1024 * 1024:
                size_str = f"({image_size / 1024:.1f} KB)"
            else:
                size_str = f"({image_size / (1024 * 1024):.1f} MB)"

        # Show model name for AI custom prompts (no provider hints)
        display = style
        if style == "پرامپت سفارشی (AI)" and model_used:
            display = model_used[:40]

        text += f"{i}. {display} {size_str}\n"
        text += f"   🕐 {ts}\n\n"

    await update.message.reply_text(
        text,
        reply_markup=get_user_panel_keyboard(),
    )


async def _show_user_stats(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
    stats = UserStorage.get_user_stats(user_id)

    if not stats:
        await update.message.reply_text(
            "❌ خطا در دریافت اطلاعات کاربری.",
            reply_markup=get_user_panel_keyboard(),
        )
        return

    user = stats["user"]
    join_date = user["join_date"][:19].replace("T", " ") if user["join_date"] else "نامشخص"
    last_active = user["last_active"][:19].replace("T", " ") if user["last_active"] else "نامشخص"
    total = user["total_transforms"]
    today_count = stats["today_count"]
    style_counts = stats["style_counts"]

    text = (
        "👤 حساب کاربری شما\n\n"
        f"🆔 شناسه: {user_id}\n"
        f"👤 نام: {user['first_name'] or 'نامشخص'}\n"
        f"📅 تاریخ عضویت: {join_date}\n"
        f"🕐 آخرین فعالیت: {last_active}\n\n"
        f"📊 آمار مصرف:\n"
        f"🖼️ کل تبدیل‌ها: {total}\n"
        f"📅 تبدیل‌های امروز: {today_count}\n\n"
    )

    if style_counts:
        text += "📈 تفکیک سبک‌ها:\n"
        # Separate AI custom prompts from real styles
        ai_count = 0
        for style in style_counts:
            label = style["style_label"]
            count = style["count"]
            # Filter out old AI model names that were stored as styles
            if label in _AI_STYLE_FILTER:
                ai_count += count
                continue
            bar = "█" * min(count, 10) + "▒" * max(0, 10 - min(count, 10))
            text += f"{label}: {bar} {count}\n"
        if ai_count > 0:
            text += f"🤖 پرامپت سفارشی (AI): {ai_count} بار\n"
    else:
        text += "هنوز سبکی را امتحان نکردی!\n"

    # ── AI Model Usage Breakdown ──
    ai_models = UserStorage.get_ai_model_counts(user_id)
    if ai_models:
        text += "\n━━━━━━━━━━━━━━━━━━\n"
        text += "🤖 AI Models Used\n"
        for model in ai_models[:5]:
            m_label = model["model_used"][:40] if model["model_used"] else "نامشخص"
            m_count = model["count"]
            bar = "█" * min(m_count, 10) + "▒" * max(0, 10 - min(m_count, 10))
            text += f"{m_label}: {bar} {m_count}\n"

    await update.message.reply_text(
        text,
        reply_markup=get_user_panel_keyboard(),
    )


async def _back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    await update.message.reply_text(
        "🔙 بازگشت به منوی اصلی\n\n"
        "📷 یه عکس بفرست تا شروع کنیم!",
        reply_markup=get_main_keyboard(is_admin=is_admin(user_id)),
    )
