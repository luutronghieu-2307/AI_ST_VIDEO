# test_github_key_store_activate.py – Tests cho activate_key & is_key_used
# Yêu cầu độ bao phủ: >= 90%

from unittest.mock import patch

from services.github_key_store import GitHubKeyStore


def _fresh_fetch(used=False, hwid=None):
    """Trả về hàm fetch_keys mới mỗi lần gọi (tránh bị mutate giữa các retry)."""
    def _fetch():
        return ({"keys": [{"key": "K1", "used": used, "hwid": hwid}]}, "sha1")
    return _fetch


# ─── Tests: activate_key ───────────────────────────────────────────────────────

class TestActivateKey:
    def test_activate_success(self):
        keys = [{"key": "K1", "used": False, "hwid": None}]
        with patch.object(GitHubKeyStore, "fetch_keys", return_value=({"keys": keys}, "sha1")), \
             patch.object(GitHubKeyStore, "_write_keys", return_value=True):
            ok, msg = GitHubKeyStore.activate_key("K1", "AURA-TEST-HWID")
            assert ok is True
            assert "thành công" in msg

    def test_activate_key_not_found(self):
        with patch.object(GitHubKeyStore, "fetch_keys", return_value=({"keys": []}, "sha1")):
            ok, msg = GitHubKeyStore.activate_key("NOPE", "HWID")
            assert ok is False
            assert "không tồn tại" in msg

    def test_activate_key_already_used(self):
        keys = [{"key": "K1", "used": True, "hwid": "OTHER"}]
        with patch.object(GitHubKeyStore, "fetch_keys", return_value=({"keys": keys}, "sha1")):
            ok, msg = GitHubKeyStore.activate_key("K1", "HWID")
            assert ok is False
            assert "đã được sử dụng" in msg

    def test_activate_retries_on_conflict_then_succeeds(self):
        with patch.object(GitHubKeyStore, "fetch_keys", side_effect=_fresh_fetch()), \
             patch.object(GitHubKeyStore, "_write_keys", side_effect=[False, True]):
            ok, msg = GitHubKeyStore.activate_key("K1", "HWID")
            assert ok is True

    def test_activate_exhausts_retries(self):
        with patch.object(GitHubKeyStore, "fetch_keys", side_effect=_fresh_fetch()), \
             patch.object(GitHubKeyStore, "_write_keys", return_value=False):
            ok, msg = GitHubKeyStore.activate_key("K1", "HWID")
            assert ok is False
            assert "Xung đột" in msg

    def test_activate_sets_hwid_and_timestamp(self):
        """Kiểm tra entry được cập nhật đúng trước khi ghi."""
        captured = {}

        def capture_write(data, sha, message):
            captured["entry"] = data["keys"][0]
            return True

        with patch.object(GitHubKeyStore, "fetch_keys", side_effect=_fresh_fetch()), \
             patch.object(GitHubKeyStore, "_write_keys", side_effect=capture_write):
            GitHubKeyStore.activate_key("K1", "AURA-MY-HWID")

        assert captured["entry"]["used"] is True
        assert captured["entry"]["hwid"] == "AURA-MY-HWID"
        assert captured["entry"]["activated_at"] is not None


# ─── Tests: is_key_used ────────────────────────────────────────────────────────

class TestIsKeyUsed:
    def test_returns_true_when_used(self):
        keys = [{"key": "K1", "used": True}]
        with patch.object(GitHubKeyStore, "fetch_keys", return_value=({"keys": keys}, "s")):
            assert GitHubKeyStore.is_key_used("K1") is True

    def test_returns_false_when_not_used(self):
        keys = [{"key": "K1", "used": False}]
        with patch.object(GitHubKeyStore, "fetch_keys", return_value=({"keys": keys}, "s")):
            assert GitHubKeyStore.is_key_used("K1") is False

    def test_returns_false_when_missing(self):
        with patch.object(GitHubKeyStore, "fetch_keys", return_value=({"keys": []}, "s")):
            assert GitHubKeyStore.is_key_used("NOPE") is False
