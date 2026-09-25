"""
license_service.py – Quản lý bản quyền với xác thực REMOTE qua GitHub.

Cơ chế mới:
1. Key được lưu trên GitHub Private Repo (keys.json) – KHÔNG nhúng trong EXE
2. Mỗi key chỉ dùng được 1 lần (trạng thái `used` lưu server-side)
3. Sau khi kích hoạt, key gắn cứng với HWID máy đầu tiên
4. Share EXE cũ vô hiệu vì trạng thái nằm trên GitHub
"""
import base64
import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Optional, Tuple

from fastapi import HTTPException

from services.hardware_service import get_hwid
from services.github_key_store import github_key_store

SECRET_SALT = "AURA_AI_MASTER_SECRET_2026_SECURE_SALT"
ACTIVATION_FILE = "activation.dat"
LICENSE_FILE = "license.key"


def get_stored_license_keys() -> list[str]:
    """Đọc danh sách key local (chỉ dùng cho chế độ offline/legacy)."""
    if not os.path.exists(LICENSE_FILE):
        return []
    try:
        with open(LICENSE_FILE, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines()]
            return [l for l in lines if l and not l.startswith("#")]
    except Exception:
        return []


def verify_license_key(key: str) -> bool:
    """
    Kiểm tra key có tồn tại trong danh sách local (legacy, không kiểm tra used).

    ⚠️ DEPRECATED: Chỉ dùng cho tương thích ngược. Ưu tiên `verify_license_key_remote()`.
    """
    cleaned_key = key.strip()
    if not cleaned_key:
        return False
    stored_keys = get_stored_license_keys()
    if stored_keys:
        return cleaned_key in stored_keys
    return False


def verify_license_key_remote(key: str) -> Tuple[bool, str]:
    """
    Xác thực key qua GitHub Private Repo (nguồn chân lý duy nhất).

    Kiểm tra:
    1. Key có tồn tại trong keys.json không
    2. Key đã được dùng chưa (used == true)

    Returns:
        (is_valid, message)
    """
    cleaned_key = key.strip()
    if not cleaned_key:
        return False, "Vui lòng nhập License Key."

    try:
        data, _ = github_key_store.fetch_keys()
    except HTTPException as e:
        return False, f"Không thể xác thực với máy chủ: {e.detail}"

    entry = github_key_store.find_key(data, cleaned_key)
    if entry is None:
        return False, "License Key không hợp lệ hoặc không tồn tại."

    if entry.get("used"):
        return False, "License Key này đã được sử dụng trên thiết bị khác."

    return True, "License Key hợp lệ và chưa được sử dụng."


def compute_activation_signature(key: str, hwid: str) -> str:
    """Tạo chữ ký kích hoạt gắn chặt Key với Mã phần cứng (HWID)."""
    payload = f"{key.strip()}::{hwid.strip()}::{SECRET_SALT}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def bind_machine(key: str) -> Tuple[bool, str]:
    """
    Kích hoạt key: xác thực REMOTE + đánh dấu used trên GitHub + lưu local.

    Quy trình:
    1. Gọi GitHub API để kiểm tra key tồn tại và chưa dùng
    2. Đánh dấu used=true + gắn HWID trên GitHub (optimistic locking)
    3. Lưu activation.dat local để check nhanh các lần sau
    """
    current_hwid = get_hwid()

    # Bước 1 + 2: Xác thực và đánh dấu trên GitHub
    ok, message = github_key_store.activate_key(key.strip(), current_hwid)
    if not ok:
        return False, message

    # Bước 3: Lưu local để check_activation() hoạt động offline
    signature = compute_activation_signature(key, current_hwid)
    activation_data = {
        "hwid": current_hwid,
        "key_masked": key[:4] + "****" + key[-4:] if len(key) >= 8 else "****",
        "signature": signature,
        "activated_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        encoded = base64.b64encode(json.dumps(activation_data).encode("utf-8")).decode("utf-8")
        with open(ACTIVATION_FILE, "w", encoding="utf-8") as f:
            f.write(encoded)
        return True, "Kích hoạt bản quyền cho thiết bị này thành công!"
    except Exception as e:
        return False, f"Lỗi lưu file kích hoạt: {str(e)}"


def check_activation() -> Tuple[bool, Optional[str]]:
    """
    Kiểm tra máy hiện tại đã kích hoạt bản quyền hợp lệ chưa (dựa vào activation.dat local).

    Trả về (is_active, message).
    """
    if not os.path.exists(ACTIVATION_FILE):
        return False, "Chưa kích hoạt bản quyền."

    try:
        with open(ACTIVATION_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
        raw_json = base64.b64decode(content.encode("utf-8")).decode("utf-8")
        data = json.loads(raw_json)
        stored_hwid = data.get("hwid")

        current_hwid = get_hwid()
        if stored_hwid != current_hwid:
            return False, "Mã phần cứng máy tính không khớp! Bản quyền không được chia sẻ giữa các máy."

        return True, "Bản quyền hợp lệ cho máy tính này."
    except Exception:
        return False, "File kích hoạt bị lỗi hoặc bị chỉnh sửa trái phép."
