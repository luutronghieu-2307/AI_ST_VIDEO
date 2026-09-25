import platform
from services.hardware_service import get_hwid, _get_raw_machine_id

def test_get_raw_machine_id():
    raw = _get_raw_machine_id()
    assert isinstance(raw, str)
    assert len(raw) > 0

def test_get_raw_machine_id_windows_branch(monkeypatch):
    monkeypatch.setattr(platform, "system", lambda: "Windows")
    raw = _get_raw_machine_id()
    assert isinstance(raw, str)
    assert len(raw) > 0

def test_get_raw_machine_id_fallback_branch(monkeypatch):
    monkeypatch.setattr(platform, "system", lambda: "UnknownOS")
    raw = _get_raw_machine_id()
    assert isinstance(raw, str)
    assert len(raw) > 0

def test_get_hwid_format():
    hwid = get_hwid()
    assert isinstance(hwid, str)
    assert hwid.startswith("AURA-")
    parts = hwid.split("-")
    assert len(parts) == 5
    assert parts[0] == "AURA"
    for part in parts[1:]:
        assert len(part) == 4

def test_get_hwid_consistency():
    hwid1 = get_hwid()
    hwid2 = get_hwid()
    assert hwid1 == hwid2
