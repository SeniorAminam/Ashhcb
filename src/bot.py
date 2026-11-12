# Project: Ashhcb Bot - Mazandaran Skills University AI Assistant
# File Path: src/bot.py
# Author: Amin Davodian
# Full Name: Mohammadamin Davodian
# Website: https://senioramin.com
# GitHub: https://github.com/SeniorAminam
# LinkedIn: https://linkedin.com/in/SudoAmin
# Developer: @SeniorAminBot
# Brand: SeniorAmin
# Created Date: 2026-06-21
# Modified Date: 2026-11-12
# Version: 5.0.0
# Purpose: Main entry point for MSU AI Assistant Bot
# License: MIT
# Copyright: (c) Amin Davodian

"""
MSU AI Assistant - Mazandaran Skills University AI Assistant Bot
🤖 A Bale bot for university assistance: FAQ, academic advising, career guidance,
    skill discovery, web scraping, and AI image generation.

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
from src.handlers.menu import get_menu_handlers
from src.handlers.chat import get_chat_handlers
from src.handlers.search import get_all_search_handlers
from src.handlers.advisory import get_advisory_handlers
from src.handlers.admin import (
    _start_broadcast_callback as _start_broadcast,
    receive_broadcast_text,
    cancel_broadcast,
    BROADCAST_TEXT,
    get_admin_handlers,
)
from src.handlers.error import error_handler
from src.services.storage import init_db
from src.services.ai_service import AIService
from src.services.agnes_service import AIService as AgnesClient
from src.services.i18n_service import I18nService

logger = logging.getLogger(__name__)


async def post_init(application) -> None:
    """Initialize shared resources after application starts."""
    # Initialize AI Service AsyncClient
    await AgnesClient.get_client()
    logger.info("AI Service AsyncClient initialized")

    # Load translations
    I18nService.load_translations()
    logger.info("Translations loaded")


async def post_shutdown(application) -> None:
    """Clean up shared resources on shutdown."""
    await AgnesClient.close_client()
    logger.info("AI Service AsyncClient closed")


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
    print("🤖 MSU AI Assistant در حال راه‌اندازی...")
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
            print("   ⚠️ سرویس هوش مصنوعی در دسترس نیست. چت کار نمی‌کند.")
        else:
            print("   ✅ سرویس Gemma 4 در دسترس است")

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
            .post_init(post_init)
            .post_shutdown(post_shutdown)
            .build()
        )

        # ---------- Register Handlers ----------

        # Menu handlers (main menu, settings, user panel, admin panel)
        for handler in get_menu_handlers():
            application.add_handler(handler)

        # Chat handlers (free-form RAG chat)
        for handler in get_chat_handlers():
            application.add_handler(handler)

        # Search handlers (general search, skills search, announcements)
        for handler in get_all_search_handlers():
            application.add_handler(handler)

        # Advisory handlers (academic advising, career guidance)
        for handler in get_advisory_handlers():
            application.add_handler(handler)

        # Admin handlers
        for handler in get_admin_handlers():
            application.add_handler(handler)

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
            ],
        )
        application.add_handler(broadcast_conv)

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