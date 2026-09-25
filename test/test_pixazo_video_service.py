# test_pixazo_video_service.py – Unit tests cho services/pixazo_video_service.py
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

from services.pixazo_video_service import PixazoVideoService


def _mock_response(status_code: int, json_data=None, text: str = ""):
    """Tạo mock requests.Response."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data if json_data is not None else {}
    resp.text = text
    return resp


def _patch_settings(**overrides):
    """Patch settings với giá trị mặc định hợp lệ."""
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


class TestBuildHeaders:
    def test_missing_api_key_raises_400(self):
        with _patch_settings(PIXAZO_API_KEY=""):
            with pytest.raises(HTTPException) as exc:
                PixazoVideoService._build_headers()
            assert exc.value.status_code == 400

    def test_placeholder_api_key_raises_400(self):
        with _patch_settings(PIXAZO_API_KEY="YOUR_SUBSCRIPTION_KEY"):
            with pytest.raises(HTTPException) as exc:
                PixazoVideoService._build_headers()
            assert exc.value.status_code == 400

    def test_valid_key_returns_headers(self):
        with _patch_settings():
            headers = PixazoVideoService._build_headers()
            assert headers["Ocp-Apim-Subscription-Key"] == "valid-key"


class TestHandleError:
    @pytest.mark.parametrize("status", [401, 402, 403, 429])
    def test_maps_known_status_codes(self, status):
        resp = _mock_response(status, text="err")
        with pytest.raises(HTTPException) as exc:
            PixazoVideoService._handle_error(resp)
        assert exc.value.status_code == status

    def test_unknown_status_uses_generic_message(self):
        resp = _mock_response(418, text="teapot")
        with pytest.raises(HTTPException) as exc:
            PixazoVideoService._handle_error(resp)
        assert exc.value.status_code == 418
        assert "teapot" in exc.value.detail


class TestSubmitVideoJob:
    def test_submit_job_success(self):
        payload = {"request_id": "ltx-1", "status": "QUEUED"}
        with _patch_settings(), patch(
            "services.pixazo_video_service.requests.post",
            return_value=_mock_response(202, payload),
        ) as mock_post:
            result = PixazoVideoService.submit_video_job("a cat")
            assert result["request_id"] == "ltx-1"
            body = mock_post.call_args.kwargs["json"]
            assert body["prompt"] == "a cat"
            assert body["negative"] == "blurry"
            assert "seed" not in body

    def test_submit_job_includes_seed_when_provided(self):
        with _patch_settings(), patch(
            "services.pixazo_video_service.requests.post",
            return_value=_mock_response(202, {"request_id": "x"}),
        ) as mock_post:
            PixazoVideoService.submit_video_job("a cat", seed=42)
            assert mock_post.call_args.kwargs["json"]["seed"] == 42

    def test_submit_job_401(self):
        with _patch_settings(), patch(
            "services.pixazo_video_service.requests.post",
            return_value=_mock_response(401, text="unauth"),
        ):
            with pytest.raises(HTTPException) as exc:
                PixazoVideoService.submit_video_job("a cat")
            assert exc.value.status_code == 401

    def test_submit_job_402(self):
        with _patch_settings(), patch(
            "services.pixazo_video_service.requests.post",
            return_value=_mock_response(402, text="no balance"),
        ):
            with pytest.raises(HTTPException) as exc:
                PixazoVideoService.submit_video_job("a cat")
            assert exc.value.status_code == 402

    def test_submit_job_429(self):
        with _patch_settings(), patch(
            "services.pixazo_video_service.requests.post",
            return_value=_mock_response(429, text="slow down"),
        ):
            with pytest.raises(HTTPException) as exc:
                PixazoVideoService.submit_video_job("a cat")
            assert exc.value.status_code == 429

    def test_submit_job_timeout(self):
        import requests as req
        with _patch_settings(), patch(
            "services.pixazo_video_service.requests.post",
            side_effect=req.exceptions.Timeout(),
        ):
            with pytest.raises(HTTPException) as exc:
                PixazoVideoService.submit_video_job("a cat")
            assert exc.value.status_code == 504

    def test_submit_job_connection_error(self):
        import requests as req
        with _patch_settings(), patch(
            "services.pixazo_video_service.requests.post",
            side_effect=req.exceptions.ConnectionError("boom"),
        ):
            with pytest.raises(HTTPException) as exc:
                PixazoVideoService.submit_video_job("a cat")
            assert exc.value.status_code == 500


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
        import requests as req
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
