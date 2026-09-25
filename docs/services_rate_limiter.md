# services/rate_limiter.py

## Mục đích
In-memory rate limiter dùng sliding window, expose như FastAPI Dependency.

## Hằng số
| Hằng | Giá trị | Mô tả |
|---|---|---|
| `RATE_LIMIT` | `20` | Max requests trong cửa sổ |
| `WINDOW_SEC` | `60` | Cửa sổ trượt (giây) |

## Functions
- **`check_rate_limit(request, limit=20, key_prefix='default') -> (bool, int)`** – kiểm tra theo IP + key_prefix, trả `(allowed, retry_after)`
- **`enforce_rate_limit(request, limit=20, key_prefix='default')`** – raise `HTTPException(429)` nếu vượt
- **`_get_client_ip(request)`** – lấy IP từ `X-Forwarded-For` hoặc `request.client.host`

## Response 429
```json
{
  "detail": {
    "message": "Bạn đã dùng hết 10 lượt/phút cho chức năng này. Vui lòng chờ 45 giây.",
    "retry_after": 45,
    "limit": 10,
    "window": 60
  }
}
```

## Áp dụng cho
- `POST /api/generate` (generate_router – 20 req/phút)
- `POST /api/suggest-prompt` (suggest_router – 20 req/phút với Standard, 10 req/phút với Advanced)

## Lưu ý
- Storage: in-memory `defaultdict(deque)` – reset khi restart server
- Hỗ trợ phân biệt key_prefix để rate limit độc lập giữa các chế độ

## Keywords
`rate_limiter`, `enforce_rate_limit`, `check_rate_limit`, `RateLimit`, `429`, `retry_after`, `sliding window`, `deque`, `X-Forwarded-For`, `IP`, `10 req/phút`, `20 req/phút`, `suggest_advanced`, `Depends`

## Phụ thuộc
- Không phụ thuộc module nội bộ nào
- Import bởi: `routers/generate_router.py`, `routers/suggest_router.py`
