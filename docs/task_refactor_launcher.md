# 📋 Kế hoạch Tối ưu & Phân tách: `launcher.py`

> **Trạng thái**: ✅ Đã hoàn thành  
> **File gốc**: `launcher.py` (Trước: 250 dòng -> Sau: 31 dòng)  
> **Kết quả**: Tạo package `launcher_core/` (`single_instance.py`: 19 dòng, `server_runner.py`: 61 dòng, `launcher_gui.py`: 161 dòng), Pytest 8/8 tests passed.

---

## 1. Phân tích Hiện trạng
File `launcher.py` hiện bao gồm:
1. **Single Instance Locking**: `ensure_single_instance` (Socket / Lock file).
2. **Server Health Check**: `wait_for_server` (Kiểm tra HTTP GET /).
3. **Tkinter GUI Building**: Toàn bộ widget setup, custom styles, copy HWID button, entry box, status label, launch button.
4. **Server Background Process Management**: `_launch_worker`, chạy subprocess `scripts/setup_and_run.sh` hoặc `uvicorn` và mở browser.
5. **License Verification Integration**: Gọi `verify_license_key_remote` và cập nhật UI.

---

## 2. Phương án Phân tách (Modular Architecture)

Tạo package `launcher_app/` hoặc tách các helper logic:

```
launcher_core/
├── __init__.py
├── single_instance.py   # (~30 dòng): Cơ chế đảm bảo chỉ có 1 instance launcher chạy
├── server_runner.py     # (~70 dòng): Subprocess management, health check, launch browser
└── launcher_gui.py      # (~140 dòng): Tkinter UI layout & event handlers
launcher.py              # (~20 dòng): Entry point khởi chạy app
```

### Chi tiết phân chia nhiệm vụ:

#### 1. `launcher_core/single_instance.py`
- `ensure_single_instance(port=49152)`: Giữ socket binding hoặc lockfile trên Linux/Windows để chống mở lặp.

#### 2. `launcher_core/server_runner.py`
- `wait_for_server(host, port, timeout)`: Polling HTTP socket đến khi FastAPI sẵn sàng.
- `start_server_process(mode)`: Khởi chạy tiến trình `main.py` ngầm.
- `open_browser(url)`: Mở trình duyệt mặc định trỏ tới URL server.

#### 3. `launcher_core/launcher_gui.py`
- Lớp `AuraLauncherApp(tk.Tk)`:
  - Khởi tạo giao diện Tkinter Dark Glassmorphic.
  - Giao tiếp với `services.license_service` để kiểm tra key.
  - Gọi `server_runner` trong background thread.

#### 4. `launcher.py`
- File entry point cực kỳ tinh gọn:
  ```python
  from launcher_core.single_instance import ensure_single_instance
  from launcher_core.launcher_gui import AuraLauncherApp

  def main():
      sock = ensure_single_instance()
      app = AuraLauncherApp()
      app.mainloop()

  if __name__ == "__main__":
      main()
  ```

---

## 3. Kế hoạch Thực hiện

- [ ] **Bước 1**: Tạo thư mục `launcher_core/` với các file `single_instance.py`, `server_runner.py`, `launcher_gui.py`.
- [ ] **Bước 2**: Chuyển các khối logic tương ứng vào các file mới.
- [ ] **Bước 3**: Cập nhật `launcher.py` thành file entry point ngắn gọn (< 30 dòng).
- [ ] **Bước 4**: Kiểm tra chạy thử `./run_launcher.sh` hoặc `python launcher.py`.
- [ ] **Bước 5**: Viết/cập nhật test trong `test/test_launcher.py`.
- [ ] **Bước 6**: Cập nhật `docs/launcher.md` và `DOCS_INDEX.md`.
