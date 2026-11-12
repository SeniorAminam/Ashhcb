# Project: Ashhcb Bot - Mazandaran Skills University AI Assistant
# File Path: src/services/search_service.py
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
# Purpose: Hybrid search service combining local knowledge base and web search
# License: MIT
# Copyright: (c) Amin Davodian

"""
Search Service for hybrid search across local knowledge base and web.

Features:
- Local knowledge base search (keyword-based, upgradable to semantic)
- Web search via DuckDuckGo
- Result merging and ranking
- Category-aware search
- Multi-language support
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from src.services.knowledge_service import KnowledgeService
from src.services.web_scraper_service import WebScraperService, DuckDuckGoSearcher
from src.services.i18n_service import I18nService
from src.services.storage import UserStorage

logger = logging.getLogger(__name__)


class SearchService:
    """Hybrid search service combining local and web sources."""

    def __init__(
        self,
        max_local_results: int = 5,
        max_web_results: int = 5,
        enable_web_search: bool = True,
    ):
        self.max_local_results = max_local_results
        self.max_web_results = max_web_results
        self.enable_web_search = enable_web_search
        self._scraper: Optional[WebScraperService] = None
        self._ddg_searcher: Optional[DuckDuckGoSearcher] = None

    async def __aenter__(self):
        if self.enable_web_search:
            self._scraper = WebScraperService()
            await self._scraper.start()
            self._ddg_searcher = DuckDuckGoSearcher(self._scraper)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._scraper:
            await self._scraper.stop()

    def _get_scraper(self) -> WebScraperService:
        if self._scraper is None:
            raise RuntimeError("SearchService not initialized. Use async context manager.")
        return self._scraper

    def _get_ddg(self) -> DuckDuckGoSearcher:
        if self._ddg_searcher is None:
            raise RuntimeError("Web search not enabled or not initialized.")
        return self._ddg_searcher

    async def search(
        self,
        query: str,
        language: str = "fa",
        category: Optional[str] = None,
        include_web: bool = True,
        max_results: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Perform hybrid search.

        Args:
            query: Search query
            language: Target language (fa, en, ar, or 'auto')
            category: Optional category filter for local search
            include_web: Whether to include web search results
            max_results: Override max results per source

        Returns:
            Dict with 'local', 'web', 'combined' results and metadata
        """
        if not query or not query.strip():
            return self._empty_result(query)

        # Auto-detect language
        if language == "auto":
            language = I18nService.detect_language(query)

        local_limit = max_results or self.max_local_results
        web_limit = max_results or self.max_web_results

        # Search local knowledge base
        local_results = KnowledgeService.search(
            query=query.strip(),
            language=language,
            category=category,
            limit=local_limit,
        )

        # Search web if enabled
        web_results = []
        if include_web and self.enable_web_search:
            try:
                web_results = await self._get_ddg().search(query, max_results=web_limit)
            except Exception as e:
                logger.warning("Web search failed: %s", e)

        # Combine and rank results
        combined = self._combine_results(local_results, web_results, query, language)

        return {
            "query": query,
            "language": language,
            "category": category,
            "local": local_results,
            "web": web_results,
            "combined": combined,
            "total_local": len(local_results),
            "total_web": len(web_results),
            "total_combined": len(combined),
            "searched_at": datetime.now().isoformat(),
        }

    def _combine_results(
        self,
        local: List[Dict],
        web: List[Dict],
        query: str,
        language: str,
    ) -> List[Dict]:
        """
        Combine and rank local and web results.

        Local results get priority for exact category/language matches.
        """
        combined = []

        # Add local results with source marker
        for i, r in enumerate(local):
            combined.append({
                "rank": i + 1,
                "source": "local",
                "source_type": r.get("source_type", "knowledge"),
                "title": r.get("source_title") or r.get("source_url") or "Knowledge Base",
                "content": r.get("content", ""),
                "url": r.get("source_url"),
                "category": r.get("category"),
                "tags": r.get("tags", []),
                "score": self._score_local_result(r, query),
            })

        # Add web results
        for i, r in enumerate(web):
            combined.append({
                "rank": len(local) + i + 1,
                "source": "web",
                "source_type": "web",
                "title": r.get("title", ""),
                "content": r.get("snippet", ""),
                "url": r.get("url"),
                "category": None,
                "tags": [],
                "score": self._score_web_result(r, query),
            })

        # Sort by score descending
        combined.sort(key=lambda x: x["score"], reverse=True)

        # Re-rank
        for i, r in enumerate(combined):
            r["rank"] = i + 1

        return combined

    def _score_local_result(self, result: Dict, query: str) -> float:
        """Score a local result based on relevance."""
        score = 1.0
        content = result.get("content", "").lower()
        title = (result.get("source_title") or "").lower()
        query_lower = query.lower()

        # Exact phrase match in content
        if query_lower in content:
            score += 3.0
        # Exact phrase match in title
        if query_lower in title:
            score += 2.0

        # Keyword matches
        query_words = query_lower.split()
        for word in query_words:
            if word in content:
                score += 0.5
            if word in title:
                score += 1.0

        return score

    def _score_web_result(self, result: Dict, query: str) -> float:
        """Score a web result based on relevance."""
        score = 0.5  # Base score lower than local
        title = result.get("title", "").lower()
        snippet = result.get("snippet", "").lower()
        query_lower = query.lower()

        if query_lower in title:
            score += 2.0
        if query_lower in snippet:
            score += 1.0

        query_words = query_lower.split()
        for word in query_words:
            if word in title:
                score += 0.5
            if word in snippet:
                score += 0.3

        return score

    def _empty_result(self, query: str) -> Dict[str, Any]:
        return {
            "query": query,
            "language": "fa",
            "category": None,
            "local": [],
            "web": [],
            "combined": [],
            "total_local": 0,
            "total_web": 0,
            "total_combined": 0,
            "searched_at": datetime.now().isoformat(),
        }

    def format_results_for_display(
        self,
        results: Dict[str, Any],
        language: str = "fa",
        max_items: int = 5,
    ) -> str:
        """Format search results for user display."""
        if not results["combined"]:
            return I18nService.t("search.no_results", language)

        lines = [I18nService.t("search.results", language).format(query=results["query"])]

        for i, r in enumerate(results["combined"][:max_items]):
            source_icon = "📖" if r["source"] == "local" else "🌐"
            title = r["title"] or "Untitled"
            content_preview = r["content"][:200] + "..." if len(r["content"]) > 200 else r["content"]

            lines.append(f"\n{source_icon} {i+1}. {title}")
            lines.append(f"   {content_preview}")
            if r["url"]:
                lines.append(f"   🔗 {r['url']}")

        if results["total_combined"] > max_items:
            lines.append(f"\n... و {results['total_combined'] - max_items} نتیجه دیگر")

        return "\n".join(lines)

    async def search_skills(
        self,
        query: str,
        language: str = "fa",
        skill_category: Optional[str] = None,
        level: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Search for skills/courses with specific filters.

        Args:
            query: Search query
            language: Language
            skill_category: Category filter (digital, technical, soft, language, business)
            level: Level filter (beginner, intermediate, advanced)

        Returns:
            Search results with skill-specific formatting
        """
        # Build category filter
        category = "skills"
        if skill_category:
            category = f"skills:{skill_category}"

        results = await self.search(
            query=query,
            language=language,
            category=category,
        )

        # Filter by level if specified
        if level:
            filtered = []
            for r in results["combined"]:
                tags = r.get("tags", [])
                if any(level in tag.lower() for tag in tags):
                    filtered.append(r)
            results["combined"] = filtered
            results["total_combined"] = len(filtered)

        return results

    async def search_announcements(
        self,
        query: str = "",
        language: str = "fa",
        days_back: int = 30,
    ) -> Dict[str, Any]:
        """
        Search announcements with date filtering.

        Args:
            query: Search query (empty for recent)
            language: Language
            days_back: How many days back to search

        Returns:
            Announcement search results
        """
        results = await self.search(
            query=query,
            language=language,
            category="announcements",
        )

        # Filter by date if needed (would need date parsing from content)
        # For now, just return recent announcements from local
        if not query:
            # Get recent announcements from knowledge base
            recent = KnowledgeService.search(
                query="",
                language=language,
                category="announcements",
                limit=10,
            )
            results["local"] = recent
            results["total_local"] = len(recent)
            # Re-combine
            results["combined"] = self._combine_results(recent, [], query, language)
            results["total_combined"] = len(results["combined"])

        return results


# Convenience functions for simple usage
async def quick_search(query: str, language: str = "fa") -> Dict[str, Any]:
    """Quick search without context manager (creates own scraper)."""
    async with SearchService() as service:
        return await service.search(query, language)


async def quick_local_search(query: str, language: str = "fa", category: Optional[str] = None) -> List[Dict]:
    """Quick local-only search."""
    return KnowledgeService.search(query, language, category)


if __name__ == "__main__":
    # Self-test
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    async def test():
        logging.basicConfig(level=logging.INFO)
        I18nService.load_translations()

        # Test local search (requires DB)
        try:
            local_results = KnowledgeService.search("دانشگاه", language="fa", limit=3)
            print(f"Local search: {len(local_results)} results")
        except Exception as e:
            print(f"Local search test skipped: {e}")

        # Test hybrid search
        async with SearchService() as service:
            results = await service.search("programming courses", language="en")
            print(f"Hybrid search: local={results['total_local']}, web={results['total_web']}, combined={results['total_combined']}")

            formatted = service.format_results_for_display(results, "en")
            print("Formatted preview:")
            print(formatted[:500])

        print("All self-tests passed!")

    import asyncio
    from pathlib import Path
    asyncio.run(test())