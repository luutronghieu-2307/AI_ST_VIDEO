"""
single_instance.py - Đảm bảo chỉ có DUY NHẤT 1 instance Launcher chạy đồng thời.
"""
import sys


def ensure_single_instance():
    """Khởi tạo mutex trên Windows để ngăn chặn chạy nhiều instance."""
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            mutex = kernel32.CreateMutexW(None, False, "AURA_AI_LAUNCHER_SINGLE_INSTANCE_MUTEX_2026")
            if kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
                sys.exit(0)
            return mutex
        except Exception:
            pass
    return None
