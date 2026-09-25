# conftest.py – Shared fixtures cho toàn bộ test suite
import json
import os
import tempfile
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def temp_data_dir():
    """Tạo thư mục data tạm thời cho tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def temp_templates_file(temp_data_dir):
    """Tạo file templates tạm thời, trả về path."""
    path = os.path.join(temp_data_dir, "test_templates.json")
    # Reset file trước mỗi test
    if os.path.exists(path):
        os.remove(path)
    yield path
    # Cleanup
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def mock_settings(temp_templates_file):
    """Mock settings để trỏ vào file test."""
    with patch("core.config.settings") as mock_s:
        mock_s.PROMPT_TEMPLATES_FILE = temp_templates_file
        mock_s.GROQ_API_KEY = "test-groq-key"
        mock_s.GROQ_MODEL = "test-model"
        mock_s.GROQ_CREATIVE_MODEL = "test-creative-model"
        mock_s.GROQ_TIMEOUT = 30
        mock_s.PIXAZO_API_KEY = "test-pixazo-key"
        mock_s.PIXAZO_GATEWAY_URL = "https://test.gateway/api"
        mock_s.REQUEST_TIMEOUT = 10
        yield mock_s


@pytest.fixture
def app_client(temp_templates_file):
    """FastAPI TestClient với settings được mock."""
    with patch("core.config.settings") as mock_s:
        mock_s.PROMPT_TEMPLATES_FILE = temp_templates_file
        mock_s.GROQ_API_KEY = "test-groq-key"
        mock_s.GROQ_MODEL = "test-model"
        mock_s.GROQ_CREATIVE_MODEL = "test-creative-model"
        mock_s.GROQ_TIMEOUT = 30
        mock_s.PIXAZO_API_KEY = "test-pixazo-key"
        mock_s.PIXAZO_GATEWAY_URL = "https://test.gateway/api"
        mock_s.REQUEST_TIMEOUT = 10
        mock_s.HOST = "0.0.0.0"
        mock_s.PORT = 8000

        # Import app sau khi patch settings
        from main import app
        client = TestClient(app)
        yield client
