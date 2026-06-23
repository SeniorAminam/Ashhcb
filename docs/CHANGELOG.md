<!--
Project:         Ashhcb Bot - AI Image Transformer on Bale
File Path:       docs/CHANGELOG.md
Author:          Amin Davodian
Full Name:       Mohammadamin Davodian
Website:         https://senioramin.com
GitHub:          https://github.com/SeniorAminam
LinkedIn:        https://linkedin.com/in/SudoAmin
Developer:       @SeniorAminBot 
Brand:           SeniorAmin
Created Date:    2026-06-23
Modified Date:   2026-06-23
Version:         2.0.0
Purpose:         Version history and changelog
License:         MIT
Copyright:       (c) Amin Davodian
-->

# Changelog

All notable changes to the **Ashhcb Bot** project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [4.0.2] — 2026-06-23

### Added
- **Rate limiting**: 60-second cooldown between API calls per user
- **Docker support**: Production-ready Dockerfile + docker-compose.yml + .dockerignore
- **Rate limit messages**: Persian cooldown notification for all three capabilities

### Changed
- Bot messages updated: help, welcome, about text now accurate for single-provider (Agnes AI)
- Dockerfile: multi-stage build with proper health check
- Docker Compose: named volumes for data persistence
- GitHub repo: `SeniorAminam/Ashhcb` throughout all docs
- `docs/INSTALL.md` and `docs/DEPLOYMENT.md` updated with Docker instructions
- `docs/README.md` rewritten to match current architecture

### Fixed
- `health_check` no longer times out on startup (graceful warning instead of crash)
- Bot messages no longer reference old multi-provider or style preset system
- `.env.example` now includes `RATE_LIMIT_SECONDS`

## [4.0.0] — 2026-06-23

### Added
- **🔍 تحلیل تصویر** (Vision) — upload photo, get Persian description via Agnes AI
- File headers on all `.py` files (Author, Version, Purpose, License, Copyright)
- `docs/` folder: ARCHITECTURE.md, INSTALL.md, DEPLOYMENT.md, API.md
- `LICENSE` (MIT), `.gitignore`, `README.md`

### Changed
- **Single-provider architecture**: Agnes AI for txt2img, img2img, and vision
- All other providers removed: Pollinations, Cloudflare, HF Spaces, Puter, ModelScope, FreeLLMAPI
- `AIService` — thin wrapper around `AgnesService` only
- `health_check` timeout raised from 15s → 30s
- Keyboard layout: 2-1-2-1 (non-admin), 2-1-2-2 (admin)
- "FLUX" text → "Agnes Image 2.0 Flash"

### Removed
- `pollinations_service.py`, `cloudflare_service.py`, `hf_spaces_service.py`
- `test_cloudflare_integration.py`, `test_hf_spaces.py`, `test_ai_services.py`, `test_modelscope.py`
- All CLOUDFLARE_*, PUTER_*, FREEAI_*, HF_* env vars
- `gradio-client` from requirements.txt

## [3.0.0] — 2026-06-21

### Added
- 8 preset artistic styles
- Custom prompt support
- HuggingFace Inference API integration
- SQLite user database with history and statistics
- Admin panel with broadcast, user list, stats
- Persian/Farsi glass-style keyboards
- Docker support

### Changed
- Complete rewrite — from preset-style pipeline to free-form prompt + real AI

## [2.0.0] — 2026-06-20

### Changed
- Full codebase refactor
- Modular handler/service architecture
- SQLite storage integration

## [1.0.0] — 2026-06-17

### Added
- Initial prototype
- Basic bot structure
