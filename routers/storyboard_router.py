"""
storyboard_router.py – API endpoints cho tính năng Storyboard Video với Subtitle SRT & Audio Muxing.
"""
from typing import List, Optional

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse

from core.config import settings
from models.storyboard import SegmentRegenerateRequest, StoryboardResponse
from services.rate_limiter import enforce_rate_limit
from services.storyboard_orchestrator import (
    create_storyboard,
    get_storyboard_status,
    regenerate_segment,
    trigger_stitching,
)
from services.storyboard_store import (
    delete_storyboard,
    get_storyboard,
    load_storyboards,
)

storyboard_router = APIRouter(prefix="/api/storyboard", tags=["Storyboard Video"])


@storyboard_router.post(
    "/create",
    response_model=StoryboardResponse,
    summary="Tạo storyboard từ phụ đề SRT (kèm file MP3 lồng tiếng tùy chọn)",
)
async def create_storyboard_endpoint(
    request: Request,
    title: str = Form(...),
    srt_text: Optional[str] = Form(None),
    srt_file: Optional[UploadFile] = File(None),
    audio_file: Optional[UploadFile] = File(None),
    groq_api_key: Optional[str] = Form(None),
    model_id: Optional[str] = Form(None),
    aspect: str = Form("16:9"),
):
    """
    Tạo storyboard từ file phụ đề SRT và tự động ghép nối video hoàn chỉnh.
    """
    enforce_rate_limit(
        request,
        limit=settings.STORYBOARD_RATE_LIMIT,
        key_prefix="storyboard_create",
    )

    # 1. Trích xuất nội dung SRT
    srt_content: Optional[str] = None
    if srt_file and srt_file.filename:
        raw_bytes = await srt_file.read()
        try:
            srt_content = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            srt_content = raw_bytes.decode("latin-1", errors="ignore")
    elif srt_text and srt_text.strip():
        srt_content = srt_text.strip()

    if not srt_content:
        raise HTTPException(
            status_code=400,
            detail="Vui lòng tải lên file .srt hoặc dán nội dung phụ đề SRT.",
        )

    # 2. Xử lý file âm thanh lồng tiếng MP3 (nếu có)
    audio_bytes: Optional[bytes] = None
    audio_filename: Optional[str] = None
    if audio_file and audio_file.filename:
        audio_bytes = await audio_file.read()
        if len(audio_bytes) > settings.AUDIO_MAX_FILE_SIZE:
            max_mb = settings.AUDIO_MAX_FILE_SIZE // (1024 * 1024)
            raise HTTPException(400, detail=f"File MP3 quá lớn (tối đa {max_mb}MB).")
        audio_filename = audio_file.filename

    return create_storyboard(
        srt_content=srt_content,
        title=title,
        audio_bytes=audio_bytes,
        audio_filename=audio_filename,
        groq_api_key=groq_api_key,
        model_id=model_id,
        aspect=aspect,
    )


@storyboard_router.get(
    "/list",
    response_model=List[StoryboardResponse],
    summary="Danh sách storyboards (mới nhất trước)",
)
async def list_storyboards_endpoint():
    """Lấy danh sách tất cả storyboards."""
    return load_storyboards()


@storyboard_router.get(
    "/{storyboard_id}",
    response_model=StoryboardResponse,
    summary="Chi tiết storyboard",
)
async def get_storyboard_endpoint(storyboard_id: str):
    """Lấy chi tiết storyboard theo ID."""
    sb = get_storyboard(storyboard_id)
    if not sb:
        raise HTTPException(404, detail=f"Không tìm thấy storyboard: {storyboard_id}")
    return sb


@storyboard_router.get(
    "/{storyboard_id}/status",
    summary="Polling tiến độ storyboard & trạng thái ghép nối",
)
async def get_status_endpoint(storyboard_id: str):
    """Polling tiến độ tổng thể của storyboard."""
    return get_storyboard_status(storyboard_id)


@storyboard_router.post(
    "/{storyboard_id}/stitch",
    summary="Kích hoạt ghép nối lại toàn bộ video",
)
async def stitch_storyboard_endpoint(storyboard_id: str):
    """Kích hoạt ghép nối và lồng tiếng lại video hoàn chỉnh."""
    merged_url = trigger_stitching(storyboard_id)
    if not merged_url:
        raise HTTPException(400, detail="Chưa đủ điều kiện ghép video (tất cả segment phải completed).")
    return {"success": True, "merged_video_url": merged_url}


@storyboard_router.post(
    "/{storyboard_id}/segment/{segment_id}/regenerate",
    summary="Tạo lại một segment với prompt tùy chỉnh",
)
async def regenerate_segment_endpoint(
    request: Request,
    storyboard_id: str,
    segment_id: str,
    payload: SegmentRegenerateRequest,
):
    """Tạo lại một segment với prompt tùy chỉnh."""
    enforce_rate_limit(
        request,
        limit=settings.STORYBOARD_RATE_LIMIT,
        key_prefix="storyboard_regen",
    )
    return regenerate_segment(storyboard_id, segment_id, payload.custom_video_prompt)


@storyboard_router.post(
    "/{storyboard_id}/segment/{segment_id}/retry",
    summary="Thử lại segment bị lỗi",
)
async def retry_segment_endpoint(
    request: Request,
    storyboard_id: str,
    segment_id: str,
):
    """Thử lại segment bị lỗi (dùng prompt cũ)."""
    enforce_rate_limit(
        request,
        limit=settings.STORYBOARD_RATE_LIMIT,
        key_prefix="storyboard_retry",
    )
    return regenerate_segment(storyboard_id, segment_id, None)


@storyboard_router.delete(
    "/{storyboard_id}",
    summary="Xóa storyboard",
)
async def delete_storyboard_endpoint(storyboard_id: str):
    """Xóa storyboard theo ID."""
    delete_storyboard(storyboard_id)
    return JSONResponse(content={"success": True, "deleted_id": storyboard_id})
