from typing import List, Optional
from pydantic import BaseModel, Field


class StoryboardSegment(BaseModel):
    """Một phân đoạn video trong storyboard"""
    id: str = Field(..., description="ID duy nhất của segment")
    order: int = Field(..., description="Thứ tự trong storyboard (1-based)")
    text: str = Field(..., description="Nội dung thoại của segment")
    start_sec: float = Field(default=0.0, description="Thời điểm bắt đầu (giây)")
    end_sec: float = Field(default=0.0, description="Thời điểm kết thúc (giây)")
    timecode: Optional[str] = Field(
        default=None, description="Chuỗi timecode SRT (vd: 00:00:00,100 --> 00:00:04,292)"
    )
    video_prompt: Optional[str] = Field(
        default=None, description="Prompt video do GPT-120B sinh"
    )
    video_url: Optional[str] = Field(
        default=None, description="URL video từ Pixazo R2 CDN"
    )
    request_id: Optional[str] = Field(
        default=None, description="ID request từ Pixazo (để poll lại nếu crash)"
    )
    status: str = Field(
        default="pending",
        description="Trạng thái: pending | processing | completed | failed"
    )
    error: Optional[str] = Field(
        default=None, description="Thông báo lỗi nếu status=failed"
    )
    duration_sec: float = Field(
        default=0.0, description="Thời lượng video (giây)"
    )
    num_frames: int = Field(
        default=121, description="Số frame (dạng 1+8k, tối đa 121)"
    )


class StoryboardResponse(BaseModel):
    """Response trả về khi tạo hoặc lấy storyboard"""
    storyboard_id: str = Field(..., description="ID duy nhất của storyboard")
    title: str = Field(..., description="Tiêu đề storyboard")
    status: str = Field(
        default="pending",
        description="Trạng thái tổng thể: pending | processing | completed | failed"
    )
    segments: List[StoryboardSegment] = Field(
        default_factory=list, description="Danh sách các segment"
    )
    total: int = Field(default=0, description="Tổng số segment")
    completed: int = Field(default=0, description="Số segment đã hoàn thành")
    audio_duration_sec: float = Field(
        default=0.0, description="Thời lượng file MP3 (giây)"
    )
    total_duration_sec: float = Field(
        default=0.0, description="Tổng thời lượng kịch bản (giây)"
    )
    merged_video_url: Optional[str] = Field(
        default=None, description="URL video hoàn chỉnh sau khi ghép và lồng tiếng"
    )
    has_audio: bool = Field(
        default=False, description="Có đính kèm âm thanh MP3 lồng tiếng hay không"
    )
    is_stitching: bool = Field(
        default=False, description="Trạng thái đang tiến hành ghép nối video"
    )
    frame_rate: int = Field(default=16, description="FPS sử dụng")
    aspect: str = Field(default="16:9", description="Tỷ lệ khung hình")
    created_at: str = Field(..., description="Timestamp ISO tạo storyboard")


class SegmentRegenerateRequest(BaseModel):
    """Request tạo lại một segment"""
    storyboard_id: str = Field(..., description="ID storyboard chứa segment")
    segment_id: str = Field(..., description="ID segment cần tạo lại")
    custom_video_prompt: Optional[str] = Field(
        default=None,
        description="Prompt tùy chỉnh (nếu None thì dùng prompt cũ)"
    )


class SegmentStatusResponse(BaseModel):
    """Response trạng thái của một segment"""
    segment_id: str = Field(..., description="ID segment")
    status: str = Field(..., description="pending | processing | completed | failed")
    video_url: Optional[str] = Field(default=None, description="URL video nếu completed")
    error: Optional[str] = Field(default=None, description="Lỗi nếu failed")
