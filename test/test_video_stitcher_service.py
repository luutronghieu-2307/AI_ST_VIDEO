import os
import subprocess
from unittest.mock import MagicMock, patch
import pytest

from services.video_stitcher_service import (
    download_video_segment,
    stitch_and_mux_storyboard,
)


class TestDownloadVideoSegment:
    @patch("urllib.request.urlopen")
    def test_download_success(self, mock_urlopen, tmp_path):
        mock_response = MagicMock()
        mock_response.read.side_effect = [b"fake_mp4_bytes", b""]
        mock_urlopen.return_value.__enter__.return_value = mock_response

        dest = str(tmp_path / "test.mp4")
        result = download_video_segment("https://example.com/video.mp4", dest)
        assert result == dest
        assert os.path.exists(dest)


class TestStitchAndMuxStoryboard:
    def test_empty_urls_raises(self):
        with pytest.raises(ValueError):
            stitch_and_mux_storyboard("sb_123", [])

    @patch("services.video_stitcher_service.download_video_segment")
    @patch("subprocess.run")
    @patch("shutil.copyfile")
    def test_stitch_without_audio_success(self, mock_copy, mock_run, mock_download, tmp_path):
        mock_download.side_effect = lambda url, dest: dest
        mock_res = MagicMock()
        mock_res.returncode = 0
        mock_run.return_value = mock_res

        url = stitch_and_mux_storyboard(
            storyboard_id="sb_test1",
            segment_urls=["https://example.com/seg1.mp4", "https://example.com/seg2.mp4"],
            audio_path=None,
        )

        assert url == "/static/merged_videos/sb_test1_final.mp4"
        assert mock_run.called

    @patch("services.video_stitcher_service.download_video_segment")
    @patch("subprocess.run")
    def test_stitch_with_audio_success(self, mock_run, mock_download, tmp_path):
        mock_download.side_effect = lambda url, dest: dest
        mock_res = MagicMock()
        mock_res.returncode = 0
        mock_run.return_value = mock_res

        dummy_audio = tmp_path / "voice.mp3"
        dummy_audio.write_bytes(b"dummy_mp3_data")

        url = stitch_and_mux_storyboard(
            storyboard_id="sb_test2",
            segment_urls=["https://example.com/seg1.mp4"],
            audio_path=str(dummy_audio),
        )

        assert url == "/static/merged_videos/sb_test2_final.mp4"
        assert mock_run.called

    @patch("services.video_stitcher_service.download_video_segment")
    @patch("subprocess.run")
    @patch("shutil.copyfile")
    def test_stitch_fallback_reencode(self, mock_copy, mock_run, mock_download):
        mock_download.side_effect = lambda url, dest: dest
        # First call fails (copy mode), second call passes (reencode mode)
        fail_res = MagicMock(returncode=1)
        pass_res = MagicMock(returncode=0)
        mock_run.side_effect = [fail_res, pass_res]

        url = stitch_and_mux_storyboard(
            storyboard_id="sb_test3",
            segment_urls=["https://example.com/seg1.mp4"],
            audio_path=None,
        )

        assert url == "/static/merged_videos/sb_test3_final.mp4"
        assert mock_run.call_count == 2
