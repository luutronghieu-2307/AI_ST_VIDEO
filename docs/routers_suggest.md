# routers/suggest_router.py

## Mục đích
4 API endpoints cho tính năng AI Prompt Builder (Groq vision LLM).

## Router
- **Prefix**: `/api`
- **Tag**: `AI Prompt Builder`
- **Export**: `suggest_router`

## Endpoints

### GET `/api/groq-models`
- **Query param**: `groq_api_key: Optional[str]`
- **Output**: `List[GroqModelInfo]`
- **Logic**: Gọi `groq_service.get_vision_models()` → chỉ lọc các model có khả năng Vision (đọc ảnh)

### POST `/api/suggest-prompt`
- **Rate Limit**: 20 req/phút với Standard mode; 10 req/phút với Advanced mode (`enforce_rate_limit`)
- **Input**: `SuggestRequest` (image_base64, image_mime, prompt_name, groq_api_key, model_id, mode: standard | advanced)
- **Logic**: Resolve API key → `groq_service.suggest_prompt(mode=payload.mode)` → `save_template()` → trả `SuggestResponse`
- **429**: Rate limit exceeded (20 req/p cho Standard, 10 req/p cho Advanced)

### GET `/api/prompt-templates`
- **Output**: `List[PromptTemplate]`
- Gọi `load_templates()` → trả toàn bộ danh sách (mặc định + user-created)

### DELETE `/api/prompt-templates/{template_id}`
- **Output**: `{"success": true, "deleted_id": "..."}`
- Gọi `delete_template(id)` → 404 nếu không tìm thấy, 403 nếu template mặc định

### POST `/api/prompt-templates/batch-delete`
- **Input**: `BatchDeleteTemplateRequest` (ids: list[str])
- **Output**: `{"success": true, "deleted_count": N, "deleted_ids": [...]}`
- Gọi `delete_templates_batch(ids)` → xóa danh sách template (bỏ qua template mặc định)

## Keywords
`suggest_router`, `/api/groq-models`, `/api/suggest-prompt`, `/api/prompt-templates`, `/api/prompt-templates/batch-delete`, `batch-delete`, `POST`, `GET`, `DELETE`, `GroqModelInfo`, `PromptTemplate`, `SuggestResponse`, `BatchDeleteTemplateRequest`, `mode`, `standard`, `advanced`, `GPT-120B`, `10 req/phút`, `groq_service`, `prompt_store`, `rate_limit`, `template_id`

## Phụ thuộc
- Import: `models.suggest`, `services.groq_service`, `services.prompt_store`, `services.rate_limiter`
- Đăng ký tại: `main.py`
