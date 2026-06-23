# Project: Ashhcb Bot - Image to Trend Transform
# File Path: src/handlers/start.py
# Author: Amin Davodian
# Full Name: Mohammadamin Davodian
# Website: https://senioramin.com
# GitHub: https://github.com/SeniorAminam
# LinkedIn: https://linkedin.com/in/SudoAmin
# Developer: @SeniorAminBot
# Brand: SeniorAmin
# Created Date: 2026-06-21
# Modified Date: 2026-06-23
# Version: 5.0.2
# Purpose: Handlers for /start, /help, /about commands and text message routing
# License: MIT
# Copyright: (c) Amin Davodian

import logging
import time

from telegram import Update
from telegram.ext import ContextTypes

from src.config.settings import BOT_VERSION, BOT_USERNAME, SUPPORT_LINK, RATE_LIMIT_SECONDS
from src.keyboards.inline import get_start_keyboard, get_model_selection_keyboard
from src.keyboards.reply import get_main_keyboard, get_user_panel_keyboard
from src.services.storage import UserStorage
from src.services.ai_service import AIService, AIServiceError
from src.handlers.admin import is_admin, admin_panel_handler
from src.handlers.user_panel import user_panel_handler
from src.utils.helpers import format_size as _format_size

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = user.id
    first_name = user.first_name or "کاربر"

    UserStorage.get_or_create_user(
        user_id=user_id,
        username=user.username,
        first_name=first_name,
    )

    welcome = (
        f"👋 سلام {first_name} عزیز!\n"
        f"به {BOT_USERNAME} خوش اومدی 🎉\n\n"
        "✨ ربات هوشمند ساخت و تبدیل عکس با هوش مصنوعی\n"
        "ساخت عکس از متن | تبدیل عکس | تحلیل تصویر\n\n"
        "📷 چطور کار می‌کنه:\n"
        "• ساخت عکس: فقط پرامپت بنویس\n"
        "• تبدیل عکس: عکس + پرامپت بفرست\n"
        "• تحلیل: عکس بفرست، توضیح دریافت کن\n\n"
        "🔥 کاملاً رایگان\n"
        "⚡ محدودیت: یک دقیقه بین درخواست‌ها\n\n"
        f"💬 توسعه‌دهنده: @SeniorAminBot | نسخه: {BOT_VERSION}"
    )

    await update.message.reply_text(
        text=welcome,
        reply_markup=get_main_keyboard(is_admin=is_admin(user_id)),
    )


async def models_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from src.services.agnes_service import AGNES_MODELS
    selected = context.user_data.get("selected_model", "")
    text = "🎨 مدل هوش مصنوعی:\n\n"
    for m in AGNES_MODELS:
        marker = "✅ " if m["id"] == selected else "• "
        text += f"{marker}{m['label']}\n"
        text += f"   کیفیت: {m.get('quality', 'N/A')} | هزینه: {m.get('cost', 'N/A')}\n\n"
    text += "🤖 تمام عملیات توسط Agnes AI انجام می‌شود."
    await update.message.reply_text(text=text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        f"💬 راهنمای ربات {BOT_USERNAME}\n\n"
        "📷 سه تا قابلیت داریم:\n\n"
        "🖼️ **ساخت عکس**:\n"
        "همینطور یه پرامپت بنویس، برات تصویر می‌سازم!\n\n"
        "📷 **شروع تبدیل عکس**:\n"
        "1. یه عکس بفرست\n"
        "2. پرامپت مورد نظرت رو بنویس\n"
        "3. عکس جدیدت رو دریافت کن!\n\n"
        "🔍 **تحلیل تصویر**:\n"
        "یه عکس بفرست تا توضیح کامل به فارسی برات بنویسم.\n\n"
        "✍️ مثال پرامپت:\n"
        "• یک گربه فضانورد در حال پرواز\n"
        "• این عکس رو به سبک کارتونی تبدیل کن\n"
        "• نقاشی رنگ روغن\n"
        "• شبیه انیمه کن\n\n"
        "💡 هر چی دوست داری بنویس، هوش مصنوعی انجام می‌ده!\n\n"
        "🚫 محدودیت‌ها:\n"
        "• حداکثر حجم عکس: 10 مگابایت\n"
        "• یک دقیقه فاصله بین درخواست‌ها\n"
        "• کاملاً رایگان 🎉\n\n"
        f"💬 پشتیبانی: {SUPPORT_LINK} | نسخه: {BOT_VERSION}"
    )

    await update.message.reply_text(
        text=help_text,
        reply_markup=get_main_keyboard(is_admin=is_admin(update.effective_user.id)),
    )


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    about_text = (
        f"🤖 درباره {BOT_USERNAME}\n\n"
        "ربات هوشمند تبدیل عکس\n"
        "عکس‌های شما رو با پردازش هوشمند تصویر\n"
        "به سبک‌های هنری مختلف تبدیل می‌کنه.\n\n"
        "⚡ فناوری:\n"
        "• هوش مصنوعی Agnes AI\n"
        "• تولید تصویر از متن (txt2img)\n"
        "• تبدیل عکس با پرامپت (img2img)\n"
        "• تحلیل هوشمند تصاویر (Vision)\n"
        "• کاملاً رایگان 🎉\n"
        "• محدودیت: یک دقیقه بین درخواست‌ها\n\n"
        "🏠 توسعه‌دهنده:\n"
        "• امین داودیان (Mohammadamin Davodian)\n"
        "• وبسایت: senioramin.com\n"
        f"💬 پشتیبانی: {SUPPORT_LINK}\n\n"
        f"📌 نسخه: {BOT_VERSION} | تاریخ: خرداد 1405\n"
        "© کلیه حقوق محفوظ است - امین داودیان"
    )

    await update.message.reply_text(
        text=about_text,
        reply_markup=get_main_keyboard(is_admin=is_admin(update.effective_user.id)),
    )


async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    user_id = update.effective_user.id

    # ===== Navigation commands list =====
    NAV_CMDS = [
        "🖼️ ساخت عکس", "📷 شروع تبدیل عکس", "🔍 تحلیل تصویر", "👤 پنل کاربری", "👑 پنل ادمین",
        "📜 تاریخچه تبدیل‌ها", "📊 آمار کاربری", "🔙 بازگشت به منوی اصلی",
        "📊 آمار کلی ربات", "👥 لیست کاربران", "📢 ارسال پیام همگانی",
        "❓ راهنما", "ℹ️ درباره",
    ]

    # ===== Check if user is waiting for a prompt (img2img) FIRST =====
    if (
        context.user_data.get("waiting_for_prompt")
        and context.user_data.get("last_image")
        and text not in NAV_CMDS
    ):
        context.user_data["waiting_for_image_gen"] = False
        await _process_prompt(update, context, text)
        return

    # ===== Check if user is waiting for an image generation prompt (txt2img) =====
    if (
        context.user_data.get("waiting_for_image_gen")
        and text not in NAV_CMDS
    ):
        await _process_image_gen(update, context, text)
        return

    # ===== Normal navigation routing =====
    if text == "🖼️ ساخت عکس":
        context.user_data["waiting_for_image_gen"] = True
        context.user_data["waiting_for_prompt"] = False
        await update.message.reply_text(
            "🖼️ باشه، پرامپت مورد نظرت رو بنویس!\n\n"
            "هر چی دوست داری بگو تا برات با هوش مصنوعی تصویرش رو بسازم ✨\n\n"
            "مثال:\n"
            "• یک گربه فضانورد در حال پرواز در کهکشان\n"
            "• منظره غروب آفتاب در کنار دریا\n"
            "• یک برج بلند در شهر آینده‌نگر\n\n"
            "💡 از مدل Agnes Image 2.0 Flash استفاده می‌شود.",
        )

    elif text == "📷 شروع تبدیل عکس":
        context.user_data["waiting_for_image_gen"] = False
        context.user_data["waiting_for_analysis"] = False
        await update.message.reply_text(
            "📷 خوب، یه عکس برام بفرست تا شروع کنیم!\n\n"
            "بعدش پرامپت مورد نظرت رو بنویس تا عکست رو پردازش کنم ✨",
        )

    elif text == "🔍 تحلیل تصویر":
        context.user_data["waiting_for_image_gen"] = False
        context.user_data["waiting_for_prompt"] = False
        context.user_data["waiting_for_analysis"] = True
        await update.message.reply_text(
            "🔍 خوب، یه عکس برام بفرست تا تحلیلش کنم!\n\n"
            "عکس رو بفرست تا توضیح کامل به فارسی برات بنویسم ✨",
        )

    elif text == "👤 پنل کاربری":
        await update.message.reply_text(
            "👤 پنل کاربری - یکی از گزینه‌های زیر را انتخاب کنید:",
            reply_markup=get_user_panel_keyboard(),
        )

    elif text in ("📜 تاریخچه تبدیل‌ها", "📊 آمار کاربری", "🔙 بازگشت به منوی اصلی"):
        await user_panel_handler(update, context)

    elif text == "👑 پنل ادمین":
        await admin_panel_handler(update, context)

    elif text in ("📊 آمار کلی ربات", "👥 لیست کاربران", "📢 ارسال پیام همگانی"):
        await admin_panel_handler(update, context)

    elif text == "❓ راهنما":
        await help_command(update, context)

    elif text == "ℹ️ درباره":
        await about_command(update, context)

    else:
        await update.message.reply_text(
            "❌ دستور نامشخص!\n\n"
            "برای شروع روی گزینه '📷 شروع تبدیل عکس' بزن\n"
            "یا یه عکس مستقیم برام بفرست!",
            reply_markup=get_main_keyboard(is_admin=is_admin(user_id)),
        )


async def _process_image_gen(update: Update, context: ContextTypes.DEFAULT_TYPE, prompt: str) -> None:
    user_id = update.effective_user.id
    context.user_data["waiting_for_image_gen"] = False

    last_call = context.user_data.get("last_api_call", 0)
    elapsed = time.time() - last_call
    if elapsed < RATE_LIMIT_SECONDS:
        remaining = int(RATE_LIMIT_SECONDS - elapsed)
        await update.message.reply_text(
            f"⏳ لطفاً {remaining} ثانیه صبر کنید.\n"
            "محدودیت یک دقیقه بین درخواست‌هاست.",
        )
        context.user_data["waiting_for_image_gen"] = True
        return

    status_msg = await update.message.reply_text(
        "🎨 در حال تولید تصویر با هوش مصنوعی...\n\n"
        f"✍️ پرامپت: {prompt[:80]}\n"
        "🤖 مدل: Agnes Image 2.0 Flash",
    )

    try:
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="upload_photo",
        )

        ai_service = AIService()
        result_bytes, effect_name, model_id = await ai_service.transform_image(
            image_bytes=b"",
            prompt=prompt,
        )

        if result_bytes:
            context.user_data["last_api_call"] = time.time()
            UserStorage.record_transform(
                user_id=user_id,
                style_key="ai_generated",
                style_label="ساخت عکس با هوش مصنوعی",
                image_size=len(result_bytes),
                model_used=model_id,
                ai_provider="agnes",
            )

            try:
                await status_msg.delete()
            except Exception:
                pass

            await update.message.reply_photo(
                photo=result_bytes,
                caption=f"✨ تصویر با موفقیت ساخته شد!\n"
                f"🎨 مدل: {effect_name}\n"
                f"📦 اندازه: {_format_size(len(result_bytes))}\n"
                f"✍️ پرامپت: {prompt[:80]}\n\n"
                f"🔄 می‌تونی دوباره پرامپت جدیدی بنویسی!",
            )

            context.user_data["waiting_for_image_gen"] = True
            await update.message.reply_text(
                "✍️ پرامپت جدیدی بنویس تا دوباره امتحان کنی!\n"
                "یا از دکمه‌های منو استفاده کن.",
            )
        else:
            await status_msg.edit_text(
                "⚠️ خطا در تولید تصویر. لطفاً دوباره تلاش کنید.",
            )

    except AIServiceError as e:
        logger.error("AI Service error in image gen: %s", str(e))
        await status_msg.edit_text(f"⚠️ {str(e)}\n\nلطفاً دوباره تلاش کنید.")
    except Exception as e:
        logger.error("Error in image gen: %s", str(e))
        try:
            await status_msg.edit_text("⚠️ خطای غیرمنتظره‌ای رخ داد. لطفاً دوباره تلاش کنید.")
        except Exception:
            pass


async def _process_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE, prompt: str) -> None:
    user_id = update.effective_user.id
    image_bytes = context.user_data.get("last_image")

    context.user_data["waiting_for_prompt"] = False

    if not image_bytes:
        await update.message.reply_text(
            "⚠️ عکسی برای پردازش وجود نداره!\n"
            "لطفاً اول یه عکس بفرست.",
        )
        return

    last_call = context.user_data.get("last_api_call", 0)
    elapsed = time.time() - last_call
    if elapsed < RATE_LIMIT_SECONDS:
        remaining = int(RATE_LIMIT_SECONDS - elapsed)
        await update.message.reply_text(
            f"⏳ لطفاً {remaining} ثانیه صبر کنید.\n"
            "محدودیت یک دقیقه بین درخواست‌هاست.",
        )
        context.user_data["waiting_for_prompt"] = True
        return

    status_msg = await update.message.reply_text(
        f"🎨 در حال ارسال عکس + پرامپت به هوش مصنوعی...\n\n"
        f"✍️ پرامپت: {prompt[:80]}\n"
        f"🤖 مدل: Agnes Image 2.0 Flash",
    )

    try:
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="upload_photo",
        )

        ai_service = AIService()
        result_bytes, effect_name, model_id = await ai_service.transform_image(
            image_bytes=image_bytes,
            prompt=prompt,
        )

        if result_bytes:
            context.user_data["last_api_call"] = time.time()
            UserStorage.record_transform(
                user_id=user_id,
                style_key="ai_custom",
                style_label="پرامپت سفارشی (AI)",
                image_size=len(result_bytes),
                model_used=model_id,
                ai_provider="agnes",
            )

            try:
                await status_msg.delete()
            except Exception:
                pass

            await update.message.reply_photo(
                photo=result_bytes,
                caption=f"✨ عکس شما با موفقیت پردازش شد!\n"
                f"🎨 مدل: {effect_name}\n"
                f"📦 اندازه: {_format_size(len(result_bytes))}\n"
                f"✍️ پرامپت: {prompt[:80]}\n\n"
                f"🔄 می‌تونی دوباره عکس بفرستی یا پرامپت جدیدی بنویسی!",
            )

            context.user_data["last_image"] = image_bytes
            context.user_data["waiting_for_prompt"] = True

            await update.message.reply_text(
                "✍️ پرامپت جدیدی بنویس تا دوباره امتحان کنی!\n"
                "یا یه عکس جدید بفرست.",
            )

        else:
            await status_msg.edit_text(
                "⚠️ خطا در پردازش عکس. لطفاً دوباره تلاش کنید.\n"
                "می‌تونی یه پرامپت دیگه هم امتحان کنی!",
            )
            context.user_data["waiting_for_prompt"] = True

    except AIServiceError as e:
        logger.error("AI Service error: %s", str(e))
        await status_msg.edit_text(f"⚠️ {str(e)}\n\nلطفاً دوباره تلاش کنید.")
        context.user_data["waiting_for_prompt"] = True
    except Exception as e:
        logger.error("Error processing prompt: %s", str(e))
        try:
            await status_msg.edit_text("⚠️ خطای غیرمنتظره‌ای رخ داد. لطفاً دوباره تلاش کنید.")
        except Exception:
            pass
        context.user_data["waiting_for_prompt"] = True
