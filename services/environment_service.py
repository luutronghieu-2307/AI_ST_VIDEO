import os
import platform
import subprocess
import sys
import urllib.request
import zipfile
from typing import Callable, Optional

PYTHON_EMBED_URL = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
GET_PIP_URL = "https://bootstrap.pypa.io/get-pip.py"
RUNTIME_DIR = "runtime"


def get_runtime_python_path() -> str:
    """Trả về đường dẫn thực thi của Python runtime nội bộ hoặc python hiện tại."""
    if platform.system() == "Windows":
        local_exe = os.path.join(RUNTIME_DIR, "python.exe")
        if os.path.exists(local_exe):
            return os.path.abspath(local_exe)
    return sys.executable


def is_environment_ready() -> bool:
    """Kiểm tra môi trường và các thư viện cần thiết đã sẵn sàng chưa."""
    py_exe = get_runtime_python_path()
    try:
        cmd = [py_exe, "-c", "import fastapi, uvicorn, pydantic, jinja2, PIL, groq; print('OK')"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        return "OK" in res.stdout
    except Exception:
        return False


def download_file_with_progress(url: str, dest: str, progress_cb: Optional[Callable[[int, int], None]] = None) -> None:
    """Tải file từ URL với báo cáo tiến trình."""
    def _reporthook(block_num: int, block_size: int, total_size: int):
        if progress_cb and total_size > 0:
            downloaded = block_num * block_size
            progress_cb(min(downloaded, total_size), total_size)

    urllib.request.urlretrieve(url, dest, reporthook=_reporthook)


def setup_python_embeddable(progress_cb: Optional[Callable[[str, float], None]] = None) -> bool:
    """
    Tải Python 3.11 Embeddable và thiết lập pip + requirements.txt cho Windows.
    """
    if platform.system() != "Windows":
        return True

    os.makedirs(RUNTIME_DIR, exist_ok=True)
    zip_path = os.path.join(RUNTIME_DIR, "python_embed.zip")

    # 1. Tải Python Embeddable
    if progress_cb:
        progress_cb("Đang tải Python 3.11 Embeddable (~10MB)...", 0.1)

    def _dl_cb(cur: int, tot: int):
        if progress_cb and tot > 0:
            pct = 0.1 + (cur / tot) * 0.4
            progress_cb(f"Đang tải Python 3.11: {int(cur/1024/1024)}MB / {int(tot/1024/1024)}MB", pct)

    download_file_with_progress(PYTHON_EMBED_URL, zip_path, _dl_cb)

    # 2. Giải nén
    if progress_cb:
        progress_cb("Đang giải nén môi trường Python 3.11...", 0.55)

    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(RUNTIME_DIR)

    if os.path.exists(zip_path):
        os.remove(zip_path)

    # 3. Kích hoạt 'import site' trong file ._pth
    pth_file = os.path.join(RUNTIME_DIR, "python311._pth")
    if os.path.exists(pth_file):
        with open(pth_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        with open(pth_file, "w", encoding="utf-8") as f:
            for line in lines:
                if "#import site" in line or line.strip() == "import site":
                    f.write("import site\n")
                else:
                    f.write(line)

    # 4. Tải get-pip.py & cài pip
    if progress_cb:
        progress_cb("Đang tải công cụ quản lý gói pip...", 0.65)

    pip_script = os.path.join(RUNTIME_DIR, "get-pip.py")
    urllib.request.urlretrieve(GET_PIP_URL, pip_script)

    py_exe = os.path.join(RUNTIME_DIR, "python.exe")
    subprocess.run([py_exe, pip_script, "--no-warn-script-location"], check=True)
    if os.path.exists(pip_script):
        os.remove(pip_script)

    # 5. Cài đặt requirements.txt
    if os.path.exists("requirements.txt"):
        if progress_cb:
            progress_cb("Đang cài đặt các thư viện (FastAPI, Uvicorn, Jinja2, Pillow...)...", 0.8)
        cmd = [py_exe, "-m", "pip", "install", "-r", "requirements.txt", "--no-warn-script-location"]
        subprocess.run(cmd, check=True)

    if progress_cb:
        progress_cb("Cài đặt môi trường hoàn tất thành công!", 1.0)

    return True
