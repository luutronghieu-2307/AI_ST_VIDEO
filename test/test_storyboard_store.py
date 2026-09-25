# test_storyboard_store.py – Unit tests cho services/storyboard_store.py
import json
import os
import threading
from unittest.mock import patch

import pytest
from fastapi import HTTPException

from models.storyboard import StoryboardResponse, StoryboardSegment
from services import storyboard_store


def _make_storyboard(sb_id: str = "sb-1", created_at: str = "2026-01-01T00:00:00+00:00"):
    """Tạo StoryboardResponse mẫu."""
    return StoryboardResponse(
        storyboard_id=sb_id,
        title="Test SB",
        segments=[
            StoryboardSegment(id="seg-1", order=1, text="Hello"),
            StoryboardSegment(id="seg-2", order=2, text="World"),
        ],
        total=2,
        created_at=created_at,
    )


@pytest.fixture
def sb_dir(tmp_path):
    """Patch settings.STORYBOARD_DIR trỏ vào tmp_path."""
    target = str(tmp_path / "storyboards")
    with patch("services.storyboard_store.settings") as mock_s:
        mock_s.STORYBOARD_DIR = target
        mock_s.MAX_STORYBOARDS = 50
        yield target


class TestSaveStoryboard:
    def test_save_storyboard_ok(self, sb_dir):
        sb = _make_storyboard()
        result = storyboard_store.save_storyboard(sb)
        assert result.storyboard_id == "sb-1"
        assert os.path.exists(os.path.join(sb_dir, "sb-1.json"))

    def test_save_creates_dir(self, sb_dir):
        assert not os.path.exists(sb_dir)
        storyboard_store.save_storyboard(_make_storyboard())
        assert os.path.isdir(sb_dir)

    def test_save_raises_500_on_write_error(self, sb_dir):
        sb = _make_storyboard()
        with patch("builtins.open", side_effect=OSError("disk full")):
            with pytest.raises(HTTPException) as exc:
                storyboard_store.save_storyboard(sb)
            assert exc.value.status_code == 500


class TestGetStoryboard:
    def test_get_storyboard_ok(self, sb_dir):
        storyboard_store.save_storyboard(_make_storyboard())
        sb = storyboard_store.get_storyboard("sb-1")
        assert sb is not None
        assert sb.title == "Test SB"
        assert len(sb.segments) == 2

    def test_get_storyboard_missing(self, sb_dir):
        assert storyboard_store.get_storyboard("nope") is None

    def test_get_storyboard_corrupt(self, sb_dir):
        os.makedirs(sb_dir, exist_ok=True)
        with open(os.path.join(sb_dir, "bad.json"), "w", encoding="utf-8") as f:
            f.write("{not valid json")
        assert storyboard_store.get_storyboard("bad") is None


class TestLoadStoryboards:
    def test_load_storyboards_empty(self, sb_dir):
        assert storyboard_store.load_storyboards() == []

    def test_load_storyboards_sorted(self, sb_dir):
        storyboard_store.save_storyboard(
            _make_storyboard("old", "2026-01-01T00:00:00+00:00")
        )
        storyboard_store.save_storyboard(
            _make_storyboard("new", "2026-06-01T00:00:00+00:00")
        )
        result = storyboard_store.load_storyboards()
        assert [s.storyboard_id for s in result] == ["new", "old"]

    def test_load_skips_corrupt(self, sb_dir):
        storyboard_store.save_storyboard(_make_storyboard("good"))
        os.makedirs(sb_dir, exist_ok=True)
        with open(os.path.join(sb_dir, "bad.json"), "w", encoding="utf-8") as f:
            f.write("garbage")
        result = storyboard_store.load_storyboards()
        assert len(result) == 1
        assert result[0].storyboard_id == "good"


class TestUpdateSegment:
    def test_update_segment_ok(self, sb_dir):
        storyboard_store.save_storyboard(_make_storyboard())
        ok = storyboard_store.update_segment(
            "sb-1", "seg-1", {"status": "completed", "video_url": "https://v/1.mp4"}
        )
        assert ok is True
        sb = storyboard_store.get_storyboard("sb-1")
        seg = next(s for s in sb.segments if s.id == "seg-1")
        assert seg.status == "completed"
        assert seg.video_url == "https://v/1.mp4"

    def test_update_segment_not_found(self, sb_dir):
        storyboard_store.save_storyboard(_make_storyboard())
        assert storyboard_store.update_segment("sb-1", "nope", {}) is False

    def test_update_segment_missing_storyboard(self, sb_dir):
        assert storyboard_store.update_segment("nope", "seg-1", {}) is False

    def test_update_segment_updates_completed(self, sb_dir):
        storyboard_store.save_storyboard(_make_storyboard())
        storyboard_store.update_segment("sb-1", "seg-1", {"status": "completed"})
        sb = storyboard_store.get_storyboard("sb-1")
        assert sb.completed == 1

    def test_update_segment_updates_status_completed(self, sb_dir):
        storyboard_store.save_storyboard(_make_storyboard())
        storyboard_store.update_segment("sb-1", "seg-1", {"status": "completed"})
        storyboard_store.update_segment("sb-1", "seg-2", {"status": "completed"})
        sb = storyboard_store.get_storyboard("sb-1")
        assert sb.status == "completed"

    def test_update_segment_updates_status_processing(self, sb_dir):
        storyboard_store.save_storyboard(_make_storyboard())
        storyboard_store.update_segment("sb-1", "seg-1", {"status": "processing"})
        sb = storyboard_store.get_storyboard("sb-1")
        assert sb.status == "processing"

    def test_update_segment_ignores_unknown_field(self, sb_dir):
        storyboard_store.save_storyboard(_make_storyboard())
        ok = storyboard_store.update_segment("sb-1", "seg-1", {"unknown": "x"})
        assert ok is True


class TestDeleteStoryboard:
    def test_delete_storyboard_ok(self, sb_dir):
        storyboard_store.save_storyboard(_make_storyboard())
        assert storyboard_store.delete_storyboard("sb-1") is True
        assert storyboard_store.get_storyboard("sb-1") is None

    def test_delete_storyboard_missing(self, sb_dir):
        with pytest.raises(HTTPException) as exc:
            storyboard_store.delete_storyboard("nope")
        assert exc.value.status_code == 404


class TestEnforceMaxStoryboards:
    def test_enforce_max_storyboards(self, sb_dir):
        with patch("services.storyboard_store.settings") as mock_s:
            mock_s.STORYBOARD_DIR = sb_dir
            mock_s.MAX_STORYBOARDS = 2
            for i in range(4):
                storyboard_store.save_storyboard(
                    _make_storyboard(f"sb-{i}", f"2026-01-0{i + 1}T00:00:00+00:00")
                )
            remaining = storyboard_store.load_storyboards()
            assert len(remaining) == 2
            # Giữ lại 2 mới nhất
            assert {s.storyboard_id for s in remaining} == {"sb-3", "sb-2"}

    def test_enforce_no_delete_under_limit(self, sb_dir):
        storyboard_store.save_storyboard(_make_storyboard("sb-1"))
        assert storyboard_store._enforce_max_storyboards() == 0


class TestThreadSafety:
    def test_file_lock_thread_safety(self, sb_dir):
        """Nhiều thread ghi đồng thời không làm hỏng file."""
        errors = []

        def worker(idx: int):
            try:
                storyboard_store.save_storyboard(_make_storyboard(f"sb-{idx}"))
            except Exception as e:  # pragma: no cover
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == []
        result = storyboard_store.load_storyboards()
        assert len(result) == 10
