# models/generate.py

## Mục đích
Định nghĩa Pydantic schema cho request/response của API sinh ảnh.

## Class & Exports
- **`GenerateRequest`** – schema input, validate dữ liệu từ client
- **`GenerateResponse`** – schema output, trả về URL ảnh

## Schema chi tiết

### GenerateRequest
| Field | Type | Default | Ràng buộc | Mô tả |
|---|---|---|---|---|
| `prompt` | `str` | bắt buộc | — | Mô tả ảnh/logo cần tạo |
| `num_steps` | `int` | `4` | 1–10 | Số bước lấy mẫu Flux.1 |
| `seed` | `Optional[int]` | `15` | — | Seed tái lập kết quả |
| `height` | `int` | `512` | 256–1024 | Chiều cao ảnh (px) |
| `width` | `int` | `512` | 256–1024 | Chiều rộng ảnh (px) |

### GenerateResponse
| Field | Type | Default | Mô tả |
|---|---|---|---|
| `output` | `str` | bắt buộc | URL công khai của ảnh được sinh |
| `status` | `str` | `"success"` | Trạng thái phản hồi |

## Keywords
`GenerateRequest`, `GenerateResponse`, `prompt`, `num_steps`, `seed`, `height`, `width`, `output`, `Pydantic`, `schema`, `DTO`, `validation`

## Phụ thuộc
- Không phụ thuộc module nội bộ nào
- Import bởi: `routers/generate_router.py`, `services/pixazo_service.py`
