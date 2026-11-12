# Project: Ashhcb Bot - Image to Trend Transform
# File Path: src/services/storage.py
# Author: Amin Davodian
# Full Name: Mohammadamin Davodian
# Website: https://senioramin.com
# GitHub: https://github.com/SeniorAminam
# LinkedIn: https://linkedin.com/in/SudoAmin
# Developer: @SeniorAminBot
# Brand: SeniorAmin
# Created Date: 2026-06-21
# Modified Date: 2026-06-21
# Version: 1.0.0
# Purpose: SQLite storage for users, history, and token tracking
# License: MIT
# Copyright: (c) Amin Davodian

import sqlite3
import os
import logging
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
DB_PATH = os.path.join(DB_DIR, "ashhc.db")


def get_db() -> sqlite3.Connection:
    """Get a database connection with row factory."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db() -> None:
    """Initialize database tables and run migrations for existing DBs."""
    conn = get_db()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                join_date TEXT NOT NULL,
                last_active TEXT NOT NULL,
                total_transforms INTEGER DEFAULT 0,
                is_admin INTEGER DEFAULT 0,
                is_banned INTEGER DEFAULT 0,
                language TEXT DEFAULT 'fa'
            );

            CREATE TABLE IF NOT EXISTS transforms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                style_key TEXT NOT NULL,
                style_label TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                image_size INTEGER DEFAULT 0,
                model_used TEXT DEFAULT '',
                ai_provider TEXT DEFAULT '',
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );

            CREATE TABLE IF NOT EXISTS ai_daily_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                total_transforms INTEGER DEFAULT 0,
                total_bytes_processed INTEGER DEFAULT 0,
                models_used TEXT DEFAULT '',
                UNIQUE(date)
            );

            -- Knowledge base for RAG
            CREATE TABLE IF NOT EXISTS knowledge_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_type TEXT NOT NULL,        -- 'web', 'file', 'manual', 'eitaa'
                source_url TEXT,                  -- original URL if web
                source_title TEXT,
                language TEXT NOT NULL DEFAULT 'fa',  -- 'fa', 'en', 'ar'
                category TEXT,                    -- 'admission', 'courses', 'announcements', 'skills', 'regulations', 'career'
                tags TEXT,                        -- JSON array
                content TEXT NOT NULL,            -- chunk text
                content_hash TEXT UNIQUE,         -- dedup
                embedding BLOB,                   -- vector embedding (optional, for semantic search)
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            -- Scraping job tracking
            CREATE TABLE IF NOT EXISTS scrape_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                url_pattern TEXT,
                selector_config TEXT,             -- JSON: CSS/XPath selectors
                schedule_cron TEXT,               -- e.g., "0 */6 * * *"
                last_run_at TEXT,
                last_status TEXT,                 -- 'success', 'failed', 'partial'
                last_error TEXT,
                is_active INTEGER DEFAULT 1
            );

            -- Scraped pages cache
            CREATE TABLE IF NOT EXISTS scraped_pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER REFERENCES scrape_jobs(id),
                url TEXT UNIQUE NOT NULL,
                title TEXT,
                content_hash TEXT,
                raw_html TEXT,
                extracted_text TEXT,
                language TEXT,
                fetched_at TEXT NOT NULL
            );
        """)
        conn.commit()

        # ── Migration: Add columns that may be missing from older databases ──
        migrations = [
            ("transforms", "model_used", "TEXT DEFAULT ''"),
            ("transforms", "ai_provider", "TEXT DEFAULT ''"),
            ("ai_daily_usage", "total_bytes_processed", "INTEGER DEFAULT 0"),
            ("users", "language", "TEXT DEFAULT 'fa'"),
        ]
        for table, column, col_def in migrations:
            try:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_def}")
                logger.info("Migration: Added column '%s' to table '%s'", column, table)
            except sqlite3.OperationalError as e:
                # Column already exists — this is fine
                if "duplicate column" not in str(e).lower():
                    logger.warning("Migration note for %s.%s: %s", table, column, str(e))

        conn.commit()
        logger.info("Database initialized at %s", DB_PATH)
    except Exception as e:
        logger.error("Failed to initialize database: %s", str(e))
        raise
    finally:
        conn.close()


class UserStorage:
    """Manage user data in SQLite."""

    @staticmethod
    def get_or_create_user(
        user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get existing user or create a new one."""
        conn = get_db()
        try:
            cursor = conn.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            )
            user = cursor.fetchone()

            now = datetime.now().isoformat()

            if user:
                # Update last active and username
                conn.execute(
                    "UPDATE users SET last_active = ?, username = ?, first_name = ? WHERE user_id = ?",
                    (now, username or "", first_name or "", user_id),
                )
                conn.commit()
                return dict(user)
            else:
                # Create new user
                conn.execute(
                    "INSERT INTO users (user_id, username, first_name, join_date, last_active) VALUES (?, ?, ?, ?, ?)",
                    (user_id, username or "", first_name or "", now, now),
                )
                conn.commit()
                cursor = conn.execute(
                    "SELECT * FROM users WHERE user_id = ?", (user_id,)
                )
                return dict(cursor.fetchone())
        finally:
            conn.close()

    @staticmethod
    def record_transform(
        user_id: int,
        style_key: str,
        style_label: str,
        image_size: int = 0,
        model_used: str = '',
        ai_provider: str = '',
    ) -> None:
        """Record a transform operation with AI model info."""
        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO transforms (user_id, style_key, style_label, timestamp, image_size, model_used, ai_provider) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (user_id, style_key, style_label, datetime.now().isoformat(), image_size, model_used, ai_provider),
            )
            conn.execute(
                "UPDATE users SET total_transforms = total_transforms + 1, last_active = ? WHERE user_id = ?",
                (datetime.now().isoformat(), user_id),
            )

            # Update daily AI usage
            today = datetime.now().strftime("%Y-%m-%d")
            conn.execute(
                """INSERT INTO ai_daily_usage (date, total_transforms, total_bytes_processed, models_used)
                   VALUES (?, 1, ?, ?)
                   ON CONFLICT(date) DO UPDATE SET
                       total_transforms = total_transforms + 1,
                       total_bytes_processed = total_bytes_processed + ?,
                       models_used = CASE
                           WHEN models_used = '' THEN ?
                           WHEN instr(models_used, ?) > 0 THEN models_used
                           ELSE models_used || ', ' || ?
                       END""",
                (today, image_size, model_used, image_size, model_used, model_used, model_used),
            )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def get_user_history(user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Get user's transform history."""
        conn = get_db()
        try:
            cursor = conn.execute(
                "SELECT * FROM transforms WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
                (user_id, limit),
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def get_user_stats(user_id: int) -> Dict[str, Any]:
        """Get user statistics."""
        conn = get_db()
        try:
            user = conn.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            ).fetchone()

            if not user:
                return {}

            # Count by style
            style_counts = conn.execute(
                "SELECT style_label, COUNT(*) as count FROM transforms WHERE user_id = ? GROUP BY style_label ORDER BY count DESC",
                (user_id,),
            ).fetchall()

            # Total transforms today
            today = datetime.now().strftime("%Y-%m-%d")
            today_count = conn.execute(
                "SELECT COUNT(*) as count FROM transforms WHERE user_id = ? AND timestamp LIKE ?",
                (user_id, f"{today}%"),
            ).fetchone()

            return {
                "user": dict(user),
                "style_counts": [dict(row) for row in style_counts],
                "today_count": dict(today_count)["count"],
            }
        finally:
            conn.close()

    @staticmethod
    def get_all_users() -> List[Dict[str, Any]]:
        """Get all users (for admin panel)."""
        conn = get_db()
        try:
            cursor = conn.execute(
                "SELECT * FROM users ORDER BY last_active DESC"
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def get_ai_model_counts(user_id: int) -> List[Dict[str, Any]]:
        """Get AI model usage breakdown for a specific user."""
        conn = get_db()
        try:
            cursor = conn.execute(
                "SELECT model_used, ai_provider, COUNT(*) as count FROM transforms "
                "WHERE user_id = ? AND model_used != '' "
                "GROUP BY model_used ORDER BY count DESC",
                (user_id,),
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def get_ai_model_counts_global() -> List[Dict[str, Any]]:
        """Get global AI model usage breakdown."""
        conn = get_db()
        try:
            cursor = conn.execute(
                "SELECT model_used, ai_provider, COUNT(*) as count FROM transforms "
                "WHERE model_used != '' "
                "GROUP BY model_used ORDER BY count DESC"
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def get_ai_usage_today() -> Optional[Dict[str, Any]]:
        """Get today's AI usage summary from ai_daily_usage table."""
        conn = get_db()
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            row = conn.execute(
                "SELECT * FROM ai_daily_usage WHERE date = ?", (today,)
            ).fetchone()
            if row:
                return dict(row)
            return None
        finally:
            conn.close()

    @staticmethod
    def get_total_stats() -> Dict[str, Any]:
        """Get overall bot statistics (for admin panel)."""
        conn = get_db()
        try:
            total_users = conn.execute(
                "SELECT COUNT(*) as count FROM users"
            ).fetchone()

            total_transforms = conn.execute(
                "SELECT COUNT(*) as count FROM transforms"
            ).fetchone()

            today = datetime.now().strftime("%Y-%m-%d")
            today_transforms = conn.execute(
                "SELECT COUNT(*) as count FROM transforms WHERE timestamp LIKE ?",
                (f"{today}%",),
            ).fetchone()

            # Top users
            top_users = conn.execute(
                "SELECT user_id, first_name, total_transforms FROM users ORDER BY total_transforms DESC LIMIT 5"
            ).fetchall()

            # Style popularity
            style_pop = conn.execute(
                "SELECT style_label, COUNT(*) as count FROM transforms GROUP BY style_label ORDER BY count DESC"
            ).fetchall()

            return {
                "total_users": dict(total_users)["count"],
                "total_transforms": dict(total_transforms)["count"],
                "today_transforms": dict(today_transforms)["count"],
                "top_users": [dict(row) for row in top_users],
                "style_popularity": [dict(row) for row in style_pop],
            }
        finally:
            conn.close()

    # ── Language preference ──
    @staticmethod
    def set_user_language(user_id: int, language: str) -> None:
        """Set user's preferred language."""
        conn = get_db()
        try:
            conn.execute(
                "UPDATE users SET language = ? WHERE user_id = ?",
                (language, user_id),
            )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def get_user_language(user_id: int) -> str:
        """Get user's preferred language, default 'fa'."""
        conn = get_db()
        try:
            row = conn.execute(
                "SELECT language FROM users WHERE user_id = ?", (user_id,)
            ).fetchone()
            return row["language"] if row and row["language"] else "fa"
        finally:
            conn.close()

    # ── Knowledge base (RAG) ──
    @staticmethod
    def add_knowledge_chunk(
        source_type: str,
        source_url: Optional[str],
        source_title: Optional[str],
        language: str,
        category: Optional[str],
        tags: List[str],
        content: str,
        content_hash: str,
    ) -> Optional[int]:
        """Add a knowledge chunk. Returns chunk ID or None if duplicate."""
        conn = get_db()
        try:
            now = datetime.now().isoformat()
            cursor = conn.execute(
                """INSERT OR IGNORE INTO knowledge_chunks
                   (source_type, source_url, source_title, language, category, tags, content, content_hash, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    source_type,
                    source_url or "",
                    source_title or "",
                    language,
                    category or "",
                    json.dumps(tags, ensure_ascii=False),
                    content,
                    content_hash,
                    now,
                    now,
                ),
            )
            conn.commit()
            if cursor.rowcount > 0:
                return cursor.lastrowid
            return None
        finally:
            conn.close()

    @staticmethod
    def search_knowledge(
        query: str,
        language: str,
        category: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Search knowledge chunks by keyword match (simple BM25-like)."""
        conn = get_db()
        try:
            # Simple keyword search using LIKE - can be upgraded to FTS5 later
            keywords = query.lower().split()
            if not keywords:
                return []

            conditions = ["language = ?"]
            params = [language]
            for kw in keywords:
                conditions.append("LOWER(content) LIKE ?")
                params.append(f"%{kw}%")
            if category:
                conditions.append("category = ?")
                params.append(category)

            where_clause = " AND ".join(conditions)
            sql = f"""
                SELECT id, source_type, source_url, source_title, language, category, tags, content, content_hash, created_at
                FROM knowledge_chunks
                WHERE {where_clause}
                ORDER BY
                    (CASE
                        WHEN LOWER(content) LIKE ? THEN 3
                        WHEN LOWER(source_title) LIKE ? THEN 2
                        ELSE 1
                    END) DESC,
                    created_at DESC
                LIMIT ?
            """
            # Add priority params for exact matches
            priority_param = f"%{query.lower()}%"
            params.extend([priority_param, priority_param, limit])

            cursor = conn.execute(sql, params)
            results = []
            for row in cursor.fetchall():
                d = dict(row)
                d["tags"] = json.loads(d["tags"]) if d["tags"] else []
                results.append(d)
            return results
        finally:
            conn.close()

    # ── Scrape jobs ──
    @staticmethod
    def upsert_scrape_job(
        name: str,
        url_pattern: Optional[str] = None,
        selector_config: Optional[Dict] = None,
        schedule_cron: Optional[str] = None,
        is_active: int = 1,
    ) -> None:
        """Create or update a scrape job."""
        conn = get_db()
        try:
            now = datetime.now().isoformat()
            conn.execute(
                """INSERT INTO scrape_jobs (name, url_pattern, selector_config, schedule_cron, is_active, last_run_at, last_status, last_error)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(name) DO UPDATE SET
                       url_pattern = excluded.url_pattern,
                       selector_config = excluded.selector_config,
                       schedule_cron = excluded.schedule_cron,
                       is_active = excluded.is_active""",
                (
                    name,
                    url_pattern or "",
                    json.dumps(selector_config) if selector_config else "{}",
                    schedule_cron or "",
                    is_active,
                    "",
                    "",
                    "",
                ),
            )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def get_active_scrape_jobs() -> List[Dict[str, Any]]:
        """Get all active scrape jobs."""
        conn = get_db()
        try:
            cursor = conn.execute(
                "SELECT * FROM scrape_jobs WHERE is_active = 1"
            )
            results = []
            for row in cursor.fetchall():
                d = dict(row)
                d["selector_config"] = json.loads(d["selector_config"]) if d["selector_config"] else {}
                results.append(d)
            return results
        finally:
            conn.close()

    @staticmethod
    def update_scrape_job_run(
        name: str,
        status: str,
        error: Optional[str] = None,
    ) -> None:
        """Update scrape job last run info."""
        conn = get_db()
        try:
            now = datetime.now().isoformat()
            conn.execute(
                """UPDATE scrape_jobs SET last_run_at = ?, last_status = ?, last_error = ? WHERE name = ?""",
                (now, status, error or "", name),
            )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def add_scraped_page(
        job_id: int,
        url: str,
        title: Optional[str],
        content_hash: str,
        raw_html: str,
        extracted_text: str,
        language: str,
    ) -> bool:
        """Add or update a scraped page. Returns True if new/updated."""
        conn = get_db()
        try:
            now = datetime.now().isoformat()
            cursor = conn.execute(
                """INSERT INTO scraped_pages (job_id, url, title, content_hash, raw_html, extracted_text, language, fetched_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(url) DO UPDATE SET
                       title = excluded.title,
                       content_hash = excluded.content_hash,
                       raw_html = excluded.raw_html,
                       extracted_text = excluded.extracted_text,
                       language = excluded.language,
                       fetched_at = excluded.fetched_at""",
                (job_id, url, title or "", content_hash, raw_html, extracted_text, language, now),
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def get_scraped_page(url: str) -> Optional[Dict[str, Any]]:
        """Get scraped page by URL."""
        conn = get_db()
        try:
            row = conn.execute(
                "SELECT * FROM scraped_pages WHERE url = ?", (url,)
            ).fetchone()
            if row:
                return dict(row)
            return None
        finally:
            conn.close()
