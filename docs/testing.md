# 🧪 Testing Suite Documentation

## Tổng quan
Dự án được trang bị bộ kiểm thử tự động toàn diện cho cả Backend (Python với Pytest) và Frontend (JavaScript với Jest), tuân thủ tiêu chí độ bao phủ (coverage) ≥ 90%.

---

## 📁 Cấu trúc thư mục Test

```
test/
├── conftest.py                        # Shared fixtures (pytest)
├── _github_key_store_helpers.py       # Shared helpers cho test github_key_store
├── test_environment_service.py        # Unit tests cho services/environment_service.py
├── test_generate_router.py            # Integration tests cho routers/generate_router.py
├── test_github_key_store.py           # Unit tests: fetch_keys, find_key, _write_keys
├── test_github_key_store_activate.py  # Unit tests: activate_key, is_key_used, retry
├── test_groq_service.py               # Unit tests cho services/groq_service.py
├── test_hardware_service.py           # Unit tests cho services/hardware_service.py
├── test_license_service.py            # Unit tests cho services/license_service.py
├── test_pixazo_service.py             # Unit tests cho services/pixazo_service.py
├── test_prompt_store.py               # Unit tests cho services/prompt_store.py
├── test_rate_limiter.py               # Unit tests cho services/rate_limiter.py
├── test_shortcut_service.py           # Unit tests cho services/shortcut_service.py
├── test_suggest_router.py             # Integration tests cho routers/suggest_router.py
├── test_token_obfuscator.py           # Unit tests cho services/token_obfuscator.py
├── test_views_router.py               # Integration tests cho routers/views_router.py
└── test_history_manager.js            # Unit tests cho templates/js/history_manager.js (Jest)
```

---

## 🚀 Cách chạy Tests

### 1. Chạy Backend Tests & Coverage:
```bash
.venv/bin/pytest --cov=. --cov-report=term-missing
```

### 2. Chạy Frontend Tests (Jest):
```bash
npm test
```

### 3. Chạy cả hai:
```bash
.venv/bin/pytest --cov=. --cov-report=term-missing && npm test
```

---

## 🎯 Tiêu chuẩn Coverage

| Layer | Tool | Min Coverage |
|---|---|---|
| Python backend (services, routers, models) | pytest + pytest-cov | ≥ 90% |
| JavaScript frontend (templates/js/) | Jest + jsdom | ≥ 90% |

### Modules bảo mật (coverage mục tiêu ≥ 90%)
- `services/github_key_store.py` — optimistic locking, xử lý lỗi 401/403/404/409/429
- `services/token_obfuscator.py` — round-trip encode/decode
- `services/license_service.py` — verify remote, bind machine, check activation

---

## 📝 Quy tắc khi thêm tính năng mới
1. Tạo file test mới trong `test/` với tên `test_<module_name>.py` (Python) hoặc `test_<filename>.js` (JS)
2. Viết test cho: happy path, edge cases, error cases
3. Chạy `pytest` và `npm test` để đảm bảo tất cả pass
4. Kiểm tra coverage ≥ 90%
5. Cập nhật `DOCS_INDEX.md` nếu thêm module mới
