# Project: Ashhcb Bot - Image to Trend Transform
# File Path: src/bot.py
# Author: Amin Davodian
# Full Name: Mohammadamin Davodian
# Website: https://senioramin.com
# GitHub: https://github.com/SeniorAminam
# LinkedIn: https://linkedin.com/in/SudoAmin
# Developer: @SeniorAminBot
# Brand: SeniorAmin
# Created Date: 2026-06-21
# Modified Date: 2026-06-23
# Version: 4.0.2
# Purpose: Main entry point for Ashhcb Bot - Bale bot for image transformation
# License: MIT
# Copyright: (c) Amin Davodian

"""
Ashhcb Bot - Image to Trend Transform
🤖 A Bale bot that transforms photos into trendy artistic styles using AI.

Usage:
    python -m src.bot
    or
    BOT_TOKEN=xxx python -m src.bot
"""

import sys
import asyncio
import logging

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
)

from src.config.settings import BOT_TOKEN, BALE_API_BASE, BALE_FILE_BASE
from src.handlers.start import (
    start_command,
    help_command,
    about_command,
    models_command,
    text_message_handler,
)
from src.handlers.photo import photo_handler
from src.handlers.callback import callback_handler
from src.handlers.error import error_handler
from src.handlers.admin import (
    admin_panel_handler,
    _start_broadcast,
    receive_broadcast_text,
    cancel_broadcast,
    BROADCAST_TEXT,
)
from src.services.storage import init_db
from src.services.ai_service import AIService

logger = logging.getLogger(__name__)


def validate_config() -> bool:
    """
    Validate required configuration before starting the bot.

    Returns:
        True if config is valid, False otherwise
    """
    if not BOT_TOKEN:
        logger.critical("BOT_TOKEN is not set! The bot cannot start.")
        print("❌ خطا: توکن ربات تنظیم نشده است!")
        print("لطفاً BOT_TOKEN را در فایل .env تنظیم کنید.")
        print("برای دریافت توکن به @botfather در بله پیام دهید.")
        return False

    token_parts = BOT_TOKEN.split(":")
    if len(token_parts) < 2 or not token_parts[0].isdigit():
        logger.error("Invalid BOT_TOKEN format: %s...", BOT_TOKEN[:10])
        print("⚠️ فرمت توکن صحیح نیست.")
        print("توکن باید به فرمت 123456789:abcd... باشد.")
        return False

    return True


def main() -> None:
    """
    Initialize and start the Bale bot.
    Uses long polling to receive updates.

    Note: Uses asyncio.new_event_loop() + run_until_complete instead of
    asyncio.run() to avoid 'no current event loop' error on Python 3.12+
    when run_polling() is subsequently called.
    """
    print("🤖 Ashhcb Bot در حال راه‌اندازی...")
    print(f"🌐 API Base: {BALE_API_BASE}")

    if not validate_config():
        sys.exit(1)

    try:
        # Initialize database
        print("🗄️ در حال راه‌اندازی دیتابیس...")
        init_db()

        # Check AI service availability
        print("🔌 در حال بررسی اتصال به سرویس هوش مصنوعی...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        ai_ok, ai_msg = loop.run_until_complete(AIService.health_check())
        print(ai_msg)
        if not ai_ok:
            print("   ⚠️ سرویس هوش مصنوعی در دسترس نیست. پردازش عکس کار نمی‌کند.")
        else:
            print("   ✅ سرویس Agnes AI در دسترس است")

        # Build the application with Bale custom base URL
        application = (
            ApplicationBuilder()
            .token(BOT_TOKEN)
            .base_url(BALE_API_BASE)
            .base_file_url(BALE_FILE_BASE)
            .read_timeout(30)
            .write_timeout(30)
            .connect_timeout(15)
            .pool_timeout(15)
            .build()
        )

        # ---------- Register Handlers ----------

        # Command handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("about", about_command))
        application.add_handler(CommandHandler("models", models_command))
        application.add_handler(CommandHandler("cancel", cancel_broadcast))

        # Broadcast conversation handler (admin only)
        broadcast_conv = ConversationHandler(
            entry_points=[
                MessageHandler(
                    filters.Text(["📢 ارسال پیام همگانی"]),
                    _start_broadcast,
                ),
            ],
            states={
                BROADCAST_TEXT: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        receive_broadcast_text,
                    ),
                ],
            },
            fallbacks=[
                CommandHandler("cancel", cancel_broadcast),
                MessageHandler(filters.TEXT, text_message_handler),
            ],
        )
        application.add_handler(broadcast_conv)

        # Photo handler
        application.add_handler(
            MessageHandler(filters.PHOTO, photo_handler)
        )

        # Text message handler (for ReplyKeyboard navigation)
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler)
        )

        # Callback query handler (inline buttons)
        application.add_handler(CallbackQueryHandler(callback_handler))

        # Error handler
        application.add_error_handler(error_handler)

        logger.info("Bot is running and ready to accept updates...")
        print("✅ ربات با موفقیت راه‌اندازی شد!")
        print("📋 منتظر دریافت پیام‌ها...")

        # Start polling (long polling)
        application.run_polling(
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=True,
        )

    except Exception as e:
        logger.critical("Failed to start bot: %s", str(e))
        print(f"❌ خطای بحرانی در راه‌اندازی ربات: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
