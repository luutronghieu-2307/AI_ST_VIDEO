# test_pixazo_video_submit.py – Unit tests submit & headers cho PixazoVideoService
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
        with _patch_settings(), patch(
            "services.pixazo_video_service.requests.post",
            side_effect=req.exceptions.Timeout(),
        ):
            with pytest.raises(HTTPException) as exc:
                PixazoVideoService.submit_video_job("a cat")
            assert exc.value.status_code == 504

    def test_submit_job_connection_error(self):
        with _patch_settings(), patch(
            "services.pixazo_video_service.requests.post",
            side_effect=req.exceptions.ConnectionError("boom"),
        ):
            with pytest.raises(HTTPException) as exc:
                PixazoVideoService.submit_video_job("a cat")
            assert exc.value.status_code == 500
