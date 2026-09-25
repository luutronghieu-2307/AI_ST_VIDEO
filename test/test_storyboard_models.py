import pytest
from pydantic import ValidationError

from models.storyboard import (
    StoryboardSegment,
    StoryboardResponse,
    SegmentRegenerateRequest,
    SegmentStatusResponse,
)


class TestStoryboardSegment:
    def test_segment_defaults(self):
        seg = StoryboardSegment(id="seg_1", order=1, text="Hello")
        assert seg.status == "pending"
        assert seg.video_prompt is None
        assert seg.video_url is None
        assert seg.request_id is None
        assert seg.error is None
        assert seg.duration_sec == 0.0
        assert seg.num_frames == 121
        assert seg.start_sec == 0.0
        assert seg.end_sec == 0.0
        assert seg.timecode is None

    def test_segment_required_fields(self):
        with pytest.raises(ValidationError):
            StoryboardSegment(order=1, text="Hello")  # thiếu id

        with pytest.raises(ValidationError):
            StoryboardSegment(id="seg_1", text="Hello")  # thiếu order

        with pytest.raises(ValidationError):
            StoryboardSegment(id="seg_1", order=1)  # thiếu text

    def test_segment_full(self):
        seg = StoryboardSegment(
            id="seg_1",
            order=1,
            text="Test",
            start_sec=0.1,
            end_sec=4.292,
            timecode="00:00:00,100 --> 00:00:04,292",
            video_prompt="A documentary shot...",
            video_url="https://cdn.example.com/v.mp4",
            request_id="ltx-123",
            status="completed",
            error=None,
            duration_sec=4.192,
            num_frames=65,
        )
        assert seg.status == "completed"
        assert seg.video_url == "https://cdn.example.com/v.mp4"
        assert seg.num_frames == 65
        assert seg.start_sec == 0.1
        assert seg.timecode == "00:00:00,100 --> 00:00:04,292"


class TestStoryboardResponse:
    def test_response_defaults(self):
        resp = StoryboardResponse(
            storyboard_id="sb_1",
            title="Test",
            created_at="2026-09-22T12:00:00+00:00",
        )
        assert resp.status == "pending"
        assert resp.segments == []
        assert resp.total == 0
        assert resp.completed == 0
        assert resp.audio_duration_sec == 0.0
        assert resp.total_duration_sec == 0.0
        assert resp.merged_video_url is None
        assert resp.has_audio is False
        assert resp.is_stitching is False
        assert resp.frame_rate == 16
        assert resp.aspect == "16:9"

    def test_response_full(self):
        seg = StoryboardSegment(id="seg_1", order=1, text="Hello")
        resp = StoryboardResponse(
            storyboard_id="sb_abc",
            title="AI và tương lai",
            status="completed",
            segments=[seg],
            total=1,
            completed=1,
            audio_duration_sec=22.09,
            total_duration_sec=22.09,
            merged_video_url="/static/merged_videos/sb_abc_final.mp4",
            has_audio=True,
            is_stitching=False,
            frame_rate=16,
            aspect="16:9",
            created_at="2026-09-22T12:00:00+00:00",
        )
        assert resp.total == 1
        assert resp.merged_video_url == "/static/merged_videos/sb_abc_final.mp4"
        assert resp.has_audio is True


class TestSegmentRegenerateRequest:
    def test_regenerate_optional_prompt(self):
        req = SegmentRegenerateRequest(storyboard_id="sb_1", segment_id="seg_1")
        assert req.custom_video_prompt is None

    def test_regenerate_with_prompt(self):
        req = SegmentRegenerateRequest(
            storyboard_id="sb_1",
            segment_id="seg_1",
            custom_video_prompt="Custom prompt here",
        )
        assert req.custom_video_prompt == "Custom prompt here"


class TestSegmentStatusResponse:
    def test_status_response_minimal(self):
        resp = SegmentStatusResponse(segment_id="seg_1", status="pending")
        assert resp.video_url is None
        assert resp.error is None
