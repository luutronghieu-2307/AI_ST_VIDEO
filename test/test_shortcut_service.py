import os
import platform
import subprocess
from services.shortcut_service import create_desktop_shortcut

def test_create_desktop_shortcut_linux(tmp_path, monkeypatch):
    target = str(tmp_path / "app.exe")
    with open(target, "w") as f:
        f.write("mock exe")
    
    icon = str(tmp_path / "logo.ico")
    with open(icon, "w") as f:
        f.write("mock icon")

    monkeypatch.setattr(platform, "system", lambda: "Linux")
    monkeypatch.setattr(os.path, "expanduser", lambda x: str(tmp_path))

    ok, msg = create_desktop_shortcut(target, icon, app_name="TestAuraApp")
    assert ok is True
    assert "shortcut Linux" in msg

def test_create_desktop_shortcut_windows(tmp_path, monkeypatch):
    target = str(tmp_path / "app.exe")
    with open(target, "w") as f:
        f.write("mock exe")
    
    icon = str(tmp_path / "logo.ico")
    with open(icon, "w") as f:
        f.write("mock icon")

    monkeypatch.setattr(platform, "system", lambda: "Windows")
    monkeypatch.setattr(os.path, "expanduser", lambda x: str(tmp_path))

    # Mock subprocess.run
    class MockRes:
        returncode = 0
        stderr = ""
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: MockRes())
    
    # Tạo sẵn file .lnk để test exists
    desktop_path = os.path.join(str(tmp_path), "Desktop")
    os.makedirs(desktop_path, exist_ok=True)
    with open(os.path.join(desktop_path, "TestAuraApp.lnk"), "w") as f:
        f.write("mock lnk")

    ok, msg = create_desktop_shortcut(target, icon, app_name="TestAuraApp")
    assert ok is True
    assert "shortcut thành công" in msg

def test_create_desktop_shortcut_unsupported_os(monkeypatch):
    monkeypatch.setattr(platform, "system", lambda: "DarwinOS")
    ok, msg = create_desktop_shortcut("/path/to/app", "/path/to/icon")
    assert ok is False
    assert "chưa được hỗ trợ" in msg
