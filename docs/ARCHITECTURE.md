<!--
Project:         Ashhcb Bot - AI Image Transformer on Bale
File Path:       docs/ARCHITECTURE.md
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
Purpose:         System architecture overview with data flow diagrams
License:         MIT
Copyright:       (c) Amin Davodian
-->

# Architecture

```
User → Polling Bot → AIService → AgnesService → Agnes AI API → Result
```

## flow: txt2img (ساخت عکس)

```
User presses "🖼️ ساخت عکس"
  → text_message_handler sets waiting_for_image_gen=True
  → User types prompt
  → _process_image_gen()
  → AIService.transform_image(image_bytes=b"", prompt)
  → AgnesService.generate_image(prompt)
  → POST /v1/images/generations { model, prompt, n, size }
  → Download image URL → Send to user
```

## flow: img2img (شروع تبدیل عکس)

```
User presses "📷 شروع تبدیل عکس"
  → User sends photo → photo_handler stores image
  → User types prompt → _process_prompt()
  → AIService.transform_image(image_bytes, prompt)
  → AgnesService.transform_image(image_bytes, prompt)
    1. Upload image to catbox.moe (temp, 72h)
    2. POST /v1/images/generations { model, prompt, image_url, n, size }
    3. Download result → Send to user
```

## flow: vision (تحلیل تصویر)

```
User presses "🔍 تحلیل تصویر"
  → waiting_for_analysis=True
  → User sends photo → photo_handler detects flag
  → _analyze_photo()
  → AIService.analyze_image(image_bytes)
  → AgnesService.analyze_image(image_bytes)
    1. Upload image to catbox.moe
    2. POST /v1/chat/completions with image_url
    3. Return Persian description → Send to user
```

## Components

- **bot.py**: Entry point, registers handlers, starts polling
- **handlers/**: Command, text, photo, callback, admin, user_panel
- **services/**: Agnes AI wrapper, AI service orchestrator, SQLite storage
- **keyboards/**: Reply keyboards (main menu), inline keyboards (model select)
- **utils/**: Image helpers (resize, dimensions, format)
- **config/**: Environment variable management
