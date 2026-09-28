"""
server_runner.py - Quản lý khởi động Uvicorn server ngầm và kiểm tra socket.
"""
import os
import time
import socket
import threading
import webbrowser


def wait_for_server(host: str = "127.0.0.1", port: int = 8000, timeout: int = 15) -> bool:
    """Chờ cổng server mở hoàn tất trước khi kích hoạt trình duyệt."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            time.sleep(0.3)
    return False


def start_uvicorn_thread(app_dir: str):
    """Khởi chạy Server Uvicorn trong background daemon thread."""
    def run_uvicorn():
        try:
            import asyncio
            import uvicorn
            from main import app

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            config = uvicorn.Config(
                app=app,
                host="127.0.0.1",
                port=8000,
                loop="asyncio",
                log_config=None,
                access_log=False,
                use_colors=False,
                reload=False
            )
            server = uvicorn.Server(config)
            server.install_signal_handlers = lambda: None
            loop.run_until_complete(server.serve())
        except Exception as ex:
            try:
                with open(os.path.join(app_dir, "server_error.log"), "w", encoding="utf-8") as f:
                    f.write(f"Lỗi khởi động Uvicorn: {str(ex)}\n")
            except Exception:
                pass

    thread = threading.Thread(target=run_uvicorn, daemon=True)
    thread.start()
    return thread


def open_browser(url: str = "http://127.0.0.1:8000"):
    """Mở trình duyệt mặc định trỏ tới ứng dụng."""
    webbrowser.open(url)
