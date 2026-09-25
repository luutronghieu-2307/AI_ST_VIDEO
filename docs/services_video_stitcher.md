# 🎬 Module Documentation: `services/video_stitcher_service.py`

## 🎯 Mục đích
Tải về các video phân đoạn MP4 do Pixazo LTX 2.5 tạo ra, ghép nối liền mạch (Video Concat) bằng FFmpeg và lồng track âm thanh MP3 (Audio Muxing) để xuất ra file video hoàn chỉnh có đầy đủ hình ảnh và tiếng lồng.

---

## ⚙️ Công nghệ sử dụng
- **`imageio-ffmpeg`**: Cung cấp binary FFmpeg độc lập nền tảng (chạy trên cả Linux, Windows, macOS không cần cài thêm tool ngoài hệ thống).
- **FFmpeg Concat Demuxer**: Ghép nối nhanh không giảm chất lượng qua `ffmpeg -f concat -c copy` (tự động fallback sang re-encode H.264 nếu cần).
- **Audio Muxing**: `ffmpeg -i temp_video.mp4 -i voice.mp3 -c:v copy -c:a aac final.mp4` (không dùng `-shortest` để video luôn phát hết thời lượng đầy đủ).

---

## 🔑 Các hàm chính

| Hàm | Tham số | Trả về | Chức năng |
|---|---|---|---|
| `download_video_segment(url, dest_path)` | `url`, `dest_path` | `str` | Tải video MP4 về thư mục tạm |
| `stitch_and_mux_storyboard(storyboard_id, segment_urls, audio_path)` | `str`, `List[str]`, `Optional[str]` | `str` (URL static) | Ghép nối video và lồng tiếng MP3 |
