<!--
Project:         Ashhcb Bot - AI Image Transformer on Bale
File Path:       docs/API.md
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
Purpose:         API reference for Agnes AI endpoints and bot services
License:         MIT
Copyright:       (c) Amin Davodian
-->

# API Reference

## Agnes AI API

**Base URL**: `https://apihub.agnes-ai.com/v1`

### txt2img — Image Generation

```http
POST /images/generations
Authorization: Bearer sk-...
Content-Type: application/json

{
  "model": "agnes-image-2.0-flash",
  "prompt": "a cat in space",
  "n": 1,
  "size": "1024x1024"
}
```

### img2img — Image Editing

```http
POST /images/generations
Authorization: Bearer sk-...
Content-Type: application/json

{
  "model": "agnes-image-2.0-flash",
  "prompt": "make it fantasy",
  "image_url": "https://catbox.moe/...png",
  "n": 1,
  "size": "1024x1024"
}
```

### Vision — Image Analysis

```http
POST /chat/completions
Authorization: Bearer sk-...
Content-Type: application/json

{
  "model": "agnes-2.0-flash",
  "messages": [{
    "role": "user",
    "content": [
      {"type": "text", "text": "Describe this image in Persian"},
      {"type": "image_url", "image_url": {"url": "https://..."}}
    ]
  }]
}
```

## Bot Internal API

### `AIService.transform_image(image_bytes, prompt)`

- Empty `image_bytes` → txt2img
- With `image_bytes` → img2img (auto-uploads to catbox)
- Returns `(bytes, model_label, model_id)`

### `AIService.analyze_image(image_bytes)`

- Returns Persian description string
