# test_video_prompt_service.py – Unit tests cho services/video_prompt_service.py
# Yêu cầu độ bao phủ: >= 90%

import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

from services.video_prompt_service import (
    build_video_prompt,
    build_batch_video_prompts,
    SYSTEM_PROMPT_VIDEO,
    DEFAULT_NEGATIVE_PROMPT,
)


# ─── Tests: build_video_prompt ─────────────────────────────────────────────────

class TestBuildVideoPrompt:
    def test_build_ok(self):
        with patch("services.video_prompt_service.groq_service") as mock_groq, \
             patch("services.video_prompt_service.settings") as mock_s:
            mock_s.GROQ_API_KEY = "test-key"
            mock_s.GROQ_CREATIVE_MODEL = "openai/gpt-oss-120b"
            mock_groq._call_chat_completions.return_value = "Documentary shot of..."

            result = build_video_prompt("Test segment")
            assert result == "Documentary shot of..."
            mock_groq._call_chat_completions.assert_called_once()

    def test_build_empty_text(self):
        with pytest.raises(HTTPException) as exc:
            build_video_prompt("")
        assert exc.value.status_code == 400
        assert "không được để trống" in exc.value.detail

    def test_build_whitespace_text(self):
        with pytest.raises(HTTPException) as exc:
            build_video_prompt("   \n  ")
        assert exc.value.status_code == 400

    def test_build_with_context(self):
        with patch("services.video_prompt_service.groq_service") as mock_groq, \
             patch("services.video_prompt_service.settings") as mock_s:
            mock_s.GROQ_API_KEY = "test-key"
            mock_s.GROQ_CREATIVE_MODEL = "openai/gpt-oss-120b"
            mock_groq._call_chat_completions.return_value = "Prompt with context"

            result = build_video_prompt("Segment", context="AI và tương lai")
            assert result == "Prompt with context"

            # Kiểm tra context được truyền vào messages
            call_args = mock_groq._call_chat_completions.call_args
            messages = call_args.kwargs["messages"]
            assert "AI và tương lai" in messages[1]["content"]

    def test_build_custom_style(self):
        with patch("services.video_prompt_service.groq_service") as mock_groq, \
             patch("services.video_prompt_service.settings") as mock_s:
            mock_s.GROQ_API_KEY = "test-key"
            mock_s.GROQ_CREATIVE_MODEL = "openai/gpt-oss-120b"
            mock_groq._call_chat_completions.return_value = "Custom style prompt"

            result = build_video_prompt("Segment", style="anime, vibrant")
            assert result == "Custom style prompt"

            call_args = mock_groq._call_chat_completions.call_args
            messages = call_args.kwargs["messages"]
            assert "anime, vibrant" in messages[1]["content"]

    def test_build_uses_creative_model(self):
        with patch("services.video_prompt_service.groq_service") as mock_groq, \
             patch("services.video_prompt_service.settings") as mock_s:
            mock_s.GROQ_API_KEY = "test-key"
            mock_s.GROQ_CREATIVE_MODEL = "openai/gpt-oss-120b"
            mock_groq._call_chat_completions.return_value = "Prompt"

            build_video_prompt("Segment")

            call_args = mock_groq._call_chat_completions.call_args
            assert call_args.kwargs["model"] == "openai/gpt-oss-120b"

    def test_build_groq_401_fallback(self):
        with patch("services.video_prompt_service.groq_service") as mock_groq, \
             patch("services.video_prompt_service.settings") as mock_s:
            mock_s.GROQ_API_KEY = "bad-key"
            mock_s.GROQ_CREATIVE_MODEL = "openai/gpt-oss-120b"
            mock_groq._call_chat_completions.side_effect = HTTPException(
                status_code=401, detail="Invalid key"
            )

            res = build_video_prompt("Segment")
            assert "A cinematic documentary video shot" in res
            assert "Segment" in res

    def test_build_groq_429_fallback(self):
        with patch("services.video_prompt_service.groq_service") as mock_groq, \
             patch("services.video_prompt_service.settings") as mock_s:
            mock_s.GROQ_API_KEY = "test-key"
            mock_s.GROQ_CREATIVE_MODEL = "openai/gpt-oss-120b"
            mock_groq._call_chat_completions.side_effect = HTTPException(
                status_code=429, detail="Rate limit"
            )

            res = build_video_prompt("Segment")
            assert "A cinematic documentary video shot" in res
            assert "Segment" in res



# ─── Tests: build_batch_video_prompts ──────────────────────────────────────────

class TestBuildBatchVideoPrompts:
    def test_batch_normal(self):
        with patch("services.video_prompt_service.build_video_prompt") as mock_build:
            mock_build.side_effect = ["Prompt 1", "Prompt 2", "Prompt 3"]

            result = build_batch_video_prompts(["A", "B", "C"])
            assert result == ["Prompt 1", "Prompt 2", "Prompt 3"]
            assert mock_build.call_count == 3

    def test_batch_partial_failure(self):
        with patch("services.video_prompt_service.build_video_prompt") as mock_build:
            mock_build.side_effect = [
                "Prompt 1",
                HTTPException(status_code=500, detail="Error"),
                "Prompt 3",
            ]

            result = build_batch_video_prompts(["A", "B", "C"])
            assert result[0] == "Prompt 1"
            assert result[1] == ""  # Placeholder cho segment lỗi
            assert result[2] == "Prompt 3"

    def test_batch_empty(self):
        result = build_batch_video_prompts([])
        assert result == []

    def test_batch_all_fail(self):
        with patch("services.video_prompt_service.build_video_prompt") as mock_build:
            mock_build.side_effect = HTTPException(status_code=500, detail="Error")

            result = build_batch_video_prompts(["A", "B"])
            assert result == ["", ""]


# ─── Tests: Constants ──────────────────────────────────────────────────────────

class TestConstants:
    def test_system_prompt_requires_english(self):
        assert "ENGLISH" in SYSTEM_PROMPT_VIDEO

    def test_system_prompt_cinematic_style(self):
        assert "cinematic" in SYSTEM_PROMPT_VIDEO.lower()
        assert "visual metaphors" in SYSTEM_PROMPT_VIDEO.lower()

    def test_system_prompt_no_text_in_video(self):
        assert "NO readable text" in SYSTEM_PROMPT_VIDEO

    def test_default_negative_prompt(self):
        assert "blurry" in DEFAULT_NEGATIVE_PROMPT
        assert "low quality" in DEFAULT_NEGATIVE_PROMPT

