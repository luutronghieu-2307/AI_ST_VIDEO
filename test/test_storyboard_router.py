import io
from unittest.mock import patch
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from routers.storyboard_router import storyboard_router


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(storyboard_router)
    return TestClient(app)


def _srt_file(name="subtitle.srt", content=b"1\n00:00:00,100 --> 00:00:04,292\nHello"):
    return {"srt_file": (name, io.BytesIO(content), "text/plain")}


def _mp3_file(name="audio.mp3", content_type="audio/mpeg", size=100):
    return {"audio_file": (name, io.BytesIO(b"x" * size), content_type)}


class TestCreateStoryboard:
    def test_create_storyboard_with_srt_text(self, client):
        with patch("routers.storyboard_router.enforce_rate_limit"), \
             patch("routers.storyboard_router.create_storyboard") as mock_create:
            mock_create.return_value = {
                "storyboard_id": "sb-1",
                "title": "T",
                "status": "pending",
                "segments": [],
                "total": 0,
                "completed": 0,
                "created_at": "2026-01-01T00:00:00+00:00",
            }
            resp = client.post(
                "/api/storyboard/create",
                data={"srt_text": "1\n00:00:00,100 --> 00:00:04,292\nHello", "title": "T"},
            )
            assert resp.status_code == 200
            assert resp.json()["storyboard_id"] == "sb-1"

    def test_create_storyboard_with_srt_file_and_mp3(self, client):
        with patch("routers.storyboard_router.enforce_rate_limit"), \
             patch("routers.storyboard_router.create_storyboard") as mock_create:
            mock_create.return_value = {
                "storyboard_id": "sb-1",
                "title": "T",
                "status": "pending",
                "segments": [],
                "total": 0,
                "completed": 0,
                "created_at": "2026-01-01T00:00:00+00:00",
            }
            files = {}
            files.update(_srt_file())
            files.update(_mp3_file())
            resp = client.post(
                "/api/storyboard/create",
                data={"title": "T"},
                files=files,
            )
            assert resp.status_code == 200

    def test_create_storyboard_with_non_utf8_srt(self, client):
        with patch("routers.storyboard_router.enforce_rate_limit"), \
             patch("routers.storyboard_router.create_storyboard") as mock_create:
            mock_create.return_value = {
                "storyboard_id": "sb-1",
                "title": "T",
                "status": "pending",
                "segments": [],
                "total": 0,
                "completed": 0,
                "created_at": "2026-01-01T00:00:00+00:00",
            }
            files = {"srt_file": ("sub.srt", io.BytesIO(b"\xff\xfe\x00\x00"), "text/plain")}
            resp = client.post(
                "/api/storyboard/create",
                data={"title": "T"},
                files=files,
            )
            assert resp.status_code == 200

    def test_create_storyboard_mp3_too_large(self, client):
        with patch("routers.storyboard_router.enforce_rate_limit"), \
             patch("routers.storyboard_router.settings") as mock_settings:
            mock_settings.STORYBOARD_RATE_LIMIT = 50
            mock_settings.AUDIO_MAX_FILE_SIZE = 10
            files = {}
            files.update(_srt_file())
            files.update(_mp3_file(size=100))
            resp = client.post(
                "/api/storyboard/create",
                data={"title": "T"},
                files=files,
            )
            assert resp.status_code == 400
            assert "quá lớn" in resp.json()["detail"]

    def test_create_missing_srt_and_text(self, client):
        with patch("routers.storyboard_router.enforce_rate_limit"):
            resp = client.post(
                "/api/storyboard/create",
                data={"title": "T"},
            )
            assert resp.status_code == 400


class TestStitchStoryboard:
    def test_stitch_ok(self, client):
        with patch("routers.storyboard_router.trigger_stitching", return_value="/static/merged_videos/sb-1_final.mp4"):
            resp = client.post("/api/storyboard/sb-1/stitch")
            assert resp.status_code == 200
            assert resp.json()["success"] is True

    def test_stitch_fail(self, client):
        with patch("routers.storyboard_router.trigger_stitching", return_value=None):
            resp = client.post("/api/storyboard/sb-1/stitch")
            assert resp.status_code == 400


class TestGetStoryboard:
    def test_get_storyboard_ok(self, client):
        with patch("routers.storyboard_router.get_storyboard") as mock_get:
            mock_get.return_value = {
                "storyboard_id": "sb-1",
                "title": "T",
                "status": "pending",
                "segments": [],
                "total": 0,
                "completed": 0,
                "created_at": "2026-01-01T00:00:00+00:00",
            }
            resp = client.get("/api/storyboard/sb-1")
            assert resp.status_code == 200

    def test_get_storyboard_404(self, client):
        with patch("routers.storyboard_router.get_storyboard", return_value=None):
            resp = client.get("/api/storyboard/nope")
            assert resp.status_code == 404

    def test_list_storyboards(self, client):
        with patch("routers.storyboard_router.load_storyboards", return_value=[]):
            resp = client.get("/api/storyboard/list")
            assert resp.status_code == 200

    def test_get_status_ok(self, client):
        with patch("routers.storyboard_router.get_storyboard_status", return_value={"status": "pending"}):
            resp = client.get("/api/storyboard/sb-1/status")
            assert resp.status_code == 200


class TestSegmentActions:
    def test_regenerate_segment_ok(self, client):
        with patch("routers.storyboard_router.enforce_rate_limit"), \
             patch("routers.storyboard_router.regenerate_segment", return_value={"id": "seg-1", "status": "completed"}):
            resp = client.post(
                "/api/storyboard/sb-1/segment/seg-1/regenerate",
                json={"storyboard_id": "sb-1", "segment_id": "seg-1", "custom_video_prompt": "new prompt"},
            )
            assert resp.status_code == 200

    def test_retry_segment_ok(self, client):
        with patch("routers.storyboard_router.enforce_rate_limit"), \
             patch("routers.storyboard_router.regenerate_segment", return_value={"id": "seg-1", "status": "completed"}):
            resp = client.post("/api/storyboard/sb-1/segment/seg-1/retry")
            assert resp.status_code == 200

    def test_delete_storyboard_ok(self, client):
        with patch("routers.storyboard_router.delete_storyboard", return_value=True):
            resp = client.delete("/api/storyboard/sb-1")
            assert resp.status_code == 200
            assert resp.json()["success"] is True
