"""
test_launcher.py - Unit tests cho launcher_core (single_instance, server_runner).
"""
import pytest
from unittest.mock import patch, MagicMock
from launcher_core.single_instance import ensure_single_instance
from launcher_core.server_runner import wait_for_server, open_browser, start_uvicorn_thread


class TestLauncherCore:
    def test_ensure_single_instance_non_windows(self):
        with patch("sys.platform", "linux"):
            assert ensure_single_instance() is None

    def test_ensure_single_instance_windows_ok(self):
        with patch("sys.platform", "win32"):
            with patch("ctypes.windll", create=True) as mock_windll:
                mock_windll.kernel32.CreateMutexW.return_value = 1234
                mock_windll.kernel32.GetLastError.return_value = 0
                assert ensure_single_instance() == 1234

    def test_ensure_single_instance_windows_already_exists(self):
        with patch("sys.platform", "win32"):
            with patch("ctypes.windll", create=True) as mock_windll:
                mock_windll.kernel32.CreateMutexW.return_value = 1234
                mock_windll.kernel32.GetLastError.return_value = 183
                with pytest.raises(SystemExit):
                    ensure_single_instance()

    def test_ensure_single_instance_windows_exception(self):
        with patch("sys.platform", "win32"):
            with patch("ctypes.windll", create=True) as mock_windll:
                mock_windll.kernel32.CreateMutexW.side_effect = Exception("OS Error")
                assert ensure_single_instance() is None

    def test_wait_for_server_immediate_success(self):
        with patch("socket.create_connection", return_value=MagicMock()):
            assert wait_for_server("127.0.0.1", 8000, timeout=1) is True

    def test_wait_for_server_timeout(self):
        with patch("socket.create_connection", side_effect=OSError("Refused")):
            assert wait_for_server("127.0.0.1", 8000, timeout=0.5) is False

    def test_open_browser(self):
        with patch("webbrowser.open") as mock_open:
            open_browser("http://127.0.0.1:8000")
            mock_open.assert_called_once_with("http://127.0.0.1:8000")

    def test_start_uvicorn_thread(self, tmp_path):
        with patch("threading.Thread") as mock_thread:
            thread_instance = MagicMock()
            mock_thread.return_value = thread_instance
            t = start_uvicorn_thread(str(tmp_path))
            assert t == thread_instance
            mock_thread.assert_called_once()
