# services/prompt_store.py

## Mục đích
Đọc/ghi danh sách prompt templates vào file JSON (`data/prompt_templates.json`).

## Functions
- **`load_templates() -> List[PromptTemplate]`** – đọc JSON, tự tạo file mặc định nếu chưa có
- **`save_template(name, prompt) -> PromptTemplate`** – tạo UUID mới, append vào JSON
- **`delete_template(id) -> bool`** – xóa theo ID, ném 404 nếu không tìm thấy, 403 nếu is_default
- **`delete_templates_batch(ids) -> List[str]`** – xóa nhiều template theo danh sách ID (bỏ qua template mặc định)
- **`_write_raw(data)`** – ghi thẳng list dict vào JSON (private)
- **`_ensure_data_dir()`** – tạo thư mục `data/` nếu chưa có

## Template mặc định (4 items)
IDs: `default-fox-logo`, `default-mecha-samurai`, `default-luxury-monogram`, `default-glass-orb`
- `is_default: True` → không thể xóa qua API

## Keywords
`prompt_store`, `load_templates`, `save_template`, `delete_template`, `delete_templates_batch`, `batch delete`, `prompt_templates.json`, `PromptTemplate`, `is_default`, `UUID`, `JSON file`, `data directory`

## Phụ thuộc
- Import: `core.config.settings`, `models.suggest.PromptTemplate`
- Import bởi: `routers/suggest_router.py`
