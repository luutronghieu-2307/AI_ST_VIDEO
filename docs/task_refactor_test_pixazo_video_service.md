# 📋 Kế hoạch Tối ưu & Phân tách: `test/test_pixazo_video_service.py`

> **Trạng thái**: ✅ Đã hoàn thành  
> **File gốc**: `test/test_pixazo_video_service.py` (Trước: 259 dòng -> Xóa và tách thành 2 file)  
> **Kết quả**: Phân tách thành `test_pixazo_video_submit.py` (130 dòng) và `test_pixazo_video_polling.py` (152 dòng), Pytest coverage đạt 97%, 27/27 tests passed.

---

## 1. Phân tích Hiện trạng
File `test/test_pixazo_video_service.py` hiện bao gồm:
1. **Kiểm tra Payload & Headers**: Request headers, Ocp-Apim-Subscription-Key, format payload, default parameters.
2. **Kiểm tra Submit Video Job**: Success response, trả về job_id, status 200/202.
3. **Kiểm tra Polling & Completion**: Quá trình lặp kiểm tra status qua `poll_status` và `wait_for_completion`.
4. **Kiểm tra Retry Logic & Xử lý Lỗi / Timeout**: Lỗi 401, 429 rate limit, 500 server error, timeout quá hạn.

---

## 2. Phương án Phân tách (Modular Test Suite)

Tách `test/test_pixazo_video_service.py` thành 2 file test:

```
test/
├── test_pixazo_video_submit.py    # (~120 dòng): Test payload, headers, submit_video_job, helper validation
└── test_pixazo_video_polling.py   # (~130 dòng): Test polling status, wait_for_completion, retry logic, timeout & errors
```

### Chi tiết phân chia test:

#### 1. `test/test_pixazo_video_submit.py`
- Test `submit_video_job` gửi đúng HTTP POST request tới Gateway URL.
- Test headers có kèm API key từ settings.
- Test payload chứa đúng `prompt`, `num_frames`, `negative_prompt`, `aspect_ratio`.
- Test xử lý exception khi API Gateway từ chối kết nối hoặc trả về status != 200/202.

#### 2. `test/test_pixazo_video_polling.py`
- Test `poll_status` đọc đúng URL và parse trạng thái `pending` / `processing` / `completed` / `failed`.
- Test `wait_for_completion` tự động lặp lại cho đến khi `completed`.
- Test `wait_for_completion` ném ngoại lệ khi job `failed` hoặc vượt quá `max_poll_seconds`.
- Test retry backoff khi gặp lỗi mạng tạm thời hoặc 429.

---

## 3. Kế hoạch Thực hiện

- [ ] **Bước 1**: Tạo `test/test_pixazo_video_submit.py` chứa các test case submit & headers.
- [ ] **Bước 2**: Tạo `test/test_pixazo_video_polling.py` chứa các test case polling, timeout & error.
- [ ] **Bước 3**: Xóa file cũ `test/test_pixazo_video_service.py`.
- [ ] **Bước 4**: Chạy `pytest test/test_pixazo_video_*.py --cov=services.pixazo_video_service --cov-report=term-missing` đảm bảo coverage ≥ 90%.
- [ ] **Bước 5**: Cập nhật `docs/testing.md` và `DOCS_INDEX.md`.
