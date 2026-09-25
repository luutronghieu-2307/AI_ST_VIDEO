# test_storyboard_orchestrator.py – Unit tests cho services/storyboard_orchestrator.py
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

import pytest
from fastapi import HTTPException

from models.storyboard import StoryboardResponse, StoryboardSegment
from services import storyboard_orchestrator as orch

SAMPLE_SRT = """1
00:00:00,100 --> 00:00:04,292
Hello world
"""


def _make_segment(seg_id="seg-1", status="pending", num_frames=65):
    return StoryboardSegment(
        id=seg_id, order=1, text="Hello world", num_frames=num_frames, status=status
    )


def _make_storyboard(sb_id="sb-1", created_at=None, segments=None):
    return StoryboardResponse(
        storyboard_id=sb_id,
        title="Test",
        segments=segments or [_make_segment()],
        total=len(segments) if segments else 1,
        created_at=created_at or datetime.now(timezone.utc).isoformat(),
    )


@pytest.fixture
def sb_dir(tmp_path):
    target = str(tmp_path / "storyboards")
    with patch("services.storyboard_store.settings") as mock_s:
        mock_s.STORYBOARD_DIR = target
        mock_s.MAX_STORYBOARDS = 50
        yield target


class TestCreateStoryboard:
    def test_create_storyboard_ok(self, sb_dir):
        with patch.object(orch.threading, "Thread") as mock_thread:
            sb = orch.create_storyboard(
                srt_content=SAMPLE_SRT,
                title="Title",
                audio_bytes=b"fake_mp3_data",
                audio_filename="voice.mp3",
            )
            assert sb.status == "pending"
            assert sb.total == 1
            assert sb.has_audio is True
            assert sb.frame_rate == 16
            mock_thread.return_value.start.assert_called_once()

    def test_create_storyboard_invalid_srt(self, sb_dir):
        with pytest.raises(HTTPException) as exc:
            orch.create_storyboard(srt_content="", title="T")
        assert exc.value.status_code == 400


class TestProcessSegment:
    def test_process_segment_ok(self):
        seg = _make_segment()
        with patch.object(orch, "build_video_prompt", return_value="a prompt"), \
             patch.object(
                 orch.pixazo_video_service, "submit_video_job",
                 return_value={"request_id": "req-1"},
             ), \
             patch.object(
                 orch.pixazo_video_service, "wait_for_completion",
                 return_value={"output": {"media_url": ["https://v/1.mp4"]}},
             ):
            result = orch.process_segment(seg, "ctx")
            assert result.status == "completed"
            assert result.video_url == "https://v/1.mp4"
            assert result.video_prompt == "a prompt"

    def test_process_segment_no_media_url_marks_failed(self):
        seg = _make_segment()
        with patch.object(orch, "build_video_prompt", return_value="p"), \
             patch.object(
                 orch.pixazo_video_service, "submit_video_job",
                 return_value={"request_id": "req-1"},
             ), \
             patch.object(
                 orch.pixazo_video_service, "wait_for_completion",
                 return_value={"output": {"media_url": []}},
             ):
            result = orch.process_segment(seg, "ctx")
            assert result.status == "failed"


class TestTriggerStitching:
    def test_trigger_stitching_success(self, sb_dir):
        seg = _make_segment(status="completed")
        seg.video_url = "https://cdn.example.com/v1.mp4"
        sb = _make_storyboard(segments=[seg])
        sb.completed = 1
        sb.total = 1
        from services.storyboard_store import save_storyboard
        save_storyboard(sb)

        with patch.object(orch, "stitch_and_mux_storyboard", return_value="/static/merged_videos/sb-1_final.mp4"):
            url = orch.trigger_stitching("sb-1")
            assert url == "/static/merged_videos/sb-1_final.mp4"

    def test_trigger_stitching_incomplete(self, sb_dir):
        seg = _make_segment(status="processing")
        sb = _make_storyboard(segments=[seg])
        sb.completed = 0
        from services.storyboard_store import save_storyboard
        save_storyboard(sb)
        assert orch.trigger_stitching("sb-1") is None

    def test_trigger_stitching_missing_url(self, sb_dir):
        seg = _make_segment(status="completed")
        seg.video_url = None
        sb = _make_storyboard(segments=[seg])
        sb.completed = 1
        sb.total = 1
        from services.storyboard_store import save_storyboard
        save_storyboard(sb)
        assert orch.trigger_stitching("sb-1") is None

    def test_trigger_stitching_exception_handled(self, sb_dir):
        seg = _make_segment(status="completed")
        seg.video_url = "https://cdn.example.com/v1.mp4"
        sb = _make_storyboard(segments=[seg])
        sb.completed = 1
        sb.total = 1
        from services.storyboard_store import save_storyboard
        save_storyboard(sb)

        with patch.object(orch, "stitch_and_mux_storyboard", side_effect=Exception("FFmpeg failed")):
            url = orch.trigger_stitching("sb-1")
            assert url is None


class TestRunInBackground:
    def test_run_in_background_sequential(self, sb_dir):
        segs = [_make_segment("s1"), _make_segment("s2")]
        sb = _make_storyboard(segments=segs)
        sb.total = 2
        from services.storyboard_store import save_storyboard
        save_storyboard(sb)

        order = []

        def fake_process(segment, *args, **kwargs):
            order.append(segment.id)
            segment.status = "completed"
            segment.video_url = "https://v/x.mp4"
            return segment

        with patch.object(orch, "process_segment", side_effect=fake_process), \
             patch.object(orch, "trigger_stitching"):
            orch._run_in_background("sb-1", "ctx", None, None, None, "16:9")
        assert order == ["s1", "s2"]

    def test_run_in_background_retry_and_fail(self, sb_dir):
        seg = _make_segment("s1")
        sb = _make_storyboard(segments=[seg])
        from services.storyboard_store import save_storyboard
        save_storyboard(sb)

        with patch.object(orch, "process_segment", side_effect=HTTPException(500, detail="Server error")), \
             patch.object(orch.time, "sleep"), \
             patch.object(orch, "trigger_stitching"):
            orch._run_in_background("sb-1", "ctx", None, None, None, "16:9")


class TestRegenerateSegment:
    def test_regenerate_segment_ok(self, sb_dir):
        sb = _make_storyboard()
        from services.storyboard_store import save_storyboard
        save_storyboard(sb)

        def fake_process(segment, *args, **kwargs):
            segment.status = "completed"
            segment.video_url = "https://v/new.mp4"
            return segment

        with patch.object(orch, "process_segment", side_effect=fake_process), \
             patch.object(orch, "trigger_stitching"):
            result = orch.regenerate_segment("sb-1", "seg-1")
            assert result.video_url == "https://v/new.mp4"

    def test_regenerate_segment_not_found(self, sb_dir):
        with pytest.raises(HTTPException) as exc:
            orch.regenerate_segment("nope", "seg-1")
        assert exc.value.status_code == 404

    def test_regenerate_segment_error_handled(self, sb_dir):
        sb = _make_storyboard()
        from services.storyboard_store import save_storyboard
        save_storyboard(sb)

        with patch.object(orch, "process_segment", side_effect=HTTPException(500, detail="fail")):
            with pytest.raises(HTTPException):
                orch.regenerate_segment("sb-1", "seg-1")


class TestGetStoryboardStatus:
    def test_get_status_ok(self, sb_dir):
        sb = _make_storyboard()
        from services.storyboard_store import save_storyboard
        save_storyboard(sb)
        status = orch.get_storyboard_status("sb-1")
        assert status["storyboard_id"] == "sb-1"
        assert status["total"] == 1
        assert len(status["segments"]) == 1

    def test_get_status_not_found(self, sb_dir):
        with pytest.raises(HTTPException):
            orch.get_storyboard_status("nope")


class TestCleanupStuckSegments:
    def test_cleanup_stuck_segments(self, sb_dir):
        old_time = (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat()
        sb = _make_storyboard(
            created_at=old_time, segments=[_make_segment(status="processing")]
        )
        from services.storyboard_store import save_storyboard, get_storyboard
        save_storyboard(sb)

        cleaned = orch.cleanup_stuck_segments()
        assert cleaned == 1
        updated = get_storyboard("sb-1")
        assert updated.segments[0].status == "failed"
