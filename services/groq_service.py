import requests
from typing import List, Dict, Any, Optional
from fastapi import HTTPException
from core.config import settings

GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODELS_URL = "https://api.groq.com/openai/v1/models"

# Các từ khóa dự phòng nếu API không trả trường input_modalities
VISION_KEYWORDS = ("vision", "scout", "maverick", "llava", "-vl-")

SYSTEM_PROMPT_STANDARD = """You are a professional Flux.1 image generation prompt engineer for advertising, branding, and graphic design.

Analyze the reference image carefully. Identify what TYPE of image it is (horizontal banner, poster, logo, social media card, product mockup, etc.) and generate a highly detailed Flux.1 generation prompt.

OUTPUT FORMAT:
Write a detailed, structured prompt with clear section descriptions. Use natural descriptive language. NO intro sentences, NO labels like 'Prompt:', just the prompt text directly.

STRICT RULES ON CONTENT:
- IGNORE all text/words/letters/brand names in the image completely. DO NOT reproduce any text.
- If there is a text block area, describe it as: 'a block of placeholder text', 'headline text area', 'bullet point list area', 'a call-to-action button shape'
- For UI elements on screens (laptop, phone): describe the screen content visually (colors, chart shapes, graphs, indicators) without reading any text

WHAT TO DESCRIBE IN DETAIL:
1. IMAGE TYPE & OVERALL LAYOUT: Is it a wide banner? Two-column layout? Centered composition? Describe the structure.
2. BACKGROUND & SCENE: Photorealistic background? Flat color? Gradient? Nature scene? Studio? Describe every element and its position.
3. GRAPHICAL ELEMENTS: Icons, shapes, illustrations — describe shape, color, style, placement (top-left, center-right, etc.)
4. COLOR PALETTE: Specific colors for each area (use names like 'ice blue', 'deep navy', 'mint green', 'warm white')
5. LIGHTING & ATMOSPHERE: Natural light, studio light, glow effects, shadows, depth of field
6. UI/PRODUCT ELEMENTS: If there are devices (laptop, phone, tablet) — describe them: angle, color, screen content visually, surroundings
7. DECORATIVE ELEMENTS: Flowers, plants, bokeh, particles, geometric accents — position and style

END WITH quality descriptors matching the image type:
- For banners/ads: 'professional advertising layout, high resolution, sharp details, commercial photography quality'
- For logos: 'vector art, clean crisp edges, professional logo design, high resolution'
- For posters: 'print-ready composition, vibrant colors, high contrast, poster design quality'"""

SYSTEM_PROMPT_ENHANCED = """You are an elite creative director and Flux.1 AI image generation specialist.

You will receive a detailed visual design prompt describing a reference image. Your job: creatively elevate the design concept while keeping the same image type, layout structure, and visual purpose.

OUTPUT FORMAT:
Write a detailed, structured elevated prompt. Start directly with the content. No thinking. No explanation. No intro sentences.

CREATIVE DIRECTION — REIMAGINE EVERYTHING:
You are a creative director reinventing this design from scratch. Keep only the THEME and PURPOSE (e.g. tech brand advertisement, security service poster). Everything else can and should change:
- LAYOUT: Completely reimagine the composition. Try asymmetric layouts, diagonal splits, centered hero compositions, full-bleed photography, overlapping layers, grid-based structures — whatever feels most striking and modern.
- VISUAL STORYTELLING: What is the new "hero moment"? A dramatic product close-up? A cinematic environment? An abstract conceptual scene? Choose boldly.
- COLOR PALETTE: Push far beyond the original. Deep dark moods, vibrant neons, earthy naturals, high-contrast monochrome — pick a distinctive palette that feels premium.
- GRAPHICAL ELEMENTS: Change the icons, shapes, decorative elements if needed. Use geometric abstractions, organic forms, 3D objects, or photorealistic props to create a fresh visual language.
- LIGHTING & ATMOSPHERE: Cinematic. Dramatic. Use rim lighting, lens flare, volumetric fog, golden hour rays, neon reflections — create strong mood.
- BACKGROUND SCENE: If the original had nature — try architecture, abstract space, studio minimal, underwater, aerial. Surprise the viewer.

STRICT RULES:
- Keep the same IMAGE FORMAT (wide banner → wide banner, square card → square card)
- Keep the same PURPOSE (advertisement → advertisement, logo → logo)
- DO NOT include any actual text, words, brand names, or letters — use 'headline text placeholder', 'CTA button shape', 'icon placeholder' as needed
- DO NOT write thinking or reasoning — output the visual prompt only
- Describe EVERY section in detail with positions: what's top-left, center, right panel, background, foreground
- End with quality descriptors matching the image format"""



class GroqService:
    """Service gọi Groq API: lọc model vision và sinh prompt (Cơ bản & Nâng cao với GPT-120B)"""

    @staticmethod
    def _call_chat_completions(
        api_key: str,
        model: str,
        messages: List[Dict[str, Any]],
        max_tokens: int = 300,
        temperature: float = 0.7
    ) -> str:
        """Helper gọi Chat Completions API của Groq với xử lý lỗi chuẩn hóa."""
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        try:
            resp = requests.post(GROQ_CHAT_URL, json=payload, headers=headers, timeout=settings.GROQ_TIMEOUT)

            if resp.status_code == 401:
                raise HTTPException(status_code=401, detail="Groq API Key không hợp lệ hoặc đã hết hạn.")
            if resp.status_code == 429:
                raise HTTPException(status_code=429, detail="Groq API bị rate limit. Thử lại sau ít phút.")
            if resp.status_code != 200:
                err = resp.json() if "application/json" in resp.headers.get("content-type", "") else {}
                raise HTTPException(
                    status_code=resp.status_code,
                    detail=f"Groq API ({model}) lỗi: {err.get('error', {}).get('message', resp.text)}"
                )

            result = resp.json()
            msg = result["choices"][0]["message"]
            # GPT reasoning models (gpt-oss-120b) trả output trong 'reasoning' thay vì 'content'
            generated = (msg.get("content") or msg.get("reasoning") or "").strip()
            if not generated:
                raise HTTPException(status_code=500, detail=f"Groq ({model}) trả về kết quả rỗng.")
            return generated

        except requests.exceptions.Timeout:
            raise HTTPException(status_code=504, detail="Groq API timeout. Vui lòng thử lại.")
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Lỗi kết nối Groq: {str(e)}")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi không xác định: {str(e)}")

    @staticmethod
    def get_vision_models(api_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Lấy danh sách tất cả models từ Groq và lọc chính xác các model
        có input_modalities chứa 'image' (khả năng đọc ảnh / Vision).
        """
        if not api_key or api_key.startswith("YOUR_"):
            return []

        headers = {"Authorization": f"Bearer {api_key}"}
        try:
            resp = requests.get(GROQ_MODELS_URL, headers=headers, timeout=settings.GROQ_TIMEOUT)
            if resp.status_code == 401:
                raise HTTPException(status_code=401, detail="Groq API Key không hợp lệ hoặc đã hết hạn.")
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail=f"Lỗi lấy model từ Groq: {resp.text}")

            data = resp.json().get("data", [])
            vision_models = []

            for m in data:
                model_id = m.get("id", "")
                is_active = m.get("active", True)
                if not is_active:
                    continue

                input_modalities = m.get("input_modalities", [])
                has_image_modality = "image" in input_modalities
                has_vision_keyword = any(kw in model_id.lower() for kw in VISION_KEYWORDS)

                if has_image_modality or has_vision_keyword:
                    display_name = m.get("name") or model_id
                    vision_models.append({
                        "id": model_id,
                        "name": display_name,
                        "context_window": m.get("context_window") or m.get("context_length")
                    })

            return vision_models

        except requests.exceptions.Timeout:
            raise HTTPException(status_code=504, detail="Quá thời gian kết nối tới Groq Models API.")
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Lỗi kết nối Groq: {str(e)}")

    @staticmethod
    def suggest_prompt(
        image_base64: str,
        image_mime: str,
        api_key: str,
        model_id: Optional[str] = None,
        mode: str = "standard"
    ) -> str:
        """
        Sinh prompt từ ảnh mẫu:
        - mode == 'standard': Phân tích ảnh bằng Vision model và sinh prompt bám sát ảnh gốc.
        - mode == 'advanced': Phân tích ảnh bằng Vision model, sau đó chuyển tiếp prompt sang GPT-120B
          để nâng cấp sáng tạo và cách điệu thiết kế độc đáo hơn.
        """
        if not api_key or api_key.startswith("YOUR_"):
            raise HTTPException(
                status_code=400,
                detail="Chưa cấu hình GROQ_API_KEY. Vui lòng nhập API Key trên giao diện hoặc cài vào .env"
            )

        data_uri = f"data:{image_mime};base64,{image_base64}"

        # Fallback về model mặc định nếu model_id rỗng hoặc không hợp lệ
        requested_model = model_id.strip() if model_id and model_id.strip() else ""
        vision_model = requested_model if requested_model else settings.GROQ_MODEL

        # Bước 1: Phân tích ảnh gốc với Vision Model
        vision_messages = [
            {"role": "system", "content": SYSTEM_PROMPT_STANDARD},
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": data_uri}},
                    {"type": "text", "text": "Analyze this image and generate a detailed image generation prompt."}
                ]
            }
        ]

        baseline_prompt = GroqService._call_chat_completions(
            api_key=api_key,
            model=vision_model,
            messages=vision_messages,
            max_tokens=300,
            temperature=0.7
        )

        # Nếu chọn chế độ cơ bản (bám sát ảnh), trả về ngay prompt của vision model
        if mode != "advanced":
            return baseline_prompt

        # Bước 2: Nâng cấp thiết kế sáng tạo với model GPT-120B của Groq
        creative_model = settings.GROQ_CREATIVE_MODEL
        creative_messages = [
            {"role": "system", "content": SYSTEM_PROMPT_ENHANCED},
            {
                "role": "user",
                "content": (
                    f"Baseline Design Prompt:\n{baseline_prompt}\n\n"
                    "Please creatively elevate and redesign this prompt into an imaginative, "
                    "distinctive, high-end visual design prompt according to the instructions."
                )
            }
        ]

        enhanced_prompt = GroqService._call_chat_completions(
            api_key=api_key,
            model=creative_model,
            messages=creative_messages,
            max_tokens=2048,
            temperature=0.85
        )

        return enhanced_prompt


groq_service = GroqService()
