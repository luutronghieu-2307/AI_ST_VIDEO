"""
video_prompt_service.py – Sinh prompt video cho LTX 2.5 bằng GPT-120B.

Sử dụng groq_service._call_chat_completions() để gọi model GPT-120B
(openai/gpt-oss-120b) sinh prompt video chi tiết bằng tiếng Anh.
"""
from typing import List, Optional

from fastapi import HTTPException

from core.config import settings
from services.groq_service import groq_service

SYSTEM_PROMPT_VIDEO = """You are a world-class cinematic director writing hyper-detailed video prompts for the LTX 2.5 FREE model.

LTX 2.5 FREE REQUIREMENT: Because this is a free-tier model with limited inference, your prompt MUST be extremely specific and detailed. Vague prompts produce bad videos. Every element must be described explicitly.

PRIME DIRECTIVE: The video must DIRECTLY and LITERALLY visualize what the narrator is SAYING. Never substitute mentioned subjects with robots, holograms, or abstract AI imagery unless the narration explicitly says so.

MANDATORY DETAIL STRUCTURE — describe ALL of these in every prompt:
1. SUBJECT: Who/what is the main focus? (e.g. "a 30-year-old professional woman in a blue blazer")
2. SPECIFIC ACTION: Exactly what are they doing, step by step? (e.g. "leans forward, places both hands on the keyboard, types rapidly, eyes scanning the screen")
3. OBJECT DETAILS: What objects are present and what do they look like? (e.g. "a slim silver MacBook with a glowing screen showing data charts")
4. ENVIRONMENT: Where exactly? Specific room/place details. (e.g. "a bright modern open-plan office with floor-to-ceiling windows, city skyline visible")
5. LIGHTING: Exact light quality, direction, color. (e.g. "warm late-afternoon golden light streaming from the left, soft shadow on the right side")
6. CAMERA: One specific shot type + movement. (e.g. "medium close-up, slow dolly-in from behind the laptop toward her face")

RULE — LITERAL CONTENT:
- Narration says "laptop" → show a real laptop. "Factory" → show a factory floor. "Person thinking" → show a person with thoughtful expression, hand on chin, eyes looking away.
- Translate abstract concepts into tangible physical scenes: "efficiency" = a worker checking items off a list quickly; "connection" = two people shaking hands firmly; "growth" = a bar chart being drawn on a whiteboard.

FEW-SHOT EXAMPLE:
Narrator says: "Laptops and computers are now the main tool for work."
GOOD prompt: "A medium close-up shot slowly dollying in: a focused young man in a gray shirt sits at a clean wooden desk, his fingers moving quickly across a full-size laptop keyboard, eyes tracking lines of content on the bright screen. Two monitors flank the laptop displaying spreadsheets. The modern home office is bathed in cool blue morning light from a wide window behind him, bokeh city buildings visible through the glass. Shallow depth of field keeps the laptop sharp while the background softly blurs."

OUTPUT RULES:
- ENGLISH only. One dense, rich paragraph. 150–220 words.
- NO "Prompt:", NO "Here is...", NO meta text. Start directly with the scene.
- NO readable text/letters/numbers visible on screen.
- Every sentence must describe a visible, physical, specific detail."""

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
        f"NARRATOR SAYS: \"{segment_text.strip()}\"\n\n"
        f"Context/Topic: {context or 'General content'}\n\n"
        f"Visual style: {style}\n\n"
        f"TASK: Generate a detailed LTX 2.5 video shot that DIRECTLY visualizes what the narrator is saying.\n"
        f"Show the EXACT objects, people, and actions mentioned or implied in the narration.\n"
        f"Do NOT replace them with robots, holograms, or AI imagery unless the narration explicitly mentions those."
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
            max_tokens=650,
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
