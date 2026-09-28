# 📋 Kế hoạch Tối ưu & Phân tách: `test/test_storyboard_manager.js`

> **Trạng thái**: ✅ Đã hoàn thành  
> **File gốc**: `test/test_storyboard_manager.js` (Trước: 286 dòng -> Sau: 143 dòng)  
> **Kết quả**: Phân tách thành `test_storyboard_audio_handler.js` (88 dòng), `test_storyboard_ui.js` (96 dòng), `test_storyboard_manager.js` (143 dòng). Toàn bộ 75 tests trong test suite đều pass.

---

## 1. Phân tích Hiện trạng
File `test/test_storyboard_manager.js` đang chứa toàn bộ test cases cho client Storyboard:
1. **Khởi tạo DOM & Form Setup**: Kiểm tra gán các event listener, render components.
2. **Xử lý Audio/SRT Upload**: Test đọc file audio, tính thời lượng, parse phụ đề, format duration.
3. **Submit Job & Tạo Storyboard**: Test gửi form multipart qua API mock, validate input.
4. **Polling Trạng thái**: Test vòng lặp polling, cập nhật progress bar, dừng polling khi completed/failed.
5. **Tương tác Timeline & Segment Actions**: Test retry segment, edit prompt, xem fullscreen, toast message.

---

## 2. Phương án Phân tách (Modular Test Suite)

Tách `test/test_storyboard_manager.js` thành các file test tương ứng với các module sau khi refactor:

```
test/
├── test_storyboard_audio_handler.js   # (~80-100 dòng): Test upload, duration calculation, estimate time
├── test_storyboard_timeline_view.js   # (~100-120 dòng): Test render timeline cards, progress & DOM events
└── test_storyboard_manager.js         # (~100-120 dòng): Test luồng chính (init, submit form, polling loop, resume)
```

### Chi tiết phân chia test:

#### 1. `test/test_storyboard_audio_handler.js`
- Test `handleAudioUpload` với file audio hợp lệ & không hợp lệ.
- Test `resetAudioUpload` dọn dẹp state và UI.
- Test `formatDuration` cho các trường hợp: 0s, 65s (`01:05`), 3600s (`60:00`).
- Test `updateInfoCard` và `estimateTime`.

#### 2. `test/test_storyboard_timeline_view.js`
- Test `renderTimeline` và `renderSegmentCard` với các status `pending`, `processing`, `completed`, `failed`.
- Test `updateProgress` tính toán % hoàn thành chính xác.
- Test `openFullscreen` và modal chỉnh sửa prompt.

#### 3. `test/test_storyboard_manager.js`
- Test `initStoryboardManager` khởi tạo đúng DOM bindings.
- Test `handleCreateStoryboard` gọi đúng API endpoint và bắt lỗi khi thiếu text/audio.
- Test `pollStoryboardStatus` với các kịch bản thành công, lỗi mạng, và tự động dừng polling.
- Test `resumeActiveStoryboard` từ `localStorage`.

---

## 3. Kế hoạch Thực hiện

- [ ] **Bước 1**: Tạo `test/test_storyboard_audio_handler.js` và di chuyển các test case liên quan đến audio.
- [ ] **Bước 2**: Tạo `test/test_storyboard_timeline_view.js` cho các test case render và UI interaction.
- [ ] **Bước 3**: Giữ lại các test case orchestration trong `test/test_storyboard_manager.js`.
- [ ] **Bước 4**: Chạy `npm test` để đảm bảo toàn bộ tests pass và coverage đạt ≥ 90%.
- [ ] **Bước 5**: Cập nhật `docs/testing.md` và `DOCS_INDEX.md`.
