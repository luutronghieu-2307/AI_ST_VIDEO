# test_groq_service.py – Unit tests cho services/groq_service.py
# Yêu cầu độ bao phủ: >= 90%

import pytest
import requests
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from services.groq_service import GroqService


class TestCallChatCompletions:
    def test_call_chat_completions_content_success(self):
        with patch("services.groq_service.requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "choices": [{"message": {"content": "Detailed prompt here"}}]
            }
            mock_post.return_value = mock_resp

            result = GroqService._call_chat_completions(
                api_key="gsk_valid",
                model="llama-3.2-11b-vision-preview",
                messages=[{"role": "user", "content": "Hi"}]
            )
            assert result == "Detailed prompt here"

    def test_call_chat_completions_reasoning_success(self):
        with patch("services.groq_service.requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "choices": [{"message": {"content": "", "reasoning": "Reasoning prompt here"}}]
            }
            mock_post.return_value = mock_resp

            result = GroqService._call_chat_completions(
                api_key="gsk_valid",
                model="openai/gpt-oss-120b",
                messages=[{"role": "user", "content": "Hi"}]
            )
            assert result == "Reasoning prompt here"

    def test_call_chat_completions_401_invalid_key(self):
        with patch("services.groq_service.requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 401
            mock_post.return_value = mock_resp

            with pytest.raises(HTTPException) as exc_info:
                GroqService._call_chat_completions("bad-key", "m", [])
            assert exc_info.value.status_code == 401

    def test_call_chat_completions_429_rate_limit(self):
        with patch("services.groq_service.requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 429
            mock_post.return_value = mock_resp

            with pytest.raises(HTTPException) as exc_info:
                GroqService._call_chat_completions("key", "m", [])
            assert exc_info.value.status_code == 429

    def test_call_chat_completions_other_error(self):
        with patch("services.groq_service.requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 503
            mock_resp.headers = {"content-type": "application/json"}
            mock_resp.json.return_value = {"error": {"message": "Service unavailable"}}
            mock_post.return_value = mock_resp

            with pytest.raises(HTTPException) as exc_info:
                GroqService._call_chat_completions("key", "m", [])
            assert exc_info.value.status_code == 503

    def test_call_chat_completions_empty_result(self):
        with patch("services.groq_service.requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "choices": [{"message": {"content": "   "}}]
            }
            mock_post.return_value = mock_resp

            with pytest.raises(HTTPException) as exc_info:
                GroqService._call_chat_completions("key", "m", [])
            assert exc_info.value.status_code == 500

    def test_call_chat_completions_timeout(self):
        with patch("services.groq_service.requests.post") as mock_post:
            mock_post.side_effect = requests.exceptions.Timeout("Timeout")
            with pytest.raises(HTTPException) as exc_info:
                GroqService._call_chat_completions("key", "m", [])
            assert exc_info.value.status_code == 504

    def test_call_chat_completions_request_exception(self):
        with patch("services.groq_service.requests.post") as mock_post:
            mock_post.side_effect = requests.exceptions.ConnectionError("Failed")
            with pytest.raises(HTTPException) as exc_info:
                GroqService._call_chat_completions("key", "m", [])
            assert exc_info.value.status_code == 500


class TestGetVisionModels:
    def test_get_vision_models_no_key(self):
        assert GroqService.get_vision_models("") == []
        assert GroqService.get_vision_models("YOUR_KEY") == []

    def test_get_vision_models_success(self):
        with patch("services.groq_service.requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "data": [
                    {"id": "meta-llama/llama-4-scout-17b-preview", "active": True, "input_modalities": ["text", "image"]},
                    {"id": "llama-3.1-8b-instant", "active": True, "input_modalities": ["text"]},
                    {"id": "inactive-vision", "active": False, "input_modalities": ["image"]},
                ]
            }
            mock_get.return_value = mock_resp

            models = GroqService.get_vision_models("gsk_valid")
            assert len(models) == 1
            assert models[0]["id"] == "meta-llama/llama-4-scout-17b-preview"

    def test_get_vision_models_401(self):
        with patch("services.groq_service.requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 401
            mock_get.return_value = mock_resp

            with pytest.raises(HTTPException) as exc_info:
                GroqService.get_vision_models("invalid_key")
            assert exc_info.value.status_code == 401

    def test_get_vision_models_timeout(self):
        with patch("services.groq_service.requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout("Timeout")
            with pytest.raises(HTTPException) as exc_info:
                GroqService.get_vision_models("key")
            assert exc_info.value.status_code == 504


class TestSuggestPrompt:
    def test_suggest_prompt_missing_key(self):
        with pytest.raises(HTTPException) as exc_info:
            GroqService.suggest_prompt("dGVzdA==", "image/png", "")
        assert exc_info.value.status_code == 400

    def test_suggest_prompt_standard_mode(self):
        with patch.object(GroqService, "_call_chat_completions") as mock_call:
            mock_call.return_value = "Standard vision prompt"
            result = GroqService.suggest_prompt(
                image_base64="dGVzdA==",
                image_mime="image/png",
                api_key="gsk_key",
                mode="standard"
            )
            assert result == "Standard vision prompt"
            assert mock_call.call_count == 1

    def test_suggest_prompt_advanced_mode(self):
        with patch.object(GroqService, "_call_chat_completions") as mock_call:
            mock_call.side_effect = ["Baseline prompt", "Enhanced 120B creative prompt"]
            result = GroqService.suggest_prompt(
                image_base64="dGVzdA==",
                image_mime="image/png",
                api_key="gsk_key",
                mode="advanced"
            )
            assert result == "Enhanced 120B creative prompt"
            assert mock_call.call_count == 2
