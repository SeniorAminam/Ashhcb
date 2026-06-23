# Project: Ashhcb Bot - Image to Trend Transform
# File Path: src/services/ai_service.py
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
# Purpose: AI service thin wrapper around AgnesService
# License: MIT
# Copyright: (c) Amin Davodian

import logging
from typing import Optional, Tuple

from src.config.settings import AGNES_API_KEY
from src.services.agnes_service import AgnesService, AgnesError

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    pass


class AIService:

    def __init__(self):
        self.agnes = None
        if AGNES_API_KEY and AGNES_API_KEY.startswith("sk-"):
            try:
                self.agnes = AgnesService()
            except Exception as e:
                logger.warning("Agnes not available: %s", str(e)[:80])

    async def transform_image(
        self,
        image_bytes: bytes,
        prompt: str,
        model_id: Optional[str] = None,
    ) -> Tuple[Optional[bytes], str, str]:
        if not self.agnes:
            raise AIServiceError("⚠️ سرویس هوش مصنوعی در دسترس نیست!\nلطفاً با پشتیبانی تماس بگیرید.")

        if not image_bytes:
            result_bytes = await self.agnes.generate_image(prompt)
            if result_bytes:
                return result_bytes, "Agnes Image 2.0 Flash", "agnes-image-2.0-flash"
            raise AIServiceError("⚠️ خطا در تولید تصویر!\nلطفاً دوباره تلاش کنید.")

        result_bytes = await self.agnes.transform_image(image_bytes, prompt)
        if result_bytes:
            return result_bytes, "Agnes Image 2.0 Flash", "agnes-image-2.0-flash"

        raise AIServiceError(
            "⚠️ خطا در پردازش تصویر!\n\n"
            "سرویس در دسترس نبود. لطفاً چند لحظه بعد دوباره تلاش کنید."
        )

    async def analyze_image(self, image_bytes: bytes) -> Optional[str]:
        if not self.agnes:
            raise AIServiceError("⚠️ سرویس هوش مصنوعی در دسترس نیست!")
        description = await self.agnes.analyze_image(image_bytes)
        if description:
            return description
        raise AIServiceError("⚠️ خطا در تحلیل تصویر!\nلطفاً دوباره تلاش کنید.")

    @staticmethod
    async def health_check() -> Tuple[bool, str]:
        return await AgnesService.health_check()
