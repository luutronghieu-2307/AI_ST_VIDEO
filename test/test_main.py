# test_main.py – Tests cho main.py (router registration + startup cleanup)
import importlib
import inspect
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


def _collect_paths(app) -> set:
    """
    Thu thập tất cả path từ app.routes.

    FastAPI mới bọc router con trong `_IncludedRouter` (không có .path),
    nên cần đệ quy vào `original_router.routes` bên trong.
    """
    paths = set()

    def _walk(routes):
        for r in routes:
            p = getattr(r, "path", None)
            if p:
                paths.add(p)
            inner = getattr(r, "original_router", None)
            if inner is not None and getattr(inner, "routes", None):
                _walk(inner.routes)

    _walk(app.routes)
    return paths


class TestRouterRegistration:
    def test_storyboard_router_registered(self):
        import main
        paths = _collect_paths(main.app)
        assert "/api/storyboard/create" in paths
        assert "/api/storyboard/list" in paths

    def test_storyboard_endpoints_exist(self):
        import main
        paths = _collect_paths(main.app)
        assert "/api/storyboard/{storyboard_id}" in paths
        assert "/api/storyboard/{storyboard_id}/status" in paths
        assert (
            "/api/storyboard/{storyboard_id}/segment/{segment_id}/regenerate" in paths
        )
        assert "/api/storyboard/{storyboard_id}/segment/{segment_id}/retry" in paths


class TestStartupCleanup:
    def test_startup_cleanup_runs(self):
        """Startup event gọi cleanup_stuck_segments (patch tại main namespace)."""
        with patch("main.cleanup_stuck_segments", return_value=2) as mock_cleanup:
            import main
            with TestClient(main.app):
                pass
            mock_cleanup.assert_called()

    def test_startup_cleanup_handles_error(self):
        """Không raise dù cleanup lỗi."""
        with patch(
            "main.cleanup_stuck_segments", side_effect=RuntimeError("boom")
        ):
            import main
            with TestClient(main.app):
                pass


class TestReloadConfig:
    def test_reload_is_false(self):
        """main.py phải chạy uvicorn với reload=False (background thread an toàn)."""
        import main

        source = inspect.getsource(main)
        assert "reload=False" in source
