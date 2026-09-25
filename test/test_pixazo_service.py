# test_pixazo_service.py – Unit tests cho services/pixazo_service.py
# Yêu cầu độ bao phủ: >= 90%

import pytest
import requests
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from models.generate import GenerateRequest
from services.pixazo_service import PixazoService


@pytest.fixture
def sample_payload():
    return GenerateRequest(
        prompt="A vibrant modern logo of a cybernetic eagle",
        num_steps=4,
        seed=42,
        height=512,
        width=512
    )


class TestPixazoService:
    def test_generate_image_success(self, sample_payload):
        with patch("services.pixazo_service.settings") as mock_s, \
             patch("services.pixazo_service.requests.post") as mock_post:
            mock_s.PIXAZO_API_KEY = "valid-key"
            mock_s.PIXAZO_GATEWAY_URL = "https://gateway.pixazo.ai/flux-1-schnell/v1/getData"
            mock_s.REQUEST_TIMEOUT = 10

            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"output": "https://cdn.pixazo.ai/image-123.png"}
            mock_post.return_value = mock_resp

            result = PixazoService.generate_image(sample_payload)
            assert result == "https://cdn.pixazo.ai/image-123.png"
            mock_post.assert_called_once()

    def test_generate_image_missing_api_key(self, sample_payload):
        with patch("services.pixazo_service.settings") as mock_s:
            mock_s.PIXAZO_API_KEY = ""
            with pytest.raises(HTTPException) as exc_info:
                PixazoService.generate_image(sample_payload)
            assert exc_info.value.status_code == 400

    def test_generate_image_placeholder_api_key(self, sample_payload):
        with patch("services.pixazo_service.settings") as mock_s:
            mock_s.PIXAZO_API_KEY = "YOUR_SUBSCRIPTION_KEY"
            with pytest.raises(HTTPException) as exc_info:
                PixazoService.generate_image(sample_payload)
            assert exc_info.value.status_code == 400

    def test_generate_image_gateway_error_response(self, sample_payload):
        with patch("services.pixazo_service.settings") as mock_s, \
             patch("services.pixazo_service.requests.post") as mock_post:
            mock_s.PIXAZO_API_KEY = "valid-key"
            mock_s.PIXAZO_GATEWAY_URL = "https://gateway.pixazo.ai/flux-1-schnell/v1/getData"
            mock_s.REQUEST_TIMEOUT = 10

            mock_resp = MagicMock()
            mock_resp.status_code = 401
            mock_resp.headers = {"content-type": "application/json"}
            mock_resp.json.return_value = {"message": "Invalid Subscription Key"}
            mock_post.return_value = mock_resp

            with pytest.raises(HTTPException) as exc_info:
                PixazoService.generate_image(sample_payload)
            assert exc_info.value.status_code == 401
            assert "Invalid Subscription Key" in exc_info.value.detail

    def test_generate_image_missing_output_field(self, sample_payload):
        with patch("services.pixazo_service.settings") as mock_s, \
             patch("services.pixazo_service.requests.post") as mock_post:
            mock_s.PIXAZO_API_KEY = "valid-key"
            mock_s.PIXAZO_GATEWAY_URL = "https://gateway.pixazo.ai/flux-1-schnell/v1/getData"
            mock_s.REQUEST_TIMEOUT = 10

            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"status": "ok"}  # Không có 'output'
            mock_post.return_value = mock_resp

            with pytest.raises(HTTPException) as exc_info:
                PixazoService.generate_image(sample_payload)
            assert exc_info.value.status_code == 500

    def test_generate_image_timeout_exception(self, sample_payload):
        with patch("services.pixazo_service.settings") as mock_s, \
             patch("services.pixazo_service.requests.post") as mock_post:
            mock_s.PIXAZO_API_KEY = "valid-key"
            mock_s.PIXAZO_GATEWAY_URL = "https://gateway.pixazo.ai/flux-1-schnell/v1/getData"
            mock_s.REQUEST_TIMEOUT = 10
            mock_post.side_effect = requests.exceptions.Timeout("Timeout")

            with pytest.raises(HTTPException) as exc_info:
                PixazoService.generate_image(sample_payload)
            assert exc_info.value.status_code == 504

    def test_generate_image_request_exception(self, sample_payload):
        with patch("services.pixazo_service.settings") as mock_s, \
             patch("services.pixazo_service.requests.post") as mock_post:
            mock_s.PIXAZO_API_KEY = "valid-key"
            mock_s.PIXAZO_GATEWAY_URL = "https://gateway.pixazo.ai/flux-1-schnell/v1/getData"
            mock_s.REQUEST_TIMEOUT = 10
            mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")

            with pytest.raises(HTTPException) as exc_info:
                PixazoService.generate_image(sample_payload)
            assert exc_info.value.status_code == 500
