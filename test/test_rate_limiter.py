# test_rate_limiter.py – Unit tests cho services/rate_limiter.py
# Yêu cầu độ bao phủ: >= 90%

import time
import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException, Request
from services.rate_limiter import (
    _get_client_ip, check_rate_limit, enforce_rate_limit, _request_log
)


@pytest.fixture(autouse=True)
def clean_request_log():
    _request_log.clear()
    yield
    _request_log.clear()


def make_mock_request(ip: str = "127.0.0.1", forwarded: str = None):
    mock = MagicMock(spec=Request)
    mock.headers = {}
    if forwarded:
        mock.headers["X-Forwarded-For"] = forwarded
    if ip:
        mock.client = MagicMock()
        mock.client.host = ip
    else:
        mock.client = None
    return mock


class TestRateLimiter:
    def test_get_client_ip_forwarded(self):
        req = make_mock_request(forwarded="203.0.113.195, 70.41.3.18")
        assert _get_client_ip(req) == "203.0.113.195"

    def test_get_client_ip_client_host(self):
        req = make_mock_request(ip="192.168.1.100")
        assert _get_client_ip(req) == "192.168.1.100"

    def test_get_client_ip_unknown(self):
        req = make_mock_request(ip=None)
        assert _get_client_ip(req) == "unknown"

    def test_check_rate_limit_allows_under_limit(self):
        req = make_mock_request(ip="10.0.0.1")
        allowed, retry_after = check_rate_limit(req, limit=5, key_prefix="test")
        assert allowed is True
        assert retry_after == 0

    def test_check_rate_limit_blocks_when_exceeded(self):
        req = make_mock_request(ip="10.0.0.2")
        limit = 3
        for _ in range(limit):
            allowed, _ = check_rate_limit(req, limit=limit, key_prefix="test_block")
            assert allowed is True

        # Lần thứ limit + 1 phải bị block
        allowed, retry_after = check_rate_limit(req, limit=limit, key_prefix="test_block")
        assert allowed is False
        assert retry_after > 0

    def test_check_rate_limit_cleans_expired_timestamps(self):
        req = make_mock_request(ip="10.0.0.3")
        key = "test_expire:10.0.0.3"
        # Giả lập 3 requests từ 70 giây trước
        old_time = time.time() - 70
        _request_log[key].extend([old_time, old_time, old_time])

        allowed, _ = check_rate_limit(req, limit=3, key_prefix="test_expire")
        assert allowed is True
        assert len(_request_log[key]) == 1

    def test_enforce_rate_limit_success(self):
        req = make_mock_request(ip="10.0.0.4")
        # Không raise exception
        enforce_rate_limit(req, limit=5, key_prefix="enforce_ok")

    def test_enforce_rate_limit_raises_429(self):
        req = make_mock_request(ip="10.0.0.5")
        limit = 2
        enforce_rate_limit(req, limit=limit, key_prefix="enforce_fail")
        enforce_rate_limit(req, limit=limit, key_prefix="enforce_fail")

        with pytest.raises(HTTPException) as exc_info:
            enforce_rate_limit(req, limit=limit, key_prefix="enforce_fail")
        assert exc_info.value.status_code == 429
        assert "retry_after" in exc_info.value.detail
