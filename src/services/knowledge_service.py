# Project: Ashhcb Bot - Mazandaran Skills University AI Assistant
# File Path: src/services/knowledge_service.py
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
# Purpose: Knowledge service for RAG pipeline - ingestion, search, context retrieval
# License: MIT
# Copyright: (c) Amin Davodian

"""
Knowledge Service for RAG (Retrieval-Augmented Generation) pipeline.

Handles:
- Text/file ingestion with chunking
- Keyword-based search (upgradable to semantic/embeddings)
- Context retrieval for LLM queries
- Multi-language support (fa, en, ar)
"""

import os
import re
import json
import hashlib
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from src.services.storage import UserStorage, get_db
from src.services.i18n_service import I18nService, SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE, RTL_LANGUAGES

logger = logging.getLogger(__name__)

# Chunking configuration
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200
MIN_CHUNK_SIZE = 100

# Supported source types
SOURCE_TYPES = {"web", "file", "manual", "eitaa"}

# Categories for knowledge chunks
CATEGORIES = {
    "admission", "courses", "announcements", "skills", "regulations", "career"
}


class KnowledgeService:
    """Knowledge service for RAG pipeline."""

    @staticmethod
    def _compute_hash(content: str) -> str:
        """Compute SHA256 hash of content for deduplication."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @staticmethod
    def _split_into_chunks(
        text: str,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        overlap: int = DEFAULT_CHUNK_OVERLAP,
    ) -> List[str]:
        """
        Split text into overlapping chunks.

        Args:
            text: Input text to chunk
            chunk_size: Target size of each chunk (characters)
            overlap: Overlap between chunks (characters)

        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text.strip()] if text.strip() else []

        chunks = []
        start = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))

            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings within the last 200 chars
                search_start = max(start + chunk_size - 200, start)
                sentence_end = -1
                for i in range(end - 1, search_start - 1, -1):
                    if text[i] in ".!?।؟":
                        sentence_end = i + 1
                        break

                if sentence_end > start:
                    end = sentence_end

            chunk = text[start:end].strip()
            if len(chunk) >= MIN_CHUNK_SIZE:
                chunks.append(chunk)

            if end >= len(text):
                break

            start = end - overlap
            if start < 0:
                start = 0

        return chunks

    @classmethod
    def ingest_text(
        cls,
        content: str,
        source_type: str,
        language: str = "fa",
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        source_url: Optional[str] = None,
        source_title: Optional[str] = None,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        overlap: int = DEFAULT_CHUNK_OVERLAP,
    ) -> List[int]:
        """
        Ingest raw text into knowledge base with chunking.

        Args:
            content: Text content to ingest
            source_type: One of 'web', 'file', 'manual', 'eitaa'
            language: Language code (fa, en, ar)
            category: Category for the content
            tags: List of tags
            source_url: Original URL if from web
            source_title: Title of the source
            chunk_size: Chunk size in characters
            overlap: Overlap between chunks

        Returns:
            List of chunk IDs that were added
        """
        if source_type not in SOURCE_TYPES:
            raise ValueError(f"Invalid source_type: {source_type}. Must be one of {SOURCE_TYPES}")

        if language not in SUPPORTED_LANGUAGES:
            language = DEFAULT_LANGUAGE

        if category and category not in CATEGORIES:
            logger.warning("Unknown category: %s", category)

        tags = tags or []
        content_hash = cls._compute_hash(content)

        # Check if exact duplicate exists
        existing = UserStorage.search_knowledge(content_hash, language, limit=1)
        if existing and existing[0].get("content_hash") == content_hash:
            logger.info("Duplicate content detected, skipping ingestion")
            return []

        chunks = cls._split_into_chunks(content, chunk_size, overlap)
        chunk_ids = []

        for i, chunk in enumerate(chunks):
            chunk_hash = cls._compute_hash(chunk)
            chunk_tags = tags + [f"chunk:{i+1}/{len(chunks)}"]

            chunk_id = UserStorage.add_knowledge_chunk(
                source_type=source_type,
                source_url=source_url,
                source_title=source_title,
                language=language,
                category=category,
                tags=chunk_tags,
                content=chunk,
                content_hash=chunk_hash,
            )

            if chunk_id:
                chunk_ids.append(chunk_id)

        logger.info("Ingested %d chunks from text (source: %s)", len(chunk_ids), source_type)
        return chunk_ids

    @classmethod
    def ingest_file(
        cls,
        file_path: str,
        source_type: str = "file",
        language: str = "fa",
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        overlap: int = DEFAULT_CHUNK_OVERLAP,
    ) -> List[int]:
        """
        Ingest a text file into knowledge base.

        Args:
            file_path: Path to the file
            source_type: Source type (default 'file')
            language: Language code
            category: Category
            tags: Tags
            chunk_size: Chunk size
            overlap: Chunk overlap

        Returns:
            List of chunk IDs
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Read file with encoding detection
        content = ""
        for encoding in ["utf-8", "utf-8-sig", "cp1256", "latin-1"]:
            try:
                content = path.read_text(encoding=encoding)
                break
            except UnicodeDecodeError:
                continue

        if not content:
            raise ValueError(f"Could not decode file: {file_path}")

        source_title = path.name
        return cls.ingest_text(
            content=content,
            source_type=source_type,
            language=language,
            category=category,
            tags=tags,
            source_url=str(path.absolute()),
            source_title=source_title,
            chunk_size=chunk_size,
            overlap=overlap,
        )

    @classmethod
    def ingest_directory(
        cls,
        directory: str,
        language: str = "fa",
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        extensions: Optional[List[str]] = None,
    ) -> Dict[str, List[int]]:
        """
        Ingest all text files in a directory.

        Args:
            directory: Directory path
            language: Language code
            category: Category
            tags: Tags
            extensions: File extensions to process (default: .txt, .md, .json)

        Returns:
            Dict mapping file paths to list of chunk IDs
        """
        extensions = extensions or [".txt", ".md", ".json"]
        path = Path(directory)

        if not path.exists() or not path.is_dir():
            raise NotADirectoryError(f"Directory not found: {directory}")

        results = {}
        for ext in extensions:
            for file_path in path.rglob(f"*{ext}"):
                try:
                    chunk_ids = cls.ingest_file(
                        str(file_path),
                        language=language,
                        category=category,
                        tags=tags,
                    )
                    if chunk_ids:
                        results[str(file_path)] = chunk_ids
                except Exception as e:
                    logger.error("Failed to ingest %s: %s", file_path, e)

        return results

    @classmethod
    def search(
        cls,
        query: str,
        language: str = "fa",
        category: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Search knowledge base for relevant chunks.

        Args:
            query: Search query
            language: Target language
            category: Optional category filter
            limit: Maximum results

        Returns:
            List of matching chunks with metadata
        """
        if not query or not query.strip():
            return []

        # Detect language if not specified or auto
        if language == "auto":
            language = I18nService.detect_language(query)

        return UserStorage.search_knowledge(
            query=query.strip(),
            language=language,
            category=category,
            limit=limit,
        )

    @classmethod
    def get_context_for_query(
        cls,
        query: str,
        language: str = "fa",
        max_chunks: int = 3,
        max_context_length: int = 3000,
    ) -> str:
        """
        Get formatted context string for LLM from knowledge base.

        Args:
            query: User query
            language: Language for context
            max_chunks: Maximum chunks to include
            max_context_length: Maximum total context length

        Returns:
            Formatted context string
        """
        results = cls.search(query, language, limit=max_chunks)

        if not results:
            return ""

        context_parts = []
        total_length = 0

        for i, chunk in enumerate(results):
            content = chunk.get("content", "")
            source = chunk.get("source_title") or chunk.get("source_url") or "Unknown"

            part = f"[Source {i+1}: {source}]\n{content}\n"
            if total_length + len(part) > max_context_length:
                break

            context_parts.append(part)
            total_length += len(part)

        return "\n".join(context_parts)

    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        # This would need a new storage method; for now return basic info
        conn = get_db()
        try:
            # Total chunks by language
            lang_stats = conn.execute("""
                SELECT language, COUNT(*) as count
                FROM knowledge_chunks
                GROUP BY language
            """).fetchall()

            # Total chunks by category
            cat_stats = conn.execute("""
                SELECT category, COUNT(*) as count
                FROM knowledge_chunks
                GROUP BY category
            """).fetchall()

            # Total chunks by source type
            src_stats = conn.execute("""
                SELECT source_type, COUNT(*) as count
                FROM knowledge_chunks
                GROUP BY source_type
            """).fetchall()

            total = conn.execute("SELECT COUNT(*) as count FROM knowledge_chunks").fetchone()

            return {
                "total_chunks": dict(total)["count"],
                "by_language": [dict(r) for r in lang_stats],
                "by_category": [dict(r) for r in cat_stats],
                "by_source_type": [dict(r) for r in src_stats],
            }
        finally:
            conn.close()

    @classmethod
    def delete_chunks_by_source(cls, source_url: str) -> int:
        """Delete all chunks from a specific source URL."""
        conn = get_db()
        try:
            cursor = conn.execute(
                "DELETE FROM knowledge_chunks WHERE source_url = ?",
                (source_url,),
            )
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()

    @classmethod
    def delete_chunks_by_category(cls, category: str, language: Optional[str] = None) -> int:
        """Delete all chunks in a category."""
        conn = get_db()
        try:
            if language:
                cursor = conn.execute(
                    "DELETE FROM knowledge_chunks WHERE category = ? AND language = ?",
                    (category, language),
                )
            else:
                cursor = conn.execute(
                    "DELETE FROM knowledge_chunks WHERE category = ?",
                    (category,),
                )
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()


if __name__ == "__main__":
    # Self-test
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    logging.basicConfig(level=logging.INFO)
    I18nService.load_translations()

    # Test chunking
    test_text = "This is a test. " * 100  # ~1500 chars
    chunks = KnowledgeService._split_into_chunks(test_text, chunk_size=500, overlap=100)
    print(f"Chunking test: {len(test_text)} chars -> {len(chunks)} chunks")
    assert len(chunks) >= 2
    assert all(len(c) <= 500 for c in chunks)

    # Test hash
    h1 = KnowledgeService._compute_hash("test")
    h2 = KnowledgeService._compute_hash("test")
    h3 = KnowledgeService._compute_hash("different")
    assert h1 == h2
    assert h1 != h3
    print("Hash test passed")

    # Test search (requires DB)
    try:
        KnowledgeService.ingest_text(
            "جامعة مهارات مازندران تقدم دورات في البرمجة والذكاء الاصطناعي.",
            source_type="manual",
            language="ar",
            category="courses",
            source_title="Test Arabic Content",
        )
        results = KnowledgeService.search("برمجة", language="ar")
        print(f"Arabic search test: {len(results)} results")
    except Exception as e:
        print(f"Search test skipped (DB may not be initialized): {e}")

    print("All self-tests passed!")