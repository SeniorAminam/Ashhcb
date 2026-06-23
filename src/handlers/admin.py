# Project: Ashhcb Bot - Image to Trend Transform
# File Path: src/handlers/admin.py
# Author: Amin Davodian
# Full Name: Mohammadamin Davodian
# Website: https://senioramin.com
# GitHub: https://github.com/SeniorAminam
# LinkedIn: https://linkedin.com/in/SudoAmin
# Developer: @SeniorAminBot
# Brand: SeniorAmin
# Created Date: 2026-06-21
# Modified Date: 2026-06-21
# Version: 3.0.0
# Purpose: Admin panel handlers — stats, user list, broadcast messaging
# License: MIT
# Copyright: (c) Amin Davodian

import os
import logging

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler

from src.config.settings import ADMIN_USER_IDS, BOT_USERNAME
from src.services.storage import UserStorage
from src.keyboards.reply import get_admin_panel_keyboard, get_main_keyboard

logger = logging.getLogger(__name__)

BROADCAST_TEXT = 1

_AI_STYLE_FILTER = {"پرامپت سفارشی (AI)"}


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_USER_IDS


async def admin_panel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("⛔ شما دسترسی ادمین ندارید!")
        return

    text = update.message.text.strip()

    if text == "👑 پنل ادمین":
        await update.message.reply_text(
            "👑 پنل مدیریت - به پنل ادمین خوش آمدید!\n\n"
            "از گزینه‌های زیر یکی را انتخاب کنید:",
            reply_markup=get_admin_panel_keyboard(),
        )
    elif text == "📊 آمار کلی ربات":
        await _show_admin_stats(update, context)
    elif text == "👥 لیست کاربران":
        await _show_users_list(update, context)
    elif text == "📢 ارسال پیام همگانی":
        await _start_broadcast(update, context)
    elif text == "🔙 بازگشت به منوی اصلی":
        await update.message.reply_text(
            "🔙 بازگشت به منوی اصلی",
            reply_markup=get_main_keyboard(is_admin=True),
        )


async def _show_admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    stats = UserStorage.get_total_stats()

    db_path = "data/ashhc.db"
    db_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0

    daily_stats = UserStorage.get_ai_usage_today()
    ai_models_global = UserStorage.get_ai_model_counts_global()

    text = (
        "👑 پنل مدیریت - آمار کلی\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🤖 Agnes AI\n"
        f"🚀 کل تبدیل‌ها: {stats['total_transforms']}\n"
        f"📅 تبدیل‌های امروز: {stats['today_transforms']}\n"
    )

    if daily_stats:
        text += (
            f"📦 بایت‌های پردازش شده امروز: {_format_size(daily_stats.get('total_bytes_processed', 0))}\n"
        )

    if ai_models_global:
        model_list = ", ".join([m["model_used"][:30] for m in ai_models_global[:3]])
        text += f"🎯 درگاه AI: {model_list}\n"

    text += (
        "\n━━━━━━━━━━━━━━━━━━\n"
        "👥 کاربران\n"
        f"کل کاربران: {stats['total_users']}\n"
        f"💾 حجم دیتابیس: {_format_size(db_size)}\n\n"
        "🏆 کاربران برتر:\n"
    )

    if stats["top_users"]:
        for i, user in enumerate(stats["top_users"], 1):
            name = user["first_name"] or f"کاربر {user['user_id']}"
            text += f"{i}. {name} - {user['total_transforms']} تبدیل\n"
    else:
        text += "هنوز کاربری وجود ندارد.\n"

    text += "\n📈 محبوب‌ترین سبک‌ها:\n"
    if stats["style_popularity"]:
        for style in stats["style_popularity"]:
            label = style['style_label']
            if label in _AI_STYLE_FILTER:
                continue  # Skip old AI model names that were stored as styles
            text += f"• {label}: {style['count']} بار\n"
    else:
        text += "هنوز تبدیلی انجام نشده.\n"

    await update.message.reply_text(text, reply_markup=get_admin_panel_keyboard())


async def _show_users_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    users = UserStorage.get_all_users()

    if not users:
        await update.message.reply_text(
            "📭 هنوز کاربری ثبت نشده است.",
            reply_markup=get_admin_panel_keyboard(),
        )
        return

    text = f"👥 لیست کاربران ({len(users)} نفر)\n\n"
    for i, user in enumerate(users[:30], 1):
        name = user["first_name"] or f"کاربر {user['user_id']}"
        username = f"@{user['username']}" if user["username"] else ""
        join_date = user["join_date"][:10] if user["join_date"] else "نامشخص"
        text += (
            f"{i}. {name} {username}\n"
            f"   🆔 {user['user_id']} | 🖼️ {user['total_transforms']} تبدیل\n"
            f"   📅 عضویت: {join_date}\n\n"
        )

    if len(users) > 30:
        text += f"... و {len(users) - 30} کاربر دیگر"

    await update.message.reply_text(text, reply_markup=get_admin_panel_keyboard())


async def _start_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("⛔ شما دسترسی ادمین ندارید!")
        return ConversationHandler.END

    await update.message.reply_text(
        "📢 ارسال پیام همگانی\n\n"
        "لطفاً متنی که می‌خواهید به همه کاربران ارسال شود را بنویسید.\n"
        "برای لغو، /cancel را بفرستید.",
        reply_markup=ReplyKeyboardRemove(),
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
        reply_markup=get_admin_panel_keyboard(),
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
        reply_markup=get_admin_panel_keyboard(),
    )

    return ConversationHandler.END


async def cancel_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "❌ ارسال پیام همگانی لغو شد.",
        reply_markup=get_admin_panel_keyboard(),
    )
    return ConversationHandler.END


def _format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def _format_number(num: int) -> str:
    """Format large numbers with commas."""
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num:,}"
    else:
        return str(num)


def _fmt_cost(cost: float) -> str:
    """Format Puter cost nicely."""
    if cost >= 1000000:
        return f"{cost / 1000000:.1f}M"
    elif cost >= 1000:
        return f"{cost / 1000:.1f}K"
    else:
        return f"{cost:.0f}"
