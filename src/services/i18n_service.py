# Project: Ashhcb Bot - Mazandaran Skills University AI Assistant
# File Path: src/services/i18n_service.py
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
# Purpose: Internationalization service for Persian, English, Arabic
# License: MIT
# Copyright: (c) Amin Davodian

"""
I18n Service for multilingual support (Persian, English, Arabic).
Uses JSON translation files in src/locales/.
Supports RTL formatting and numeral conversion for Persian/Arabic.
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Supported languages
SUPPORTED_LANGUAGES = ["fa", "en", "ar"]
DEFAULT_LANGUAGE = "fa"
RTL_LANGUAGES = {"fa", "ar"}

# Persian/Arabic-Indic numerals
PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
ARABIC_DIGITS = "٠١٢٣٤٥٦٧٨٩"
WESTERN_DIGITS = "0123456789"


class I18nService:
    """Internationalization service with translation loading and RTL support."""

    _translations: Dict[str, Dict[str, str]] = {}
    _loaded = False

    @classmethod
    def load_translations(cls, locales_dir: Optional[str] = None) -> None:
        """Load all translation files from locales directory."""
        if cls._loaded:
            return

        if locales_dir is None:
            locales_dir = str(Path(__file__).parent.parent / "locales")

        for lang in SUPPORTED_LANGUAGES:
            file_path = Path(locales_dir) / f"{lang}.json"
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        cls._translations[lang] = json.load(f)
                    logger.info("Loaded translations for %s: %d keys", lang, len(cls._translations[lang]))
                except Exception as e:
                    logger.error("Failed to load translations for %s: %s", lang, e)
                    cls._translations[lang] = {}
            else:
                logger.warning("Translation file not found: %s", file_path)
                cls._translations[lang] = {}

        cls._loaded = True

    @classmethod
    def t(cls, key: str, language: str = DEFAULT_LANGUAGE, **kwargs) -> str:
        """
        Translate a key to the given language.

        Args:
            key: Translation key (e.g., "menu.search")
            language: Target language code (fa, en, ar)
            **kwargs: Format arguments for the translation string

        Returns:
            Translated string, or key if not found
        """
        if not cls._loaded:
            cls.load_translations()

        lang = language if language in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
        translations = cls._translations.get(lang, {})

        # Navigate nested keys (e.g., "menu.search" -> translations["menu"]["search"])
        value = translations
        for part in key.split("."):
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                # Fallback to English, then key
                fallback = cls._translations.get("en", {})
                for part in key.split("."):
                    if isinstance(fallback, dict) and part in fallback:
                        fallback = fallback[part]
                    else:
                        return key
                value = fallback
                break

        if isinstance(value, str):
            try:
                return value.format(**kwargs) if kwargs else value
            except KeyError:
                return value
        return key

    @classmethod
    def detect_language(cls, text: str) -> str:
        """
        Detect language from text using simple heuristics.
        Returns 'fa', 'ar', or 'en'.
        """
        if not text:
            return DEFAULT_LANGUAGE

        # Count Persian/Arabic vs Latin characters
        persian_arabic = sum(1 for c in text if "؀" <= c <= "ۿ" or "ݐ" <= c <= "ݿ")
        latin = sum(1 for c in text if "a" <= c.lower() <= "z")

        if persian_arabic > latin:
            # Check for Persian-specific characters
            if any(c in text for c in "پچگک"):
                return "fa"
            return "ar"
        return "en"

    @classmethod
    def is_rtl(cls, language: str) -> bool:
        """Check if language is RTL."""
        return language in RTL_LANGUAGES

    @classmethod
    def format_rtl(cls, text: str, language: str) -> str:
        """
        Format text for RTL display by adding RLM (Right-to-Left Mark).
        """
        if cls.is_rtl(language) and text:
            return f"‏{text}"
        return text

    @classmethod
    def to_local_numerals(cls, number: str | int, language: str) -> str:
        """
        Convert Western numerals to Persian/Arabic-Indic numerals.
        """
        num_str = str(number)
        if language == "fa":
            return num_str.translate(str.maketrans(WESTERN_DIGITS, PERSIAN_DIGITS))
        elif language == "ar":
            return num_str.translate(str.maketrans(WESTERN_DIGITS, ARABIC_DIGITS))
        return num_str

    @classmethod
    def from_local_numerals(cls, text: str, language: str) -> str:
        """
        Convert Persian/Arabic-Indic numerals back to Western.
        """
        if language == "fa":
            return text.translate(str.maketrans(PERSIAN_DIGITS, WESTERN_DIGITS))
        elif language == "ar":
            return text.translate(str.maketrans(ARABIC_DIGITS, WESTERN_DIGITS))
        return text

    @classmethod
    def get_language_name(cls, language: str) -> str:
        """Get native language name."""
        names = {"fa": "فارسی", "en": "English", "ar": "العربية"}
        return names.get(language, language)

    @classmethod
    def get_language_flag(cls, language: str) -> str:
        """Get flag emoji for language."""
        flags = {"fa": "🇮🇷", "en": "🇬🇧", "ar": "🇸🇦"}
        return flags.get(language, "🏳️")