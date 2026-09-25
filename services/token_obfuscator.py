"""
token_obfuscator.py – Mã hóa/giải mã GitHub Token để nhúng vào EXE.

Mục đích: Tránh lộ token dạng plaintext khi dùng lệnh `strings` trên file EXE.
Lưu ý: Đây là obfuscation (security through obscurity), KHÔNG phải mã hóa bảo mật
thực sự. Kẻ tấn công có kỹ năng vẫn có thể decompile để lấy token.
"""
import base64
import os
from typing import Optional

# Khóa XOR tĩnh dùng cho obfuscation (không phải secret thực sự)
_XOR_KEY = b"AURA_AI_TOKEN_OBFUSCATION_KEY_2026"
_PREFIX = "enc::"


def _xor_bytes(data: bytes, key: bytes) -> bytes:
    """XOR dữ liệu với key theo chu kỳ."""
    if not key:
        return data
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def obfuscate_token(token: str) -> str:
    """
    Mã hóa token thành chuỗi obfuscated để nhúng vào source/EXE.

    Quy trình: XOR -> base64 -> đảo ngược chuỗi -> thêm prefix.
    """
    if not token:
        return ""
    raw = token.encode("utf-8")
    xored = _xor_bytes(raw, _XOR_KEY)
    encoded = base64.b64encode(xored).decode("ascii")
    return _PREFIX + encoded[::-1]


def deobfuscate_token(obfuscated: str) -> str:
    """
    Giải mã chuỗi obfuscated về token gốc.

    Trả về chuỗi rỗng nếu input không hợp lệ hoặc không có prefix.
    """
    if not obfuscated or not obfuscated.startswith(_PREFIX):
        return ""
    try:
        payload = obfuscated[len(_PREFIX):][::-1]
        xored = base64.b64decode(payload.encode("ascii"))
        raw = _xor_bytes(xored, _XOR_KEY)
        return raw.decode("utf-8")
    except Exception:
        return ""


def resolve_token(env_token: Optional[str] = None, obfuscated_token: Optional[str] = None) -> str:
    """
    Ưu tiên token từ biến môi trường, fallback sang token đã obfuscate nhúng trong EXE.

    Thứ tự ưu tiên:
    1. `env_token` (từ .env hoặc biến môi trường) – dùng khi phát triển
    2. `obfuscated_token` (nhúng trong EXE) – dùng khi phân phối
    """
    if env_token and env_token.strip():
        return env_token.strip()
    if obfuscated_token:
        return deobfuscate_token(obfuscated_token)
    return ""


def get_embedded_token() -> str:
    """
    Đọc token đã obfuscate được nhúng trong file `_embedded_token.py` (nếu có).

    File này được sinh tự động bởi `scripts/build_bootstrap_exe.py` khi đóng gói.
    Trả về chuỗi rỗng nếu chưa có file.
    """
    try:
        from services import _embedded_token  # type: ignore
        return deobfuscate_token(getattr(_embedded_token, "OBFUSCATED_TOKEN", ""))
    except ImportError:
        return ""
    except Exception:
        return ""
