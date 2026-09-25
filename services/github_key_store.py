"""
github_key_store.py – Đọc/ghi danh sách License Key trên GitHub Private Repo.

Sử dụng GitHub Contents API để:
1. Đọc file keys.json (chứa danh sách key + trạng thái used)
2. Đánh dấu key đã dùng (used=true) + gắn HWID máy kích hoạt
3. Chống race condition bằng optimistic locking qua trường `sha`

Trạng thái `used` lưu SERVER-SIDE trên GitHub → share EXE cũ vô hiệu.
"""
import base64
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import requests
from fastapi import HTTPException

from core.config import settings
from services.token_obfuscator import get_embedded_token, resolve_token

MAX_RETRY = 3


class GitHubKeyStore:
    """Quản lý kho License Key trên GitHub Private Repo qua Contents API."""

    @staticmethod
    def _resolve_token() -> str:
        """Lấy token từ .env, fallback sang token nhúng trong EXE."""
        return resolve_token(settings.GITHUB_TOKEN, get_embedded_token())

    @staticmethod
    def _build_headers(token: str) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    @staticmethod
    def _contents_url() -> str:
        return (
            f"{settings.GITHUB_API_BASE}/repos/{settings.GITHUB_REPO}"
            f"/contents/{settings.GITHUB_KEYS_PATH}"
        )

    @staticmethod
    def _validate_config(token: str) -> None:
        """Kiểm tra cấu hình bắt buộc trước khi gọi API."""
        if not token:
            raise HTTPException(
                status_code=500,
                detail="Chưa cấu hình GITHUB_TOKEN. Vui lòng thêm vào .env hoặc build lại EXE.",
            )
        if not settings.GITHUB_REPO or "/" not in settings.GITHUB_REPO:
            raise HTTPException(
                status_code=500,
                detail="GITHUB_REPO chưa đúng định dạng 'owner/repo'.",
            )

    @staticmethod
    def _handle_error(resp: requests.Response) -> None:
        """Chuyển đổi lỗi HTTP từ GitHub thành HTTPException thân thiện."""
        if resp.status_code == 401:
            raise HTTPException(status_code=401, detail="GitHub Token không hợp lệ hoặc đã hết hạn.")
        if resp.status_code == 403:
            raise HTTPException(status_code=403, detail="GitHub Token thiếu quyền truy cập repo.")
        if resp.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f"Không tìm thấy repo hoặc file '{settings.GITHUB_KEYS_PATH}'.",
            )
        if resp.status_code == 429:
            raise HTTPException(status_code=429, detail="GitHub API bị rate limit. Thử lại sau.")
        raise HTTPException(
            status_code=resp.status_code,
            detail=f"Lỗi GitHub API: {resp.text[:200]}",
        )

    @staticmethod
    def fetch_keys() -> Tuple[Dict[str, Any], str]:
        """
        Đọc file keys.json từ GitHub.

        Returns:
            Tuple[data_dict, sha] – dữ liệu JSON đã parse và SHA của file (dùng cho optimistic locking).
        """
        token = GitHubKeyStore._resolve_token()
        GitHubKeyStore._validate_config(token)

        try:
            resp = requests.get(
                GitHubKeyStore._contents_url(),
                headers=GitHubKeyStore._build_headers(token),
                timeout=settings.GITHUB_API_TIMEOUT,
            )
        except requests.exceptions.Timeout:
            raise HTTPException(status_code=504, detail="Quá thời gian kết nối tới GitHub.")
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Lỗi kết nối GitHub: {str(e)}")

        if resp.status_code != 200:
            GitHubKeyStore._handle_error(resp)

        payload = resp.json()
        sha = payload.get("sha", "")
        try:
            content = base64.b64decode(payload.get("content", "")).decode("utf-8")
            data = json.loads(content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"File keys.json trên GitHub bị hỏng: {str(e)}")

        return data, sha

    @staticmethod
    def _write_keys(data: Dict[str, Any], sha: str, message: str) -> bool:
        """
        Ghi file keys.json lên GitHub với optimistic locking.

        Returns:
            True nếu ghi thành công, False nếu gặp conflict (409) cần retry.
        """
        token = GitHubKeyStore._resolve_token()
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        raw = json.dumps(data, ensure_ascii=False, indent=2)
        encoded = base64.b64encode(raw.encode("utf-8")).decode("ascii")

        body = {"message": message, "content": encoded, "sha": sha}

        try:
            resp = requests.put(
                GitHubKeyStore._contents_url(),
                headers=GitHubKeyStore._build_headers(token),
                json=body,
                timeout=settings.GITHUB_API_TIMEOUT,
            )
        except requests.exceptions.Timeout:
            raise HTTPException(status_code=504, detail="Quá thời gian ghi lên GitHub.")
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Lỗi kết nối GitHub: {str(e)}")

        if resp.status_code == 409:
            return False  # Conflict – cần đọc lại và retry
        if resp.status_code not in (200, 201):
            GitHubKeyStore._handle_error(resp)
        return True

    @staticmethod
    def find_key(data: Dict[str, Any], license_key: str) -> Optional[Dict[str, Any]]:
        """Tìm entry key trong dữ liệu keys.json."""
        target = license_key.strip()
        for entry in data.get("keys", []):
            if entry.get("key", "").strip() == target:
                return entry
        return None

    @staticmethod
    def activate_key(license_key: str, hwid: str) -> Tuple[bool, str]:
        """
        Kích hoạt key: kiểm tra tồn tại + chưa dùng, sau đó đánh dấu used=true.

        Sử dụng optimistic locking: nếu ghi gặp conflict (409), đọc lại và retry
        tối đa MAX_RETRY lần để chống race condition.

        Returns:
            (success, message)
        """
        for attempt in range(MAX_RETRY):
            data, sha = GitHubKeyStore.fetch_keys()
            entry = GitHubKeyStore.find_key(data, license_key)

            if entry is None:
                return False, "License Key không tồn tại trong hệ thống."

            if entry.get("used"):
                return False, "License Key này đã được sử dụng trên thiết bị khác."

            entry["used"] = True
            entry["hwid"] = hwid
            entry["activated_at"] = datetime.now(timezone.utc).isoformat()

            message = f"Activate license key {license_key[:14]}*** on {hwid}"
            if GitHubKeyStore._write_keys(data, sha, message):
                return True, "Kích hoạt bản quyền thành công!"

            # Conflict → thử lại
            if attempt < MAX_RETRY - 1:
                continue

        return False, "Xung đột dữ liệu khi kích hoạt. Vui lòng thử lại."

    @staticmethod
    def is_key_used(license_key: str) -> bool:
        """Kiểm tra nhanh key đã được dùng chưa (dùng cho check_activation)."""
        data, _ = GitHubKeyStore.fetch_keys()
        entry = GitHubKeyStore.find_key(data, license_key)
        return bool(entry and entry.get("used"))


github_key_store = GitHubKeyStore()
