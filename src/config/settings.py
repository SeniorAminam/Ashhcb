# Project: Ashhcb Bot - Image to Trend Transform
# File Path: src/config/settings.py
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
# Purpose: Central configuration — env vars, bot metadata
# License: MIT
# Copyright: (c) Amin Davodian

import os
import logging
from dotenv import load_dotenv

load_dotenv()

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, LOG_LEVEL, logging.INFO),
)

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

# ---------- Agnes AI (only provider) ----------
AGNES_API_KEY: str = os.getenv("AGNES_API_KEY", "")

# ---------- Bot Limits ----------
MAX_PHOTO_SIZE_MB: int = int(os.getenv("MAX_PHOTO_SIZE_MB", "10"))
DOWNLOAD_TIMEOUT: int = int(os.getenv("DOWNLOAD_TIMEOUT", "30"))
API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "120"))
RATE_LIMIT_SECONDS: int = int(os.getenv("RATE_LIMIT_SECONDS", "60"))

# ---------- Bot Metadata ----------
BOT_USERNAME: str = "AshhcbBot"
BOT_VERSION: str = "4.0.2"
SUPPORT_LINK: str = "https://ble.ir/SeniorAminBot"
