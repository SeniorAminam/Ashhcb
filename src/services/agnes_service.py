# Project: Ashhcb Bot - Mazandaran Skills University AI Assistant
# File Path: src/services/agnes_service.py
# Author: Amin Davodian
# Full Name: Mohammadamin Davodian
# Website: https://senioramin.com
# GitHub: https://github.com/SeniorAminam
# LinkedIn: https://linkedin.com/in/SudoAmin
# Developer: @SeniorAminBot
# Brand: SeniorAmin
# Created Date: 2026-11-12
# Modified Date: 2026-11-12
# Version: 3.0.0
# Purpose: AI Service (OpenAI-compatible, Gemma 4) — chat completions & vision only (text-first)
# License: MIT
# Copyright: (c) Amin Davodian

import logging
from typing import Optional, Tuple, List, Dict, Any

import httpx

from src.config.settings import (
    AI_API_KEY, AI_BASE_URL, AI_MODEL_CHAT, AI_MODEL_VISION,
    API_TIMEOUT, DOWNLOAD_TIMEOUT
)

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    pass


class AIService:
    """Async OpenAI-compatible AI client (Gemma 4) — chat completions & vision only."""

    _client: Optional[httpx.AsyncClient] = None

    def __init__(self):
        if not AI_API_KEY or not AI_API_KEY.strip():
            raise AIServiceError("AI_API_KEY is not set or invalid")
        self.api_key = AI_API_KEY
        self.base_url = AI_BASE_URL.rstrip("/")
        self.chat_model = AI_MODEL_CHAT
        self.vision_model = AI_MODEL_VISION

    @classmethod
    async def get_client(cls) -> httpx.AsyncClient:
        """Get or create shared AsyncClient."""
        if cls._client is None or cls._client.is_closed:
            cls._client = httpx.AsyncClient(
                timeout=httpx.Timeout(
                    connect=15.0,
                    read=API_TIMEOUT,
                    write=API_TIMEOUT,
                    pool=15.0,
                ),
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
            )
        return cls._client

    @classmethod
    async def close_client(cls) -> None:
        """Close shared AsyncClient on shutdown."""
        if cls._client and not cls._client.is_closed:
            await cls._client.aclose()
            cls._client = None

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def _upload_image(self, image_bytes: bytes) -> Optional[str]:
        """Upload image to temporary hosting (litterbox) for vision."""
        client = await self.get_client()
        try:
            resp = await client.post(
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

    # ── Chat Completions (OpenAI-compatible) ──

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Optional[str]:
        """
        Generate chat completion using OpenAI-compatible API (Gemma 4).

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Returns:
            Response text or None on failure
        """
        payload = {
            "model": self.chat_model,
            "messages": messages,
            "temperature": temperature,
            "stream": False,  # Ensure non-streaming response
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        client = await self.get_client()
        try:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=self._headers(),
                timeout=API_TIMEOUT,
            )
            if resp.status_code != 200:
                logger.warning("Chat completion HTTP %d: %s", resp.status_code, resp.text[:200])
                return None

            # Handle potential streaming or malformed responses
            text = resp.text.strip()
            if not text:
                logger.warning("Empty response from chat completion")
                return None

            # Try parsing as JSON, handle potential extra data
            try:
                data = resp.json()
            except Exception as json_err:
                # Try to extract JSON from response (some APIs wrap in data: or have extra text)
                import json
                try:
                    # Find first { and last }
                    start = text.find('{')
                    end = text.rfind('}')
                    if start >= 0 and end > start:
                        data = json.loads(text[start:end+1])
                    else:
                        raise json_err
                except Exception:
                    logger.error("Failed to parse JSON response: %s", text[:200])
                    return None

            choices = data.get("choices", [])
            if not choices:
                return None

            message = choices[0].get("message", {})
            content = message.get("content", "")
            return content if content else None

        except httpx.TimeoutException:
            logger.error("Chat completion timeout")
            return None
        except Exception as e:
            logger.error("Chat completion failed: %s", str(e)[:100])
            return None

    # ── Vision (Image Analysis) — optional future feature ──

    async def analyze_image(self, image_bytes: bytes, prompt: Optional[str] = None) -> Optional[str]:
        """Analyze image using vision model (Gemma 4 vision)."""
        image_url = await self._upload_image(image_bytes)
        if not image_url:
            return None

        default_prompt = "Describe this image in detail in Persian (Farsi). What do you see? List all objects, colors, and the overall scene."
        vision_prompt = prompt or default_prompt

        payload = {
            "model": self.vision_model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": vision_prompt},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }
            ],
            "max_tokens": 500,
        }
        client = await self.get_client()
        try:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=self._headers(),
                timeout=API_TIMEOUT,
            )
            if resp.status_code != 200:
                logger.warning("vision HTTP %d: %s", resp.status_code, resp.text[:150])
                return None

            data = resp.json()
            text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return text if text else None
        except Exception as e:
            logger.error("vision failed: %s", str(e)[:100])
        return None

    # ── Health Check ──

    @staticmethod
    async def health_check() -> Tuple[bool, str]:
        if not AI_API_KEY or not AI_API_KEY.strip():
            return False, "⚠️ AI_API_KEY is not set!"

        try:
            async with AIService() as svc:
                response = await svc.chat_completion(
                    messages=[{"role": "user", "content": "test"}],
                    temperature=0.1,
                    max_tokens=10,
                )

            if response is not None:
                return True, f"✅ AI Service ({AI_BASE_URL}, model: {AI_MODEL_CHAT}) is accessible."
            return False, "❌ AI Service: No response from chat completion"

        except httpx.ConnectError:
            return False, f"❌ Cannot connect to {AI_BASE_URL}"
        except Exception as e:
            return False, f"❌ AI Service: {str(e)[:80]}"

    # Context manager support
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass  # Shared client closed on shutdown


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    import asyncio
    logging.basicConfig(level=logging.INFO)

    async def test():
        print(f"Base URL: {AI_BASE_URL}")
        print(f"Chat Model: {AI_MODEL_CHAT}")
        print(f"Vision Model: {AI_MODEL_VISION}")
        print(f"API Key: {'***' + AI_API_KEY[-4:] if AI_API_KEY else 'NOT SET'}")

        ok, msg = await AIService.health_check()
        print(f"Health: {msg}")

    asyncio.run(test())