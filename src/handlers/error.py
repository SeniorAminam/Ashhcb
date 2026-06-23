# Project: Ashhcb Bot - Image to Trend Transform
# File Path: src/handlers/error.py
# Author: Amin Davodian
# Full Name: Mohammadamin Davodian
# Website: https://senioramin.com
# GitHub: https://github.com/SeniorAminam
# LinkedIn: https://linkedin.com/in/SudoAmin
# Developer: @SeniorAminBot
# Brand: SeniorAmin
# Created Date: 2026-06-21
# Modified Date: 2026-06-21
# Version: 1.0.0
# Purpose: Error handler for unhandled exceptions
# License: MIT
# Copyright: (c) Amin Davodian

import logging
import traceback

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle unhandled exceptions in the bot.
    Logs the error and notifies the user if possible.
    """
    logger.error("Exception while handling an update: %s", context.error)

    # Log full traceback
    tb = traceback.format_exception(
        type(context.error), context.error, context.error.__traceback__
    )
    logger.error("Full traceback:\n%s", "".join(tb))

    # Notify the user if the update contains a message
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "\u26a0\ufe0f خطای داخلی ربات رخ داده است.\n\n"
            "لطفاً چند لحظه بعد دوباره تلاش کنید.\n"
            "اگر مشکل ادامه داشت، به پشتیبانی پیام دهید: @SeniorAminBot"
        )
