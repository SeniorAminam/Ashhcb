# Project: Ashhcb Bot - Image to Trend Transform
# File Path: src/keyboards/reply.py
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
# Purpose: Reply keyboards (main menu, user panel, admin panel)
# License: MIT
# Copyright: (c) Amin Davodian

from telegram import ReplyKeyboardMarkup, KeyboardButton


def get_main_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    if is_admin:
        buttons = [
            [
                KeyboardButton(text="🖼️ ساخت عکس"),
                KeyboardButton(text="📷 شروع تبدیل عکس"),
            ],
            [
                KeyboardButton(text="🔍 تحلیل تصویر"),
            ],
            [
                KeyboardButton(text="👤 پنل کاربری"),
                KeyboardButton(text="👑 پنل ادمین"),
            ],
            [
                KeyboardButton(text="❓ راهنما"),
                KeyboardButton(text="ℹ️ درباره"),
            ],
        ]
    else:
        buttons = [
            [
                KeyboardButton(text="🖼️ ساخت عکس"),
                KeyboardButton(text="📷 شروع تبدیل عکس"),
            ],
            [
                KeyboardButton(text="🔍 تحلیل تصویر"),
            ],
            [
                KeyboardButton(text="👤 پنل کاربری"),
                KeyboardButton(text="❓ راهنما"),
            ],
            [
                KeyboardButton(text="ℹ️ درباره"),
            ],
        ]

    return ReplyKeyboardMarkup(
        buttons,
        resize_keyboard=True,
        input_field_placeholder="یک گزینه را انتخاب کنید...",
    )


def get_user_panel_keyboard() -> ReplyKeyboardMarkup:
    buttons = [
        [
            KeyboardButton(text="📜 تاریخچه تبدیل‌ها"),
        ],
        [
            KeyboardButton(text="📊 آمار کاربری"),
        ],
        [
            KeyboardButton(text="🔙 بازگشت به منوی اصلی"),
        ],
    ]

    return ReplyKeyboardMarkup(
        buttons,
        resize_keyboard=True,
        input_field_placeholder="گزینه مورد نظر را انتخاب کنید...",
    )


def get_admin_panel_keyboard() -> ReplyKeyboardMarkup:
    buttons = [
        [
            KeyboardButton(text="📊 آمار کلی ربات"),
        ],
        [
            KeyboardButton(text="👥 لیست کاربران"),
        ],
        [
            KeyboardButton(text="📢 ارسال پیام همگانی"),
        ],
        [
            KeyboardButton(text="🔙 بازگشت به منوی اصلی"),
        ],
    ]

    return ReplyKeyboardMarkup(
        buttons,
        resize_keyboard=True,
        input_field_placeholder="گزینه مدیریتی را انتخاب کنید...",
    )
