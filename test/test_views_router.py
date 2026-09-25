# test_views_router.py – Tests cho routers/views_router.py
# Yêu cầu độ bao phủ: >= 90%

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestViewsRouter:
    def test_serve_index_success(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "AURA" in response.text

    def test_serve_index_missing_template(self, client):
        with patch("routers.views_router.os.path.exists") as mock_exists:
            mock_exists.return_value = False
            response = client.get("/")
            assert response.status_code == 404
            assert "không tồn tại" in response.json()["detail"]
