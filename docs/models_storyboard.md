# 📦 Module Documentation: `models/storyboard.py`

## 🎯 Mục đích
Định nghĩa các Pydantic Schemas / DTOs phục vụ luồng tạo Storyboard Video từ Subtitle SRT và ghép nối âm thanh MP3.

---

## 📋 Schemas

### 1. `StoryboardSegment`
- `id: str`: ID định danh phân đoạn (vd: `seg_a1b2c3d4`).
- `order: int`: Thứ tự trong storyboard (1-based).
- `text: str`: Lời thoại của phân đoạn.
- `start_sec: float`: Mốc thời gian bắt đầu (giây).
- `end_sec: float`: Mốc thời gian kết thúc (giây).
- `timecode: Optional[str]`: Chuỗi SRT timecode (`00:00:00,100 --> 00:00:04,292`).
- `video_prompt: Optional[str]`: Prompt sinh từ GPT-120B.
- `video_url: Optional[str]`: URL video MP4 từ Pixazo.
- `request_id: Optional[str]`: ID request Pixazo.
- `status: str`: `pending` | `processing` | `completed` | `failed`.
- `error: Optional[str]`: Chi tiết lỗi nếu thất bại.
- `duration_sec: float`: Thời lượng phân đoạn ($\Delta t$).
- `num_frames: int`: Số khung hình chuẩn `1 + 8k` @ 16fps.

### 2. `StoryboardResponse`
- `storyboard_id: str`: ID storyboard.
- `title: str`: Tiêu đề storyboard.
- `status: str`: Trạng thái tổng thể.
- `segments: List[StoryboardSegment]`: Danh sách phân đoạn.
- `total: int`: Tổng số phân đoạn.
- `completed: int`: Số phân đoạn đã hoàn thành.
- `total_duration_sec: float`: Tổng thời lượng kịch bản.
- `merged_video_url: Optional[str]`: Đường dẫn static tới file video hoàn chỉnh sau khi ghép & lồng tiếng.
- `has_audio: bool`: Đã lồng tiếng file MP3.
- `is_stitching: bool`: Đang trong quá trình ghép nối video.
- `frame_rate: int`: 16 fps.
- `aspect: str`: Tỷ lệ khung hình (`16:9`, `9:16`, `1:1`, `21:9`, `4:3`).
- `created_at: str`: ISO timestamp.
