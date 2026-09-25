# ⚙️ Module Documentation: `services/storyboard_orchestrator.py`

## 🎯 Mục đích
Bộ điều phối trung tâm của pipeline Text-to-Video Storyboard:
1. Gọi `services/srt_parser.py` để phân đoạn kịch bản và tính toán số khung hình.
2. Lưu file âm thanh MP3 đính kèm (nếu có) vào `data/audio_uploads/`.
3. Khởi động Background Thread gọi GPT-120B sinh prompt và Pixazo LTX 2.5 tạo video cho từng phân đoạn.
4. Tự động kích hoạt `services/video_stitcher_service.py` để ghép nối video và lồng tiếng MP3 khi toàn bộ phân đoạn hoàn thành.
5. Hỗ trợ tạo lại (regenerate) phân đoạn và tự động cập nhật lại video hoàn chỉnh.
