# 🎬 AURA - AI Video Storyboard & Visual Generator

Ứng dụng web tạo **Video Storyboard AI phân đoạn từ Kịch bản / Phụ đề SRT kèm Âm thanh Lồng tiếng**, kết hợp công cụ tạo **Logo & Hình ảnh nghệ thuật AI**, xây dựng trên nền tảng **FastAPI** và giao diện **Modular Jinja2 Templates** hiện đại (Dark Glassmorphism).

---

## ✨ Tính năng nổi bật

### 🎥 1. AI Video Storyboard & Movie Maker (Tính năng cốt lõi)
- 📝 **Tách phân đoạn thông minh (Text/SRT Parsing)**: Tự động phân tích kịch bản văn bản hoặc file phụ đề `.srt` thành các đoạn phân cảnh ngắn chuẩn điện ảnh.
- 🎙️ **Đồng bộ Âm thanh Lồng tiếng (Audio Sync)**: Phân tích thời lượng file âm thanh `.mp3` (qua `mutagen`), tự động tính toán số khung hình chuẩn video (`1 + 8k` @ 16fps).
- 🧠 **Tự động viết Prompt Điện ảnh (GPT-120B & Groq)**: Sử dụng mô hình LLM sáng tạo (`openai/gpt-oss-120b`) để chuyển đổi nội dung từng cảnh thành prompt tiếng Anh điện ảnh chi tiết.
- ⚡ **Tạo Video AI Phân đoạn (LTX 2.5)**: Tích hợp API tạo video thế hệ mới LTX 2.5 qua **Pixazo Gateway**, cơ chế Polling bất đồng bộ theo thời gian thực.
- 🎬 **Ghép nối & Lồng tiếng Video Tự động (FFmpeg Stitching & Muxing)**: Tự động ghép các phân đoạn video thành 1 video liền mạch và lồng track âm thanh MP3 hoàn chỉnh.
- 📊 **Timeline Trực quan**: Theo dõi tiến độ render từng phân cảnh, hỗ trợ tạo lại (Regenerate) từng cảnh bị lỗi, xem trước (Preview) và tải video thành phẩm.

---

### 🎨 2. AI Logo & Visual Generator
- ⚡ **Tạo ảnh siêu tốc**: Tích hợp mô hình **Flux.1 Schnell** từ Pixazo Gateway.
- 💡 **Trợ lý AI Nâng cấp Prompt**: Tự động tối ưu hóa và làm giàu mô tả thiết kế bằng AI.
- 🎲 **Mẫu Prompt phong phú**: Đa dạng phong cách thiết kế logo (Cyberpunk, Origami, Mascot, Minimalist, 3D Orb, Futuristic).
- 🖼️ **Trình xem & Lịch sử**: Phóng to toàn màn hình (Lightbox Modal), tải ảnh về máy và tự động lưu lịch sử sáng tạo.

---

### 💎 3. Trải nghiệm & Thiết kế
- 🌌 **Giao diện Dark Glassmorphism**: Hiệu ứng kính mờ, ánh sáng neon hiện đại, tương thích hoàn hảo trên cả Desktop và Mobile.
- 🤖 **Tự động hóa 100% (1-Click Run)**: Tự tạo môi trường ảo `.venv`, tự kiểm tra và cài đặt đầy đủ thư viện cần thiết khi mang sang máy mới.

---

## 🏗️ Cấu trúc thư mục

```text
AI_logo/
├── README.md                  # Tài liệu hướng dẫn sử dụng dự án
├── requirements.txt           # Danh sách thư viện Python cần thiết
├── .env                       # Cấu hình API Keys (PIXAZO, GROQ)
├── .env.example               # File mẫu cấu hình biến môi trường
├── run.bat                    # Phím tắt 1-click chạy server trên Windows
├── run.sh                     # Phím tắt chạy server trên Linux/macOS
├── main.py                    # Entry point chính của ứng dụng FastAPI
│
├── core/                      # Cấu hình hệ thống & constants
│   ├── __init__.py
│   └── config.py              # Đọc cấu hình từ .env
│
├── models/                    # Pydantic Schemas / DTOs
│   ├── generate.py            # Schemas cho API tạo ảnh Logo
│   ├── suggest.py             # Schemas cho API gợi ý & nâng cấp prompt
│   └── storyboard.py          # Schemas cho API tạo Video Storyboard
│
├── services/                  # Business Logic & Third-party APIs
│   ├── pixazo_video_service.py # Gọi API LTX 2.5 tạo Video AI
│   ├── pixazo_service.py      # Gọi API Flux.1 Schnell tạo Ảnh
│   ├── groq_service.py        # Tích hợp Groq LLM (GPT-120B)
│   ├── video_prompt_service.py# Sinh Prompt Video điện ảnh cho từng cảnh
│   ├── srt_parser.py          # Phân tích file phụ đề SRT
│   ├── audio_service.py       # Phân tích thời lượng file âm thanh MP3
│   ├── video_stitcher_service.py # Nối ghép Video & Muxing âm thanh bằng FFmpeg
│   ├── storyboard_orchestrator.py # Điều phối render video ngầm
│   ├── storyboard_store.py    # Lưu trữ trạng thái và lịch sử Storyboard
│   └── prompt_store.py        # Quản lý thư viện mẫu prompt
│
├── routers/                   # API Endpoints & Web Views
│   ├── views_router.py        # Phục vụ giao diện Web Jinja2
│   ├── generate_router.py     # Endpoint tạo ảnh Logo (/api/generate)
│   ├── suggest_router.py      # Endpoint gợi ý Prompt (/api/suggest-prompt)
│   └── storyboard_router.py   # Endpoint Video Storyboard (/api/storyboard/*)
│
├── scripts/                   # Script tự động hóa môi trường
│   ├── runner.py              # Cross-platform runner (Windows, Linux, macOS)
│   └── setup_and_run.sh       # Bash script cho Linux/macOS
│
└── templates/                 # Giao diện Frontend (Modular Jinja2)
    ├── base.html              # Layout skeleton chuẩn
    ├── index.html             # Trang chủ (Logo & Storyboard)
    ├── components/            # UI components độc lập
    │   ├── header.html        # Thanh điều hướng & trạng thái
    │   ├── storyboard_input.html # Khu vực nhập kịch bản, upload SRT & MP3
    │   ├── storyboard_timeline.html # Timeline tiến độ render video
    │   ├── storyboard_history.html # Lịch sử các dự án Storyboard
    │   ├── control_form.html  # Form tạo Logo AI
    │   ├── preview_panel.html # Khung xem trước & tải ảnh
    │   └── modal.html         # Lightbox xem ảnh / video toàn màn hình
    ├── css/
    │   ├── style.css          # CSS Dark Glassmorphism chính
    │   └── storyboard.css     # CSS cho giao diện Video Storyboard
    └── js/
        ├── app.js             # Logic xử lý tạo Logo & UI
        ├── storyboard_manager.js # Quản lý luồng Storyboard, Polling & Render
        └── history_manager.js # Quản lý lịch sử tạo ảnh
```

---

## 🚀 Hướng dẫn cài đặt & Khởi chạy

### 📋 Yêu cầu tiên quyết
- Đã cài đặt **Python 3.10+** (khuyên dùng Python 3.11 hoặc 3.12).
- **API Keys**:
  - **Pixazo API Key**: Lấy tại [Pixazo Gateway](https://pixazo.ai) (dùng cho Video LTX 2.5 & Flux.1 Schnell).
  - **Groq API Key**: Lấy tại [Groq Console](https://console.groq.com) (dùng cho LLM GPT-120B sinh prompt).

---

### 🟢 Cách 1: Khởi chạy nhanh tự động (Khuyên dùng)

1. **Cấu hình API Key**:
   Sao chép file cấu hình mẫu:
   ```bash
   cp .env.example .env
   ```
   Mở file `.env` và điền API Keys của bạn:
   ```env
   PIXAZO_API_KEY=your_actual_pixazo_key_here
   GROQ_API_KEY=your_actual_groq_key_here
   ```

2. **Khởi chạy ứng dụng**:
   - **Trên Windows**:
     - Chạy qua Terminal / CMD / PowerShell:
       ```cmd
       python scripts/runner.py
       ```
   - **Trên Linux / macOS**:
     ```bash
     ./run.sh
     # Hoặc:
     python3 scripts/runner.py
     ```

> 💡 *Script sẽ tự động kiểm tra và tạo môi trường ảo `.venv`, tự động cài đặt đầy đủ tất cả thư viện cần thiết từ `requirements.txt`, và tự động bật Web Server.*

---

### 🟡 Cách 2: Cài đặt và khởi chạy thủ công

```bash
# 1. Tạo môi trường ảo
python3 -m venv .venv

# 2. Kích hoạt môi trường ảo
# Trên Linux/macOS:
source .venv/bin/activate
# Trên Windows:
# .venv\Scripts\activate

# 3. Cài đặt các thư viện phụ thuộc
pip install -r requirements.txt

# 4. Khởi động server
python main.py
```

---

## 🌐 Truy cập ứng dụng

- 🖥️ **Giao diện Web**: [http://localhost:8000](http://localhost:8000)
- 📖 **Tài liệu API tương tác (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- 📌 **Tài liệu ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 📄 Giấy phép & Bản quyền
Dự án được xây dựng phục vụ mục đích cá nhân và nghiên cứu công nghệ Generative AI.
