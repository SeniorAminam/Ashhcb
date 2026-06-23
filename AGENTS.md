<!--
Project:         Ashhcb Bot - AI Image Transformer on Bale
File Path:       AGENTS.md
Author:          Amin Davodian
Full Name:       Mohammadamin Davodian
Website:         https://senioramin.com
GitHub:          https://github.com/SeniorAminam
LinkedIn:        https://linkedin.com/in/SudoAmin
Developer:       @SeniorAminBot
Brand:           SeniorAmin
Created Date:    2026-06-23
Modified Date:   2026-06-23
Version:         1.0.0
Purpose:         Agent instructions for AI coding assistant (opencode)
License:         MIT
Copyright:       (c) Amin Davodian
-->

## Goal
Create a complete free image bot on Bale using **Agnes AI** as the sole provider for txt2img, img2img, and vision.

## Architecture
**Only one provider: Agnes AI** (free tier, no payment method, ~20 req/min, unlimited daily)

```
User → Polling Bot → AIService → AgnesService → Agnes AI API → Result
```

### Three capabilities:
1. **txt2img** (ساخت عکس) → `POST /images/generations` with prompt → 1024x1024 image
2. **img2img** (شروع تبدیل عکس) → upload image to catbox.moe → `POST /images/generations` with `image_url` → 1024x1024 result
3. **vision** (image analysis) → `POST /chat/completions` with `image_url` → Persian description text

### Key implementation details:
- img2img uses `/images/generations` with `image_url` (NOT `/images/edits` — that endpoint has an upstream UTF-8 bug)
- Images uploaded to catbox.moe (temp hosting, 72h expiry) with `time=72h` parameter
- Uses HTTPS for all requests
- OpenAI-compatible interface (can also use `openai` Python library)

## Project Structure
```
src/
  bot.py                    # Main entry point, registers handlers, starts polling
  config/
    settings.py             # Central config: BOT_TOKEN, AGNES_API_KEY, etc.
  handlers/
    start.py                # /start, /help, /about, /models, text routing, _process_image_gen, _process_prompt
    photo.py                # Handles incoming photos, stores in user_data, shows model info
    callback.py             # Inline button handler (model selection, about, back)
    admin.py                # Admin panel: stats, user list, broadcast
    error.py                # Global error handler
    user_panel.py           # User history and stats
  keyboards/
    inline.py               # Inline keyboards (model selection, start, back)
    reply.py                # Glass-style reply keyboards (main menu, user panel, admin panel)
  services/
    agnes_service.py         # Core AI service: generate_image, transform_image, analyze_image, health_check
    ai_service.py            # Thin wrapper around AgnesService with transform_image() interface
    storage.py               # SQLite storage for users, transforms, AI daily usage
  utils/
    helpers.py               # format_size, resize_image, image dimensions, etc.
tests/
  test_agnes.py              # Test script for Agnes API (txt2img, img2img, vision)
```

## Config (.env)
```
BOT_TOKEN=xxx
AGNES_API_KEY=sk-xxx
ADMIN_USER_IDS=xxx
```

## Critical Context
- **Agnes AI base URL**: `https://apihub.agnes-ai.com/v1`
- **txt2img model**: `agnes-image-2.0-flash` (also `agnes-image-2.1-flash`)
- **Vision model**: `agnes-2.0-flash`
- **Rate limit**: ~20 requests per minute
- **Image quality**: Up to 4K resolution, ~1.6-1.8 MB per image
- **Speed**: ~24-30 seconds per request
- **Images generated so far with this key**: ~3 (all successful)

## Removed Providers
- **Pollinations FLUX** — removed (was primary txt2img)
- **Cloudflare Workers AI** — removed (was primary img2img)
- **HF CPU Spaces** — removed (was fallback, CPU SDXL/FastSD)
- **Puter.js Bridge** — removed (was fallback, token-limited)
- **ModelScope Qwen-Image** — never integrated (test file deleted)
- **FreeLLMAPI** — removed earlier (429 rate-limited)

## History
- Initial: Multi-provider hybrid with Cloudflare + Pollinations + HF Spaces + Puter
- Bug: Model routing was broken (waiting_for_image_gen checked before waiting_for_prompt)
- Fix: Check waiting_for_prompt first, clear flags on mode switch
- Current: Single-provider (Agnes AI) for all three capabilities
