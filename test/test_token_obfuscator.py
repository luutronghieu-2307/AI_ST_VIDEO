# test_token_obfuscator.py – Unit tests cho services/token_obfuscator.py
# Yêu cầu độ bao phủ: >= 90%

import pytest
from unittest.mock import patch, MagicMock

from services.token_obfuscator import (
    obfuscate_token,
    deobfuscate_token,
    resolve_token,
    get_embedded_token,
    _xor_bytes,
    _PREFIX,
)


class TestObfuscateToken:
    def test_obfuscate_returns_prefixed_string(self):
        result = obfuscate_token("ghp_testtoken123")
        assert result.startswith(_PREFIX)
        assert "ghp_testtoken123" not in result

    def test_obfuscate_empty_returns_empty(self):
        assert obfuscate_token("") == ""

    def test_obfuscate_is_deterministic(self):
        assert obfuscate_token("abc") == obfuscate_token("abc")

    def test_obfuscate_different_tokens_differ(self):
        assert obfuscate_token("token-a") != obfuscate_token("token-b")


class TestDeobfuscateToken:
    def test_round_trip_recovers_original(self):
        original = "github_pat_11ABCDEFG0abcdefghijklmnop"
        assert deobfuscate_token(obfuscate_token(original)) == original

    def test_round_trip_unicode(self):
        original = "token-với-ký-tự-đặc-biệt-🔑"
        assert deobfuscate_token(obfuscate_token(original)) == original

    def test_deobfuscate_empty_returns_empty(self):
        assert deobfuscate_token("") == ""

    def test_deobfuscate_without_prefix_returns_empty(self):
        assert deobfuscate_token("no-prefix-here") == ""

    def test_deobfuscate_invalid_base64_returns_empty(self):
        assert deobfuscate_token(_PREFIX + "!!!invalid!!!") == ""

    def test_deobfuscate_corrupt_payload_returns_empty(self):
        # Chuỗi hợp lệ về prefix nhưng base64 decode ra bytes không phải utf-8
        assert deobfuscate_token(_PREFIX + "////") == ""


class TestXorBytes:
    def test_xor_with_empty_key_returns_original(self):
        data = b"hello"
        assert _xor_bytes(data, b"") == data

    def test_xor_is_reversible(self):
        data = b"secret-data"
        key = b"mykey"
        assert _xor_bytes(_xor_bytes(data, key), key) == data


class TestResolveToken:
    def test_prefers_env_token(self):
        assert resolve_token("env-token", obfuscate_token("embedded")) == "env-token"

    def test_falls_back_to_obfuscated(self):
        embedded = obfuscate_token("embedded-token")
        assert resolve_token("", embedded) == "embedded-token"

    def test_falls_back_when_env_is_whitespace(self):
        embedded = obfuscate_token("embedded-token")
        assert resolve_token("   ", embedded) == "embedded-token"

    def test_returns_empty_when_both_missing(self):
        assert resolve_token(None, None) == ""
        assert resolve_token("", "") == ""


class TestGetEmbeddedToken:
    def test_returns_empty_when_module_missing(self):
        with patch.dict("sys.modules", {"services._embedded_token": None}):
            assert get_embedded_token() == ""

    def test_returns_decoded_token_when_module_exists(self):
        fake_module = MagicMock()
        fake_module.OBFUSCATED_TOKEN = obfuscate_token("real-token")
        with patch.dict("sys.modules", {"services._embedded_token": fake_module}):
            assert get_embedded_token() == "real-token"

    def test_returns_empty_on_exception(self):
        fake_module = MagicMock()
        fake_module.OBFUSCATED_TOKEN = None
        with patch.dict("sys.modules", {"services._embedded_token": fake_module}):
            assert get_embedded_token() == ""
