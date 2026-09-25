# test_github_key_store.py – Unit tests cho services/github_key_store.py
# Yêu cầu độ bao phủ: >= 90%

import base64
import pytest
import requests
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

from services.github_key_store import GitHubKeyStore, github_key_store
from _github_key_store_helpers import make_keys_payload, mock_settings


# ─── Tests: _resolve_token ─────────────────────────────────────────────────────

class TestResolveToken:
    def test_uses_env_token(self):
        with patch("services.github_key_store.settings") as mock_s, \
             patch("services.github_key_store.get_embedded_token", return_value=""):
            mock_s.GITHUB_TOKEN = "env-token"
            assert GitHubKeyStore._resolve_token() == "env-token"

    def test_falls_back_to_embedded(self):
        with patch("services.github_key_store.settings") as mock_s, \
             patch("services.github_key_store.resolve_token", return_value="embedded-token"):
            mock_s.GITHUB_TOKEN = ""
            assert GitHubKeyStore._resolve_token() == "embedded-token"


# ─── Tests: _validate_config ───────────────────────────────────────────────────

class TestValidateConfig:
    def test_raises_when_token_missing(self):
        with patch("services.github_key_store.settings") as mock_s:
            mock_s.GITHUB_REPO = "owner/repo"
            with pytest.raises(HTTPException) as exc:
                GitHubKeyStore._validate_config("")
            assert exc.value.status_code == 500
            assert "GITHUB_TOKEN" in exc.value.detail

    def test_raises_when_repo_invalid(self):
        with patch("services.github_key_store.settings") as mock_s:
            mock_s.GITHUB_REPO = "invalid-repo-no-slash"
            with pytest.raises(HTTPException) as exc:
                GitHubKeyStore._validate_config("token")
            assert exc.value.status_code == 500
            assert "owner/repo" in exc.value.detail

    def test_passes_with_valid_config(self):
        with patch("services.github_key_store.settings") as mock_s:
            mock_s.GITHUB_REPO = "owner/repo"
            GitHubKeyStore._validate_config("token")  # Không raise


# ─── Tests: _handle_error ──────────────────────────────────────────────────────

class TestHandleError:
    @pytest.mark.parametrize("status,expected", [
        (401, 401), (403, 403), (404, 404), (429, 429), (500, 500),
    ])
    def test_maps_status_codes(self, status, expected):
        resp = MagicMock()
        resp.status_code = status
        resp.text = "error body"
        with pytest.raises(HTTPException) as exc:
            GitHubKeyStore._handle_error(resp)
        assert exc.value.status_code == expected


# ─── Tests: fetch_keys ─────────────────────────────────────────────────────────

class TestFetchKeys:
    def test_fetch_success(self):
        keys = [{"key": "K1", "used": False}]
        with patch("services.github_key_store.settings") as mock_s, \
             patch("services.github_key_store.get_embedded_token", return_value=""), \
             patch("services.github_key_store.requests.get") as mock_get:
            mock_settings(mock_s)
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = make_keys_payload(keys, sha="sha-1")
            mock_get.return_value = mock_resp

            data, sha = GitHubKeyStore.fetch_keys()
            assert sha == "sha-1"
            assert data["keys"][0]["key"] == "K1"

    def test_fetch_timeout(self):
        with patch("services.github_key_store.settings") as mock_s, \
             patch("services.github_key_store.get_embedded_token", return_value=""), \
             patch("services.github_key_store.requests.get") as mock_get:
            mock_settings(mock_s)
            mock_get.side_effect = requests.exceptions.Timeout("timeout")
            with pytest.raises(HTTPException) as exc:
                GitHubKeyStore.fetch_keys()
            assert exc.value.status_code == 504

    def test_fetch_connection_error(self):
        with patch("services.github_key_store.settings") as mock_s, \
             patch("services.github_key_store.get_embedded_token", return_value=""), \
             patch("services.github_key_store.requests.get") as mock_get:
            mock_settings(mock_s)
            mock_get.side_effect = requests.exceptions.ConnectionError("refused")
            with pytest.raises(HTTPException) as exc:
                GitHubKeyStore.fetch_keys()
            assert exc.value.status_code == 500

    def test_fetch_401(self):
        with patch("services.github_key_store.settings") as mock_s, \
             patch("services.github_key_store.get_embedded_token", return_value=""), \
             patch("services.github_key_store.requests.get") as mock_get:
            mock_settings(mock_s)
            mock_resp = MagicMock()
            mock_resp.status_code = 401
            mock_resp.text = "unauthorized"
            mock_get.return_value = mock_resp
            with pytest.raises(HTTPException) as exc:
                GitHubKeyStore.fetch_keys()
            assert exc.value.status_code == 401

    def test_fetch_corrupt_json(self):
        with patch("services.github_key_store.settings") as mock_s, \
             patch("services.github_key_store.get_embedded_token", return_value=""), \
             patch("services.github_key_store.requests.get") as mock_get:
            mock_settings(mock_s)
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "sha": "s1",
                "content": base64.b64encode(b"NOT_JSON{{{").decode("ascii"),
            }
            mock_get.return_value = mock_resp
            with pytest.raises(HTTPException) as exc:
                GitHubKeyStore.fetch_keys()
            assert exc.value.status_code == 500


# ─── Tests: find_key ───────────────────────────────────────────────────────────

class TestFindKey:
    def test_finds_existing_key(self):
        data = {"keys": [{"key": "K1"}, {"key": "K2"}]}
        assert GitHubKeyStore.find_key(data, "K2")["key"] == "K2"

    def test_returns_none_for_missing(self):
        data = {"keys": [{"key": "K1"}]}
        assert GitHubKeyStore.find_key(data, "NOPE") is None

    def test_strips_whitespace(self):
        data = {"keys": [{"key": "K1"}]}
        assert GitHubKeyStore.find_key(data, "  K1  ") is not None

    def test_empty_keys_list(self):
        assert GitHubKeyStore.find_key({"keys": []}, "K1") is None


# ─── Tests: _write_keys ────────────────────────────────────────────────────────

class TestWriteKeys:
    def test_write_success(self):
        with patch("services.github_key_store.settings") as mock_s, \
             patch("services.github_key_store.get_embedded_token", return_value=""), \
             patch("services.github_key_store.requests.put") as mock_put:
            mock_settings(mock_s)
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_put.return_value = mock_resp
            assert GitHubKeyStore._write_keys({"keys": []}, "sha", "msg") is True

    def test_write_conflict_returns_false(self):
        with patch("services.github_key_store.settings") as mock_s, \
             patch("services.github_key_store.get_embedded_token", return_value=""), \
             patch("services.github_key_store.requests.put") as mock_put:
            mock_settings(mock_s)
            mock_resp = MagicMock()
            mock_resp.status_code = 409
            mock_put.return_value = mock_resp
            assert GitHubKeyStore._write_keys({"keys": []}, "sha", "msg") is False

    def test_write_timeout(self):
        with patch("services.github_key_store.settings") as mock_s, \
             patch("services.github_key_store.get_embedded_token", return_value=""), \
             patch("services.github_key_store.requests.put") as mock_put:
            mock_settings(mock_s)
            mock_put.side_effect = requests.exceptions.Timeout("t")
            with pytest.raises(HTTPException) as exc:
                GitHubKeyStore._write_keys({"keys": []}, "sha", "msg")
            assert exc.value.status_code == 504

    def test_write_connection_error(self):
        with patch("services.github_key_store.settings") as mock_s, \
             patch("services.github_key_store.get_embedded_token", return_value=""), \
             patch("services.github_key_store.requests.put") as mock_put:
            mock_settings(mock_s)
            mock_put.side_effect = requests.exceptions.ConnectionError("c")
            with pytest.raises(HTTPException) as exc:
                GitHubKeyStore._write_keys({"keys": []}, "sha", "msg")
            assert exc.value.status_code == 500

    def test_write_403_error(self):
        with patch("services.github_key_store.settings") as mock_s, \
             patch("services.github_key_store.get_embedded_token", return_value=""), \
             patch("services.github_key_store.requests.put") as mock_put:
            mock_settings(mock_s)
            mock_resp = MagicMock()
            mock_resp.status_code = 403
            mock_resp.text = "forbidden"
            mock_put.return_value = mock_resp
            with pytest.raises(HTTPException) as exc:
                GitHubKeyStore._write_keys({"keys": []}, "sha", "msg")
            assert exc.value.status_code == 403


# ─── Tests: singleton ──────────────────────────────────────────────────────────

def test_singleton_exists():
    assert github_key_store is not None
    assert isinstance(github_key_store, GitHubKeyStore)
