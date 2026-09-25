# 🔐 Hướng dẫn Setup GitHub License Store

Hướng dẫn từng bước để cấu hình hệ thống bảo mật License Key mới (remote qua GitHub Private Repo).

---

## Bước 1: Tạo Private Repo chứa keys.json

1. Vào GitHub → **New repository**
2. Đặt tên, ví dụ: `aura-license-keys`
3. Chọn **Private** ⚠️ (bắt buộc)
4. Tạo file `keys.json` với nội dung mẫu từ [`data/keys.json`](../data/keys.json:1):

```json
{
  "version": 1,
  "updated_at": "2026-09-22T00:00:00+00:00",
  "keys": [
    {
      "key": "AURA-VIP-2026-F4rtvlZU2o",
      "used": false,
      "hwid": null,
      "activated_at": null
    }
  ]
}
```

> 💡 Copy toàn bộ 10 key từ [`data/keys.json`](../data/keys.json:1) vào repo này.

---

## Bước 2: Tạo Fine-grained Personal Access Token

1. Vào **GitHub Settings** → **Developer settings** → **Personal access tokens** → **Fine-grained tokens**
2. Bấm **Generate new token**
3. Cấu hình:
   - **Token name**: `AURA License Manager`
   - **Expiration**: Chọn thời hạn phù hợp (khuyến nghị 1 năm, nhớ gia hạn)
   - **Repository access**: Chọn **Only select repositories** → chọn đúng repo `aura-license-keys`
   - **Permissions** → **Repository permissions**:
     - **Contents**: `Read and write` ⚠️ (bắt buộc để ghi trạng thái `used`)
4. Bấm **Generate token** và **copy ngay** (chỉ hiện 1 lần)

> 🔒 **Bảo mật**: Token này chỉ có quyền trên 1 repo duy nhất. Nếu bị lộ, thiệt hại giới hạn trong repo đó.

---

## Bước 3: Cấu hình file .env

Mở file `.env` và thêm:

```env
GITHUB_TOKEN=github_pat_xxxxxxxxxxxxxxxxxxxx
GITHUB_REPO=your-username/aura-license-keys
GITHUB_KEYS_PATH=keys.json
GITHUB_API_TIMEOUT=15
```

> ⚠️ **KHÔNG commit file `.env`** lên Git. File này đã có trong `.gitignore`.

---

## Bước 4: Bật Branch Protection (khuyến nghị)

1. Vào repo → **Settings** → **Branches**
2. Thêm rule cho branch `main`:
   - ✅ Require pull request before merging (tùy chọn)
   - ✅ Restrict deletions
   - ✅ Block force pushes

> Mục đích: Chống kẻ tấn công có token xóa toàn bộ repo.

---

## Bước 5: Kiểm tra hoạt động

### Test đọc keys.json:
```bash
.venv/bin/python -c "
from services.github_key_store import github_key_store
data, sha = github_key_store.fetch_keys()
print(f'✅ Đọc thành công {len(data[\"keys\"])} keys, sha={sha[:8]}...')
"
```

### Test kích hoạt key (sẽ đánh dấu used=true thật):
```bash
.venv/bin/python -c "
from services.license_service import verify_license_key_remote
ok, msg = verify_license_key_remote('AURA-VIP-2026-F4rtvlZU2o')
print(f'{ok}: {msg}')
"
```

---

## Bước 6: Build EXE với token nhúng

Khi build để phân phối:

```bash
.venv/bin/python scripts/build_bootstrap_exe.py
```

Script sẽ:
1. Đọc `GITHUB_TOKEN` từ `.env`
2. Sinh `services/_embedded_token.py` với token đã obfuscate
3. Đóng gói EXE (KHÔNG kèm `license.key`)
4. Tự động xóa `_embedded_token.py` sau khi build

> ⚠️ **Lưu ý**: Token vẫn có thể bị trích xuất từ EXE bằng decompile. Đây là giới hạn vật lý của kiến trúc client-side. Xem [`plans/security_upgrade_design.md`](../plans/security_upgrade_design.md:1) để biết giải pháp nâng cao (Phương án 3 – server riêng).

---

## Quản lý Key

### Thêm key mới
Sửa trực tiếp `keys.json` trên GitHub:
```json
{
  "key": "AURA-VIP-2026-NEWKEY123",
  "used": false,
  "hwid": null,
  "activated_at": null
}
```

### Thu hồi key (revoke)
Đổi `used` thành `true`:
```json
{
  "key": "AURA-VIP-2026-LEAKEDKEY",
  "used": true,
  "hwid": "REVOKED",
  "activated_at": "2026-09-22T00:00:00Z"
}
```

### Reset key (cho phép dùng lại)
Đổi `used` về `false` và xóa `hwid`:
```json
{
  "key": "AURA-VIP-2026-RESETKEY",
  "used": false,
  "hwid": null,
  "activated_at": null
}
```

---

## Xử lý sự cố

| Lỗi | Nguyên nhân | Cách khắc phục |
|---|---|---|
| `Chưa cấu hình GITHUB_TOKEN` | Thiếu token trong `.env` | Thêm `GITHUB_TOKEN` vào `.env` |
| `GitHub Token không hợp lệ` (401) | Token sai/hết hạn | Tạo token mới |
| `Token thiếu quyền truy cập repo` (403) | Token thiếu quyền `Contents: RW` | Sửa quyền token |
| `Không tìm thấy repo hoặc file` (404) | Sai `GITHUB_REPO` hoặc `GITHUB_KEYS_PATH` | Kiểm tra lại cấu hình |
| `GitHub API bị rate limit` (429) | Quá nhiều request | Chờ 1 giờ hoặc dùng token khác |
| `Xung đột dữ liệu khi kích hoạt` | Race condition | Thử lại (hệ thống tự retry 3 lần) |

---

## Bảo mật – Điểm cần lưu ý

| Rủi ro | Mức độ | Giảm thiểu |
|---|---|---|
| Token trích xuất từ EXE | 🔴 Cao | Obfuscation + scope tối thiểu (1 repo) |
| Repo bị xóa | 🟠 Trung bình | Branch protection + token scope hẹp |
| Race condition | 🟡 Thấp | Optimistic locking (tự động retry) |
| Cần internet | 🟡 Thấp | Chấp nhận (app vốn cần internet) |

> 📖 Chi tiết đầy đủ: [`plans/security_upgrade_design.md`](../plans/security_upgrade_design.md:1)
