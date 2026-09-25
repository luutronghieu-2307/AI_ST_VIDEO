# _github_key_store_helpers.py – Shared helpers cho test_github_key_store*.py
import base64
import json


def make_keys_payload(keys, sha="abc123"):
    """Tạo response giả lập từ GitHub Contents API."""
    content = json.dumps({"version": 1, "keys": keys})
    encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")
    return {"sha": sha, "content": encoded}


def mock_settings(mock_s):
    """Gán các giá trị settings giả lập cho GitHub."""
    mock_s.GITHUB_TOKEN = "ghp_test_token"
    mock_s.GITHUB_REPO = "owner/repo"
    mock_s.GITHUB_KEYS_PATH = "keys.json"
    mock_s.GITHUB_API_TIMEOUT = 15
    mock_s.GITHUB_API_BASE = "https://api.github.com"
    return mock_s
