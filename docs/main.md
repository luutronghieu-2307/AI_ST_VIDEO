# main.py

## Mục đích
Entry point của ứng dụng FastAPI. Khởi tạo app, cấu hình middleware, mount static files và đăng ký routers.

## Khởi tạo App
```python
app = FastAPI(title, description, version)  # từ settings
```

## Middleware
- **CORSMiddleware**: `allow_origins=["*"]` – cho phép tất cả origin

## Static Files (Mount)
| Route | Thư mục | Name |
|---|---|---|
| `/css` | `templates/css` | `css` |
| `/js` | `templates/js` | `js` |
| `/templates` | `templates` | `templates` |

> Chỉ mount nếu thư mục tồn tại (`os.path.exists`).

## Routers đăng ký
- `views_router` → phục vụ trang web (GET `/`)
- `generate_router` → API sinh ảnh (POST `/api/generate`)
- `suggest_router` → API gợi ý prompt (Groq)
- `storyboard_router` → API Storyboard Video (prefix `/api/storyboard`)

## Startup Event
```python
@app.on_event("startup")
async def startup_cleanup():
    """Cleanup segment treo khi server khởi động."""
    cleaned = cleanup_stuck_segments()
```
- Gọi `cleanup_stuck_segments()` từ `services/storyboard_orchestrator.py`
- Đánh dấu segment `processing` > 10 phút thành `failed`
- Bọc try/except để không chặn khởi động

## Khởi chạy
```bash
python main.py
# hoặc
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

> ⚠️ **Lưu ý**: `main.py` chạy `uvicorn.run(..., reload=False)`. KHÔNG dùng `reload=True` khi test storyboard vì background thread (8-15 phút) sẽ bị kill mỗi lần reload code.

## Keywords
`FastAPI`, `app`, `CORSMiddleware`, `StaticFiles`, `mount`, `include_router`, `views_router`, `generate_router`, `suggest_router`, `storyboard_router`, `startup_cleanup`, `cleanup_stuck_segments`, `on_event`, `reload=False`, `uvicorn`, `entry point`, `startup`

## Phụ thuộc
- Import: `core.config.settings`, `routers.views_router`, `routers.generate_router`, `routers.suggest_router`, `routers.storyboard_router`, `services.storyboard_orchestrator.cleanup_stuck_segments`
