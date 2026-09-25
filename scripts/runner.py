#!/usr/bin/env python3
"""
Runner script tự động hóa: kiểm tra venv, kiểm tra thư viện và chạy FastAPI Server.
Chạy được trên cả Linux, macOS và Windows.
"""
import os
import sys
import subprocess
import venv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
VENV_DIR = BASE_DIR / ".venv"
REQ_FILE = BASE_DIR / "requirements.txt"
ENV_FILE = BASE_DIR / ".env"
ENV_EXAMPLE = BASE_DIR / ".env.example"

def get_venv_python():
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"

def get_venv_pip():
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "pip.exe"
    return VENV_DIR / "bin" / "pip"

def ensure_venv():
    if not VENV_DIR.exists():
        print("⚙️ Đang tạo môi trường ảo .venv...")
        venv.create(VENV_DIR, with_pip=True)
        print("✅ Đã tạo xong .venv.")
    else:
        print("✅ Môi trường ảo .venv đã sẵn sàng.")

def ensure_env_file():
    if not ENV_FILE.exists() and ENV_EXAMPLE.exists():
        print("📝 Đang tạo .env từ .env.example...")
        ENV_FILE.write_text(ENV_EXAMPLE.read_text())

def check_dependencies(python_path):
    cmd = [
        str(python_path), "-c",
        "import fastapi, uvicorn, pydantic, requests, dotenv, jinja2, groq, PIL, mutagen, imageio_ffmpeg; print('OK')"
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return "OK" in res.stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_dependencies(pip_path):
    print("📦 Đang tải và cài đặt thư viện từ requirements.txt...")
    subprocess.run([str(pip_path), "install", "-r", str(REQ_FILE)], check=True)
    print("✅ Đã cài đặt xong thư viện.")

def run_server(python_path):
    print("🚀 Đang khởi động Server FastAPI...")
    os.chdir(BASE_DIR)
    subprocess.run([str(python_path), "main.py"])

def main():
    print("==================================================")
    print("⚡ AURA AI LOGO - RUNNER & SETUP SCRIPT")
    print("==================================================")
    ensure_venv()
    ensure_env_file()
    
    python_path = get_venv_python()
    pip_path = get_venv_pip()
    
    if not check_dependencies(python_path):
        install_dependencies(pip_path)
    else:
        print("✅ Tất cả thư viện đã có sẵn, không cần cài đặt lại.")
        
    run_server(python_path)

if __name__ == "__main__":
    main()
