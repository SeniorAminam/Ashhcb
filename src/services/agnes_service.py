# Project: Ashhcb Bot - Image to Trend Transform
# File Path: src/services/agnes_service.py
# Author: Amin Davodian
# Full Name: Mohammadamin Davodian
# Website: https://senioramin.com
# GitHub: https://github.com/SeniorAminam
# LinkedIn: https://linkedin.com/in/SudoAmin
# Developer: @SeniorAminBot
# Brand: SeniorAmin
# Created Date: 2026-06-23
# Modified Date: 2026-06-23
# Version: 1.0.0
# Purpose: Agnes AI service — txt2img, img2img, and vision
# License: MIT
# Copyright: (c) Amin Davodian

import base64
import io
import logging
from typing import Optional, Tuple

import httpx

from src.config.settings import AGNES_API_KEY

logger = logging.getLogger(__name__)

BASE_URL = "https://apihub.agnes-ai.com/v1"
TXT2IMG_MODEL = "agnes-image-2.0-flash"
IMG2IMG_MODEL = "agnes-image-2.0-flash"
VISION_MODEL = "agnes-2.0-flash"

AGNES_MODELS = [
    {
        "id": "agnes-image-2.0-flash",
        "label": "Agnes Image 2.0 Flash",
        "quality": "⭐ عالی",
        "cost": "رایگان",
    },
]


class AgnesError(Exception):
    pass


class AgnesService:

    def __init__(self):
        if not AGNES_API_KEY or not AGNES_API_KEY.startswith("sk-"):
            raise AgnesError("AGNES_API_KEY is not set or invalid")
        self.api_key = AGNES_API_KEY

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def _upload_image(self, image_bytes: bytes) -> Optional[str]:
        try:
            resp = httpx.post(
                "https://litterbox.catbox.moe/resources/internals/api.php",
                data={"reqtype": "fileupload", "time": "72h"},
                files={"fileToUpload": ("image.png", image_bytes, "image/png")},
                timeout=30,
            )
            if resp.status_code == 200 and resp.text.startswith("https://"):
                return resp.text.strip()
        except Exception as e:
            logger.warning("Image upload failed: %s", str(e)[:80])
        return None

    async def generate_image(self, prompt: str) -> Optional[bytes]:
        payload = {
            "model": TXT2IMG_MODEL,
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024",
        }
        try:
            resp = httpx.post(
                f"{BASE_URL}/images/generations",
                json=payload,
                headers=self._headers(),
                timeout=120,
            )
            if resp.status_code != 200:
                logger.warning("Agnes txt2img HTTP %d: %s", resp.status_code, resp.text[:150])
                return None
            data = resp.json()
            images = data.get("data", [])
            if not images:
                return None
            url = images[0].get("url")
            if url and url.startswith("http"):
                img_resp = httpx.get(url, timeout=60, follow_redirects=True)
                if img_resp.status_code == 200 and len(img_resp.content) > 500:
                    return img_resp.content
        except Exception as e:
            logger.error("Agnes txt2img failed: %s", str(e)[:100])
        return None

    async def transform_image(self, image_bytes: bytes, prompt: str) -> Optional[bytes]:
        image_url = await self._upload_image(image_bytes)
        if not image_url:
            logger.error("Could not upload image for img2img")
            return None
        payload = {
            "model": IMG2IMG_MODEL,
            "prompt": prompt,
            "image_url": image_url,
            "n": 1,
            "size": "1024x1024",
        }
        try:
            resp = httpx.post(
                f"{BASE_URL}/images/generations",
                json=payload,
                headers=self._headers(),
                timeout=120,
            )
            if resp.status_code != 200:
                logger.warning("Agnes img2img HTTP %d: %s", resp.status_code, resp.text[:150])
                return None
            data = resp.json()
            images = data.get("data", [])
            if not images:
                return None
            url = images[0].get("url")
            if url and url.startswith("http"):
                img_resp = httpx.get(url, timeout=60, follow_redirects=True)
                if img_resp.status_code == 200 and len(img_resp.content) > 500:
                    return img_resp.content
        except Exception as e:
            logger.error("Agnes img2img failed: %s", str(e)[:100])
        return None

    async def analyze_image(self, image_bytes: bytes) -> Optional[str]:
        image_url = await self._upload_image(image_bytes)
        if not image_url:
            return None
        payload = {
            "model": VISION_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe this image in detail in Persian (Farsi). What do you see? List all objects, colors, and the overall scene."},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }
            ],
            "max_tokens": 500,
        }
        try:
            resp = httpx.post(
                f"{BASE_URL}/chat/completions",
                json=payload,
                headers=self._headers(),
                timeout=120,
            )
            if resp.status_code != 200:
                return None
            data = resp.json()
            text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return text if text else None
        except Exception as e:
            logger.error("Agnes vision failed: %s", str(e)[:100])
        return None

    @staticmethod
    async def health_check() -> Tuple[bool, str]:
        if not AGNES_API_KEY or not AGNES_API_KEY.startswith("sk-"):
            return False, "⚠️ کلید API Agnes AI تنظیم نشده!"
        try:
            payload = {
                "model": TXT2IMG_MODEL,
                "prompt": "test",
                "n": 1,
                "size": "512x512",
            }
            headers = {
                "Authorization": f"Bearer {AGNES_API_KEY}",
                "Content-Type": "application/json",
            }
            resp = httpx.post(
                f"{BASE_URL}/images/generations",
                json=payload,
                headers=headers,
                timeout=30,
            )
            if resp.status_code == 200:
                return True, "✅ سرویس Agnes AI در دسترس است."
            return False, f"❌ Agnes AI: HTTP {resp.status_code}"
        except httpx.ConnectError:
            return False, "❌ اتصال به Agnes AI برقرار نیست."
        except Exception as e:
            return False, f"❌ Agnes AI: {str(e)[:60]}"
