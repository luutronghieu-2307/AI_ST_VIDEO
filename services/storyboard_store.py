"""
storyboard_store.py – CRUD storyboard với file JSON riêng + Lock.

Mỗi storyboard là 1 file `{storyboard_id}.json` trong `settings.STORYBOARD_DIR`.
Dùng `threading.Lock()` để chống race condition khi ghi file.
"""
import json
import os
import threading
from typing import Any, Dict, List, Optional

from fastapi import HTTPException

from core.config import settings
from models.storyboard import StoryboardResponse

# Lock chống race condition khi ghi/xóa file
_file_lock = threading.Lock()


def _ensure_dir() -> None:
    """Tạo thư mục storyboards nếu chưa có."""
    os.makedirs(settings.STORYBOARD_DIR, exist_ok=True)


def _storyboard_path(storyboard_id: str) -> str:
    """Trả về đường dẫn file JSON của storyboard."""
    return os.path.join(settings.STORYBOARD_DIR, f"{storyboard_id}.json")


def save_storyboard(storyboard: StoryboardResponse) -> StoryboardResponse:
    """
    Lưu storyboard vào file JSON riêng.

    Raises:
        HTTPException(500): Nếu ghi file lỗi.
    """
    _ensure_dir()
    path = _storyboard_path(storyboard.storyboard_id)

    with _file_lock:
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(storyboard.model_dump(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise HTTPException(500, detail=f"Lỗi lưu storyboard: {str(e)}")

    _enforce_max_storyboards()
    return storyboard


def get_storyboard(storyboard_id: str) -> Optional[StoryboardResponse]:
    """Đọc storyboard từ file JSON. Trả None nếu không tìm thấy hoặc file hỏng."""
    path = _storyboard_path(storyboard_id)
    if not os.path.exists(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return StoryboardResponse(**data)
    except Exception:
        return None


def load_storyboards() -> List[StoryboardResponse]:
    """Đọc tất cả storyboards, sắp xếp mới nhất trước. Bỏ qua file lỗi."""
    _ensure_dir()
    result: List[StoryboardResponse] = []

    try:
        files = [f for f in os.listdir(settings.STORYBOARD_DIR) if f.endswith(".json")]
    except Exception:
        return []

    for filename in files:
        storyboard_id = filename[:-5]  # Bỏ .json
        sb = get_storyboard(storyboard_id)
        if sb:
            result.append(sb)

    result.sort(key=lambda x: x.created_at, reverse=True)
    return result


def update_segment(
    storyboard_id: str,
    segment_id: str,
    data: Dict[str, Any],
) -> bool:
    """
    Cập nhật một segment trong storyboard.

    Tự động cập nhật `completed` count và `status` tổng thể.

    Returns:
        bool: True nếu thành công.
    """
    sb = get_storyboard(storyboard_id)
    if not sb:
        return False

    found = False
    for seg in sb.segments:
        if seg.id == segment_id:
            for key, value in data.items():
                if hasattr(seg, key):
                    setattr(seg, key, value)
            found = True
            break

    if not found:
        return False

    # Cập nhật completed count
    sb.completed = sum(1 for s in sb.segments if s.status == "completed")

    # Cập nhật status tổng thể
    if sb.completed == sb.total:
        sb.status = "completed"
    elif any(s.status == "processing" for s in sb.segments):
        sb.status = "processing"

    save_storyboard(sb)
    return True


def delete_storyboard(storyboard_id: str) -> bool:
    """
    Xóa storyboard.

    Raises:
        HTTPException(404): Nếu không tìm thấy.
        HTTPException(500): Nếu xóa lỗi.
    """
    path = _storyboard_path(storyboard_id)
    if not os.path.exists(path):
        raise HTTPException(404, detail=f"Không tìm thấy storyboard: {storyboard_id}")

    try:
        with _file_lock:
            os.remove(path)
        return True
    except Exception as e:
        raise HTTPException(500, detail=f"Lỗi xóa storyboard: {str(e)}")


def _enforce_max_storyboards() -> int:
    """
    Xóa storyboard cũ nhất nếu vượt giới hạn `MAX_STORYBOARDS`.

    Returns:
        int: Số storyboard đã xóa.
    """
    storyboards = load_storyboards()
    max_count = settings.MAX_STORYBOARDS

    if len(storyboards) <= max_count:
        return 0

    # Xóa các storyboard cũ nhất (cuối list vì đã sắp mới nhất trước)
    to_delete = storyboards[max_count:]
    deleted = 0
    for sb in to_delete:
        try:
            path = _storyboard_path(sb.storyboard_id)
            if os.path.exists(path):
                os.remove(path)
                deleted += 1
        except Exception:
            pass

    return deleted
