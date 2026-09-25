# test_config.py – Unit tests cho core/config.py
# Yêu cầu độ bao phủ: >= 90%

import os
import pytest
from unittest.mock import patch


class TestVideoConfigDefaults:
    """Kiểm tra giá trị mặc định của config Storyboard Video."""

    def test_video_gateway_url_is_text_to_video(self):
        from core.config import settings
        assert "text-to-video" in settings.PIXAZO_VIDEO_GATEWAY_URL

    def test_status_url(self):
        from core.config import settings
        assert "requests/status" in settings.PIXAZO_STATUS_URL

    def test_video_request_timeout(self):
        from core.config import settings
        assert settings.VIDEO_REQUEST_TIMEOUT == 180

    def test_poll_interval_start(self):
        from core.config import settings
        assert settings.VIDEO_POLL_INTERVAL_START == 5

    def test_poll_interval_max(self):
        from core.config import settings
        assert settings.VIDEO_POLL_INTERVAL_MAX == 20

    def test_poll_max_attempts(self):
        from core.config import settings
        assert settings.VIDEO_POLL_MAX_ATTEMPTS == 90

    def test_video_max_retry(self):
        from core.config import settings
        assert settings.VIDEO_MAX_RETRY == 3


class TestStoryboardConfig:
    """Kiểm tra config liên quan đến storyboard."""

    def test_max_segments_is_15(self):
        from core.config import settings
        assert settings.MAX_SEGMENTS_PER_REQUEST == 15

    def test_max_storyboards_is_50(self):
        from core.config import settings
        assert settings.MAX_STORYBOARDS == 50

    def test_storyboard_rate_limit_is_50(self):
        from core.config import settings
        assert settings.STORYBOARD_RATE_LIMIT == 50

    def test_storyboard_dir_is_absolute(self):
        from core.config import settings
        assert os.path.isabs(settings.STORYBOARD_DIR)
        assert settings.STORYBOARD_DIR.endswith(os.path.join("data", "storyboards"))


class TestVideoDefaults:
    """Kiểm tra giá trị mặc định của video."""

    def test_frame_rate_is_16(self):
        from core.config import settings
        assert settings.VIDEO_DEFAULT_FRAME_RATE == 16

    def test_num_frames_is_121(self):
        from core.config import settings
        assert settings.VIDEO_DEFAULT_NUM_FRAMES == 121

    def test_aspect_is_16_9(self):
        from core.config import settings
        assert settings.VIDEO_DEFAULT_ASPECT == "16:9"

    def test_style_is_documentary(self):
        from core.config import settings
        assert "documentary" in settings.VIDEO_DEFAULT_STYLE
        assert "realistic" in settings.VIDEO_DEFAULT_STYLE

    def test_negative_prompt_not_empty(self):
        from core.config import settings
        assert settings.VIDEO_DEFAULT_NEGATIVE
        assert "blurry" in settings.VIDEO_DEFAULT_NEGATIVE


class TestAudioConfig:
    """Kiểm tra config upload audio."""

    def test_audio_max_file_size_is_50mb(self):
        from core.config import settings
        assert settings.AUDIO_MAX_FILE_SIZE == 50 * 1024 * 1024

    def test_audio_allowed_types(self):
        from core.config import settings
        assert "audio/mpeg" in settings.AUDIO_ALLOWED_TYPES
        assert "audio/mp3" in settings.AUDIO_ALLOWED_TYPES

    def test_audio_temp_dir_is_absolute(self):
        from core.config import settings
        assert os.path.isabs(settings.AUDIO_TEMP_DIR)
        assert settings.AUDIO_TEMP_DIR.endswith(os.path.join("data", "audio_temp"))


class TestConfigFromEnv:
    """Kiểm tra đọc config từ biến môi trường."""

    def test_video_config_from_env(self):
        with patch.dict(os.environ, {
            "VIDEO_REQUEST_TIMEOUT": "300",
            "MAX_SEGMENTS_PER_REQUEST": "20",
            "VIDEO_DEFAULT_FRAME_RATE": "24",
        }):
            # Re-import để đọc lại env
            import importlib
            import core.config
            importlib.reload(core.config)
            assert core.config.settings.VIDEO_REQUEST_TIMEOUT == 300
            assert core.config.settings.MAX_SEGMENTS_PER_REQUEST == 20
            assert core.config.settings.VIDEO_DEFAULT_FRAME_RATE == 24

        # Reload lại để reset về mặc định
        import importlib
        import core.config
        importlib.reload(core.config)
