# test_license_service.py – Unit tests cho services/license_service.py
# Yêu cầu độ bao phủ: >= 90%

import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

from services.license_service import (
    verify_license_key,
    verify_license_key_remote,
    compute_activation_signature,
    bind_machine,
    check_activation,
    get_stored_license_keys,
    ACTIVATION_FILE,
    LICENSE_FILE,
)


# ─── Tests: get_stored_license_keys ────────────────────────────────────────────

class TestGetStoredLicenseKeys:
    def test_returns_empty_when_file_missing(self, monkeypatch):
        monkeypatch.setattr("services.license_service.LICENSE_FILE", "nonexistent.key")
        assert get_stored_license_keys() == []

    def test_reads_keys_ignoring_comments(self, tmp_path, monkeypatch):
        key_file = str(tmp_path / "license.key")
        with open(key_file, "w", encoding="utf-8") as f:
            f.write("# Comment\nKEY_ABC_12345678\n\nKEY_XYZ_87654321\n")
        monkeypatch.setattr("services.license_service.LICENSE_FILE", key_file)
        keys = get_stored_license_keys()
        assert keys == ["KEY_ABC_12345678", "KEY_XYZ_87654321"]

    def test_returns_empty_on_read_error(self, monkeypatch):
        monkeypatch.setattr("services.license_service.LICENSE_FILE", "/root/forbidden.key")
        assert get_stored_license_keys() == []


# ─── Tests: verify_license_key (legacy local) ──────────────────────────────────

class TestVerifyLicenseKeyLegacy:
    def test_empty_key_returns_false(self):
        assert verify_license_key("") is False
        assert verify_license_key("   ") is False

    def test_valid_key_in_file(self, tmp_path, monkeypatch):
        key_file = str(tmp_path / "license.key")
        with open(key_file, "w", encoding="utf-8") as f:
            f.write("KEY_ABC_12345678\n")
        monkeypatch.setattr("services.license_service.LICENSE_FILE", key_file)
        assert verify_license_key("KEY_ABC_12345678") is True
        assert verify_license_key("KEY_INVALID") is False

    def test_no_file_returns_false(self, monkeypatch):
        """Không còn fallback bypass – key không có trong file là không hợp lệ."""
        monkeypatch.setattr("services.license_service.LICENSE_FILE", "nonexistent.key")
        assert verify_license_key("AURA-1234-5678-ABCD") is False
        assert verify_license_key("SHORT") is False


# ─── Tests: verify_license_key_remote ──────────────────────────────────────────

class TestVerifyLicenseKeyRemote:
    def test_empty_key_returns_false(self):
        ok, msg = verify_license_key_remote("")
        assert ok is False
        assert "Vui lòng nhập" in msg

    def test_valid_unused_key(self):
        data = {"keys": [{"key": "K1", "used": False}]}
        with patch("services.license_service.github_key_store") as mock_store:
            mock_store.fetch_keys.return_value = (data, "sha")
            mock_store.find_key.side_effect = lambda d, k: next(
                (e for e in d["keys"] if e["key"] == k), None
            )
            ok, msg = verify_license_key_remote("K1")
            assert ok is True
            assert "chưa được sử dụng" in msg

    def test_key_not_found(self):
        data = {"keys": []}
        with patch("services.license_service.github_key_store") as mock_store:
            mock_store.fetch_keys.return_value = (data, "sha")
            mock_store.find_key.return_value = None
            ok, msg = verify_license_key_remote("NOPE")
            assert ok is False
            assert "không hợp lệ" in msg

    def test_key_already_used(self):
        data = {"keys": [{"key": "K1", "used": True}]}
        with patch("services.license_service.github_key_store") as mock_store:
            mock_store.fetch_keys.return_value = (data, "sha")
            mock_store.find_key.return_value = {"key": "K1", "used": True}
            ok, msg = verify_license_key_remote("K1")
            assert ok is False
            assert "đã được sử dụng" in msg

    def test_network_error_returns_false(self):
        with patch("services.license_service.github_key_store") as mock_store:
            mock_store.fetch_keys.side_effect = HTTPException(status_code=504, detail="Timeout")
            ok, msg = verify_license_key_remote("K1")
            assert ok is False
            assert "Không thể xác thực" in msg


# ─── Tests: compute_activation_signature ───────────────────────────────────────

def test_compute_activation_signature():
    sig1 = compute_activation_signature("KEY123", "AURA-1111")
    sig2 = compute_activation_signature("KEY123", "AURA-1111")
    sig3 = compute_activation_signature("KEY123", "AURA-2222")
    assert sig1 == sig2
    assert sig1 != sig3


# ─── Tests: bind_machine ───────────────────────────────────────────────────────

class TestBindMachine:
    def test_bind_success(self, tmp_path, monkeypatch):
        act_file = str(tmp_path / "activation.dat")
        monkeypatch.setattr("services.license_service.ACTIVATION_FILE", act_file)
        with patch("services.license_service.github_key_store") as mock_store:
            mock_store.activate_key.return_value = (True, "OK")
            ok, msg = bind_machine("AURA-KEY-VALID-1234")
            assert ok is True
            assert os.path.exists(act_file)

    def test_bind_fails_when_remote_rejects(self, tmp_path, monkeypatch):
        act_file = str(tmp_path / "activation.dat")
        monkeypatch.setattr("services.license_service.ACTIVATION_FILE", act_file)
        with patch("services.license_service.github_key_store") as mock_store:
            mock_store.activate_key.return_value = (False, "Key đã dùng")
            ok, msg = bind_machine("AURA-USED-KEY-1234")
            assert ok is False
            assert "đã dùng" in msg
            assert not os.path.exists(act_file)

    def test_bind_fails_on_write_error(self, monkeypatch):
        with patch("services.license_service.github_key_store") as mock_store, \
             patch("builtins.open", side_effect=OSError("disk full")):
            mock_store.activate_key.return_value = (True, "OK")
            ok, msg = bind_machine("AURA-KEY-VALID-1234")
            assert ok is False
            assert "Lỗi lưu file" in msg


# ─── Tests: check_activation ───────────────────────────────────────────────────

class TestCheckActivation:
    def test_not_activated_when_file_missing(self, monkeypatch):
        monkeypatch.setattr("services.license_service.ACTIVATION_FILE", "nonexistent.dat")
        is_active, msg = check_activation()
        assert is_active is False
        assert "Chưa kích hoạt" in msg

    def test_activated_on_same_machine(self, tmp_path, monkeypatch):
        act_file = str(tmp_path / "activation.dat")
        monkeypatch.setattr("services.license_service.ACTIVATION_FILE", act_file)
        with patch("services.license_service.github_key_store") as mock_store:
            mock_store.activate_key.return_value = (True, "OK")
            bind_machine("AURA-KEY-VALID-1234")
        is_active, msg = check_activation()
        assert is_active is True
        assert "hợp lệ" in msg

    def test_hwid_mismatch_detected(self, tmp_path, monkeypatch):
        act_file = str(tmp_path / "activation.dat")
        monkeypatch.setattr("services.license_service.ACTIVATION_FILE", act_file)
        with patch("services.license_service.github_key_store") as mock_store:
            mock_store.activate_key.return_value = (True, "OK")
            bind_machine("AURA-KEY-VALID-1234")

        monkeypatch.setattr("services.license_service.get_hwid", lambda: "AURA-DIFFERENT-9999")
        is_active, msg = check_activation()
        assert is_active is False
        assert "không khớp" in msg

    def test_corrupt_activation_file(self, tmp_path, monkeypatch):
        act_file = str(tmp_path / "activation.dat")
        with open(act_file, "w", encoding="utf-8") as f:
            f.write("NOT_VALID_BASE64!!!")
        monkeypatch.setattr("services.license_service.ACTIVATION_FILE", act_file)
        is_active, msg = check_activation()
        assert is_active is False
        assert "bị lỗi" in msg
