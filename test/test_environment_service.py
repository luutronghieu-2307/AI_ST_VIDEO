import os
import platform
import subprocess
import zipfile
from services.environment_service import (
    get_runtime_python_path,
    is_environment_ready,
    download_file_with_progress,
    setup_python_embeddable
)

def test_get_runtime_python_path():
    path = get_runtime_python_path()
    assert isinstance(path, str)
    assert os.path.exists(path)

def test_is_environment_ready():
    ready = is_environment_ready()
    assert ready is True

def test_download_file_with_progress(tmp_path, monkeypatch):
    dest = str(tmp_path / "test.txt")
    progress_recorded = []
    
    def mock_retrieve(url, path, reporthook=None):
        with open(path, "w") as f:
            f.write("sample content")
        if reporthook:
            reporthook(1, 100, 100)

    monkeypatch.setattr("urllib.request.urlretrieve", mock_retrieve)
    
    def cb(cur, tot):
        progress_recorded.append((cur, tot))

    download_file_with_progress("http://fake.url/test.txt", dest, cb)
    assert os.path.exists(dest)
    assert len(progress_recorded) > 0

def test_setup_python_embeddable_non_windows(monkeypatch):
    monkeypatch.setattr(platform, "system", lambda: "Linux")
    ok = setup_python_embeddable()
    assert ok is True

def test_setup_python_embeddable_windows(tmp_path, monkeypatch):
    monkeypatch.setattr(platform, "system", lambda: "Windows")
    runtime_dir = str(tmp_path / "runtime")
    monkeypatch.setattr("services.environment_service.RUNTIME_DIR", runtime_dir)

    # Mock download_file_with_progress để tạo zip ảo
    def mock_dl(url, dest, cb=None):
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with zipfile.ZipFile(dest, "w") as z:
            z.writestr("python311._pth", "#import site\n.\n")
            z.writestr("python.exe", "fake exe")
        if cb:
            cb(100, 100)

    monkeypatch.setattr("services.environment_service.download_file_with_progress", mock_dl)
    monkeypatch.setattr("urllib.request.urlretrieve", lambda url, dest: None)
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: None)

    progress_steps = []
    def progress_cb(msg, val):
        progress_steps.append((msg, val))

    ok = setup_python_embeddable(progress_cb)
    assert ok is True
    assert len(progress_steps) > 0
