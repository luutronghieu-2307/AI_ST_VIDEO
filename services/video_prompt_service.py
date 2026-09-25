"""
video_prompt_service.py – Sinh prompt video cho LTX 2.5 bằng GPT-120B.

Sử dụng groq_service._call_chat_completions() để gọi model GPT-120B
(openai/gpt-oss-120b) sinh prompt video chi tiết bằng tiếng Anh.
"""
from typing import List, Optional

from fastapi import HTTPException

from core.config import settings
from services.groq_service import groq_service

SYSTEM_PROMPT_VIDEO = """You are an award-winning cinematic director and visual storyteller for the LTX 2.5 video model.

Your mission: Transform narrative voiceovers into VIVID, DYNAMIC, STORY-DRIVEN visual scenes with powerful visual metaphors instead of boring abstract graphics.

CRITICAL CREATIVE RULES:
1. BAN GENERIC ABSTRACT CLICHÉS:
   - NEVER use generic glowing neural networks, floating 0/1 binary code, abstract digital cubes, or spinning brain holograms.
   - ALWAYS turn abstract concepts into TANGIBLE REAL-WORLD METAPHORS and STORY-DRIVEN SCENES.

2. MASTER VISUAL METAPHORS & HUMAN-TECH INTERACTIONS:
   - If talking about "AI vs Human consciousness": Show contrasting juxtaposition (e.g. an artist freely painting with emotion beside a precise robotic arm waiting for a prompt; or a thoughtful human smiling next to a metallic android in a warm studio).
   - If talking about "Algorithms & training on data": Show vivid learning metaphors (e.g. a scientist feeding endless historical books into a luminous optical scanner, or a mentor teaching a curious robot in a sunlit classroom).
   - If talking about "Speed & computation": Show dynamic real-world action (e.g. time-lapse of a bustling modern city at dusk with light trails, or scientists inspecting ultra-fast holographic telemetry in a futuristic lab).
   - If talking about "Human guidance & teamwork": Show human hands and AI robotic tools working in harmony on an architectural masterplan.

3. CINEMATOGRAPHY & MOVEMENT:
   - Describe smooth camera motion (e.g. "Slow cinematic dolly-in", "Elegant tracking shot", "Wide dynamic pan").
   - Cinematic lighting (golden hour, soft volumetric rim lighting, dramatic shadows, shallow depth of field, 35mm film look).
   - Rich physical textures (metallic surfaces, dust motes in sunbeams, rich fabric, natural environments).

OUTPUT CONSTRAINTS:
- Output directly in ENGLISH, one cohesive descriptive paragraph (< 180 words).
- NO introductory text, NO "Prompt:", NO meta-commentary or thinking.
- NO readable text/words/letters/typography in the scene.
- Use active, visual, present-tense descriptions."""

DEFAULT_NEGATIVE_PROMPT = (
    "blurry, low quality, distorted, worst quality, abstract floating numbers, text overlay, watermark"
)



def build_video_prompt(
    segment_text: str,
    context: str = "",
    style: str = "documentary, realistic",
    groq_api_key: Optional[str] = None,
) -> str:
    """
    Sinh prompt video chi tiết cho LTX 2.5 từ segment text.
    Nếu Groq API Key không có hoặc lỗi, sẽ tự động Fallback sang template prompt mặc định.

    Args:
        segment_text: Nội dung thoại của segment
        context: Ngữ cảnh chung của storyboard (tiêu đề, chủ đề)
        style: Phong cách video (mặc định documentary, realistic)
        groq_api_key: Tùy chọn Groq API Key do client truyền vào

    Returns:
        str: Prompt video bằng tiếng Anh
    """
    if not segment_text or not segment_text.strip():
        raise HTTPException(
            status_code=400, detail="Segment text không được để trống."
        )

    api_key = groq_api_key or settings.GROQ_API_KEY
    if not api_key or api_key.startswith("YOUR_"):
        # Fallback prompt cơ bản nếu chưa có key Groq
        return f"A cinematic documentary video shot, photorealistic, 4k resolution, cinematic lighting, {style}, depicting: {segment_text.strip()}."

    user_content = (
        f"Narration segment: {segment_text}\n\n"
        f"Storyboard context: {context or 'General documentary'}\n\n"
        f"Visual style: {style}\n\n"
        f"Generate a detailed LTX 2.5 video prompt for this segment."
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_VIDEO},
        {"role": "user", "content": user_content},
    ]

    try:
        return groq_service._call_chat_completions(
            api_key=api_key,
            model=settings.GROQ_CREATIVE_MODEL,
            messages=messages,
            max_tokens=500,
            temperature=0.7,
        )
    except Exception as e:
        # Fallback mềm để pipeline không bị đứt đoạn sang Pixazo
        print(f"⚠️ Groq video prompt error ({e}), fallback sang default prompt.")
        return f"A cinematic documentary video shot, photorealistic, 4k resolution, cinematic lighting, {style}, depicting: {segment_text.strip()}."



def build_batch_video_prompts(
    segments: List[str], context: str = ""
) -> List[str]:
    """
    Sinh prompt video cho nhiều segment (tuần tự).

    Không dừng cả batch khi 1 segment lỗi — chỉ log và trả placeholder rỗng.

    Args:
        segments: Danh sách text segments
        context: Ngữ cảnh chung

    Returns:
        List[str]: Danh sách prompts (phần tử rỗng nếu segment đó lỗi)
    """
    prompts: List[str] = []
    for i, seg in enumerate(segments, 1):
        try:
            prompt = build_video_prompt(seg, context)
            prompts.append(prompt)
        except HTTPException as e:
            print(f"⚠️ Lỗi sinh prompt segment {i}: {e.detail}")
            prompts.append("")
    return prompts
