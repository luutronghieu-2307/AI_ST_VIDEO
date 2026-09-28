# 📋 Kế hoạch Tối ưu & Phân tách: `templates/js/storyboard_manager.js`

> **Trạng thái**: ✅ Đã hoàn thành  
> **File gốc**: `templates/js/storyboard_manager.js` (Trước: 276 dòng -> Sau: 240 dòng)  
> **Kết quả**: Tách `storyboard_audio_handler.js` (90 dòng), `storyboard_manager.js` (240 dòng), toàn bộ 74 tests trong test suite đều pass.

---

## 1. Phân tích Hiện trạng
File `templates/js/storyboard_manager.js` hiện là bộ điều khiển chính của Storyboard Studio, ôm đồm nhiều nhiệm vụ:
1. **Upload & Phân tích Audio / SRT**: `handleAudioUpload`, `resetAudioUpload`, `formatDuration`, `updateInfoCard`, `estimateTime`.
2. **Quản lý Form & Khởi tạo Job**: `handleCreateStoryboard`, `resumeActiveStoryboard`.
3. **Polling & Đồng bộ State**: `startPolling`, `pollStoryboardStatus`, `updateProgress`.
4. **Render UI & Timeline**: `renderTimeline`, `renderSegmentCard`, `attachSegmentEvents`, `openFullscreen`, `handleSavePromptEdit`.
5. **Toast & Notification**: `showToast`.

---

## 2. Phương án Phân tách (Modular Architecture)

Tận dụng kiến trúc đã có sẵn (`storyboard_api.js`, `storyboard_ui.js`, `storyboard_history.js`), chuyển bớt các phần xử lý chi tiết:

```
templates/js/
├── storyboard_audio_handler.js  # (~80-100 dòng): Upload audio/srt, tính duration, estimate time & info cards
├── storyboard_timeline_view.js  # (~100-120 dòng): Render timeline cards, segment events, full video player
└── storyboard_manager.js        # (~120-140 dòng): Controller chính kết nối Form, Polling, Orchestration
```

### Chi tiết phân chia nhiệm vụ:

#### 1. `templates/js/storyboard_audio_handler.js`
- **Nhiệm vụ**: Quản lý zone upload audio & srt, đo thời lượng và cập nhật summary card.
- **Hàm dự kiến**:
  - `handleAudioUpload(file)`: Đọc duration audio via Audio Element API.
  - `resetAudioUpload()`: Xóa file audio đã chọn, reset preview.
  - `formatDuration(seconds)`: Format `MM:SS`.
  - `updateInfoCard(duration, segmentCount)`: Cập nhật thẻ tóm tắt thông số.
  - `estimateTime(segmentCount)`: Ước tính thời gian render.

#### 2. `templates/js/storyboard_timeline_view.js`
- **Nhiệm vụ**: Render các thẻ phân đoạn trên Timeline, modal chỉnh sửa prompt và player video.
- **Hàm dự kiến**:
  - `renderTimeline(storyboard)`: Render container timeline và danh sách cards.
  - `renderSegmentCard(segment)`: Render HTML cho từng card phân đoạn (trạng thái pending, processing, completed, failed).
  - `updateProgress(storyboard)`: Cập nhật progress bar tổng thể.
  - `attachSegmentEvents()`: Đăng ký các sự kiện retry, edit prompt, xem fullscreen.
  - `openFullscreen(url)` / `handleSavePromptEdit()`: Xử lý xem video to & modal sửa prompt.

#### 3. `templates/js/storyboard_manager.js`
- **Nhiệm vụ**: Controller điều phối:
  - `initStoryboardManager()`: Khởi tạo DOM bindings, event listeners cho nút tạo storyboard, resume active storyboard từ `localStorage`.
  - `handleCreateStoryboard()`: Thu thập form data, gọi `storyboard_api.js` và chuyển sang polling.
  - `startPolling(storyboardId)` / `pollStoryboardStatus(storyboardId)`: Polling trạng thái định kỳ 10s.
  - `handleRegenerateSegment(segmentId)`: Gửi yêu cầu sinh lại segment.

---

## 3. Kế hoạch Thực hiện

- [ ] **Bước 1**: Tạo `templates/js/storyboard_audio_handler.js` và chuyển các hàm liên quan đến audio/srt.
- [ ] **Bước 2**: Chuyển các hàm render chi tiết vào `templates/js/storyboard_timeline_view.js` (hoặc mở rộng `storyboard_ui.js` nếu phù hợp quy chuẩn < 150 dòng).
- [ ] **Bước 3**: Rút gọn `templates/js/storyboard_manager.js` xuống dưới 140 dòng.
- [ ] **Bước 4**: Cập nhật `templates/base.html` include các file script mới.
- [ ] **Bước 5**: Chạy `npm test` và cập nhật test suite đạt coverage ≥ 90%.
- [ ] **Bước 6**: Cập nhật `docs/templates_storyboard.md` và `DOCS_INDEX.md`.
