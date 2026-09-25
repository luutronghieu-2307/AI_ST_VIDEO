# routers/generate_router.py

## Mục đích
API endpoint xử lý yêu cầu sinh ảnh/logo từ client, delegate logic xuống `pixazo_service`.

## Router
- **Prefix**: `/api`
- **Tag**: `Image Generation`
- **Export**: `generate_router`

## Endpoints

### POST `/api/generate`
- **Request body**: `GenerateRequest` (JSON)
- **Response**: `GenerateResponse` (JSON)
- **Logic**: Gọi `pixazo_service.generate_image(payload)` → trả `GenerateResponse(output=url, status="success")`
- **Lỗi**: Delegate hoàn toàn từ `pixazo_service` (HTTPException)

## Keywords
`generate_router`, `/api/generate`, `POST`, `GenerateRequest`, `GenerateResponse`, `pixazo_service`, `image generation`, `API endpoint`

## Phụ thuộc
- Import: `models.generate`, `services.pixazo_service`
- Đăng ký tại: `main.py` (`app.include_router`)
