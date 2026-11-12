# Project: Ashhcb Bot - Mazandaran Skills University AI Assistant
# File Path: src/utils/helpers.py
# Author: Amin Davodian
# Full Name: Mohammadamin Davodian
# Website: https://senioramin.com
# GitHub: https://github.com/SeniorAminam
# LinkedIn: https://linkedin.com/in/SudoAmin
# Developer: @SeniorAminBot
# Brand: SeniorAmin
# Created Date: 2026-06-21
# Modified Date: 2026-11-12
# Version: 1.1.0
# Purpose: Utility helper functions
# License: MIT
# Copyright: (c) Amin Davodian

import os
import io
import hashlib
import re
from typing import Optional

from PIL import Image


def get_file_extension(filename: str) -> str:
    """Extract file extension from filename."""
    return os.path.splitext(filename)[1].lower()


def format_size(size_bytes: int) -> str:
    """Format file size into human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def format_number(num: int) -> str:
    """Format large numbers with commas or shorthand."""
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num:,}"
    else:
        return str(num)


def escape_markdown(text: str, version: int = 2) -> str:
    """Escape Markdown special characters for Telegram.

    Args:
        text: Text to escape
        version: Markdown version (1 or 2)

    Returns:
        Escaped text safe for Telegram MarkdownV2
    """
    if version == 2:
        # MarkdownV2 special characters: _ * [ ] ( ) ~ ` > # + - = | { } . !
        escape_chars = r"_*[]()~`>#+-=|{}.!"
    else:
        # MarkdownV1 special characters: _ * [ ] ( ) `
        escape_chars = r"_*[]()`"

    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)
