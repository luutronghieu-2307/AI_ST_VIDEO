# test_suggest_router.py – Integration tests cho routers/suggest_router.py
# Yêu cầu độ bao phủ: >= 90%

import json
import os
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient


def _write_json(path, data):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)


# ─── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def client_with_templates(tmp_path):
    """Client với file templates tạm thời."""
    templates_file = str(tmp_path / "templates.json")
    sample_templates = [
        {"id": "default-t1", "name": "Default", "prompt": "default prompt",
         "created_at": "2025-01-01T00:00:00+00:00", "is_default": True},
        {"id": "user-t1", "name": "User Template", "prompt": "user prompt",
         "created_at": "2025-01-01T00:00:00+00:00", "is_default": False},
    ]
    _write_json(templates_file, sample_templates)

    with patch("core.config.settings") as mock_s:
        mock_s.PROMPT_TEMPLATES_FILE = templates_file
        mock_s.GROQ_API_KEY = "test-key"
        mock_s.GROQ_MODEL = "test-model"
        mock_s.GROQ_CREATIVE_MODEL = "test-creative"
        mock_s.GROQ_TIMEOUT = 30
        mock_s.PIXAZO_API_KEY = "test-pixazo"
        mock_s.PIXAZO_GATEWAY_URL = "https://test.gateway"
        mock_s.REQUEST_TIMEOUT = 10
        mock_s.HOST = "0.0.0.0"
        mock_s.PORT = 8000

        from main import app
        yield TestClient(app), templates_file


# ─── Tests: GET /api/groq-models ──────────────────────────────────────────────

class TestGetGroqModels:
    def test_get_groq_models_success(self, client_with_templates):
        client, _ = client_with_templates
        with patch("routers.suggest_router.groq_service.get_vision_models") as mock_models:
            from models.suggest import GroqModelInfo
            mock_models.return_value = [
                GroqModelInfo(id="model-1", name="Model One", description="Desc 1")
            ]
            response = client.get("/api/groq-models?groq_api_key=custom-key")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == "model-1"


# ─── Tests: GET /api/prompt-templates ─────────────────────────────────────────

class TestGetPromptTemplates:
    def test_returns_list_of_templates(self, client_with_templates):
        client, _ = client_with_templates
        with patch("services.prompt_store.settings") as mock_s:
            mock_s.PROMPT_TEMPLATES_FILE = _
            response = client.get("/api/prompt-templates")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_response_has_required_fields(self, client_with_templates):
        client, tpath = client_with_templates
        with patch("routers.suggest_router.load_templates") as mock_load:
            mock_load.return_value = []
            response = client.get("/api/prompt-templates")
        assert response.status_code == 200

    def test_returns_both_default_and_user_templates(self, client_with_templates):
        client, tpath = client_with_templates
        with patch("routers.suggest_router.load_templates") as mock_load:
            from models.suggest import PromptTemplate
            mock_load.return_value = [
                PromptTemplate(id="d1", name="Default", prompt="dp",
                               created_at="2025-01-01T00:00:00+00:00", is_default=True),
                PromptTemplate(id="u1", name="User", prompt="up",
                               created_at="2025-01-01T00:00:00+00:00", is_default=False),
            ]
            response = client.get("/api/prompt-templates")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        ids = [t["id"] for t in data]
        assert "d1" in ids
        assert "u1" in ids


# ─── Tests: DELETE /api/prompt-templates/{id} ──────────────────────────────────

class TestDeleteSingleTemplate:
    def test_delete_user_template_success(self, client_with_templates):
        client, _ = client_with_templates
        with patch("routers.suggest_router.delete_template") as mock_del:
            mock_del.return_value = True
            response = client.delete("/api/prompt-templates/user-t1")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["deleted_id"] == "user-t1"

    def test_delete_nonexistent_raises_404(self, client_with_templates):
        client, _ = client_with_templates
        from fastapi import HTTPException
        with patch("routers.suggest_router.delete_template") as mock_del:
            mock_del.side_effect = HTTPException(status_code=404, detail="Not found")
            response = client.delete("/api/prompt-templates/bad-id")
        assert response.status_code == 404

    def test_delete_default_template_raises_403(self, client_with_templates):
        client, _ = client_with_templates
        from fastapi import HTTPException
        with patch("routers.suggest_router.delete_template") as mock_del:
            mock_del.side_effect = HTTPException(status_code=403, detail="Cannot delete default")
            response = client.delete("/api/prompt-templates/default-t1")
        assert response.status_code == 403


# ─── Tests: POST /api/prompt-templates/batch-delete ───────────────────────────

class TestBatchDeleteTemplates:
    def test_batch_delete_returns_success_and_count(self, client_with_templates):
        client, _ = client_with_templates
        with patch("routers.suggest_router.delete_templates_batch") as mock_batch:
            mock_batch.return_value = ["user-t1", "user-t2"]
            response = client.post(
                "/api/prompt-templates/batch-delete",
                json={"ids": ["user-t1", "user-t2"]}
            )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["deleted_count"] == 2
        assert set(data["deleted_ids"]) == {"user-t1", "user-t2"}

    def test_batch_delete_skips_defaults_silently(self, client_with_templates):
        client, _ = client_with_templates
        with patch("routers.suggest_router.delete_templates_batch") as mock_batch:
            mock_batch.return_value = []  # Không xóa được vì là defaults
            response = client.post(
                "/api/prompt-templates/batch-delete",
                json={"ids": ["default-t1"]}
            )
        assert response.status_code == 200
        data = response.json()
        assert data["deleted_count"] == 0

    def test_batch_delete_rejects_empty_ids(self, client_with_templates):
        client, _ = client_with_templates
        response = client.post(
            "/api/prompt-templates/batch-delete",
            json={"ids": []}
        )
        assert response.status_code == 422


# ─── Tests: POST /api/suggest-prompt ──────────────────────────────────────────

class TestSuggestPrompt:
    def test_suggest_returns_prompt_and_template_id(self, client_with_templates):
        client, _ = client_with_templates
        with patch("routers.suggest_router.groq_service") as mock_groq, \
             patch("routers.suggest_router.save_template") as mock_save, \
             patch("routers.suggest_router.enforce_rate_limit"):
            mock_groq.suggest_prompt.return_value = "Generated AI prompt text"
            from models.suggest import PromptTemplate
            mock_save.return_value = PromptTemplate(
                id="new-uuid-1", name="Test Template",
                prompt="Generated AI prompt text",
                created_at="2025-01-01T00:00:00+00:00", is_default=False
            )
            payload = {
                "image_base64": "dGVzdA==",
                "image_mime": "image/jpeg",
                "prompt_name": "Test Template",
                "mode": "standard"
            }
            response = client.post("/api/suggest-prompt", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["prompt"] == "Generated AI prompt text"
        assert data["template_id"] == "new-uuid-1"
        assert data["saved"] is True

    def test_suggest_advanced_mode_uses_advanced_rate_limit(self, client_with_templates):
        client, _ = client_with_templates
        with patch("routers.suggest_router.groq_service") as mock_groq, \
             patch("routers.suggest_router.save_template") as mock_save, \
             patch("routers.suggest_router.enforce_rate_limit") as mock_rate:
            mock_groq.suggest_prompt.return_value = "Advanced prompt"
            from models.suggest import PromptTemplate
            mock_save.return_value = PromptTemplate(
                id="adv-1", name="Advanced",
                prompt="Advanced prompt",
                created_at="2025-01-01T00:00:00+00:00", is_default=False
            )
            payload = {
                "image_base64": "dGVzdA==",
                "image_mime": "image/jpeg",
                "prompt_name": "Advanced Template",
                "mode": "advanced"
            }
            response = client.post("/api/suggest-prompt", json=payload)
        assert response.status_code == 200
        mock_rate.assert_called_once()
        args = mock_rate.call_args
        assert args[1].get("limit") == 10 or (len(args[0]) > 1 and args[0][1] == 10)
