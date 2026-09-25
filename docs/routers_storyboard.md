# 🌐 Module Documentation: `routers/storyboard_router.py`

## 🎯 Mục đích
Cung cấp các REST API endpoints cho tính năng Storyboard Video với đầu vào Subtitle SRT, đính kèm MP3 lồng tiếng và ghép nối video tự động.

---

## 📡 Endpoints

| Method | Endpoint | Request | Response | Chức năng |
|---|---|---|---|---|
| `POST` | `/api/storyboard/create` | Form (`title`, `srt_text`, `srt_file`, `audio_file`, `aspect`...) | `StoryboardResponse` | Khởi tạo storyboard từ SRT và chạy render ngầm |
| `GET` | `/api/storyboard/list` | None | `List[StoryboardResponse]` | Danh sách tất cả storyboard (mới nhất trước) |
| `GET` | `/api/storyboard/{id}` | None | `StoryboardResponse` | Chi tiết storyboard |
| `GET` | `/api/storyboard/{id}/status` | None | `Dict` (tiến độ, `merged_video_url`...) | Polling tiến độ render & ghép nối |
| `POST` | `/api/storyboard/{id}/stitch` | None | `Dict` | Kích hoạt ghép & lồng tiếng lại thủ công |
| `POST` | `/api/storyboard/{id}/segment/{idx}/regenerate` | `SegmentRegenerateRequest` | `StoryboardSegment` | Tạo lại segment với custom prompt |
| `POST` | `/api/storyboard/{id}/segment/{idx}/retry` | None | `StoryboardSegment` | Thử lại segment lỗi |
| `DELETE` | `/api/storyboard/{id}` | None | `Dict` | Xóa storyboard |
