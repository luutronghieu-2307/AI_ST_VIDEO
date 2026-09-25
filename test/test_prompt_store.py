# test_prompt_store.py – Unit tests cho services/prompt_store.py
# Yêu cầu độ bao phủ: >= 90%

import json
import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException


# ─── Helpers ───────────────────────────────────────────────────────────────────

def _write_json(path, data):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)


def _read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ─── Tests: load_templates ─────────────────────────────────────────────────────

class TestLoadTemplates:
    def test_creates_default_file_when_missing(self, temp_templates_file):
        """Khi file chưa tồn tại, phải tạo mới với DEFAULT_TEMPLATES."""
        with patch("services.prompt_store.settings") as mock_s:
            mock_s.PROMPT_TEMPLATES_FILE = temp_templates_file
            from services.prompt_store import load_templates
            templates = load_templates()
        assert len(templates) == 4
        assert any(t.is_default for t in templates)
        assert os.path.exists(temp_templates_file)

    def test_returns_templates_from_existing_file(self, temp_templates_file):
        """Khi file đã tồn tại, phải đọc đúng dữ liệu từ file."""
        sample = [
            {"id": "t1", "name": "Test Template", "prompt": "A cool logo",
             "created_at": "2025-01-01T00:00:00+00:00", "is_default": False}
        ]
        _write_json(temp_templates_file, sample)
        with patch("services.prompt_store.settings") as mock_s:
            mock_s.PROMPT_TEMPLATES_FILE = temp_templates_file
            from services.prompt_store import load_templates
            templates = load_templates()
        assert len(templates) == 1
        assert templates[0].id == "t1"
        assert templates[0].name == "Test Template"

    def test_raises_http_exception_on_corrupt_json(self, temp_templates_file):
        """Khi file bị hỏng (JSON không hợp lệ), phải raise HTTPException 500."""
        with open(temp_templates_file, "w") as f:
            f.write("NOT_VALID_JSON{{{")
        with patch("services.prompt_store.settings") as mock_s:
            mock_s.PROMPT_TEMPLATES_FILE = temp_templates_file
            from services.prompt_store import load_templates
            with pytest.raises(HTTPException) as exc:
                load_templates()
        assert exc.value.status_code == 500

    def test_default_templates_have_correct_structure(self, temp_templates_file):
        """Tất cả default templates phải có đầy đủ các field bắt buộc."""
        with patch("services.prompt_store.settings") as mock_s:
            mock_s.PROMPT_TEMPLATES_FILE = temp_templates_file
            from services.prompt_store import load_templates
            templates = load_templates()
        for t in templates:
            assert t.id
            assert t.name
            assert t.prompt
            assert t.created_at
            assert t.is_default is True


# ─── Tests: save_template ──────────────────────────────────────────────────────

class TestSaveTemplate:
    def test_saves_new_template_successfully(self, temp_templates_file):
        """save_template phải tạo mới template với UUID và is_default=False."""
        with patch("services.prompt_store.settings") as mock_s:
            mock_s.PROMPT_TEMPLATES_FILE = temp_templates_file
            from services.prompt_store import save_template
            result = save_template("My Logo", "A beautiful logo prompt")
        assert result.id
        assert result.name == "My Logo"
        assert result.prompt == "A beautiful logo prompt"
        assert result.is_default is False

    def test_saved_template_persisted_to_file(self, temp_templates_file):
        """Template mới phải được ghi vào file JSON."""
        with patch("services.prompt_store.settings") as mock_s:
            mock_s.PROMPT_TEMPLATES_FILE = temp_templates_file
            from services.prompt_store import save_template, load_templates
            t = save_template("Persist Test", "test prompt")
            all_templates = load_templates()
        ids = [x.id for x in all_templates]
        assert t.id in ids

    def test_multiple_saves_accumulate(self, temp_templates_file):
        """Nhiều lần save phải tích lũy, không ghi đè."""
        with patch("services.prompt_store.settings") as mock_s:
            mock_s.PROMPT_TEMPLATES_FILE = temp_templates_file
            from services.prompt_store import save_template, load_templates
            save_template("First", "prompt 1")
            save_template("Second", "prompt 2")
            templates = load_templates()
        names = [t.name for t in templates]
        assert "First" in names
        assert "Second" in names

    def test_saved_id_is_valid_uuid(self, temp_templates_file):
        """ID của template mới phải là UUID4 hợp lệ."""
        import uuid
        with patch("services.prompt_store.settings") as mock_s:
            mock_s.PROMPT_TEMPLATES_FILE = temp_templates_file
            from services.prompt_store import save_template
            result = save_template("UUID Test", "prompt")
        assert uuid.UUID(result.id, version=4)


# ─── Tests: delete_template ────────────────────────────────────────────────────

class TestDeleteTemplate:
    def test_deletes_existing_user_template(self, temp_templates_file):
        """delete_template phải xóa thành công template do user tạo."""
        sample = [
            {"id": "user-t1", "name": "User Template", "prompt": "p1",
             "created_at": "2025-01-01T00:00:00+00:00", "is_default": False}
        ]
        _write_json(temp_templates_file, sample)
        with patch("services.prompt_store.settings") as mock_s:
            mock_s.PROMPT_TEMPLATES_FILE = temp_templates_file
            from services.prompt_store import delete_template, load_templates
            result = delete_template("user-t1")
            remaining = load_templates()
        assert result is True
        assert all(t.id != "user-t1" for t in remaining)

    def test_raises_404_for_nonexistent_template(self, temp_templates_file):
        """delete_template phải raise HTTPException 404 nếu ID không tồn tại."""
        _write_json(temp_templates_file, [])
        with patch("services.prompt_store.settings") as mock_s:
            mock_s.PROMPT_TEMPLATES_FILE = temp_templates_file
            from services.prompt_store import delete_template
            with pytest.raises(HTTPException) as exc:
                delete_template("non-existent-id")
        assert exc.value.status_code == 404

    def test_raises_403_for_default_template(self, temp_templates_file):
        """delete_template phải raise HTTPException 403 khi xóa template mặc định."""
        sample = [
            {"id": "default-t1", "name": "Default", "prompt": "p1",
             "created_at": "2025-01-01T00:00:00+00:00", "is_default": True}
        ]
        _write_json(temp_templates_file, sample)
        with patch("services.prompt_store.settings") as mock_s:
            mock_s.PROMPT_TEMPLATES_FILE = temp_templates_file
            from services.prompt_store import delete_template
            with pytest.raises(HTTPException) as exc:
                delete_template("default-t1")
        assert exc.value.status_code == 403


# ─── Tests: delete_templates_batch ─────────────────────────────────────────────

class TestDeleteTemplatesBatch:
    def test_batch_delete_multiple_user_templates(self, temp_templates_file):
        """batch delete phải xóa nhiều user templates cùng lúc."""
        sample = [
            {"id": "u1", "name": "U1", "prompt": "p1",
             "created_at": "2025-01-01T00:00:00+00:00", "is_default": False},
            {"id": "u2", "name": "U2", "prompt": "p2",
             "created_at": "2025-01-01T00:00:00+00:00", "is_default": False},
            {"id": "d1", "name": "D1", "prompt": "p3",
             "created_at": "2025-01-01T00:00:00+00:00", "is_default": True},
        ]
        _write_json(temp_templates_file, sample)
        with patch("services.prompt_store.settings") as mock_s:
            mock_s.PROMPT_TEMPLATES_FILE = temp_templates_file
            from services.prompt_store import delete_templates_batch, load_templates
            deleted = delete_templates_batch(["u1", "u2"])
            remaining = load_templates()
        assert set(deleted) == {"u1", "u2"}
        assert len(remaining) == 1
        assert remaining[0].id == "d1"

    def test_batch_delete_skips_default_templates(self, temp_templates_file):
        """batch delete phải bỏ qua các default templates, không xóa chúng."""
        sample = [
            {"id": "d1", "name": "Default", "prompt": "p1",
             "created_at": "2025-01-01T00:00:00+00:00", "is_default": True},
        ]
        _write_json(temp_templates_file, sample)
        with patch("services.prompt_store.settings") as mock_s:
            mock_s.PROMPT_TEMPLATES_FILE = temp_templates_file
            from services.prompt_store import delete_templates_batch, load_templates
            deleted = delete_templates_batch(["d1"])
            remaining = load_templates()
        assert deleted == []
        assert len(remaining) == 1

    def test_batch_delete_returns_only_deleted_ids(self, temp_templates_file):
        """batch delete phải trả về đúng danh sách ID đã thực sự xóa."""
        sample = [
            {"id": "u1", "name": "U1", "prompt": "p1",
             "created_at": "2025-01-01T00:00:00+00:00", "is_default": False},
        ]
        _write_json(temp_templates_file, sample)
        with patch("services.prompt_store.settings") as mock_s:
            mock_s.PROMPT_TEMPLATES_FILE = temp_templates_file
            from services.prompt_store import delete_templates_batch
            deleted = delete_templates_batch(["u1", "non-existent"])
        assert "u1" in deleted
        assert "non-existent" not in deleted

    def test_batch_delete_with_empty_ids(self, temp_templates_file):
        """batch delete với danh sách ID rỗng phải không xóa gì."""
        sample = [
            {"id": "u1", "name": "U1", "prompt": "p1",
             "created_at": "2025-01-01T00:00:00+00:00", "is_default": False},
        ]
        _write_json(temp_templates_file, sample)
        with patch("services.prompt_store.settings") as mock_s:
            mock_s.PROMPT_TEMPLATES_FILE = temp_templates_file
            from services.prompt_store import delete_templates_batch, load_templates
            deleted = delete_templates_batch([])
            remaining = load_templates()
        assert deleted == []
        assert len(remaining) == 1
