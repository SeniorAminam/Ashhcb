# Project: Ashhcb Bot - Image to Trend Transform
# File Path: src/keyboards/inline.py
# Author: Amin Davodian
# Full Name: Mohammadamin Davodian
# Website: https://senioramin.com
# GitHub: https://github.com/SeniorAminam
# LinkedIn: https://linkedin.com/in/SudoAmin
# Developer: @SeniorAminBot
# Brand: SeniorAmin
# Created Date: 2026-06-23
# Modified Date: 2026-06-23
# Version: 4.0.0
# Purpose: Inline keyboard builders for bot menu navigation
# License: MIT
# Copyright: (c) Amin Davodian

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

AGNES_MODELS = [
    {
        "id": "agnes-image-2.0-flash",
        "label": "Agnes Image 2.0 Flash",
        "quality": "⭐ عالی",
        "cost": "رایگان",
    },
]


def get_start_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="📷 شروع تبدیل عکس", callback_data="start_transform"
            ),
        ],
        [
            InlineKeyboardButton(
                text="ℹ️ درباره ربات", callback_data="about"
            ),
        ],
        [
            InlineKeyboardButton(
                text="💬 پشتیبانی", url="https://ble.ir/SeniorAminBot"
            ),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="🔙 بازگشت به منو", callback_data="back_to_menu"
            ),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_model_selection_keyboard(selected_model_id: str = "") -> InlineKeyboardMarkup:
    keyboard = []
    for i, model in enumerate(AGNES_MODELS, 1):
        mid = model["id"]
        label = model["label"]
        quality = model.get("quality", "")
        cost = model.get("cost", "")

        is_selected = (mid == selected_model_id)
        prefix = "✅ " if is_selected else f"{i}. "
        display = f"{prefix}{label.split('(')[0].strip()} | {quality} | {cost}"

        keyboard.append([
            InlineKeyboardButton(
                text=display,
                callback_data=f"model_{mid}",
            ),
        ])

    keyboard.append([
        InlineKeyboardButton(
            text="🔙 بازگشت به منو", callback_data="back_to_menu"
        ),
    ])
    return InlineKeyboardMarkup(keyboard)
