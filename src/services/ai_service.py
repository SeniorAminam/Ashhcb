# Project: Ashhcb Bot - Mazandaran Skills University AI Assistant
# File Path: src/services/ai_service.py
# Author: Amin Davodian
# Full Name: Mohammadamin Davodian
# Website: https://senioramin.com
# GitHub: https://github.com/SeniorAminam
# LinkedIn: https://linkedin.com/in/SudoAmin
# Developer: @SeniorAminBot
# Brand: SeniorAmin
# Created Date: 2026-06-23
# Modified Date: 2026-11-12
# Version: 3.0.0
# Purpose: AI service with RAG for chat, academic advising, career guidance (text-only, Gemma 4)
# License: MIT
# Copyright: (c) Amin Davodian

import logging
from typing import Optional, Tuple, List, Dict, Any

from src.config.settings import AI_API_KEY
from src.services.agnes_service import AIService as AgnesClient
from src.services.knowledge_service import KnowledgeService
from src.services.i18n_service import I18nService

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    pass


class AIService:
    """AI Service with RAG capabilities for university assistant (text-only)."""

    # System prompts for different modes
    SYSTEM_PROMPTS = {
        "chat": """شما دستیار هوشمند دانشگاه ملی مهارت مازندران هستید.
به سوالات دانشجویان و متقاضیان درباره پذیرش، مهارت‌ها، دوره‌ها، مقررات و مشاوره تحصیلی پاسخ دهید.
از اطلاعات زیر به عنوان زمینه (context) استفاده کنید و پاسخ‌های دقیق، مفید و دوستانه دهید.
اگر پاسخ در اطلاعات موجود نیست، بگویید که نمی‌دانید و راهنمایی کنید از منوی جستجو استفاده کنند.
پاسخ به زبان {language} دهید.""",

        "admissions": """شما مشاور پذیرش دانشگاه ملی مهارت مازندران هستید.
راهنمای کامل درباره شرایط ثبت‌نام، مدارک مورد نیاز، مهلت‌ها و مراحل پذیرش دهید.
از اطلاعات موجود در پایگاه دانش استفاده کنید.
پاسخ به زبان {language} دهید.""",

        "career": """شما مشاور شغلی و Karriere دانشگاه ملی مهارت مازندران هستید.
بر اساس علایق، مهارت‌ها و گرایش‌های کاربر، مسیرهای شغلی مناسب پیشنهاد دهید.
بازار کار، مهارت‌های مورد نیاز و نقشه‌راه یادگیری را توضیح دهید.
پاسخ به زبان {language} دهید.""",

        "skills": """شما مشاور مهارت‌ها و دوره‌های آموزشی دانشگاه ملی مهارت مازندران هستید.
دوره‌های مناسب، پیش‌نیازها، سطح مهارت، مدت زمان و گواهینامه‌ها را معرفی کنید.
از پایگاه دانش مهارت‌ها و دوره‌ها استفاده کنید.
پاسخ به زبان {language} دهید.""",
    }

    def __init__(self):
        self.agnes = None
        if AI_API_KEY and AI_API_KEY.strip():
            try:
                self.agnes = AgnesClient()
            except Exception as e:
                logger.warning("AI Service not available: %s", str(e)[:80])

    # ── RAG Chat ──

    async def chat_with_rag(
        self,
        user_message: str,
        language: str = "fa",
        mode: str = "chat",
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Generate response using RAG (Retrieval-Augmented Generation).

        Args:
            user_message: User's question
            language: Response language (fa, en, ar)
            mode: Chat mode (chat, admissions, career, skills)
            conversation_history: Previous messages for context

        Returns:
            Tuple of (response_text, sources_list)
        """
        if not self.agnes:
            return I18nService.t("errors.api_unavailable", language), []

        # Get relevant context from knowledge base
        context = KnowledgeService.get_context_for_query(
            query=user_message,
            language=language,
            max_chunks=3,
            max_context_length=2500,
        )

        # Build system prompt
        system_prompt = self.SYSTEM_PROMPTS.get(mode, self.SYSTEM_PROMPTS["chat"]).format(
            language=I18nService.get_language_name(language)
        )

        if context:
            system_prompt += f"\n\n--- زمینه دانش ---\n{context}\n--- پایان زمینه ---"

        # Build conversation
        messages = [{"role": "system", "content": system_prompt}]

        if conversation_history:
            for msg in conversation_history[-6:]:  # Last 6 messages
                messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({"role": "user", "content": user_message})

        # Call chat completion
        try:
            response = await self.agnes.chat_completion(messages, temperature=0.7)
            if not response:
                return I18nService.t("chat.no_answer", language), []

            # Extract sources from context
            sources = self._extract_sources_from_context(context)

            return response, sources

        except Exception as e:
            logger.error("RAG chat error: %s", e)
            return I18nService.t("errors.api_unavailable", language), []

    def _extract_sources_from_context(self, context: str) -> List[Dict[str, Any]]:
        """Extract source references from context string."""
        sources = []
        if not context:
            return sources

        # Parse [Source N: title] patterns
        import re
        pattern = r"\[Source (\d+): ([^\]]+)\]"
        for match in re.finditer(pattern, context):
            sources.append({
                "index": int(match.group(1)),
                "title": match.group(2).strip(),
            })
        return sources

    # ── Academic Advising ──

    async def academic_advice(
        self,
        student_profile: Dict[str, Any],
        language: str = "fa",
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Provide academic advising based on student profile.

        Args:
            student_profile: Dict with keys:
                - interests: List[str]
                - skills: List[str]
                - education_level: str
                - goals: str
                - preferred_fields: List[str]
            language: Response language

        Returns:
            Tuple of (advice_text, sources)
        """
        # Search for relevant programs and courses
        query_parts = []
        if student_profile.get("interests"):
            query_parts.extend(student_profile["interests"])
        if student_profile.get("preferred_fields"):
            query_parts.extend(student_profile["preferred_fields"])

        query = " ".join(query_parts) if query_parts else "دوره‌های آموزشی مهارت‌ها"
        context = KnowledgeService.get_context_for_query(query, language, max_chunks=5)

        system_prompt = f"""شما مشاور تحصیلی ارشد دانشگاه ملی مهارت مازندران هستید.
پروفایل دانشجو:
- علایق: {', '.join(student_profile.get('interests', []))}
- مهارت‌های فعلی: {', '.join(student_profile.get('skills', []))}
- سطح تحصیلات: {student_profile.get('education_level', 'نامشخص')}
- اهداف: {student_profile.get('goals', 'نامشخص')}
- رشته‌های ترجیحی: {', '.join(student_profile.get('preferred_fields', []))}

بر اساس اطلاعات زیر، برنامه تحصیلی شخصی‌سازی شده، پیشنهاد دوره‌ها، و مسیر پیشرفت ارائه دهید.
پاسخ به زبان {I18nService.get_language_name(language)} دهید."""

        if context:
            system_prompt += f"\n\n--- اطلاعات دوره‌ها و مهارت‌ها ---\n{context}\n--- پایان اطلاعات ---"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "راهنمایی تحصیلی کامل برای من تدوین کنید."}
        ]

        try:
            response = await self.agnes.chat_completion(messages, temperature=0.7)
            sources = self._extract_sources_from_context(context)
            return response or I18nService.t("chat.no_answer", language), sources
        except Exception as e:
            logger.error("Academic advice error: %s", e)
            return I18nService.t("errors.api_unavailable", language), []

    # ── Career Guidance ──

    async def career_guidance(
        self,
        user_profile: Dict[str, Any],
        language: str = "fa",
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Provide career guidance based on user profile.

        Args:
            user_profile: Dict with keys:
                - interests: List[str]
                - skills: List[str]
                - experience: str
                - education: str
                - preferred_industries: List[str]
                - location_preference: str
            language: Response language
        """
        query_parts = []
        if user_profile.get("interests"):
            query_parts.extend(user_profile["interests"])
        if user_profile.get("preferred_industries"):
            query_parts.extend(user_profile["preferred_industries"])

        query = " ".join(query_parts) if query_parts else "بازار کار مهارت‌ها شغل"
        context = KnowledgeService.get_context_for_query(query, language, max_chunks=5, category="career")

        system_prompt = f"""شما مشاور کار و مهارت‌های شغلی دانشگاه ملی مهارت مازندران هستید.
پروفایل متقاضی:
- علایق: {', '.join(user_profile.get('interests', []))}
- مهارت‌ها: {', '.join(user_profile.get('skills', []))}
- تجربه کاری: {user_profile.get('experience', 'نامشخص')}
- تحصیلات: {user_profile.get('education', 'نامشخص')}
- صنایع ترجیحی: {', '.join(user_profile.get('preferred_industries', []))}
- ترجیح مکان: {user_profile.get('location_preference', 'نامشخص')}

بر اساس بازار کار و اطلاعات زیر، مسیرهای شغلی، مهارت‌های مورد نیاز، و نقشه‌راه یادگیری پیشنهاد دهید.
پاسخ به زبان {I18nService.get_language_name(language)} دهید."""

        if context:
            system_prompt += f"\n\n--- اطلاعات بازار کار و مهارت‌ها ---\n{context}\n--- پایان اطلاعات ---"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "مسیر شغلی و مهارت‌های مورد نیاز برای من را پیشنهاد دهید."}
        ]

        try:
            response = await self.agnes.chat_completion(messages, temperature=0.7)
            sources = self._extract_sources_from_context(context)
            return response or I18nService.t("chat.no_answer", language), sources
        except Exception as e:
            logger.error("Career guidance error: %s", e)
            return I18nService.t("errors.api_unavailable", language), []

    # ── Skill/Course Recommendation ──

    async def recommend_skills(
        self,
        query: str,
        language: str = "fa",
        category: Optional[str] = None,
        level: Optional[str] = None,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Recommend skills/courses based on query.

        Args:
            query: What the user wants to learn
            language: Response language
            category: Skill category filter
            level: Difficulty level filter
        """
        context = KnowledgeService.get_context_for_query(
            query=query,
            language=language,
            max_chunks=5,
            max_context_length=3000,
        )

        filters = []
        if category:
            filters.append(f"دسته‌بندی: {category}")
        if level:
            filters.append(f"سطح: {level}")

        filter_str = " | ".join(filters) if filters else "بدون فیلتر"

        system_prompt = f"""شما مشاور مهارت‌ها و دوره‌های آموزشی دانشگاه ملی مهارت مازندران هستید.
درخواست کاربر: {query}
فیلترها: {filter_str}

بر اساس اطلاعات زیر، دوره‌های مناسب، پیش‌نیازها، مدت زمان، هزینه و گواهینامه‌ها را به صورت ساختاریافته پیشنهاد دهید.
پاسخ به زبان {I18nService.get_language_name(language)} دهید."""

        if context:
            system_prompt += f"\n\n--- اطلاعات دوره‌ها و مهارت‌ها ---\n{context}\n--- پایان اطلاعات ---"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "دوره‌های مناسب برای من را پیشنهاد دهید."}
        ]

        try:
            response = await self.agnes.chat_completion(messages, temperature=0.7)
            sources = self._extract_sources_from_context(context)
            return response or I18nService.t("chat.no_answer", language), sources
        except Exception as e:
            logger.error("Skill recommendation error: %s", e)
            return I18nService.t("errors.api_unavailable", language), []

    # ── Admissions Info ──

    async def admissions_info(
        self,
        query: str,
        language: str = "fa",
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Provide admissions information."""
        context = KnowledgeService.get_context_for_query(
            query=query,
            language=language,
            max_chunks=5,
            category="admission",
        )

        system_prompt = f"""شما مشاور پذیرش دانشگاه ملی مهارت مازندران هستید.
سوال: {query}

اطلاعات دقیق درباره شرایط ثبت‌نام، مدارک، مهلت‌ها، هزینه‌ها و مراحل پذیرش ارائه دهید.
پاسخ به زبان {I18nService.get_language_name(language)} دهید."""

        if context:
            system_prompt += f"\n\n--- اطلاعات پذیرش ---\n{context}\n--- پایان اطلاعات ---"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]

        try:
            response = await self.agnes.chat_completion(messages, temperature=0.5)
            sources = self._extract_sources_from_context(context)
            return response or I18nService.t("chat.no_answer", language), sources
        except Exception as e:
            logger.error("Admissions info error: %s", e)
            return I18nService.t("errors.api_unavailable", language), []

    # ── Announcements Summary ──

    async def summarize_announcements(
        self,
        language: str = "fa",
        limit: int = 5,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Summarize recent announcements."""
        # Get recent announcements from knowledge base
        results = KnowledgeService.search(
            query="",
            language=language,
            category="announcements",
            limit=limit,
        )

        if not results:
            return I18nService.t("announcements.title", language) + "\n\nهیچ اطلاعیه‌ای یافت نشد.", []

        # Build context from announcements
        context_parts = []
        for i, r in enumerate(results):
            content = r.get("content", "")[:500]
            title = r.get("source_title") or "اطلاعیه"
            context_parts.append(f"[اطلاعیه {i+1}: {title}]\n{content}")

        context = "\n\n".join(context_parts)

        system_prompt = f"""شما خبرنگار دانشگاه ملی مهارت مازندران هستید.
خلاصه‌ای از اطلاعیه‌های اخیر به صورت جذاب و منظم تهیه کنید.
برای هر اطلاعیه: عنوان، تاریخ (اگر موجود)، و نکات کلیدی را ذکر کنید.
پاسخ به زبان {I18nService.get_language_name(language)} دهید."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"خلاصه اطلاعیه‌ها:\n\n{context}"}
        ]

        try:
            response = await self.agnes.chat_completion(messages, temperature=0.5)
            sources = [{"index": i+1, "title": r.get("source_title", f"اطلاعیه {i+1}")} for i, r in enumerate(results)]
            return response or "خطا در خلاصه‌سازی", sources
        except Exception as e:
            logger.error("Announcements summary error: %s", e)
            return I18nService.t("errors.api_unavailable", language), []

    @staticmethod
    async def health_check() -> Tuple[bool, str]:
        return await AgnesClient.health_check()


if __name__ == "__main__":
    # Self-test
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    logging.basicConfig(level=logging.INFO)

    print("AIService structure verified")
    print("Methods available:")
    for method in dir(AIService):
        if not method.startswith("_"):
            print(f"  - {method}")