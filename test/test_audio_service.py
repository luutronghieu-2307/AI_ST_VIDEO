# test_audio_service.py – Unit tests cho services/audio_service.py
# Yêu cầu độ bao phủ: >= 90%

import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

from services.audio_service import (
    save_uploaded_audio,
    get_audio_duration,
    round_to_1_plus_8k,
    allocate_frames_to_segments,
    cleanup_temp_audio,
    MIN_FRAMES,
    MAX_FRAMES,
)


# ─── Tests: save_uploaded_audio ────────────────────────────────────────────────

class TestSaveUploadedAudio:
    def test_save_ok(self, tmp_path):
        with patch("services.audio_service.settings") as mock_s:
            mock_s.AUDIO_MAX_FILE_SIZE = 50 * 1024 * 1024
            mock_s.AUDIO_TEMP_DIR = str(tmp_path)
            path = save_uploaded_audio(b"fake mp3 content", "test.mp3")
            assert os.path.exists(path)
            assert path.endswith("test.mp3")

    def test_save_too_large(self, tmp_path):
        with patch("services.audio_service.settings") as mock_s:
            mock_s.AUDIO_MAX_FILE_SIZE = 100
            mock_s.AUDIO_TEMP_DIR = str(tmp_path)
            with pytest.raises(HTTPException) as exc:
                save_uploaded_audio(b"x" * 200, "test.mp3")
            assert exc.value.status_code == 400
            assert "quá lớn" in exc.value.detail

    def test_save_wrong_extension(self, tmp_path):
        with patch("services.audio_service.settings") as mock_s:
            mock_s.AUDIO_MAX_FILE_SIZE = 50 * 1024 * 1024
            mock_s.AUDIO_TEMP_DIR = str(tmp_path)
            with pytest.raises(HTTPException) as exc:
                save_uploaded_audio(b"content", "test.wav")
            assert exc.value.status_code == 400
            assert "MP3" in exc.value.detail

    def test_save_empty_filename(self, tmp_path):
        with patch("services.audio_service.settings") as mock_s:
            mock_s.AUDIO_MAX_FILE_SIZE = 50 * 1024 * 1024
            mock_s.AUDIO_TEMP_DIR = str(tmp_path)
            with pytest.raises(HTTPException) as exc:
                save_uploaded_audio(b"content", "")
            assert exc.value.status_code == 400

    def test_save_write_error(self, tmp_path):
        with patch("services.audio_service.settings") as mock_s, \
             patch("builtins.open", side_effect=OSError("disk full")):
            mock_s.AUDIO_MAX_FILE_SIZE = 50 * 1024 * 1024
            mock_s.AUDIO_TEMP_DIR = str(tmp_path)
            with pytest.raises(HTTPException) as exc:
                save_uploaded_audio(b"content", "test.mp3")
            assert exc.value.status_code == 500


# ─── Tests: get_audio_duration ─────────────────────────────────────────────────

class TestGetAudioDuration:
    def test_duration_ok(self, tmp_path):
        fake_file = tmp_path / "test.mp3"
        fake_file.write_bytes(b"fake")

        with patch("services.audio_service.MP3") as mock_mp3:
            mock_audio = MagicMock()
            mock_audio.info.length = 180.5
            mock_mp3.return_value = mock_audio

            duration = get_audio_duration(str(fake_file))
            assert duration == 180.5

    def test_duration_missing_file(self):
        with pytest.raises(HTTPException) as exc:
            get_audio_duration("/nonexistent/path.mp3")
        assert exc.value.status_code == 400
        assert "không tồn tại" in exc.value.detail

    def test_duration_empty_path(self):
        with pytest.raises(HTTPException) as exc:
            get_audio_duration("")
        assert exc.value.status_code == 400

    def test_duration_corrupt_file(self, tmp_path):
        fake_file = tmp_path / "test.mp3"
        fake_file.write_bytes(b"fake")

        from mutagen import MutagenError
        with patch("services.audio_service.MP3", side_effect=MutagenError("corrupt")):
            with pytest.raises(HTTPException) as exc:
                get_audio_duration(str(fake_file))
            assert exc.value.status_code == 400
            assert "hỏng" in exc.value.detail

    def test_duration_zero_length(self, tmp_path):
        fake_file = tmp_path / "test.mp3"
        fake_file.write_bytes(b"fake")

        with patch("services.audio_service.MP3") as mock_mp3:
            mock_audio = MagicMock()
            mock_audio.info.length = 0
            mock_mp3.return_value = mock_audio

            with pytest.raises(HTTPException) as exc:
                get_audio_duration(str(fake_file))
            assert exc.value.status_code == 400
            assert "không hợp lệ" in exc.value.detail

    def test_duration_unexpected_error(self, tmp_path):
        fake_file = tmp_path / "test.mp3"
        fake_file.write_bytes(b"fake")

        with patch("services.audio_service.MP3", side_effect=ValueError("unexpected")):
            with pytest.raises(HTTPException) as exc:
                get_audio_duration(str(fake_file))
            assert exc.value.status_code == 400


# ─── Tests: round_to_1_plus_8k ─────────────────────────────────────────────────

class TestRoundTo1Plus8k:
    def test_exact_121(self):
        assert round_to_1_plus_8k(121) == 121

    def test_exact_25(self):
        assert round_to_1_plus_8k(25) == 25

    def test_round_up(self):
        # 30 → gần 33 hơn 25
        assert round_to_1_plus_8k(30) == 33

    def test_round_down(self):
        # 27 → gần 25 hơn 33
        assert round_to_1_plus_8k(27) == 25

    def test_clamp_min(self):
        assert round_to_1_plus_8k(10) == MIN_FRAMES

    def test_clamp_max(self):
        assert round_to_1_plus_8k(200) == MAX_FRAMES

    def test_negative(self):
        assert round_to_1_plus_8k(-5) == MIN_FRAMES


# ─── Tests: allocate_frames_to_segments ────────────────────────────────────────

class TestAllocateFrames:
    def test_allocate_normal(self):
        segments = ["A" * 100, "B" * 100, "C" * 100]
        result = allocate_frames_to_segments(segments, 180.0, 16)
        assert len(result) == 3
        for frames in result:
            assert MIN_FRAMES <= frames <= MAX_FRAMES
            assert (frames - 1) % 8 == 0

    def test_allocate_empty(self):
        with pytest.raises(HTTPException) as exc:
            allocate_frames_to_segments([], 180.0, 16)
        assert exc.value.status_code == 400
        assert "rỗng" in exc.value.detail

    def test_allocate_zero_text(self):
        with pytest.raises(HTTPException) as exc:
            allocate_frames_to_segments(["", ""], 180.0, 16)
        assert exc.value.status_code == 400
        assert "bằng 0" in exc.value.detail

    def test_allocate_proportional(self):
        # Segment dài hơn → nhiều frames hơn
        segments = ["A" * 10, "B" * 1000]
        result = allocate_frames_to_segments(segments, 180.0, 16)
        assert result[1] >= result[0]

    def test_allocate_clamps_to_max(self):
        # 1 segment duy nhất → chiếm toàn bộ thời lượng → clamp 121
        result = allocate_frames_to_segments(["A" * 100], 180.0, 16)
        assert result[0] == MAX_FRAMES

    def test_allocate_clamps_to_min(self):
        # Segment rất ngắn trong tổng rất dài
        segments = ["A" * 10000, "B"]
        result = allocate_frames_to_segments(segments, 10.0, 16)
        assert result[1] == MIN_FRAMES

    def test_allocate_custom_frame_rate(self):
        segments = ["A" * 100]
        result_16 = allocate_frames_to_segments(segments, 180.0, 16)
        result_24 = allocate_frames_to_segments(segments, 180.0, 24)
        # Cả 2 đều clamp về max vì duration lớn
        assert result_16[0] == MAX_FRAMES
        assert result_24[0] == MAX_FRAMES


# ─── Tests: cleanup_temp_audio ─────────────────────────────────────────────────

class TestCleanupTempAudio:
    def test_cleanup_ok(self, tmp_path):
        fake_file = tmp_path / "test.mp3"
        fake_file.write_bytes(b"fake")
        cleanup_temp_audio(str(fake_file))
        assert not fake_file.exists()

    def test_cleanup_missing_file(self):
        # Không raise exception
        cleanup_temp_audio("/nonexistent/path.mp3")

    def test_cleanup_empty_path(self):
        cleanup_temp_audio("")

    def test_cleanup_error_swallowed(self, tmp_path):
        fake_file = tmp_path / "test.mp3"
        fake_file.write_bytes(b"fake")
        with patch("services.audio_service.os.remove", side_effect=OSError("locked")):
            # Không raise
            cleanup_temp_audio(str(fake_file))
