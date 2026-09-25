# models/suggest.py

## Mục đích
Định nghĩa Pydantic schema cho tính năng AI Prompt Builder (Groq LLM).

## Class & Exports
- **`SuggestRequest`** – input: ảnh base64 + tên prompt + groq key + model_id
- **`GroqModelInfo`** – thông tin model Groq vision trả về từ API
- **`SuggestResponse`** – output: prompt được sinh + tên + ID template
- **`PromptTemplate`** – đại diện một template lưu trữ trong JSON

## Schema chi tiết

### SuggestRequest
| Field | Type | Default | Mô tả |
|---|---|---|---|
| `image_base64` | `str` | bắt buộc | Ảnh mẫu encode base64 |
| `image_mime` | `str` | `image/jpeg` | MIME type ảnh |
| `prompt_name` | `str` | bắt buộc | Tên template (1-80 chars) |
| `groq_api_key` | `Optional[str]` | `None` | Key client-side (ưu tiên hơn .env) |
| `model_id` | `Optional[str]` | `None` | ID model Groq vision được chọn |
| `mode` | `str` | `"standard"` | Chế độ sinh: `'standard'` (bám sát ảnh) hoặc `'advanced'` (sáng tạo GPT-120B) |

### GroqModelInfo
| Field | Type | Default | Mô tả |
|---|---|---|---|
| `id` | `str` | bắt buộc | Model ID trên Groq (VD: `meta-llama/llama-4-scout-17b-16e-instruct`) |
| `name` | `str` | bắt buộc | Tên hiển thị của model |
| `context_window` | `Optional[int]` | `None` | Context length (token) |

### SuggestResponse
| Field | Type | Mô tả |
|---|---|---|
| `prompt` | `str` | Prompt do LLM sinh ra |
| `name` | `str` | Tên template đã lưu |
| `saved` | `bool` | Luôn `True` |
| `template_id` | `str` | UUID của template vừa tạo |
| `mode` | `str` | Chế độ đã thực thi (`'standard'` hoặc `'advanced'`) |

### PromptTemplate
| Field | Type | Mô tả |
|---|---|---|
| `id` | `str` | UUID4 duy nhất |
| `name` | `str` | Tên hiển thị trong dropdown |
| `prompt` | `str` | Nội dung prompt |
| `created_at` | `str` | ISO timestamp |
| `is_default` | `bool` | Template mặc định (không xóa được) |

## Keywords
`SuggestRequest`, `GroqModelInfo`, `SuggestResponse`, `PromptTemplate`, `image_base64`, `image_mime`, `prompt_name`, `groq_api_key`, `model_id`, `mode`, `standard`, `advanced`, `template_id`, `is_default`

## Phụ thuộc
- Import bởi: `routers/suggest_router.py`, `services/prompt_store.py`
