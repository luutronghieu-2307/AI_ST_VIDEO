# 📄 Module Documentation: `services/srt_parser.py`

## 🎯 Mục đích
Phân tích cú pháp tệp phụ đề SubRip (`.srt`), trích xuất mốc thời gian (timecodes), nội dung lời thoại (text), tính toán thời lượng và quy đổi số khung hình video chuẩn hóa `1 + 8k` ở tốc độ 16fps cho mô hình Pixazo LTX 2.5.

---

## 🔑 Các hàm chính

| Hàm | Input | Output | Chức năng |
|---|---|---|---|
| `parse_timestamp(ts_str)` | `str` (vd: `00:01:23,456`) | `float` (giây) | Chuyển đổi timestamp SRT sang giây |
| `calculate_frames_1_plus_8k(duration_sec, fps, min_frames, max_frames)` | `float`, `int` | `int` | Tính số frame theo công thức `1 + 8k` (clamp `[25, 121]`) |
| `parse_srt(srt_content, fps, max_segments, extra_padding_sec)` | `str`, `int`, `int`, `float` | `List[ParsedSrtSegment]` | Parse toàn bộ SRT, tự động đệm `+1.0s` cho phân đoạn cuối cùng |

---

## 📦 Cấu trúc `ParsedSrtSegment`
- `order: int` (Thứ tự phân đoạn, bắt đầu từ 1)
- `start_sec: float` (Giây bắt đầu)
- `end_sec: float` (Giây kết thúc)
- `duration_sec: float` ($\Delta t = \text{end\_sec} - \text{start\_sec}$, segment cuối có +1.0s đệm)
- `timecode: str` (Chuỗi SRT `00:00:00,100 --> 00:00:04,292`)
- `text: str` (Nội dung thoại sạch)
- `num_frames: int` (Số frame `1+8k`)

