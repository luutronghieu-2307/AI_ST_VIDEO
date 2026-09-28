# test_pixazo_video_polling.py – Unit tests polling & completion cho PixazoVideoService
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
import requests as req

from services.pixazo_video_service import PixazoVideoService


def _mock_response(status_code: int, json_data=None, text: str = ""):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data if json_data is not None else {}
    resp.text = text
    return resp


def _patch_settings(**overrides):
    defaults = {
        "PIXAZO_API_KEY": "valid-key",
        "PIXAZO_VIDEO_GATEWAY_URL": "https://gw/ttv",
        "PIXAZO_STATUS_URL": "https://gw/status",
        "VIDEO_REQUEST_TIMEOUT": 180,
        "VIDEO_POLL_INTERVAL_START": 5,
        "VIDEO_POLL_INTERVAL_MAX": 20,
        "VIDEO_POLL_MAX_ATTEMPTS": 90,
        "VIDEO_DEFAULT_NEGATIVE": "blurry",
    }
    defaults.update(overrides)
    return patch("services.pixazo_video_service.settings", **defaults)


class TestPollStatus:
    def test_poll_status_success(self):
        with _patch_settings(), patch(
            "services.pixazo_video_service.requests.get",
            return_value=_mock_response(200, {"status": "PROCESSING"}),
        ) as mock_get:
            result = PixazoVideoService.poll_status("ltx-1")
            assert result["status"] == "PROCESSING"
            assert mock_get.call_args.args[0] == "https://gw/status/ltx-1"

    def test_poll_status_404(self):
        with _patch_settings(), patch(
            "services.pixazo_video_service.requests.get",
            return_value=_mock_response(404, text="not found"),
        ):
            with pytest.raises(HTTPException) as exc:
                PixazoVideoService.poll_status("ltx-1")
            assert exc.value.status_code == 404

    def test_poll_status_timeout(self):
        with _patch_settings(), patch(
            "services.pixazo_video_service.requests.get",
            side_effect=req.exceptions.Timeout(),
        ):
            with pytest.raises(HTTPException) as exc:
                PixazoVideoService.poll_status("ltx-1")
            assert exc.value.status_code == 504


class TestWaitForCompletion:
    def test_wait_for_completion_immediate(self):
        with _patch_settings(), patch.object(
            PixazoVideoService, "poll_status",
            return_value={"status": "COMPLETED", "output": {}},
        ):
            result = PixazoVideoService.wait_for_completion("ltx-1")
            assert result["status"] == "COMPLETED"

    def test_wait_for_completion_after_polls(self):
        seq = [
            {"status": "QUEUED"},
            {"status": "PROCESSING"},
            {"status": "COMPLETED", "output": {}},
        ]
        with _patch_settings(), patch.object(
            PixazoVideoService, "poll_status", side_effect=seq
        ), patch("services.pixazo_video_service.time.sleep") as mock_sleep:
            result = PixazoVideoService.wait_for_completion("ltx-1")
            assert result["status"] == "COMPLETED"
            assert mock_sleep.call_count == 2

    def test_wait_for_completion_failed(self):
        with _patch_settings(), patch.object(
            PixazoVideoService, "poll_status",
            return_value={"status": "FAILED", "error": "boom"},
        ):
            with pytest.raises(HTTPException) as exc:
                PixazoVideoService.wait_for_completion("ltx-1")
            assert exc.value.status_code == 500
            assert "boom" in exc.value.detail

    def test_wait_for_completion_error_status(self):
        with _patch_settings(), patch.object(
            PixazoVideoService, "poll_status",
            return_value={"status": "ERROR", "error": None},
        ):
            with pytest.raises(HTTPException) as exc:
                PixazoVideoService.wait_for_completion("ltx-1")
            assert exc.value.status_code == 500

    def test_wait_for_completion_timeout(self):
        with _patch_settings(VIDEO_POLL_MAX_ATTEMPTS=3), patch.object(
            PixazoVideoService, "poll_status",
            return_value={"status": "PROCESSING"},
        ), patch("services.pixazo_video_service.time.sleep"):
            with pytest.raises(HTTPException) as exc:
                PixazoVideoService.wait_for_completion("ltx-1")
            assert exc.value.status_code == 504

    def test_wait_interval_increases(self):
        seq = [{"status": "PROCESSING"}] * 4 + [{"status": "COMPLETED"}]
        with _patch_settings(), patch.object(
            PixazoVideoService, "poll_status", side_effect=seq
        ), patch("services.pixazo_video_service.time.sleep") as mock_sleep:
            PixazoVideoService.wait_for_completion("ltx-1")
            intervals = [c.args[0] for c in mock_sleep.call_args_list]
            assert intervals == [5, 10, 15, 20]


class TestGenerateVideo:
    def test_generate_video_success(self):
        with _patch_settings(), patch.object(
            PixazoVideoService, "submit_video_job",
            return_value={"request_id": "ltx-1"},
        ), patch.object(
            PixazoVideoService, "wait_for_completion",
            return_value={"output": {"media_url": ["https://cdn/v.mp4"]}},
        ):
            url = PixazoVideoService.generate_video("a cat")
            assert url == "https://cdn/v.mp4"

    def test_generate_video_no_media_url(self):
        with _patch_settings(), patch.object(
            PixazoVideoService, "submit_video_job",
            return_value={"request_id": "ltx-1"},
        ), patch.object(
            PixazoVideoService, "wait_for_completion",
            return_value={"output": {"media_url": []}},
        ):
            with pytest.raises(HTTPException) as exc:
                PixazoVideoService.generate_video("a cat")
            assert exc.value.status_code == 500

    def test_generate_video_no_request_id(self):
        with _patch_settings(), patch.object(
            PixazoVideoService, "submit_video_job", return_value={}
        ):
            with pytest.raises(HTTPException) as exc:
                PixazoVideoService.generate_video("a cat")
            assert exc.value.status_code == 500
