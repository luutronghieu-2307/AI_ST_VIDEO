# services/pixazo_service.py

## Mục đích
Tầng business logic trung tâm, chịu trách nhiệm gọi Pixazo Gateway (Flux.1 Schnell) để sinh ảnh AI.

## Class & Exports
- **`PixazoService`** – class chứa logic gọi API
- **`pixazo_service`** – singleton instance dùng trong routers

## Method quan trọng

### `generate_image(payload: GenerateRequest) -> str`
- **Input**: `GenerateRequest` (prompt, num_steps, seed, height, width)
- **Output**: `str` – URL công khai của ảnh đã sinh
- **Logic**:
  1. Kiểm tra `PIXAZO_API_KEY` hợp lệ → 400 nếu thiếu
  2. Build header: `Ocp-Apim-Subscription-Key`, `Content-Type`, `Cache-Control`
  3. POST tới `settings.PIXAZO_GATEWAY_URL` với timeout `settings.REQUEST_TIMEOUT`
  4. Parse `response.json()["output"]` → URL ảnh
  5. Raise `HTTPException` nếu: status != 200, thiếu trường `output`, timeout, lỗi kết nối

## Xử lý lỗi
| Trường hợp | HTTP Code | Mô tả |
|---|---|---|
| Thiếu API Key | 400 | Chưa cấu hình PIXAZO_API_KEY |
| Gateway trả lỗi | `gateway_status` | Forward status + message từ Pixazo |
| Thiếu trường `output` | 500 | Gateway không trả URL ảnh |
| Timeout | 504 | Vượt quá REQUEST_TIMEOUT |
| Lỗi kết nối | 500 | `requests.RequestException` |

## Keywords
`pixazo_service`, `generate_image`, `PixazoService`, `Pixazo`, `Flux.1`, `API_KEY`, `Ocp-Apim-Subscription-Key`, `gateway`, `HTTPException`, `timeout`, `requests`, `image_url`, `output`

## Phụ thuộc
- Import: `core.config.settings`, `models.generate.GenerateRequest`
- Import bởi: `routers/generate_router.py`
