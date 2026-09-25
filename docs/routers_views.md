# routers/views_router.py

## Mục đích
Router phục vụ giao diện Frontend, render Jinja2 Template trả HTML cho trình duyệt.

## Router
- **Tag**: `Frontend Views`
- **Export**: `views_router`
- **Template dir**: `"templates"` (dùng `Jinja2Templates`)

## Endpoints

### GET `/`
- **Response class**: `HTMLResponse`
- **Ẩn khỏi OpenAPI schema**: `include_in_schema=False`
- **Logic**: Kiểm tra sự tồn tại `templates/index.html` → render với context `{"title": "AURA AI Logo Generator"}`
- **Lỗi 404**: Nếu `index.html` không tìm thấy

## Keywords
`views_router`, `Jinja2Templates`, `HTMLResponse`, `serve_index`, `index.html`, `template`, `frontend`, `GET /`, `context`, `title`

## Phụ thuộc
- Dùng: `Jinja2Templates` từ FastAPI
- Đăng ký tại: `main.py`
- Render: `templates/index.html` → `base.html` → các components
