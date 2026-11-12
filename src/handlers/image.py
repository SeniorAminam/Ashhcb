# Project: Ashhcb Bot - Mazandaran Skills University AI Assistant
# File Path: src/handlers/image.py
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
# Purpose: Image generation and editing handlers
# License: MIT
# Copyright: (c) Amin Davodian

"""
Image Handler for AI image generation and editing.

Handles:
- Text-to-image generation
- Image-to-image transformation
- Image analysis/description
- Model selection
"""

import logging
import io
from typing import List, Optional

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    CommandHandler,
)

from src.services.ai_service import AIService, AIServiceError
from src.services.agnes_service import AgnesService
from src.services.i18n_service import I18nService
from src.services.storage import UserStorage
from src.utils.helpers import format_number, escape_markdown

logger = logging.getLogger(__name__)

# Conversation states
IMAGE_MODE, TXT2IMG_PROMPT, IMG2IMG_PROMPT, MODEL_SELECT = range(4)

# AI Service instance
_ai_service = AIService()


async def image_menu_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry point for image menu."""
    query = update.callback_query
    if query:
        await query.answer()

    user_id = update.effective_user.id
    language = UserStorage.get_user_language(user_id)

    await query.edit_message_text(
        I18nService.t("image.title", language),
        reply_markup=_get_image_mode_keyboard(language),
    )
    return IMAGE_MODE


async def image_mode_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle image mode selection."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    language = UserStorage.get_user_language(user_id)
    data = query.data

    if data == "img_mode_txt2img":
        context.user_data["image_mode"] = "txt2img"
        await query.edit_message_text(
            I18nService.t("image.txt2img_prompt", language),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(I18nService.t("common.cancel", language), callback_data="img_cancel")
            ]]),
        )
        return TXT2IMG_PROMPT

    elif data == "img_mode_img2img":
        context.user_data["image_mode"] = "img2img"
        await query.edit_message_text(
            I18nService.t("image.img2img_prompt", language),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(I18nService.t("common.cancel", language), callback_data="img_cancel")
            ]]),
        )
        return IMG2IMG_PROMPT

    elif data == "img_mode_analyze":
        context.user_data["image_mode"] = "analyze"
        await query.edit_message_text(
            I18nService.t("image.analyzing", language).replace("...", "") + "\n\nعکس را ارسال کنید:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(I18nService.t("common.cancel", language), callback_data="img_cancel")
            ]]),
        )
        return IMG2IMG_PROMPT  # Reuse state for photo handling

    elif data == "img_mode_models":
        await query.edit_message_text(
            "مدل را انتخاب کنید:",
            reply_markup=_get_model_keyboard(language),
        )
        return MODEL_SELECT

    elif data == "img_back":
        from src.handlers.menu import menu_callback
        await menu_callback(update, context)
        return ConversationHandler.END

    return IMAGE_MODE


async def txt2img_prompt_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process text-to-image prompt."""
    user_id = update.effective_user.id
    language = UserStorage.get_user_language(user_id)
    prompt = update.message.text.strip()

    if not prompt:
        await update.message.reply_text(I18nService.t("errors.invalid_input", language))
        return TXT2IMG_PROMPT

    # Send generating message
    generating_msg = await update.message.reply_text(I18nService.t("image.generating", language))

    try:
        # Generate image
        image_bytes, model_name, model_id = await _ai_service.transform_image(
            image_bytes=b"",
            prompt=prompt,
        )

        if image_bytes:
            # Send image
            photo_file = InputFile(io.BytesIO(image_bytes), filename="generated.png")
            await generating_msg.delete()
            await update.message.reply_photo(
                photo=photo_file,
                caption=f"✅ {I18nService.t('image.done', language)}\n📝 {prompt}\n🤖 {model_name}",
                reply_markup=_get_image_action_keyboard(language),
            )
        else:
            await generating_msg.edit_text("❌ خطا در تولید تصویر. دوباره تلاش کنید.")

    except AIServiceError as e:
        await generating_msg.edit_text(str(e))
    except Exception as e:
        logger.error("txt2img error: %s", e)
        await generating_msg.edit_text(I18nService.t("errors.api_unavailable", language))

    return ConversationHandler.END


async def img2img_photo_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle photo for img2img or analyze."""
    user_id = update.effective_user.id
    language = UserStorage.get_user_language(user_id)
    mode = context.user_data.get("image_mode", "img2img")

    # Get largest photo
    photo = update.message.photo[-1]
    photo_file = await photo.get_file()
    image_bytes = await photo_file.download_as_bytearray()

    if mode == "analyze":
        await _handle_analyze(update, context, bytes(image_bytes), language)
        return ConversationHandler.END

    # For img2img, ask for prompt
    context.user_data["source_image"] = bytes(image_bytes)
    await update.message.reply_text(
        I18nService.t("image.img2img_prompt", language),
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(I18nService.t("common.cancel", language), callback_data="img_cancel")
        ]]),
    )
    return IMG2IMG_PROMPT


async def img2img_prompt_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process image-to-image prompt."""
    user_id = update.effective_user.id
    language = UserStorage.get_user_language(user_id)
    prompt = update.message.text.strip()
    source_image = context.user_data.get("source_image")

    if not prompt or not source_image:
        await update.message.reply_text(I18nService.t("errors.invalid_input", language))
        return IMG2IMG_PROMPT

    generating_msg = await update.message.reply_text(I18nService.t("image.transforming", language))

    try:
        image_bytes, model_name, model_id = await _ai_service.transform_image(
            image_bytes=source_image,
            prompt=prompt,
        )

        if image_bytes:
            photo_file = InputFile(io.BytesIO(image_bytes), filename="transformed.png")
            await generating_msg.delete()
            await update.message.reply_photo(
                photo=photo_file,
                caption=f"✅ {I18nService.t('image.done', language)}\n📝 {prompt}\n🤖 {model_name}",
                reply_markup=_get_image_action_keyboard(language),
            )
        else:
            await generating_msg.edit_text("❌ خطا در تبدیل تصویر.")

    except AIServiceError as e:
        await generating_msg.edit_text(str(e))
    except Exception as e:
        logger.error("img2img error: %s", e)
        await generating_msg.edit_text(I18nService.t("errors.api_unavailable", language))

    context.user_data.pop("source_image", None)
    return ConversationHandler.END


async def _handle_analyze(update: Update, context: ContextTypes.DEFAULT_TYPE, image_bytes: bytes, language: str) -> None:
    """Handle image analysis."""
    analyzing_msg = await update.message.reply_text(I18nService.t("image.analyzing", language))

    try:
        description = await _ai_service.analyze_image(image_bytes)
        if description:
            await analyzing_msg.edit_text(
                f"🔍 {I18nService.t('image.analyzing', language).replace('...', '')}\n\n{description}",
                reply_markup=_get_image_action_keyboard(language),
            )
        else:
            await analyzing_msg.edit_text("❌ خطا در تحلیل تصویر.")
    except AIServiceError as e:
        await analyzing_msg.edit_text(str(e))
    except Exception as e:
        logger.error("analyze error: %s", e)
        await analyzing_msg.edit_text(I18nService.t("errors.api_unavailable", language))


async def model_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle model selection."""
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("img_model_"):
        model_id = data.replace("img_model_", "")
        context.user_data["selected_model"] = model_id
        model_name = AgnesService.AGNES_MODELS.get(model_id, {}).get("label", model_id)
        await query.edit_message_text(
            f"مدل انتخاب شد: {model_name}",
            reply_markup=_get_image_mode_keyboard(UserStorage.get_user_language(query.from_user.id)),
        )
    elif data == "img_model_back":
        await query.edit_message_text(
            I18nService.t("image.title", UserStorage.get_user_language(query.from_user.id)),
            reply_markup=_get_image_mode_keyboard(UserStorage.get_user_language(query.from_user.id)),
        )

    return IMAGE_MODE


async def image_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle image action callbacks."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    language = UserStorage.get_user_language(user_id)
    data = query.data

    if data == "img_cancel":
        from src.handlers.menu import menu_callback
        await menu_callback(update, context)
    elif data == "img_generate_again":
        await image_menu_entry(update, context)
    elif data == "img_back_to_menu":
        from src.handlers.menu import menu_callback
        await menu_callback(update, context)


def _get_image_mode_keyboard(language: str) -> InlineKeyboardMarkup:
    """Get image mode selection keyboard."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎨 متن به تصویر (txt2img)", callback_data="img_mode_txt2img")],
        [InlineKeyboardButton("🔄 تصویر به تصویر (img2img)", callback_data="img_mode_img2img")],
        [InlineKeyboardButton("🔍 تحلیل تصویر", callback_data="img_mode_analyze")],
        [InlineKeyboardButton("🤖 انتخاب مدل", callback_data="img_mode_models")],
        [InlineKeyboardButton(I18nService.t("common.back", language), callback_data="img_back")],
    ])


def _get_model_keyboard(language: str) -> InlineKeyboardMarkup:
    """Get model selection keyboard."""
    buttons = []
    for model_id, info in AgnesService.AGNES_MODELS.items():
        buttons.append([InlineKeyboardButton(info["label"], callback_data=f"img_model_{model_id}")])
    buttons.append([InlineKeyboardButton(I18nService.t("common.back", language), callback_data="img_model_back")])
    return InlineKeyboardMarkup(buttons)


def _get_image_action_keyboard(language: str) -> InlineKeyboardMarkup:
    """Get post-generation action keyboard."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 تولید مجدد", callback_data="img_generate_again")],
        [InlineKeyboardButton(I18nService.t("common.back", language), callback_data="img_back_to_menu")],
    ])


def get_image_conversation_handler() -> ConversationHandler:
    """Get image conversation handler."""
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(image_menu_entry, pattern=r"^menu_image$")],
        states={
            IMAGE_MODE: [CallbackQueryHandler(image_mode_selected, pattern=r"^img_mode_")],
            TXT2IMG_PROMPT: [MessageHandler(filters.TEXT & ~filters.COMMAND, txt2img_prompt_received)],
            IMG2IMG_PROMPT: [
                MessageHandler(filters.PHOTO, img2img_photo_received),
                MessageHandler(filters.TEXT & ~filters.COMMAND, img2img_prompt_received),
            ],
            MODEL_SELECT: [CallbackQueryHandler(model_selected, pattern=r"^img_model_")],
        },
        fallbacks=[CallbackQueryHandler(image_callback, pattern=r"^img_cancel$")],
        per_user=True,
        per_chat=True,
    )


def get_image_callback_handlers() -> List:
    """Get image callback handlers."""
    return [
        CallbackQueryHandler(image_callback, pattern=r"^img_(generate_again|back_to_menu)$"),
    ]


def get_all_image_handlers() -> List:
    """Get all image handlers."""
    return [
        get_image_conversation_handler(),
        *get_image_callback_handlers(),
    ]