# docs/launcher.md – Mini Launcher GUI & Quản lý Bản quyền

## Mục đích
Ứng dụng GUI khởi động trước khi bật backend FastAPI, tích hợp kiểm tra bản quyền License Key **REMOTE qua GitHub** và ràng buộc mã phần cứng máy tính (HWID Binding).

## Chức năng chính
1. **Chống bypass Local Web**: FastAPI server không chạy khi mở Launcher. Chỉ chạy khi đã nhập đúng Key và người dùng bấm nút Khởi động.
2. **Xác thực REMOTE**: Key được kiểm tra qua GitHub Private Repo (`keys.json`). Mỗi key chỉ dùng được **1 lần** — trạng thái `used` lưu server-side, share EXE cũ vô hiệu.
3. **Khóa máy (HWID Binding)**: Tự động trích xuất HWID máy và lưu mã hóa vào `activation.dat`. Nếu copy sang máy khác → HWID lệch → Khóa app.
4. **Auto-Provisioning**: Tự động tải Python 3.11 Embeddable và chạy `pip install -r requirements.txt` trong lần chạy đầu tiên.
5. **Desktop Shortcut**: Tự động tạo biểu tượng lối tắt ngoài màn hình Desktop kèm icon H-AURA.

## Luồng xác thực
```text
_initial_check()  → check_activation() (local, dựa vào activation.dat)
  │
  ▼ Nếu chưa kích hoạt
_on_key_change()  → verify_license_key_remote(key)
  │   └─► GitHub API: kiểm tra tồn tại + used == false
  │
  ▼ Nếu hợp lệ → enable nút Khởi động
_on_launch_clicked() → _launch_worker()
  │   └─► bind_machine(key) → github_key_store.activate_key()
  │         └─ Đánh dấu used=true trên GitHub (optimistic locking)
  │
  ▼ Khởi chạy Uvicorn server (background thread)
  │
  ▼ wait_for_server() → mở trình duyệt
```

## Hàm quan trọng
| Hàm | Mô tả |
|---|---|
| `ensure_single_instance()` | Mutex chống mở nhiều cửa sổ Launcher (Windows) |
| `wait_for_server(host, port, timeout)` | Poll cổng mạng đến khi server sẵn sàng |
| `_set_window_icon()` | Nạp icon H-AURA (.ico hoặc .png) |
| `_build_ui()` | Dựng giao diện Dark Theme (Tkinter) |
| `_on_key_change()` | Xác thực key REMOTE khi người dùng nhập |
| `_initial_check()` | Kiểm tra trạng thái kích hoạt + tạo shortcut |
| `_launch_worker()` | Bind license + khởi chạy Uvicorn trong thread |

## Từ khóa
`launcher`, `AuraLauncherApp`, `hwid`, `activation.dat`, `license.key`, `tkinter`, `desktop shortcut`, `auto-provisioning`, `launch_btn`, `verify_license_key_remote`, `github_key_store`, `remote license`

## Phụ thuộc
- Import: `services.hardware_service`, `services.license_service`, `services.shortcut_service`
- Đóng gói bởi: `AURA_Launcher.spec`, `scripts/build_bootstrap_exe.py`
