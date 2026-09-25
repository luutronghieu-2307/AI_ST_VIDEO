import json
import os
import uuid
from datetime import datetime, timezone
from typing import List
from fastapi import HTTPException
from core.config import settings
from models.suggest import PromptTemplate

_DEFAULT_TEMPLATES: List[dict] = [
    {
        "id": "default-fox-logo",
        "name": "🦊 Fox Logo",
        "prompt": "Minimalist geometric logo of a fox, sharp lines, gold and navy blue gradient, clean vector aesthetic, white background",
        "created_at": "2025-01-01T00:00:00+00:00",
        "is_default": True
    },
    {
        "id": "default-mecha-samurai",
        "name": "⚡ Mecha Samurai",
        "prompt": "Futuristic esports gaming mascot logo of a mecha samurai with katana, neon purple and lime green, bold outlines",
        "created_at": "2025-01-01T00:00:00+00:00",
        "is_default": True
    },
    {
        "id": "default-luxury-monogram",
        "name": "👑 Luxury Monogram",
        "prompt": "Luxury typography monogram letter 'A' entwined with golden leaves, black matte background, ultra realistic 3D",
        "created_at": "2025-01-01T00:00:00+00:00",
        "is_default": True
    },
    {
        "id": "default-glass-orb",
        "name": "🔮 3D Glass Orb",
        "prompt": "Modern tech startup icon, glowing 3D glassmorphism sphere with colorful neon ribbons, sleek and clean",
        "created_at": "2025-01-01T00:00:00+00:00",
        "is_default": True
    }
]


def _ensure_data_dir() -> None:
    data_dir = os.path.dirname(settings.PROMPT_TEMPLATES_FILE)
    if data_dir:
        os.makedirs(data_dir, exist_ok=True)


def load_templates() -> List[PromptTemplate]:
    """Đọc tất cả templates từ JSON. Tự tạo file với dữ liệu mặc định nếu chưa có."""
    _ensure_data_dir()
    if not os.path.exists(settings.PROMPT_TEMPLATES_FILE):
        _write_raw(_DEFAULT_TEMPLATES)
    try:
        with open(settings.PROMPT_TEMPLATES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [PromptTemplate(**item) for item in data]
    except (json.JSONDecodeError, Exception) as e:
        raise HTTPException(status_code=500, detail=f"Lỗi đọc file templates: {str(e)}")


def save_template(name: str, prompt: str) -> PromptTemplate:
    """Tạo template mới và append vào JSON file."""
    templates = load_templates()
    new_template = PromptTemplate(
        id=str(uuid.uuid4()),
        name=name,
        prompt=prompt,
        created_at=datetime.now(timezone.utc).isoformat(),
        is_default=False
    )
    templates.append(new_template)
    _write_raw([t.model_dump() for t in templates])
    return new_template


def delete_template(template_id: str) -> bool:
    """Xóa template theo ID. Không cho xóa template mặc định."""
    templates = load_templates()
    target = next((t for t in templates if t.id == template_id), None)
    if not target:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy template ID: {template_id}")
    if target.is_default:
        raise HTTPException(status_code=403, detail="Không thể xóa template mặc định.")
    filtered = [t for t in templates if t.id != template_id]
    _write_raw([t.model_dump() for t in filtered])
    return True


def delete_templates_batch(ids: List[str]) -> List[str]:
    """Xóa nhiều template theo danh sách ID (bỏ qua template mặc định). Trả về danh sách ID đã xóa."""
    templates = load_templates()
    target_ids = set(ids)
    deleted_ids = [t.id for t in templates if t.id in target_ids and not t.is_default]
    remaining = [t for t in templates if t.id not in set(deleted_ids)]
    _write_raw([t.model_dump() for t in remaining])
    return deleted_ids


def _write_raw(data: list) -> None:
    _ensure_data_dir()
    with open(settings.PROMPT_TEMPLATES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

