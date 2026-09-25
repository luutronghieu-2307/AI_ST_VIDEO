# services/groq_service.py

## Mục đích
Gọi Groq REST API để lấy danh sách các model Vision và phân tích ảnh sinh prompt AI cho Flux.1.

## Class & Exports
- **`GroqService`** – class với static methods
- **`groq_service`** – singleton instance

## Methods

### `get_vision_models(api_key: Optional[str]) -> List[Dict[str, Any]]`
- GET `https://api.groq.com/openai/v1/models`
- Kiểm tra `api_key`: nếu rỗng trả về `[]`
- Lọc theo trường chính thức từ Groq: `image in model["input_modalities"]` hoặc các keyword dự phòng (`vision`, `scout`, `maverick`, `llava`, `-vl-`)
- Bỏ qua các model không active
- Trả về danh sách `[{"id": "...", "name": "...", "context_window": ...}]`

### `suggest_prompt(image_base64, image_mime, api_key, model_id=None, mode='standard') -> str`
- Build `data URI`: `data:{mime};base64,{b64}`
- **Bước 1 (Cơ bản)**: Gọi Groq Vision model (`model_id or settings.GROQ_MODEL`) với `SYSTEM_PROMPT_STANDARD` để trích xuất prompt bám sát ảnh gốc.
- **Bước 2 (Nâng cao - khi mode='advanced')**: Gửi baseline prompt sang `settings.GROQ_CREATIVE_MODEL` (`openai/gpt-oss-120b`) với `SYSTEM_PROMPT_ENHANCED` để nâng cấp thiết kế sáng tạo, độc đáo, không rập khuôn ảnh mẫu.
- Trả về: chuỗi prompt hoàn chỉnh cho Flux.1 Schnell.

## Xử lý lỗi
| Case | HTTP | Mô tả |
|---|---|---|
| Thiếu API key | 400 | Chưa cấu hình GROQ_API_KEY |
| Key sai | 401 | Groq trả 401 |
| Groq rate limit | 429 | Groq API bị giới hạn |
| Timeout | 504 | Vượt `GROQ_TIMEOUT` |
| Kết nối lỗi | 500 | `requests.RequestException` |

## Keywords
`groq_service`, `suggest_prompt`, `get_vision_models`, `GroqService`, `Groq`, `Llama 4 Scout`, `GPT 120B`, `gpt-oss-120b`, `SYSTEM_PROMPT_STANDARD`, `SYSTEM_PROMPT_ENHANCED`, `vision`, `multimodal`, `image_base64`, `data URI`, `chat/completions`, `system_prompt`, `model_id`, `mode`, `standard`, `advanced`

## Phụ thuộc
- Import: `core.config.settings`
- Import bởi: `routers/suggest_router.py`
