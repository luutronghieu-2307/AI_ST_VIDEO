# services/token_obfuscator.py

## Mục đích
Mã hóa/giải mã GitHub Token để nhúng vào EXE, tránh lộ token dạng plaintext khi dùng lệnh `strings`.

> ⚠️ **Lưu ý bảo mật**: Đây là **obfuscation** (security through obscurity), KHÔNG phải mã hóa bảo mật thực sự. Kẻ tấn công có kỹ năng vẫn có thể decompile để lấy token. Mục tiêu là chống các cuộc tấn công cơ bản.

## Hằng số
| Hằng | Giá trị | Mô tả |
|---|---|---|
| `_XOR_KEY` | `b"AURA_AI_TOKEN_OBFUSCATION_KEY_2026"` | Khóa XOR tĩnh |
| `_PREFIX` | `"enc::"` | Prefix đánh dấu chuỗi đã obfuscate |

## Functions

### `obfuscate_token(token: str) -> str`
Mã hóa token theo quy trình: **XOR → base64 → đảo ngược chuỗi → thêm prefix**.
- Input rỗng → trả về `""`
- Kết quả có dạng `enc::<chuỗi_đảo_ngược>`

### `deobfuscate_token(obfuscated: str) -> str`
Giải mã ngược về token gốc.
- Trả về `""` nếu input rỗng, thiếu prefix, hoặc payload hỏng

### `resolve_token(env_token, obfuscated_token) -> str`
Chọn token theo thứ tự ưu tiên:
1. `env_token` (từ `.env`) — dùng khi phát triển
2. `obfuscated_token` (nhúng trong EXE) — dùng khi phân phối

### `get_embedded_token() -> str`
Đọc token đã obfuscate từ module `services/_embedded_token.py` (sinh tự động bởi [`scripts/build_bootstrap_exe.py`](../scripts/build_bootstrap_exe.py:1)).
- Trả về `""` nếu file chưa tồn tại (ImportError) hoặc có lỗi

### `_xor_bytes(data, key) -> bytes`
Helper XOR dữ liệu với key theo chu kỳ. Key rỗng → trả nguyên dữ liệu.

## Quy trình Build
```text
.env (GITHUB_TOKEN=ghp_xxx)
    │
    ▼ build_bootstrap_exe.py đọc token
    │
    ▼ obfuscate_token() → "enc::xxxxx"
    │
    ▼ Ghi vào services/_embedded_token.py
    │
    ▼ PyInstaller đóng gói
    │
    ▼ Xóa _embedded_token.py sau khi build (cleanup)
```

## Keywords
`token_obfuscator`, `obfuscate_token`, `deobfuscate_token`, `resolve_token`, `get_embedded_token`, `_embedded_token`, `OBFUSCATED_TOKEN`, `XOR`, `base64`, `obfuscation`, `GITHUB_TOKEN`, `security through obscurity`

## Phụ thuộc
- Không phụ thuộc module nội bộ nào
- Import bởi: `services/github_key_store.py`, `scripts/build_bootstrap_exe.py`
- Test: `test/test_token_obfuscator.py`
