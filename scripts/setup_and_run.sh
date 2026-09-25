#!/usr/bin/env bash

# ==============================================================================
# Script tự động khởi tạo môi trường, kiểm tra thư viện và chạy ứng dụng AURA AI Logo
# ==============================================================================

set -e

# Chuyển về thư mục gốc của dự án
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "======================================================"
echo "⚡ KHỞI ĐỘNG DỰ ÁN AURA AI LOGO GENERATOR"
echo "📂 Thư mục dự án: $PROJECT_DIR"
echo "======================================================"

VENV_DIR="$PROJECT_DIR/.venv"
REQUIREMENTS_FILE="$PROJECT_DIR/requirements.txt"

# 1. Kiểm tra môi trường ảo venv
if [ ! -d "$VENV_DIR" ]; then
    echo "⚙️ Không tìm thấy môi trường ảo .venv. Đang tiến hành tạo mới..."
    python3 -m venv "$VENV_DIR"
    echo "✅ Đã tạo thành công môi trường ảo tại $VENV_DIR"
else
    echo "✅ Đã tìm thấy môi trường ảo .venv."
fi

# 2. Kích hoạt môi trường ảo
source "$VENV_DIR/bin/activate"

# 3. Kiểm tra file .env
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "📝 Chưa có file .env, tự động copy từ .env.example..."
        cp .env.example .env
        echo "⚠️ Lưu ý: Hãy cập nhật PIXAZO_API_KEY trong file .env nếu chưa có."
    fi
fi

# 4. Kiểm tra xem các thư viện cần thiết đã cài đặt đủ chưa
echo "🔍 Đang kiểm tra các gói thư viện phụ thuộc..."

NEED_INSTALL=0
python3 - << 'EOF' || NEED_INSTALL=1
import sys

required = [
    "fastapi", "uvicorn", "pydantic", "requests", "dotenv",
    "jinja2", "groq", "PIL", "mutagen", "imageio_ffmpeg"
]
missing = []

for mod in required:
    try:
        __import__(mod)
    except ImportError:
        missing.append(mod)

if missing:
    print(f"⚠️ Thiếu các thư viện: {', '.join(missing)}")
    sys.exit(1)
else:
    print("✅ Tất cả thư viện phụ thuộc đã được cài đặt đầy đủ!")
    sys.exit(0)
EOF

# 5. Nếu thiếu thư viện thì mới tiến hành cài đặt
if [ "$NEED_INSTALL" -eq 1 ]; then
    echo "📦 Đang cài đặt thư viện từ requirements.txt..."
    pip install -r "$REQUIREMENTS_FILE"
    echo "✅ Đã cài đặt hoàn tất các gói thư viện."
fi

# 6. Tự động giải phóng cổng 8000 nếu đang bị tiến trình cũ chiếm giữ
if command -v fuser >/dev/null 2>&1; then
    fuser -k 8000/tcp >/dev/null 2>&1 || true
fi

# 7. Khởi chạy ứng dụng FastAPI
echo "======================================================"
echo "🚀 Đang khởi động Server FastAPI tại http://localhost:8000"
echo "======================================================"
python3 main.py
