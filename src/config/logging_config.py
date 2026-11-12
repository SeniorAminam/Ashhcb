# Project: Ashhcb Bot - Mazandaran Skills University AI Assistant
# File Path: src/config/logging_config.py
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
# Purpose: Comprehensive file-based logging configuration
# License: MIT
# Copyright: (c) Amin Davodian

"""
Logging Configuration for MSU AI Assistant.

Provides:
- File-based logging to logs/ directory
- Rotating file handlers (size-based)
- Separate log files for different levels (debug, info, error)
- Structured JSON logging option
- Console output with colors
"""

import os
import sys
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Colored console formatter."""

    COLORS = {
        "DEBUG": "\033[36m",    # Cyan
        "INFO": "\033[32m",     # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",    # Red
        "CRITICAL": "\033[35m", # Magenta
        "RESET": "\033[0m",
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


def setup_logging(
    log_dir: str = "logs",
    level: str = "INFO",
    json_format: bool = False,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
) -> logging.Logger:
    """
    Setup comprehensive logging with file rotation.

    Args:
        log_dir: Directory for log files
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        json_format: Use JSON format for files
        max_bytes: Max size per log file before rotation
        backup_count: Number of backup files to keep

    Returns:
        Root logger configured with file and console handlers
    """
    # Create log directory
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Clear existing handlers
    root_logger.handlers.clear()

    # Timestamp for log files
    timestamp = datetime.now().strftime("%Y%m%d")

    # Format strings
    console_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_format = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
    json_format_str = '{"timestamp": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", "file": "%(filename)s", "line": %(lineno)d, "message": "%(message)s"}'

    # Console handler (with colors)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
    console_handler.setFormatter(ColoredFormatter(console_format, datefmt="%H:%M:%S"))
    root_logger.addHandler(console_handler)

    # Main rotating file handler (all levels)
    main_log = log_path / f"bot_{timestamp}.log"
    main_handler = logging.handlers.RotatingFileHandler(
        main_log,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    main_handler.setLevel(logging.DEBUG)
    main_handler.setFormatter(logging.Formatter(file_format, datefmt="%Y-%m-%d %H:%M:%S"))
    root_logger.addHandler(main_handler)

    # Error-only rotating file handler
    error_log = log_path / f"error_{timestamp}.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(file_format, datefmt="%Y-%m-%d %H:%M:%S"))
    root_logger.addHandler(error_handler)

    # Debug-only rotating file handler (verbose)
    debug_log = log_path / f"debug_{timestamp}.log"
    debug_handler = logging.handlers.RotatingFileHandler(
        debug_log,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(logging.Formatter(file_format, datefmt="%Y-%m-%d %H:%M:%S"))
    root_logger.addHandler(debug_handler)

    # Optional: Separate handler for AI service calls
    ai_log = log_path / f"ai_calls_{timestamp}.log"
    ai_handler = logging.handlers.RotatingFileHandler(
        ai_log,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    ai_handler.setLevel(logging.INFO)
    ai_handler.addFilter(lambda record: record.name.startswith("src.services.ai_service") or
                                      record.name.startswith("src.services.agnes_service"))
    ai_handler.setFormatter(logging.Formatter(file_format, datefmt="%Y-%m-%d %H:%M:%S"))
    root_logger.addHandler(ai_handler)

    # Optional: Separate handler for scraper
    scraper_log = log_path / f"scraper_{timestamp}.log"
    scraper_handler = logging.handlers.RotatingFileHandler(
        scraper_log,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    scraper_handler.setLevel(logging.INFO)
    scraper_handler.addFilter(lambda record: record.name.startswith("src.services.web_scraper_service"))
    scraper_handler.setFormatter(logging.Formatter(file_format, datefmt="%Y-%m-%d %H:%M:%S"))
    root_logger.addHandler(scraper_handler)

    # Suppress noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.INFO)
    logging.getLogger("apscheduler").setLevel(logging.INFO)

    root_logger.info(f"Logging initialized - dir: {log_path.absolute()}, level: {level}")
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get logger for module."""
    return logging.getLogger(name)


# Convenience: Quick setup for scripts
def quick_setup(level: str = "INFO") -> logging.Logger:
    """Quick logging setup for standalone scripts."""
    return setup_logging(log_dir="logs", level=level)


if __name__ == "__main__":
    # Test logging setup
    logger = setup_logging(level="DEBUG")

    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")

    # Test child loggers
    ai_logger = logging.getLogger("src.services.ai_service")
    ai_logger.info("AI service call test")

    scraper_logger = logging.getLogger("src.services.web_scraper_service")
    scraper_logger.info("Scraper test")

    print(f"\nLog files created in: {Path('logs').absolute()}")
    for f in Path("logs").glob("*.log"):
        print(f"  {f.name} ({f.stat().st_size} bytes)")