"""
storyboard_orchestrator.py – Điều phối pipeline tạo Storyboard Video từ Subtitle SRT.
"""
import os
import threading
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import HTTPException

from core.config import settings
from models.storyboard import StoryboardResponse, StoryboardSegment
from services.pixazo_video_service import pixazo_video_service
from services.srt_parser import parse_srt
from services.storyboard_store import (
    get_storyboard,
    load_storyboards,
    save_storyboard,
    update_segment,
)
from services.video_prompt_service import build_video_prompt
from services.video_stitcher_service import stitch_and_mux_storyboard

STUCK_TIMEOUT_SEC = 10 * 60
AUDIO_UPLOADS_DIR = os.path.join("data", "audio_uploads")


def _save_uploaded_audio_file(storyboard_id: str, audio_bytes: bytes, filename: str) -> str:
    """Lưu file âm thanh MP3 đính kèm vào data/audio_uploads/."""
    os.makedirs(AUDIO_UPLOADS_DIR, exist_ok=True)
    ext = os.path.splitext(filename)[1].lower() or ".mp3"
    audio_path = os.path.join(AUDIO_UPLOADS_DIR, f"{storyboard_id}{ext}")
    with open(audio_path, "wb") as f:
        f.write(audio_bytes)
    return audio_path


def create_storyboard(
    srt_content: str,
    title: str,
    audio_bytes: Optional[bytes] = None,
    audio_filename: Optional[str] = None,
    groq_api_key: Optional[str] = None,
    model_id: Optional[str] = None,
    aspect: str = "16:9",
) -> StoryboardResponse:
    """Khởi tạo Storyboard từ phụ đề SRT (kèm file âm thanh lồng tiếng tùy chọn)."""
    parsed = parse_srt(srt_content, fps=16)
    sb_id = f"sb_{uuid.uuid4().hex[:8]}"
    audio_path = (
        _save_uploaded_audio_file(sb_id, audio_bytes, audio_filename)
        if audio_bytes and audio_filename
        else None
    )

    segments = [
        StoryboardSegment(
            id=f"seg_{uuid.uuid4().hex[:8]}",
            order=p.order,
            text=p.text,
            start_sec=p.start_sec,
            end_sec=p.end_sec,
            timecode=p.timecode,
            duration_sec=p.duration_sec,
            num_frames=p.num_frames,
            status="pending",
        )
        for p in parsed
    ]
    duration = max((s.end_sec for s in segments), default=0.0)

    storyboard = StoryboardResponse(
        storyboard_id=sb_id,
        title=title,
        status="pending",
        segments=segments,
        total=len(segments),
        completed=0,
        audio_duration_sec=duration,
        total_duration_sec=duration,
        has_audio=bool(audio_path),
        frame_rate=16,
        aspect=aspect,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    save_storyboard(storyboard)

    threading.Thread(
        target=_run_in_background,
        args=(sb_id, title, audio_path, groq_api_key, model_id, aspect),
        daemon=True,
    ).start()
    return storyboard


def process_segment(
    segment: StoryboardSegment,
    context: str,
    groq_api_key: Optional[str] = None,
    model_id: Optional[str] = None,
    aspect: str = "16:9",
) -> StoryboardSegment:
    """Xử lý 1 phân đoạn: Sinh prompt video -> Gọi Pixazo LTX 2.5."""
    prompt = build_video_prompt(segment_text=segment.text, context=context, groq_api_key=groq_api_key)
    job = pixazo_video_service.submit_video_job(
        prompt=prompt, aspect=aspect, num_frames=segment.num_frames, frame_rate=16
    )
    segment.request_id = job.get("request_id")
    segment.video_prompt = prompt
    segment.status = "processing"

    result = pixazo_video_service.wait_for_completion(segment.request_id)
    urls = result.get("output", {}).get("media_url", [])
    segment.video_url = urls[0] if urls else None
    segment.status = "completed" if segment.video_url else "failed"
    return segment


def trigger_stitching(storyboard_id: str, audio_path: Optional[str] = None) -> Optional[str]:
    """Kích hoạt ghép nối toàn bộ video phân đoạn và lồng tiếng MP3."""
    sb = get_storyboard(storyboard_id)
    if not sb or sb.completed != sb.total:
        return None
    valid_urls = [s.video_url for s in sb.segments if s.video_url]
    if len(valid_urls) != sb.total:
        return None

    try:
        sb.is_stitching = True
        save_storyboard(sb)
        if not audio_path:
            check_audio = os.path.join(AUDIO_UPLOADS_DIR, f"{storyboard_id}.mp3")
            if os.path.exists(check_audio):
                audio_path = check_audio

        merged_url = stitch_and_mux_storyboard(storyboard_id, valid_urls, audio_path)
        sb = get_storyboard(storyboard_id)
        if sb:
            sb.merged_video_url = merged_url
            sb.is_stitching = False
            sb.has_audio = bool(audio_path and os.path.exists(audio_path))
            save_storyboard(sb)
        return merged_url
    except Exception:
        sb = get_storyboard(storyboard_id)
        if sb:
            sb.is_stitching = False
            save_storyboard(sb)
        return None


def _run_in_background(
    storyboard_id: str,
    context: str,
    audio_path: Optional[str],
    groq_api_key: Optional[str],
    model_id: Optional[str],
    aspect: str,
) -> None:
    """Vòng lặp Worker xử lý background tuần tự."""
    sb = get_storyboard(storyboard_id)
    if not sb:
        return

    for seg in sb.segments:
        update_segment(storyboard_id, seg.id, {"status": "processing"})
        for attempt in range(settings.VIDEO_MAX_RETRY):
            try:
                updated = process_segment(seg, context, groq_api_key, model_id, aspect)
                update_segment(storyboard_id, seg.id, updated.model_dump())
                break
            except HTTPException as e:
                if attempt == settings.VIDEO_MAX_RETRY - 1:
                    update_segment(storyboard_id, seg.id, {"status": "failed", "error": str(e.detail)})
                else:
                    time.sleep(5)
    trigger_stitching(storyboard_id, audio_path)


def regenerate_segment(
    storyboard_id: str, segment_id: str, custom_prompt: Optional[str] = None
) -> StoryboardSegment:
    """Tạo lại một phân đoạn và tự động ghép nối lại toàn bộ video sau khi hoàn tất."""
    sb = get_storyboard(storyboard_id)
    if not sb:
        raise HTTPException(404, detail="Không tìm thấy storyboard.")
    target = next((s for s in sb.segments if s.id == segment_id), None)
    if not target:
        raise HTTPException(404, detail="Không tìm thấy segment.")

    target.status = "processing"
    target.error = None
    update_segment(storyboard_id, segment_id, target.model_dump())
    try:
        updated = process_segment(target, sb.title)
        update_segment(storyboard_id, segment_id, updated.model_dump())
        trigger_stitching(storyboard_id)
        return updated
    except HTTPException as e:
        update_segment(storyboard_id, segment_id, {"status": "failed", "error": str(e.detail)})
        raise


def get_storyboard_status(storyboard_id: str) -> Dict[str, Any]:
    """Lấy trạng thái tổng thể và tiến trình ghép video."""
    sb = get_storyboard(storyboard_id)
    if not sb:
        raise HTTPException(404, detail="Không tìm thấy storyboard.")
    return {
        "storyboard_id": sb.storyboard_id,
        "status": sb.status,
        "total": sb.total,
        "completed": sb.completed,
        "is_stitching": sb.is_stitching,
        "merged_video_url": sb.merged_video_url,
        "has_audio": sb.has_audio,
        "segments": [s.model_dump() for s in sb.segments],
    }


def cleanup_stuck_segments() -> int:
    """Dọn dẹp các phân đoạn bị kẹt trạng thái processing khi khởi động server."""
    cleaned, now = 0, datetime.now(timezone.utc)
    for sb in load_storyboards():
        changed = False
        for seg in sb.segments:
            if seg.status == "processing":
                try:
                    if (now - datetime.fromisoformat(sb.created_at)).total_seconds() > STUCK_TIMEOUT_SEC:
                        seg.status = "failed"
                        seg.error = "Server bị gián đoạn, vui lòng thử lại."
                        changed = True
                        cleaned += 1
                except Exception:
                    pass
        if changed:
            sb.completed = sum(1 for s in sb.segments if s.status == "completed")
            save_storyboard(sb)
    return cleaned
