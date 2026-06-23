# Project: Ashhcb Bot - Image to Trend Transform
# File Path: src/handlers/photo.py
# Author: Amin Davodian
# Full Name: Mohammadamin Davodian
# Website: https://senioramin.com
# GitHub: https://github.com/SeniorAminam
# LinkedIn: https://linkedin.com/in/SudoAmin
# Developer: @SeniorAminBot
# Brand: SeniorAmin
# Created Date: 2026-06-23
# Modified Date: 2026-06-23
# Version: 2.1.0
# Purpose: Handles incoming photos — routes to img2img or analysis
# License: MIT
# Copyright: (c) Amin Davodian

import io
import logging
import time

import httpx
from PIL import Image
from telegram import Update
from telegram.ext import ContextTypes

from src.config.settings import MAX_PHOTO_SIZE_MB, RATE_LIMIT_SECONDS
from src.services.ai_service import AIService, AIServiceError
from src.services.storage import UserStorage

logger = logging.getLogger(__name__)


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.photo:
        return

    user = update.effective_user
    user_id = user.id

    UserStorage.get_or_create_user(
        user_id=user_id,
        username=user.username,
        first_name=user.first_name,
    )

    photo = update.message.photo[-1]

    if photo.file_size and photo.file_size > MAX_PHOTO_SIZE_MB * 1024 * 1024:
        await update.message.reply_text(
            f"⚠️ حجم عکس بیشتر از {MAX_PHOTO_SIZE_MB} مگابایت است.\n"
            f"لطفاً عکسی با حجم کمتر ارسال کنید.",
        )
        return

    processing_msg = await update.message.reply_text("🔄 در حال دریافت عکس...")

    try:
        photo_file = await photo.get_file()
        image_bytes = await photo_file.download_as_bytearray()
        image_bytes = bytes(image_bytes)

        context.user_data["last_image"] = image_bytes

        img = Image.open(io.BytesIO(image_bytes))
        w, h = img.size

        try:
            await processing_msg.delete()
        except Exception:
            pass

        if context.user_data.get("waiting_for_analysis"):
            context.user_data["waiting_for_analysis"] = False
            await _analyze_photo(update, context, image_bytes, w, h)
            return

        await update.message.reply_text(
            f"✅ عکس با موفقیت دریافت شد!\n"
            f"📐 {w}×{h} | 💾 {_format_size(len(image_bytes))}\n\n"
            f"🤖 مدل: Agnes Image 2.0 Flash\n\n"
            f"✍️ حالا پرامپت مورد نظرت رو بنویس تا عکست پردازش بشه.\n\n"
            f"مثال پرامپت:\n"
            f"• این عکس رو به سبک کارتونی تبدیل کن\n"
            f"• به سبک نقاشی رنگ روغن دربیار\n"
            f"• شبیه انیمه‌های ژاپنی کن\n"
            f"• سیاه و سفید کن مثل طراحی مدادی\n"
            f"• هر چی دوست داری بنویس! ✨",
        )

        context.user_data["waiting_for_prompt"] = True
        context.user_data["waiting_for_image_gen"] = False

    except httpx.TimeoutException:
        logger.error("Timeout downloading photo")
        try:
            await processing_msg.edit_text("⚠️ زمان دریافت عکس به پایان رسید. لطفاً دوباره تلاش کنید.")
        except Exception:
            pass
    except Exception as e:
        logger.error("Error downloading photo: %s", str(e))
        try:
            await processing_msg.edit_text("⚠️ خطا در دریافت عکس. لطفاً دوباره تلاش کنید.")
        except Exception:
            pass


async def _analyze_photo(update: Update, context: ContextTypes.DEFAULT_TYPE, image_bytes: bytes, w: int, h: int) -> None:
    last_call = context.user_data.get("last_api_call", 0)
    elapsed = time.time() - last_call
    if elapsed < RATE_LIMIT_SECONDS:
        remaining = int(RATE_LIMIT_SECONDS - elapsed)
        await update.message.reply_text(
            f"⏳ لطفاً {remaining} ثانیه صبر کنید.\n"
            "محدودیت یک دقیقه بین درخواست‌هاست.",
        )
        return

    status_msg = await update.message.reply_text(
        "🔍 در حال تحلیل تصویر با هوش مصنوعی...\n"
        "🤖 مدل: Agnes 2.0 Flash",
    )

    try:
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing",
        )

        ai_service = AIService()
        description = await ai_service.analyze_image(image_bytes)

        if description:
            context.user_data["last_api_call"] = time.time()
            try:
                await status_msg.delete()
            except Exception:
                pass

            await update.message.reply_text(
                f"🔍 نتیجه تحلیل تصویر:\n\n{description}\n\n"
                f"📐 {w}×{h} | 💾 {_format_size(len(image_bytes))}",
            )

            UserStorage.record_transform(
                user_id=update.effective_user.id,
                style_key="ai_analysis",
                style_label="تحلیل تصویر (AI)",
                image_size=len(image_bytes),
                model_used="agnes-2.0-flash",
                ai_provider="agnes",
            )
        else:
            await status_msg.edit_text("⚠️ خطا در تحلیل تصویر. لطفاً دوباره تلاش کنید.")

    except AIServiceError as e:
        await status_msg.edit_text(f"⚠️ {str(e)}\n\nلطفاً دوباره تلاش کنید.")
    except Exception as e:
        logger.error("Error analyzing photo: %s", str(e))
        try:
            await status_msg.edit_text("⚠️ خطای غیرمنتظره‌ای رخ داد. لطفاً دوباره تلاش کنید.")
        except Exception:
            pass


def _format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
