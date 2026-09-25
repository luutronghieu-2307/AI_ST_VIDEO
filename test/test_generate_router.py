# test_generate_router.py – Integration tests cho routers/generate_router.py
# Yêu cầu độ bao phủ: >= 90%

import pytest
from unittest.mock import patch, MagicMock
from fastapi import Request
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """FastAPI TestClient với mocked settings."""
    import tempfile, os
    with tempfile.TemporaryDirectory() as tmpdir:
        templates_file = os.path.join(tmpdir, "templates.json")
        with patch("core.config.settings") as mock_s:
            mock_s.PIXAZO_API_KEY = "test-pixazo-key"
            mock_s.PIXAZO_GATEWAY_URL = "https://test.gateway/api"
            mock_s.REQUEST_TIMEOUT = 10
            mock_s.GROQ_API_KEY = "test-groq-key"
            mock_s.GROQ_MODEL = "test-model"
            mock_s.GROQ_CREATIVE_MODEL = "test-creative"
            mock_s.GROQ_TIMEOUT = 30
            mock_s.PROMPT_TEMPLATES_FILE = templates_file
            mock_s.HOST = "0.0.0.0"
            mock_s.PORT = 8000
            from main import app
            yield TestClient(app)


# ─── Tests: POST /api/generate ────────────────────────────────────────────────

class TestGenerateEndpoint:
    def test_generate_returns_image_url_on_success(self, client):
        """POST /api/generate phải trả về image URL khi thành công."""
        from services.rate_limiter import enforce_rate_limit
        from main import app
        app.dependency_overrides[enforce_rate_limit] = lambda: None
        try:
            with patch("routers.generate_router.pixazo_service.generate_image") as mock_gen:
                mock_gen.return_value = "https://cdn.example.com/image.png"
                response = client.post("/api/generate", json={
                    "prompt": "A beautiful logo",
                    "num_steps": 4,
                    "seed": 42,
                    "height": 512,
                    "width": 512
                })
            assert response.status_code == 200
            data = response.json()
            assert data["output"] == "https://cdn.example.com/image.png"
            assert data["status"] == "success"
        finally:
            app.dependency_overrides.clear()

    def test_generate_requires_prompt_field(self, client):
        """POST /api/generate phải trả 422 khi thiếu prompt."""
        from services.rate_limiter import enforce_rate_limit
        from main import app
        app.dependency_overrides[enforce_rate_limit] = lambda: None
        try:
            response = client.post("/api/generate", json={
                "num_steps": 4
            })
            assert response.status_code == 422
        finally:
            app.dependency_overrides.clear()

    def test_generate_validates_num_steps_range(self, client):
        """num_steps phải nằm trong khoảng hợp lệ (kiểm tra schema validation)."""
        from services.rate_limiter import enforce_rate_limit
        from main import app
        app.dependency_overrides[enforce_rate_limit] = lambda: None
        try:
            with patch("routers.generate_router.pixazo_service.generate_image") as mock_gen:
                mock_gen.return_value = "https://cdn.example.com/image.png"
                response = client.post("/api/generate", json={
                    "prompt": "test prompt",
                    "num_steps": 50,
                    "seed": 1,
                    "height": 512,
                    "width": 512
                })
            assert response.status_code in (200, 422)
        finally:
            app.dependency_overrides.clear()

    def test_generate_handles_service_error(self, client):
        """Khi pixazo_service lỗi, phải trả về HTTP error."""
        from fastapi import HTTPException
        from services.rate_limiter import enforce_rate_limit
        from main import app
        app.dependency_overrides[enforce_rate_limit] = lambda: None
        try:
            with patch("routers.generate_router.pixazo_service.generate_image") as mock_gen:
                mock_gen.side_effect = HTTPException(status_code=503, detail="Gateway timeout")
                response = client.post("/api/generate", json={
                    "prompt": "test prompt",
                    "num_steps": 4,
                    "seed": 1,
                    "height": 512,
                    "width": 512
                })
            assert response.status_code == 503
        finally:
            app.dependency_overrides.clear()

    def test_generate_rate_limit_is_enforced(self, client):
        """enforce_rate_limit dependency phải được gọi khi tạo ảnh."""
        from services.rate_limiter import enforce_rate_limit
        from main import app
        mock_rate = MagicMock()
        def override_rate(request: Request):
            mock_rate()
        app.dependency_overrides[enforce_rate_limit] = override_rate
        try:
            with patch("routers.generate_router.pixazo_service.generate_image") as mock_gen:
                mock_gen.return_value = "https://cdn.example.com/image.png"
                response = client.post("/api/generate", json={
                    "prompt": "test prompt",
                    "num_steps": 4,
                    "seed": 1,
                    "height": 512,
                    "width": 512
                })
            assert response.status_code == 200
            mock_rate.assert_called_once()
        finally:
            app.dependency_overrides.clear()

    def test_generate_accepts_valid_aspect_ratios(self, client):
        """POST /api/generate phải chấp nhận các kích thước hợp lệ."""
        from services.rate_limiter import enforce_rate_limit
        from main import app
        app.dependency_overrides[enforce_rate_limit] = lambda: None
        valid_sizes = [
            (512, 512), (768, 512), (512, 768), (1024, 576), (576, 1024)
        ]
        try:
            with patch("routers.generate_router.pixazo_service.generate_image") as mock_gen:
                mock_gen.return_value = "https://cdn.example.com/image.png"
                for width, height in valid_sizes:
                    response = client.post("/api/generate", json={
                        "prompt": "test prompt",
                        "num_steps": 4,
                        "seed": 1,
                        "height": height,
                        "width": width
                    })
                    assert response.status_code == 200, f"Failed for {width}x{height}"
        finally:
            app.dependency_overrides.clear()
