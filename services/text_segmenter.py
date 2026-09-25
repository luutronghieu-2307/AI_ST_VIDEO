"""
text_segmenter.py – Parse và chia text thành các segment có nghĩa.

Hỗ trợ 2 định dạng input:
- text: đoạn văn thuần, tách theo dấu câu
- json: mảng các đoạn thoại có cấu trúc
"""
import json
import re
from typing import List, Tuple

from fastapi import HTTPException

from core.config import settings

MAX_SEGMENT_CHARS = 200
MIN_SEGMENT_CHARS = 50


def parse_input(raw_text: str, input_format: str = "text") -> List[str]:
    """
    Parse input thành danh sách segments.

    Args:
        raw_text: Nội dung input (text thuần hoặc JSON string)
        input_format: "text" hoặc "json"

    Returns:
        List[str]: Danh sách các đoạn text

    Raises:
        HTTPException(400): Nếu input rỗng hoặc JSON không hợp lệ
    """
    if not raw_text or not raw_text.strip():
        raise HTTPException(status_code=400, detail="Input không được để trống.")

    if input_format == "json":
        return _parse_json(raw_text)
    return _parse_text(raw_text)


def _parse_json(raw_text: str) -> List[str]:
    """Parse JSON input, hỗ trợ 2 cấu trúc: dict có 'segments' hoặc array."""
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"JSON không hợp lệ: {str(e)}")

    # Hỗ trợ 2 cấu trúc
    if isinstance(data, dict):
        items = data.get("segments", [])
    elif isinstance(data, list):
        items = data
    else:
        raise HTTPException(
            status_code=400,
            detail="JSON phải là object có 'segments' hoặc array.",
        )

    if not isinstance(items, list):
        raise HTTPException(status_code=400, detail="Trường 'segments' phải là array.")

    segments: List[str] = []
    for item in items:
        if isinstance(item, dict):
            text = item.get("text", "")
        else:
            text = str(item)
        if text and text.strip():
            segments.append(text.strip())

    if not segments:
        raise HTTPException(status_code=400, detail="Không tìm thấy text trong JSON.")
    return segments


def _parse_text(raw_text: str) -> List[str]:
    """Parse text thuần, tách theo dấu câu (. ? !) hoặc xuống dòng kép."""
    parts = re.split(r"(?<=[.!?])\s+|\n\n+", raw_text.strip())
    return [p.strip() for p in parts if p.strip()]


def split_into_segments(text: str, max_segments: int = 15) -> List[str]:
    """
    Chia text thành các segment có nghĩa trọn vẹn.

    Args:
        text: Đoạn text cần chia
        max_segments: Số segment tối đa

    Returns:
        List[str]: Danh sách segments

    Raises:
        HTTPException(400): Nếu không chia được hoặc vượt max_segments
    """
    sentences = _parse_text(text)
    if not sentences:
        raise HTTPException(
            status_code=400, detail="Không thể chia text thành segments."
        )

    merged = _merge_short_sentences(sentences)
    final = _split_long_sentences(merged)

    if len(final) > max_segments:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Vượt giới hạn {max_segments} segment (có {len(final)}). "
                f"Vui lòng rút ngắn nội dung."
            ),
        )
    return final


def _merge_short_sentences(sentences: List[str]) -> List[str]:
    """Gộp các câu ngắn liên tiếp thành câu dài hơn."""
    merged: List[str] = []
    buffer = ""
    for s in sentences:
        if len(buffer) + len(s) < MIN_SEGMENT_CHARS:
            buffer = f"{buffer} {s}".strip()
        else:
            if buffer:
                merged.append(buffer)
            buffer = s
    if buffer:
        merged.append(buffer)
    return merged


def _split_long_sentences(sentences: List[str]) -> List[str]:
    """Tách câu dài (> MAX_SEGMENT_CHARS) tại dấu phẩy."""
    result: List[str] = []
    for s in sentences:
        if len(s) <= MAX_SEGMENT_CHARS:
            result.append(s)
            continue

        parts = s.split(", ")
        buffer = ""
        for p in parts:
            if len(buffer) + len(p) < MAX_SEGMENT_CHARS:
                buffer = f"{buffer}, {p}".strip(", ")
            else:
                if buffer:
                    result.append(buffer)
                buffer = p
        if buffer:
            result.append(buffer)
    return result


def validate_segments(segments: List[str]) -> Tuple[bool, str]:
    """
    Validate danh sách segments.

    Returns:
        Tuple[bool, str]: (is_valid, message)
    """
    if not segments:
        return False, "Danh sách segment rỗng."

    max_seg = settings.MAX_SEGMENTS_PER_REQUEST
    if len(segments) > max_seg:
        return False, f"Vượt giới hạn {max_seg} segment (có {len(segments)})."

    for i, seg in enumerate(segments, 1):
        if not seg.strip():
            return False, f"Segment {i} rỗng."
        if len(seg) > MAX_SEGMENT_CHARS:
            return False, (
                f"Segment {i} quá dài ({len(seg)} > {MAX_SEGMENT_CHARS} ký tự)."
            )

    return True, "Hợp lệ."
