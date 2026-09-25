# scripts/ – Setup & Runner Scripts

## Mục đích
Tự động hóa môi trường và khởi chạy server, hỗ trợ cross-platform.

---

## scripts/runner.py
Script Python cross-platform (Linux/macOS/Windows) tự động:
1. Tạo `.venv` nếu chưa có (`venv.create`)
2. Copy `.env` từ `.env.example` nếu chưa có
3. Kiểm tra dependencies (`fastapi, uvicorn, pydantic, requests, dotenv, jinja2, groq, Pillow, mutagen, imageio-ffmpeg`)
4. Cài đặt từ `requirements.txt` nếu thiếu
5. `os.chdir(BASE_DIR)` → `python main.py`

---

## run.bat (Root)
File batch cho Windows người dùng click đúp trực tiếp để gọi `scripts/runner.py`.

**Hằng số**:
- `BASE_DIR`: root project (2 cấp trên `runner.py`)
- `VENV_DIR`: `.venv/`
- `REQ_FILE`: `requirements.txt`
- `ENV_FILE`: `.env`
- `ENV_EXAMPLE`: `.env.example`

**Keywords**: `runner.py`, `ensure_venv`, `ensure_env_file`, `check_dependencies`, `install_dependencies`, `run_server`, `venv`, `pip install`, `cross-platform`, `setup`

---

## scripts/setup_and_run.sh
Bash script tương đương cho Linux/macOS:
- Kiểm tra và tạo `.venv`
- Activate venv
- Kiểm tra và cài `requirements.txt`
- Khởi động `main.py`

**Keywords**: `setup_and_run.sh`, `bash`, `venv activate`, `pip install`, `uvicorn`, `startup`, `shell script`

---

## scripts/build_bootstrap_exe.py
Đóng gói EXE Launcher với token GitHub đã obfuscate:
1. Đọc `GITHUB_TOKEN` từ `.env` hoặc biến môi trường
2. Sinh file `services/_embedded_token.py` chứa token đã obfuscate
3. Chạy PyInstaller đóng gói (**KHÔNG** kèm `license.key` nữa)
4. Dọn dẹp `_embedded_token.py` sau khi build (kể cả khi lỗi)

**Hàm**:
- `_read_env_token()` – đọc token từ `.env`/env var
- `generate_embedded_token()` – sinh file token obfuscated
- `cleanup_embedded_token()` – xóa file token tạm
- `build_exe()` – chạy PyInstaller

**Keywords**: `build_bootstrap_exe.py`, `PyInstaller`, `generate_embedded_token`, `_embedded_token.py`, `OBFUSCATED_TOKEN`, `cleanup_embedded_token`, `GITHUB_TOKEN`, `build exe`

---

## scripts/convert_icon.py
Chuyển đổi PNG sang ICO cho icon ứng dụng.

**Keywords**: `convert_icon.py`, `convert_png_to_ico`, `PNG`, `ICO`, `icon`

## Phụ thuộc
- Gọi `main.py` để khởi động server
- `build_bootstrap_exe.py` import `services/token_obfuscator.py`
- Không phụ thuộc module nội bộ nào khác
