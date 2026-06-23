# Project: Ashhcb Bot - Image to Trend Transform
# File Path: src/utils/helpers.py
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
# Purpose: Utility helper functions
# License: MIT
# Copyright: (c) Amin Davodian

import os
import io
import hashlib
from datetime import datetime
from typing import Optional

from PIL import Image


def get_file_extension(filename: str) -> str:
    """Extract file extension from filename."""
    return os.path.splitext(filename)[1].lower()


def is_supported_image_format(filename: str) -> bool:
    """Check if the file extension is a supported image format."""
    supported = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}
    return get_file_extension(filename) in supported


def generate_file_hash(data: bytes) -> str:
    """Generate SHA-256 hash of file data."""
    return hashlib.sha256(data).hexdigest()


def format_size(size_bytes: int) -> str:
    """Format file size into human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def resize_image_if_needed(
    image_bytes: bytes, max_size: tuple = (1024, 1024)
) -> bytes:
    """
    Resize image if it exceeds max dimensions while maintaining aspect ratio.

    Args:
        image_bytes: Input image bytes
        max_size: Maximum (width, height) tuple

    Returns:
        Resized image bytes
    """
    img = Image.open(io.BytesIO(image_bytes))
    img.thumbnail(max_size, Image.Resampling.LANCZOS)

    output = io.BytesIO()
    img.save(output, format="PNG")
    return output.getvalue()


def get_image_dimensions(image_bytes: bytes) -> Optional[tuple]:
    """
    Get image dimensions without loading full image into memory.

    Args:
        image_bytes: Image bytes

    Returns:
        (width, height) tuple or None
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        return img.size
    except Exception:
        return None
