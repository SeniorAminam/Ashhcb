# Project: Ashhcb Bot - Mazandaran Skills University AI Assistant
# File Path: src/config/settings.py
# Author: Amin Davodian
# Full Name: Mohammadamin Davodian
# Website: https://senioramin.com
# GitHub: https://github.com/SeniorAminam
# LinkedIn: https://linkedin.com/in/SudoAmin
# Developer: @SeniorAminBot
# Brand: SeniorAmin
# Created Date: 2026-06-23
# Modified Date: 2026-11-12
# Version: 5.0.0
# Purpose: Central configuration — env vars, bot metadata
# License: MIT
# Copyright: (c) Amin Davodian

import os
from dotenv import load_dotenv

load_dotenv()

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_DIR = os.getenv("LOG_DIR", "logs")
LOG_JSON = os.getenv("LOG_JSON", "false").lower() == "true"

# Initialize comprehensive logging
from src.config.logging_config import setup_logging
setup_logging(log_dir=LOG_DIR, level=LOG_LEVEL, json_format=LOG_JSON)

# ---------- Bale Bot ----------
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
if not BOT_TOKEN:
    print("WARNING: BOT_TOKEN is not set!")

BALE_API_BASE: str = os.getenv("BALE_API_BASE", "https://tapi.bale.ai/bot{token}")
BALE_FILE_BASE: str = os.getenv("BALE_FILE_BASE", "https://tapi.bale.ai/file/bot{token}")

# ---------- Admin Configuration ----------
_admin_ids_str: str = os.getenv("ADMIN_USER_IDS", "")
ADMIN_USER_IDS: list = []
if _admin_ids_str:
    for part in _admin_ids_str.split(","):
        part = part.strip()
        if part.isdigit():
            ADMIN_USER_IDS.append(int(part))

# ---------- AI Service (OpenAI-compatible, Gemma 4) ----------
AI_API_KEY: str = os.getenv("AI_API_KEY", "")
AI_BASE_URL: str = os.getenv("AI_BASE_URL", "https://apihub.agnes-ai.com/v1")
AI_MODEL_CHAT: str = os.getenv("AI_MODEL_CHAT", "gemma-4")
AI_MODEL_VISION: str = os.getenv("AI_MODEL_VISION", "gemma-4")

# Legacy (deprecated)
AGNES_API_KEY: str = os.getenv("AGNES_API_KEY", AI_API_KEY)

# ---------- Bot Limits ----------
MAX_PHOTO_SIZE_MB: int = int(os.getenv("MAX_PHOTO_SIZE_MB", "10"))
DOWNLOAD_TIMEOUT: int = int(os.getenv("DOWNLOAD_TIMEOUT", "30"))
API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "120"))
RATE_LIMIT_SECONDS: int = int(os.getenv("RATE_LIMIT_SECONDS", "60"))

# ---------- Feature Flags ----------
ENABLE_WEB_SEARCH: bool = os.getenv("ENABLE_WEB_SEARCH", "true").lower() == "true"
ENABLE_SCRAPERS: bool = os.getenv("ENABLE_SCRAPERS", "true").lower() == "true"
DEFAULT_LANGUAGE: str = os.getenv("DEFAULT_LANGUAGE", "fa")

# ---------- Bot Metadata ----------
BOT_USERNAME: str = "MSUSkillsBot"
BOT_VERSION: str = "5.0.0"
SUPPORT_LINK: str = "https://ble.ir/SeniorAminBot"
