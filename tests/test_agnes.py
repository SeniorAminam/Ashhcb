#!/usr/bin/env python3
# Project: Ashhcb Bot - Image to Trend Transform
# File Path: tests/test_agnes.py
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
# Purpose: Test Agnes AI API (txt2img + img2img)
# License: MIT
# Copyright: (c) Amin Davodian

"""
Agnes AI API Tester
====================
Tests both text-to-image and image-to-image via Agnes AI API.
OpenAI-compatible, free tier, no payment method required.

API key: https://agnes-ai.com (sign up, free tier)
Base URL: https://apihub.agnes-ai.com/v1
Models: agnes-image-2.0-flash, agnes-image-2.1-flash

Usage:
    set AGNES_API_KEY=sk-...
    python tests/test_agnes.py --mode txt2img
    python tests/test_agnes.py --mode img2img --image photo.jpg
    python tests/test_agnes.py --mode all
"""

import argparse
import base64
import io
import os
import sys
import time
from pathlib import Path
from typing import Optional

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("AGNES_API_KEY", "")
BASE_URL = "https://apihub.agnes-ai.com/v1"
TXT2IMG_MODEL = "agnes-image-2.0-flash"
IMG2IMG_MODEL = "agnes-image-2.0-flash"
VISION_MODEL = "agnes-2.0-flash"

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def banner(text: str):
    print(f"\n{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{text}{RESET}")
    print(f"{CYAN}{'='*60}{RESET}")


def ok(text: str):
    print(f"  {GREEN}OK{RESET} {text}")


def fail(text: str):
    print(f"  {RED}FAIL{RESET} {text}")


def warn(text: str):
    print(f"  {YELLOW}WARN{RESET} {text}")


def info(text: str):
    print(f"  {CYAN}INFO{RESET} {text}")


def generate_test_image(size: tuple = (512, 512)) -> bytes:
    from PIL import Image, ImageDraw
    img = Image.new("RGBA", size, color=(30, 30, 50, 255))
    draw = ImageDraw.Draw(img)
    draw.ellipse([100, 100, 400, 400], fill=(200, 100, 50, 255), outline=(255, 200, 100, 255))
    draw.rectangle([150, 200, 350, 300], fill=(50, 150, 200, 255))
    draw.ellipse([200, 150, 300, 250], fill=(255, 255, 100, 255))
    draw.text((50, 50), "TEST", fill=(255, 255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def download_image(url: str) -> Optional[bytes]:
    try:
        resp = httpx.get(url, timeout=60, follow_redirects=True)
        if resp.status_code == 200 and len(resp.content) > 500:
            return resp.content
        info(f"Download HTTP {resp.status_code}: {len(resp.content)} bytes")
    except Exception as e:
        warn(f"Download failed: {e}")
    return None


def test_txt2img(prompt: str) -> Optional[float]:
    banner("TXT2IMG: Agnes AI")
    info(f"Model: {TXT2IMG_MODEL}")
    info(f"Prompt: {prompt[:60]}...")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": TXT2IMG_MODEL,
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024",
    }

    t0 = time.time()
    try:
        resp = httpx.post(
            f"{BASE_URL}/images/generations",
            json=payload,
            headers=headers,
            timeout=120,
        )
        elapsed = time.time() - t0

        if resp.status_code != 200:
            fail(f"HTTP {resp.status_code}: {resp.text[:200]}")
            return None

        data = resp.json()
        images = data.get("data", [])
        if not images:
            fail("No images in response")
            info(f"Response: {str(data)[:200]}")
            return None

        url = images[0].get("url") or images[0].get("b64_json")
        elapsed = time.time() - t0

        if url and url.startswith("http"):
            img_bytes = download_image(url)
            if img_bytes:
                ok(f"{len(img_bytes)} bytes in {elapsed:.1f}s")
                Path("test_agnes_txt2img.jpg").write_bytes(img_bytes)
                info("Saved: test_agnes_txt2img.jpg")
                return elapsed
        elif url:
            img_bytes = base64.b64decode(url)
            ok(f"{len(img_bytes)} bytes (base64) in {elapsed:.1f}s")
            Path("test_agnes_txt2img.jpg").write_bytes(img_bytes)
            info("Saved: test_agnes_txt2img.jpg")
            return elapsed

        fail(f"No valid image URL/b64 in response ({elapsed:.1f}s)")
        info(f"Response keys: {list(data.keys())}")
    except Exception as e:
        fail(f"Request failed: {str(e)[:150]}")
    return None


def upload_to_temp_hosting(image_bytes: bytes) -> Optional[str]:
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
        warn(f"Temp upload failed: {e}")
    return None


def test_img2img(image_bytes: bytes, prompt: str) -> Optional[float]:
    banner("IMG2IMG: Agnes AI")
    info(f"Model: {IMG2IMG_MODEL}")
    info(f"Prompt: {prompt[:60]}...")

    image_url = upload_to_temp_hosting(image_bytes)
    if not image_url:
        fail("Could not upload image")
        return None
    info(f"Uploaded: {image_url[:60]}...")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": IMG2IMG_MODEL,
        "prompt": prompt,
        "image_url": image_url,
        "n": 1,
        "size": "1024x1024",
    }

    t0 = time.time()
    try:
        resp = httpx.post(
            f"{BASE_URL}/images/generations",
            json=payload,
            headers=headers,
            timeout=120,
        )
        elapsed = time.time() - t0

        if resp.status_code != 200:
            fail(f"HTTP {resp.status_code}: {resp.text[:200]}")
            return None

        data = resp.json()
        images = data.get("data", [])
        if not images:
            fail("No images in response")
            info(f"Response: {str(data)[:200]}")
            return None

        url = images[0].get("url") or images[0].get("b64_json")
        if url and url.startswith("http"):
            img_bytes = download_image(url)
            if img_bytes:
                ok(f"{len(img_bytes)} bytes in {elapsed:.1f}s")
                Path("test_agnes_img2img.jpg").write_bytes(img_bytes)
                info("Saved: test_agnes_img2img.jpg")
                return elapsed
        elif url:
            img_bytes = base64.b64decode(url)
            ok(f"{len(img_bytes)} bytes (base64) in {elapsed:.1f}s")
            Path("test_agnes_img2img.jpg").write_bytes(img_bytes)
            info("Saved: test_agnes_img2img.jpg")
            return elapsed

        fail(f"No valid image in response ({elapsed:.1f}s)")
    except Exception as e:
        fail(f"Request failed: {str(e)[:150]}")
    return None


def test_vision(image_url: str) -> Optional[float]:
    banner("VISION: Agnes AI Image Analysis")
    info(f"Model: {VISION_MODEL}")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
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

    t0 = time.time()
    try:
        resp = httpx.post(
            f"{BASE_URL}/chat/completions",
            json=payload,
            headers=headers,
            timeout=120,
        )
        elapsed = time.time() - t0

        if resp.status_code != 200:
            fail(f"HTTP {resp.status_code}: {resp.text[:200]}")
            return None

        data = resp.json()
        text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        if text:
            ok(f"Analyzed in {elapsed:.1f}s")
            info(f"Response ({len(text)} chars): {text[:300]}...")
            return elapsed

        fail(f"No content in response: {str(data)[:200]}")
    except Exception as e:
        fail(f"Request failed: {str(e)[:150]}")
    return None


def _resolve_vision_image(args) -> str:
    if args.image_url:
        return args.image_url
    if args.image and os.path.exists(args.image):
        img_bytes = Path(args.image).read_bytes()
        url = upload_to_temp_hosting(img_bytes)
        if url:
            return url
        b64 = base64.b64encode(img_bytes).decode()
        return f"data:image/png;base64,{b64}"
    img_bytes = generate_test_image()
    url = upload_to_temp_hosting(img_bytes)
    if url:
        return url
    b64 = base64.b64encode(img_bytes).decode()
    return f"data:image/png;base64,{b64}"


def main():
    parser = argparse.ArgumentParser(description="Agnes AI API Tester")
    parser.add_argument("--image", "-i", type=str, help="Path to test image for img2img/vision")
    parser.add_argument("--image-url", "-u", type=str, help="URL for vision analysis (overrides --image)")
    parser.add_argument("--prompt", "-p", type=str, default="A cute orange cat wearing a space helmet, floating in outer space with stars and planets in the background, digital art, high quality", help="Prompt")
    parser.add_argument("--mode", choices=["txt2img", "img2img", "vision", "all"], default="all")
    args = parser.parse_args()

    if not API_KEY or not API_KEY.startswith("sk-"):
        print(f"\n{RED}ERROR: Valid AGNES_API_KEY not found{RESET}")
        print(f"  Get a free API key from: https://agnes-ai.com")
        print(f"  Then set it in .env as:  AGNES_API_KEY=sk-your-key-here\n")
        return

    banner("Agnes AI API Tester")
    print(f"\n  API Key   : {API_KEY[:12]}...{API_KEY[-4:]}")
    print(f"  Base URL  : {BASE_URL}")
    print(f"  txt2img   : {TXT2IMG_MODEL}")
    print(f"  img2img   : {IMG2IMG_MODEL}")

    results = {"txt2img": False, "img2img": False, "vision": False}

    if args.mode in ("txt2img", "all"):
        t = test_txt2img(args.prompt)
        if t:
            results["txt2img"] = True

    if args.mode in ("img2img", "all"):
        img_bytes = None
        if args.image and os.path.exists(args.image):
            img_bytes = Path(args.image).read_bytes()
        else:
            img_bytes = generate_test_image()
        info(f"Input image: {len(img_bytes)} bytes")
        t = test_img2img(img_bytes, "Transform this image into a fantasy landscape with mountains, rivers, and a castle in the background")
        if t:
            results["img2img"] = True

    if args.mode in ("vision", "all"):
        image_url = _resolve_vision_image(args)
        info(f"Vision input: {image_url[:60]}...")
        t = test_vision(image_url)
        if t:
            results["vision"] = True

    print()
    banner("Summary")
    ok_t = f"{GREEN}OK{RESET}" if results["txt2img"] else f"{RED}FAIL{RESET}"
    ok_i = f"{GREEN}OK{RESET}" if results["img2img"] else f"{RED}FAIL{RESET}"
    ok_v = f"{GREEN}OK{RESET}" if results["vision"] else f"{RED}FAIL{RESET}"
    print(f"{'txt2img (Agnes Image)':<25} {ok_t}")
    print(f"{'img2img (Agnes Edit)':<25} {ok_i}")
    print(f"{'vision (Agnes Text)':<25} {ok_v}")

    if results["txt2img"]:
        ok("txt2img: Agnes AI works!")
    if results["img2img"]:
        ok("img2img: Agnes AI image editing works!")
    if results["vision"]:
        ok("vision: Agnes AI understands images!")


if __name__ == "__main__":
    main()
