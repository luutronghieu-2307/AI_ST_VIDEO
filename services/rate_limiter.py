import time
from collections import defaultdict, deque
from fastapi import HTTPException, Request
from typing import Tuple

RATE_LIMIT = 20   # max requests per window
WINDOW_SEC = 60   # sliding window in seconds

# In-memory store: { client_ip: deque[timestamp] }
_request_log: dict[str, deque] = defaultdict(deque)


def _get_client_ip(request: Request) -> str:
    """Lấy IP thực của client, hỗ trợ proxy/load balancer"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def check_rate_limit(
    request: Request, 
    limit: int = RATE_LIMIT, 
    key_prefix: str = "default"
) -> Tuple[bool, int]:
    """
    Kiểm tra rate limit theo IP và key_prefix.
    Returns: (allowed: bool, retry_after_seconds: int)
    """
    ip = _get_client_ip(request)
    key = f"{key_prefix}:{ip}" if key_prefix else ip
    now = time.time()
    dq = _request_log[key]

    # Loại bỏ các timestamp ngoài cửa sổ 60 giây
    while dq and now - dq[0] > WINDOW_SEC:
        dq.popleft()

    if len(dq) >= limit:
        oldest = dq[0]
        retry_after = int(WINDOW_SEC - (now - oldest)) + 1
        return False, max(retry_after, 1)

    dq.append(now)
    return True, 0


def enforce_rate_limit(
    request: Request, 
    limit: int = RATE_LIMIT, 
    key_prefix: str = "default"
) -> None:
    """
    Kiểm tra và raise HTTP 429 nếu vượt rate limit cho tính năng tương ứng.
    """
    allowed, retry_after = check_rate_limit(request, limit=limit, key_prefix=key_prefix)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail={
                "message": f"Bạn đã dùng hết {limit} lượt/phút cho chức năng này. Vui lòng chờ {retry_after} giây.",
                "retry_after": retry_after,
                "limit": limit,
                "window": WINDOW_SEC
            }
        )
