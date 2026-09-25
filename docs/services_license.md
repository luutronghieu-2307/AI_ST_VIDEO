# docs/services_license.md – Dịch vụ Bản quyền & Khóa Phần cứng (HWID)

## Mục đích
Quản lý mã phần cứng máy tính (Hardware ID), xác thực License Key **REMOTE qua GitHub Private Repo** và lưu trữ trạng thái kích hoạt ràng buộc cứng với thiết bị.

> 🔐 **Cơ chế mới (v2)**: Key KHÔNG còn nhúng trong EXE. Trạng thái `used` lưu server-side trên GitHub → mỗi key chỉ dùng được **1 lần**, share EXE cũ vô hiệu.

## Các hàm chính

### `verify_license_key_remote(key) -> Tuple[bool, str]`
**Hàm xác thực chính** — gọi GitHub API để kiểm tra:
1. Key có tồn tại trong `keys.json` không
2. Key đã được dùng chưa (`used == true`)

Trả về `(is_valid, message)`. Không raise exception — trả `False` kèm thông báo lỗi.

### `bind_machine(key) -> Tuple[bool, str]`
Kích hoạt key theo quy trình 3 bước:
1. Gọi `github_key_store.activate_key(key, hwid)` — xác thực + đánh dấu `used=true` trên GitHub
2. Nếu thành công → tạo chữ ký `compute_activation_signature(key, hwid)`
3. Lưu `activation.dat` local (base64 JSON) để `check_activation()` chạy offline

### `check_activation() -> Tuple[bool, Optional[str]]`
Kiểm tra máy hiện tại đã kích hoạt chưa (dựa vào `activation.dat` local).
- So sánh `stored_hwid` với `get_hwid()` hiện tại
- HWID lệch → từ chối (chống copy sang máy khác)

### `verify_license_key(key) -> bool`
⚠️ **DEPRECATED** — chỉ kiểm tra key có trong file `license.key` local (legacy).
Không còn fallback bypass (đã fix lỗ hổng V3).

### `compute_activation_signature(key, hwid) -> str`
Tạo chữ ký SHA256 gắn Key + HWID + `SECRET_SALT`.

### `get_stored_license_keys() -> list[str]`
Đọc danh sách key từ file `license.key` local (chỉ dùng cho legacy/offline).

## Hằng số
| Hằng | Giá trị |
|---|---|
| `SECRET_SALT` | `"AURA_AI_MASTER_SECRET_2026_SECURE_SALT"` |
| `ACTIVATION_FILE` | `"activation.dat"` |
| `LICENSE_FILE` | `"license.key"` |

## Luồng kích hoạt
```text
Người dùng nhập key
  │
  ▼ verify_license_key_remote(key)
  │   └─► github_key_store.fetch_keys() → kiểm tra tồn tại + used
  │
  ▼ bind_machine(key)
  │   └─► github_key_store.activate_key(key, hwid)
  │         ├─ GET keys.json (data + sha)
  │         ├─ Kiểm tra used == false
  │         ├─ PUT keys.json (used=true, hwid, activated_at)
  │         └─ 409 Conflict → retry (tối đa 3 lần)
  │
  ▼ Lưu activation.dat local
  │
  ▼ check_activation() → so sánh HWID
```

## Từ khóa
`license_service`, `hardware_service`, `get_hwid`, `verify_license_key`, `verify_license_key_remote`, `bind_machine`, `check_activation`, `compute_activation_signature`, `activation.dat`, `license.key`, `shortcut_service`, `github_key_store`, `remote license`, `key dùng 1 lần`

## Phụ thuộc
- Import: `services.hardware_service`, `services.github_key_store`
- Import bởi: `launcher.py`
- Test: `test/test_license_service.py`
