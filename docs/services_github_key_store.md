# services/github_key_store.py

## Mục đích
Quản lý kho License Key trên **GitHub Private Repo** qua GitHub Contents API. Đây là nguồn chân lý (source of truth) cho trạng thái key — thay thế hoàn toàn cơ chế nhúng `license.key` vào EXE.

## Class & Exports
- **`GitHubKeyStore`** – class với static methods
- **`github_key_store`** – singleton instance dùng trong `license_service`

## Hằng số
| Hằng | Giá trị | Mô tả |
|---|---|---|
| `MAX_RETRY` | `3` | Số lần retry tối đa khi gặp conflict (409) |

## Methods

### `_resolve_token() -> str`
Lấy token theo thứ tự ưu tiên: `settings.GITHUB_TOKEN` (.env) → token obfuscated nhúng trong EXE.

### `_validate_config(token) -> None`
Kiểm tra `GITHUB_TOKEN` và `GITHUB_REPO` (định dạng `owner/repo`). Raise `HTTPException(500)` nếu thiếu.

### `_handle_error(resp) -> None`
Chuyển lỗi HTTP từ GitHub thành `HTTPException` thân thiện:
| GitHub Status | HTTPException |
|---|---|
| 401 | 401 – Token không hợp lệ |
| 403 | 403 – Thiếu quyền truy cập |
| 404 | 404 – Không tìm thấy repo/file |
| 429 | 429 – Rate limit |
| Khác | Forward status |

### `fetch_keys() -> Tuple[Dict, str]`
- GET `/repos/{owner}/{repo}/contents/{path}`
- Decode base64 content → parse JSON
- Trả về `(data_dict, sha)` — `sha` dùng cho optimistic locking
- Lỗi: 504 (timeout), 500 (connection error, JSON hỏng)

### `_write_keys(data, sha, message) -> bool`
- PUT `/repos/{owner}/{repo}/contents/{path}` với `sha` cũ
- Tự cập nhật `updated_at` trước khi ghi
- Trả `False` nếu gặp **409 Conflict** (cần retry), `True` nếu thành công

### `find_key(data, license_key) -> Optional[Dict]`
Tìm entry key trong `data["keys"]`, tự động strip whitespace.

### `activate_key(license_key, hwid) -> Tuple[bool, str]`
**Phương thức cốt lõi** — kích hoạt key với optimistic locking:
1. `fetch_keys()` → lấy data + sha
2. Kiểm tra key tồn tại → nếu không: `(False, "không tồn tại")`
3. Kiểm tra `used` → nếu đã dùng: `(False, "đã được sử dụng")`
4. Đánh dấu `used=true`, gán `hwid`, `activated_at`
5. `_write_keys()` → nếu conflict (409) thì retry (tối đa `MAX_RETRY` lần)
6. Hết retry → `(False, "Xung đột dữ liệu...")`

### `is_key_used(license_key) -> bool`
Kiểm tra nhanh trạng thái `used` của key.

## Cấu trúc `keys.json`
```json
{
  "version": 1,
  "updated_at": "2026-09-22T10:00:00Z",
  "keys": [
    {"key": "AURA-VIP-2026-xxx", "used": false, "hwid": null, "activated_at": null},
    {"key": "AURA-VIP-2026-yyy", "used": true, "hwid": "AURA-1A2B-...", "activated_at": "..."}
  ]
}
```

## Cơ chế chống Race Condition
Khi 2 máy kích hoạt cùng lúc:
1. Cả 2 GET `keys.json` với cùng `sha`
2. Máy A PUT thành công → GitHub tạo commit mới, `sha` thay đổi
3. Máy B PUT với `sha` cũ → GitHub trả **409 Conflict**
4. Máy B tự động retry: GET lại → thấy `used=true` → từ chối

## Keywords
`github_key_store`, `GitHubKeyStore`, `fetch_keys`, `activate_key`, `is_key_used`, `find_key`, `_write_keys`, `optimistic locking`, `sha`, `409 Conflict`, `MAX_RETRY`, `keys.json`, `GitHub Contents API`, `GITHUB_TOKEN`, `GITHUB_REPO`, `GITHUB_KEYS_PATH`, `race condition`, `remote license`

## Phụ thuộc
- Import: `core.config.settings`, `services.token_obfuscator`
- Import bởi: `services/license_service.py`
- Test: `test/test_github_key_store.py`
