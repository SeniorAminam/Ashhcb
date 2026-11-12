# Project: Ashhcb Bot - Mazandaran Skills University AI Assistant
# File Path: src/services/web_scraper_service.py
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
# Purpose: Web scraping service for university website, Eitaa channels, announcements
# License: MIT
# Copyright: (c) Amin Davodian

"""
Web Scraper Service for automated data collection.

Scrapes:
- University website (announcements, courses, admissions)
- Eitaa channels (via public web views)
- RSS feeds
- General web search via DuckDuckGo

Uses selectolax for fast HTML parsing, httpx for async HTTP.
"""

import asyncio
import hashlib
import json
import logging
import re
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse

import httpx
from selectolax.lexbor import LexborHTMLParser as HTMLParser

from src.services.storage import UserStorage
from src.services.knowledge_service import KnowledgeService
from src.services.i18n_service import I18nService

logger = logging.getLogger(__name__)

# Default configuration for known sources
DEFAULT_SCRAPER_CONFIGS = {
    "university_website": {
        "name": "university_website",
        "base_url": "https://msu.ac.ir",  # Mazandaran Skills University - update as needed
        "list_url": "https://msu.ac.ir/fa/news",
        "list_selector": ".news-list .item, .news-item, article",
        "title_selector": "h3 a, h2 a, .title a, a",
        "link_selector": "a",
        "content_selector": ".news-content, .article-content, .post-content, article",
        "date_selector": ".date, .published, time",
        "pagination": "?page={page}",
        "max_pages": 5,
        "language": "fa",
        "category": "announcements",
        "schedule_cron": "0 */6 * * *",  # Every 6 hours
    },
    "university_admissions": {
        "name": "university_admissions",
        "base_url": "https://msu.ac.ir",
        "list_url": "https://msu.ac.ir/fa/admissions",
        "list_selector": ".admission-item, .card, .item",
        "title_selector": "h3, h4, .title",
        "link_selector": "a",
        "content_selector": ".content, .description, .details",
        "language": "fa",
        "category": "admission",
        "schedule_cron": "0 2 * * *",  # Daily at 2 AM
    },
    "university_courses": {
        "name": "university_courses",
        "base_url": "https://msu.ac.ir",
        "list_url": "https://msu.ac.ir/fa/courses",
        "list_selector": ".course-item, .program-item, .card",
        "title_selector": "h3, h4, .title",
        "link_selector": "a",
        "content_selector": ".content, .description, .curriculum",
        "language": "fa",
        "category": "courses",
        "schedule_cron": "0 3 * * 0",  # Weekly Sunday 3 AM
    },
    "eitaa_channel": {
        "name": "eitaa_channel",
        "base_url": "https://eitaa.com",
        # Note: Eitaa channels may need specific handling - public channels have web views
        "list_url": "https://eitaa.com/@channel_username",  # Replace with actual channel
        "list_selector": ".message, .bubble, .post",
        "title_selector": ".message-text, .text, .content",
        "content_selector": ".message-text, .text, .content",
        "date_selector": ".time, .date",
        "language": "fa",
        "category": "announcements",
        "schedule_cron": "*/30 * * * *",  # Every 30 minutes
        "requires_auth": False,  # Public channel only
    },
}


class WebScraperService:
    """Async web scraper service with knowledge base integration."""

    def __init__(
        self,
        timeout: float = 30.0,
        max_concurrent: int = 3,
        user_agent: str = "Mozilla/5.0 (compatible; MSU-Bot/1.0; +https://msu.ac.ir)",
    ):
        self.timeout = timeout
        self.max_concurrent = max_concurrent
        self.user_agent = user_agent
        self._client: Optional[httpx.AsyncClient] = None
        self._semaphore: Optional[asyncio.Semaphore] = None

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()

    async def start(self):
        """Initialize HTTP client and semaphore."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                headers={"User-Agent": self.user_agent},
                follow_redirects=True,
                limits=httpx.Limits(max_connections=self.max_concurrent, max_keepalive_connections=5),
            )
            self._semaphore = asyncio.Semaphore(self.max_concurrent)

    async def stop(self):
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
            self._semaphore = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("Scraper not started. Call start() or use async context manager.")
        return self._client

    async def fetch_page(self, url: str) -> Optional[str]:
        """Fetch a single page with retries."""
        client = self._get_client()
        for attempt in range(3):
            try:
                async with self._semaphore:
                    resp = await client.get(url)
                    resp.raise_for_status()
                    return resp.text
            except httpx.HTTPStatusError as e:
                if e.response.status_code >= 500 and attempt < 2:
                    await asyncio.sleep(2 ** attempt)
                    continue
                logger.warning("HTTP error fetching %s: %s", url, e)
                return None
            except Exception as e:
                logger.warning("Error fetching %s (attempt %d): %s", url, attempt + 1, e)
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)
                else:
                    return None
        return None

    def parse_list_page(self, html: str, config: Dict) -> List[Dict[str, str]]:
        """Parse list page to extract item URLs and basic info."""
        parser = HTMLParser(html)
        items = []

        list_selector = config.get("list_selector", ".item")
        title_selector = config.get("title_selector", "h3 a")
        link_selector = config.get("link_selector", "a")

        for node in parser.css(list_selector):
            try:
                # Get title
                title_node = node.css_first(title_selector)
                title = title_node.text(strip=True) if title_node else ""

                # Get link
                link_node = node.css_first(link_selector)
                link = link_node.attributes.get("href", "") if link_node else ""

                if link and not link.startswith("http"):
                    base_url = config.get("base_url", "")
                    link = urljoin(base_url, link)

                if title and link:
                    items.append({"title": title, "url": link})
            except Exception as e:
                logger.debug("Error parsing list item: %s", e)

        return items

    def parse_detail_page(self, html: str, config: Dict) -> Dict[str, str]:
        """Parse detail page to extract content."""
        parser = HTMLParser(html)

        content_selector = config.get("content_selector", "article, .content, main")
        date_selector = config.get("date_selector", "time, .date")

        # Remove unwanted elements
        for selector in ["script", "style", "nav", "header", "footer", ".ads", ".sidebar"]:
            for node in parser.css(selector):
                node.decompose()

        content_node = parser.css_first(content_selector)
        content = content_node.text(separator="\n", strip=True) if content_node else ""

        # Get date
        date_node = parser.css_first(date_selector)
        date_str = date_node.text(strip=True) if date_node else ""

        # Get title from page
        title_node = parser.css_first("h1, h2.title, .page-title")
        title = title_node.text(strip=True) if title_node else ""

        return {
            "content": content,
            "date": date_str,
            "title": title,
        }

    def compute_content_hash(self, content: str) -> str:
        """Compute hash for deduplication."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    async def scrape_job(self, config: Dict) -> Dict[str, Any]:
        """
        Run a complete scrape job based on config.

        Returns:
            Dict with stats: pages_fetched, new_chunks, errors
        """
        job_name = config["name"]
        logger.info("Starting scrape job: %s", job_name)

        stats = {
            "job_name": job_name,
            "pages_fetched": 0,
            "new_chunks": 0,
            "errors": 0,
            "started_at": datetime.now().isoformat(),
        }

        try:
            # Update job status to running
            UserStorage.update_scrape_job_run(job_name, "running")

            # Fetch list page(s)
            list_url = config.get("list_url")
            max_pages = config.get("max_pages", 1)
            pagination = config.get("pagination")

            all_items = []

            for page in range(1, max_pages + 1):
                if pagination and page > 1:
                    page_url = list_url.replace("{page}", str(page))
                else:
                    page_url = list_url

                html = await self.fetch_page(page_url)
                if not html:
                    stats["errors"] += 1
                    continue

                stats["pages_fetched"] += 1
                items = self.parse_list_page(html, config)
                all_items.extend(items)

                # Be polite
                await asyncio.sleep(0.5)

            logger.info("Found %d items in job %s", len(all_items), job_name)

            # Fetch detail pages
            semaphore = asyncio.Semaphore(self.max_concurrent)

            async def fetch_and_process(item: Dict[str, str]):
                async with semaphore:
                    detail_html = await self.fetch_page(item["url"])
                    if not detail_html:
                        return None

                    detail = self.parse_detail_page(detail_html, config)
                    detail["url"] = item["url"]
                    detail["list_title"] = item["title"]
                    return detail

            detail_tasks = [fetch_and_process(item) for item in all_items]
            details = await asyncio.gather(*detail_tasks, return_exceptions=True)

            # Process details and ingest to knowledge base
            language = config.get("language", "fa")
            category = config.get("category", "general")
            source_type = config.get("source_type", "web")

            for detail in details:
                if isinstance(detail, Exception) or detail is None:
                    stats["errors"] += 1
                    continue

                content = detail.get("content", "").strip()
                if not content or len(content) < 100:
                    continue

                # Check if already scraped (by URL)
                existing = UserStorage.get_scraped_page(detail["url"])
                content_hash = self.compute_content_hash(content)

                if existing and existing.get("content_hash") == content_hash:
                    continue  # No changes

                # Ingest to knowledge base
                title = detail.get("title") or detail.get("list_title") or "Untitled"
                chunk_ids = KnowledgeService.ingest_text(
                    content=content,
                    source_type=source_type,
                    language=language,
                    category=category,
                    source_url=detail["url"],
                    source_title=title,
                    tags=["scraped", job_name],
                )

                if chunk_ids:
                    stats["new_chunks"] += len(chunk_ids)

                    # Update scraped pages cache
                    UserStorage.add_scraped_page(
                        job_id=0,  # Would need job ID from upsert
                        url=detail["url"],
                        title=title,
                        content_hash=content_hash,
                        raw_html=detail_html if "detail_html" in locals() else "",
                        extracted_text=content,
                        language=language,
                    )

            # Update job status
            status = "success" if stats["errors"] == 0 else "partial"
            UserStorage.update_scrape_job_run(job_name, status)

        except Exception as e:
            logger.error("Scrape job %s failed: %s", job_name, e)
            UserStorage.update_scrape_job_run(job_name, "failed", str(e))
            stats["errors"] += 1

        stats["completed_at"] = datetime.now().isoformat()
        logger.info("Scrape job %s completed: %s", job_name, stats)
        return stats

    async def run_all_jobs(self, configs: Optional[List[Dict]] = None) -> List[Dict[str, Any]]:
        """Run all configured scrape jobs."""
        configs = configs or list(DEFAULT_SCRAPER_CONFIGS.values())
        results = []

        for config in configs:
            if config.get("requires_auth"):
                logger.warning("Skipping job %s: requires auth", config["name"])
                continue
            result = await self.scrape_job(config)
            results.append(result)

        return results


class DuckDuckGoSearcher:
    """Simple web search using DuckDuckGo HTML (no API key needed)."""

    def __init__(self, scraper: WebScraperService):
        self.scraper = scraper

    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Search DuckDuckGo and return result snippets.

        Returns list of {title, url, snippet}
        """
        # DuckDuckGo HTML endpoint
        url = f"https://html.duckduckgo.com/html/?q={httpx.QueryParams({'q': query})}"
        html = await self.scraper.fetch_page(url)
        if not html:
            return []

        parser = HTMLParser(html)
        results = []

        for result_node in parser.css(".result__body"):
            try:
                title_node = result_node.css_first(".result__title a")
                snippet_node = result_node.css_first(".result__snippet")
                url_node = result_node.css_first(".result__url")

                title = title_node.text(strip=True) if title_node else ""
                snippet = snippet_node.text(strip=True) if snippet_node else ""
                link = title_node.attributes.get("href", "") if title_node else ""

                if title and link:
                    results.append({"title": title, "url": link, "snippet": snippet})
                    if len(results) >= max_results:
                        break
            except Exception as e:
                logger.debug("Error parsing DDG result: %s", e)

        return results


async def run_scheduled_scrapers():
    """Entry point for APScheduler to run scrapers."""
    async with WebScraperService() as scraper:
        await scraper.run_all_jobs()


if __name__ == "__main__":
    # Self-test
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    async def test():
        logging.basicConfig(level=logging.INFO)
        async with WebScraperService() as scraper:
            # Test fetch
            html = await scraper.fetch_page("https://example.com")
            assert html is not None
            assert "Example Domain" in html
            print("Fetch test passed")

            # Test parsing
            items = scraper.parse_list_page(html, {"list_selector": "p", "link_selector": "a"})
            print(f"Parse test: {len(items)} items")

            # Test DDG search
            ddg = DuckDuckGoSearcher(scraper)
            results = await ddg.search("Mazandaran university skills")
            print(f"DDG search: {len(results)} results")

    asyncio.run(test())
    print("All self-tests passed!")