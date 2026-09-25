# services/storyboard_store.py

## Mục đích
CRUD storyboard với file JSON riêng + `threading.Lock()`.

## Functions
### `save_storyboard(storyboard) -> StoryboardResponse`
- Ghi file `{STORYBOARD_DIR}/{id}.json`
- Có Lock chống race condition
- Tự xóa cũ nếu vượt 50

### `get_storyboard(id) -> Optional[StoryboardResponse]`
- Trả None nếu không tìm thấy hoặc file hỏng

### `load_storyboards() -> List[StoryboardResponse]`
- Sắp xếp mới nhất trước, bỏ qua file lỗi

### `update_segment(storyboard_id, segment_id, data) -> bool`
- Cập nhật `completed` count và `status` tổng thể

### `delete_storyboard(id) -> bool`
- 404 nếu không tìm thấy

### `_enforce_max_storyboards() -> int`
- Xóa cũ nhất nếu vượt `MAX_STORYBOARDS` (50)

## Keywords
`storyboard_store`, `save_storyboard`, `get_storyboard`, `load_storyboards`, `update_segment`, `delete_storyboard`, `_enforce_max_storyboards`, `threading.Lock`, `race condition`, `MAX_STORYBOARDS`, `file riêng`

## Phụ thuộc
- Import: `core.config.settings`, `models.storyboard`
- Import bởi: `services/storyboard_orchestrator.py`, `routers/storyboard_router.py`
- Test: `test/test_storyboard_store.py`
