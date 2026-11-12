# Project: Ashhcb Bot - Mazandaran Skills University AI Assistant
# File Path: src/keyboards/builders.py
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
# Purpose: Dynamic keyboard builders with i18n support
# License: MIT
# Copyright: (c) Amin Davodian

"""
Keyboard Builders for dynamic inline and reply keyboards.

Provides:
- Language-aware keyboard generation
- Dynamic button creation from config
- Consistent styling across handlers
"""

from typing import List, Dict, Any, Optional, Callable
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from src.services.i18n_service import I18nService, SUPPORTED_LANGUAGES


class KeyboardBuilder:
    """Base keyboard builder with i18n support."""

    def __init__(self, language: str = "fa"):
        self.language = language
        self.rows: List[List[InlineKeyboardButton]] = []

    def t(self, key: str, **kwargs) -> str:
        """Translate key for current language."""
        return I18nService.t(key, self.language, **kwargs)

    def add_row(self, *buttons: InlineKeyboardButton) -> "KeyboardBuilder":
        """Add a row of buttons."""
        self.rows.append(list(buttons))
        return self

    def add_button(self, text: str, callback_data: str, **kwargs) -> "KeyboardBuilder":
        """Add a button to the last row or create new row."""
        btn = InlineKeyboardButton(text, callback_data=callback_data, **kwargs)
        if not self.rows:
            self.rows.append([])
        self.rows[-1].append(btn)
        return self

    def add_url_button(self, text: str, url: str) -> "KeyboardBuilder":
        """Add a URL button."""
        btn = InlineKeyboardButton(text, url=url)
        if not self.rows:
            self.rows.append([])
        self.rows[-1].append(btn)
        return self

    def row(self, *buttons: InlineKeyboardButton) -> "KeyboardBuilder":
        """Add a new row with buttons."""
        return self.add_row(*buttons)

    def back_button(self, callback_data: str = "main_menu") -> "KeyboardBuilder":
        """Add a back button."""
        return self.add_button(self.t("common.back"), callback_data)

    def cancel_button(self, callback_data: str = "cancel") -> "KeyboardBuilder":
        """Add a cancel button."""
        return self.add_button(self.t("common.cancel"), callback_data)

    def build(self) -> InlineKeyboardMarkup:
        """Build the keyboard markup."""
        return InlineKeyboardMarkup(self.rows)

    def clear(self) -> "KeyboardBuilder":
        """Clear all rows."""
        self.rows = []
        return self


class InlineKeyboardBuilder(KeyboardBuilder):
    """Builder for inline keyboards."""

    @classmethod
    def main_menu(cls, language: str) -> InlineKeyboardMarkup:
        """Build main menu keyboard."""
        return cls(language).row(
            InlineKeyboardButton(I18nService.t("menu.search", language), callback_data="menu_search"),
            InlineKeyboardButton(I18nService.t("menu.chat", language), callback_data="menu_chat"),
        ).row(
            InlineKeyboardButton(I18nService.t("menu.skills", language), callback_data="menu_skills"),
            InlineKeyboardButton(I18nService.t("menu.admissions", language), callback_data="menu_admissions"),
        ).row(
            InlineKeyboardButton(I18nService.t("menu.career", language), callback_data="menu_career"),
            InlineKeyboardButton(I18nService.t("menu.announcements", language), callback_data="menu_announcements"),
        ).row(
            InlineKeyboardButton(I18nService.t("menu.settings", language), callback_data="menu_settings"),
        ).row(
            InlineKeyboardButton(I18nService.t("menu.user_panel", language), callback_data="menu_user_panel"),
        ).build()

    @classmethod
    def language_selection(cls, language: str, current: str) -> InlineKeyboardMarkup:
        """Build language selection keyboard."""
        builder = cls(language)
        flags = {"fa": "🇮🇷", "en": "🇬🇧", "ar": "🇸🇦"}
        for lang in SUPPORTED_LANGUAGES:
            name = I18nService.get_language_name(lang)
            flag = flags.get(lang, "")
            marker = " ✅" if lang == current else ""
            builder.row(InlineKeyboardButton(f"{flag} {name}{marker}", callback_data=f"lang_{lang}"))
        builder.row(InlineKeyboardButton(I18nService.t("common.back", language), callback_data="settings_back"))
        return builder.build()

    @classmethod
    def search_categories(cls, language: str, categories: Dict[str, str], prefix: str = "search_cat_") -> InlineKeyboardMarkup:
        """Build category selection keyboard."""
        builder = cls(language)
        items = list(categories.items())
        for i in range(0, len(items), 2):
            row_buttons = []
            for key, label in items[i:i+2]:
                row_buttons.append(InlineKeyboardButton(label, callback_data=f"{prefix}{key}"))
            builder.row(*row_buttons)
        builder.row(InlineKeyboardButton(I18nService.t("common.cancel", language), callback_data="search_cancel"))
        return builder.build()

    @classmethod
    def paginated_list(
        cls,
        language: str,
        items: List[Dict[str, Any]],
        page: int,
        per_page: int,
        item_formatter: Callable[[Dict], InlineKeyboardButton],
        page_callback_prefix: str,
        extra_rows: Optional[List[List[InlineKeyboardButton]]] = None,
    ) -> InlineKeyboardMarkup:
        """Build paginated list keyboard."""
        builder = cls(language)
        total_pages = (len(items) + per_page - 1) // per_page
        start = page * per_page
        end = min(start + per_page, len(items))

        for item in items[start:end]:
            builder.row(item_formatter(item))

        # Pagination controls
        if total_pages > 1:
            nav_row = []
            if page > 0:
                nav_row.append(InlineKeyboardButton("⬅️ قبلی", callback_data=f"{page_callback_prefix}{page-1}"))
            nav_row.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="noop"))
            if page < total_pages - 1:
                nav_row.append(InlineKeyboardButton("بعدی ➡️", callback_data=f"{page_callback_prefix}{page+1}"))
            builder.row(*nav_row)

        if extra_rows:
            for row in extra_rows:
                builder.row(*row)

        return builder.build()


class ReplyKeyboardBuilder:
    """Builder for reply keyboards (custom keyboards)."""

    def __init__(self, language: str = "fa", resize: bool = True, one_time: bool = False):
        self.language = language
        self.rows: List[List[KeyboardButton]] = []
        self.resize = resize
        self.one_time = one_time

    def t(self, key: str, **kwargs) -> str:
        return I18nService.t(key, self.language, **kwargs)

    def add_row(self, *buttons: KeyboardButton) -> "ReplyKeyboardBuilder":
        self.rows.append(list(buttons))
        return self

    def add_button(self, text: str, request_contact: bool = False, request_location: bool = False) -> "ReplyKeyboardBuilder":
        btn = KeyboardButton(text, request_contact=request_contact, request_location=request_location)
        if not self.rows:
            self.rows.append([])
        self.rows[-1].append(btn)
        return self

    def row(self, *buttons: KeyboardButton) -> "ReplyKeyboardBuilder":
        return self.add_row(*buttons)

    def build(self) -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            self.rows,
            resize_keyboard=self.resize,
            one_time_keyboard=self.one_time,
            input_field_placeholder=self.t("chat.placeholder") if self.rows else None,
        )

    @classmethod
    def main_menu(cls, language: str) -> ReplyKeyboardMarkup:
        """Build main reply keyboard."""
        return cls(language).row(
            KeyboardButton(I18nService.t("menu.search", language)),
            KeyboardButton(I18nService.t("menu.chat", language)),
        ).row(
            KeyboardButton(I18nService.t("menu.skills", language)),
            KeyboardButton(I18nService.t("menu.admissions", language)),
        ).row(
            KeyboardButton(I18nService.t("menu.career", language)),
            KeyboardButton(I18nService.t("menu.announcements", language)),
        ).row(
            KeyboardButton(I18nService.t("menu.settings", language)),
        ).build()

    @classmethod
    def chat_mode(cls, language: str) -> ReplyKeyboardMarkup:
        """Build chat mode reply keyboard."""
        return cls(language, one_time=True).row(
            KeyboardButton("💬 چت عمومی"),
            KeyboardButton("📝 مشاوره پذیرش"),
        ).row(
            KeyboardButton("💼 مشاوره شغلی"),
            KeyboardButton("🎓 مهارت‌ها"),
        ).row(
            KeyboardButton(I18nService.t("common.cancel", language)),
        ).build()

    @classmethod
    def remove_keyboard(cls) -> ReplyKeyboardMarkup:
        """Return keyboard removal."""
        from telegram import ReplyKeyboardRemove
        return ReplyKeyboardRemove()


def get_main_menu_keyboard(language: str) -> InlineKeyboardMarkup:
    """Convenience function for main menu."""
    return InlineKeyboardBuilder.main_menu(language)


def get_language_keyboard(language: str, current: str) -> InlineKeyboardMarkup:
    """Convenience function for language selection."""
    return InlineKeyboardBuilder.language_selection(language, current)


def get_reply_main_menu(language: str) -> ReplyKeyboardMarkup:
    """Convenience function for reply main menu."""
    return ReplyKeyboardBuilder.main_menu(language)