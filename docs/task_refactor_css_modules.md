# 📋 Kế hoạch Tối ưu & Module hóa CSS: `templates/css/`

> **Trạng thái**: ✅ Đã hoàn thành  
> **File gốc**: `style.css` (Trước: 1676 dòng -> Sau: 20 dòng) & `storyboard.css` (Trước: 420 dòng -> Sau: 8 dòng)  
> **Kết quả**: Module hóa toàn bộ CSS thành các file con trong `base/`, `components/`, `storyboard/`, mỗi file đều ≤ 246 dòng, tuân thủ tuyệt đối quy định của AGENTS.md.

---

## 1. Phân tích Hiện trạng
- `templates/css/style.css` hiện có **1676 dòng**, chứa tất cả từ CSS Reset, Design Tokens (CSS Variables), Base layout, Animation, Form controls, Preview panel, Modals, History, Tooltips, Toast, Responsive media queries.
- `templates/css/storyboard.css` có **420 dòng**, chứa toàn bộ CSS của Storyboard Timeline, Upload Zones, Video Player, Status badges, Progress bar.

---

## 2. Phương án Phân tách (Modular CSS Architecture)

Cấu trúc lại thư mục `templates/css/` theo chuẩn Component-based:

```
templates/css/
├── base/
│   ├── variables.css      # (~80 dòng): Color tokens, typography, shadows, glassmorphism vars
│   ├── reset.css          # (~50 dòng): Reset cơ bản, box-sizing, typography base
│   └── animations.css     # (~80 dòng): Keyframes animations, glow effects, skeleton pulse
├── components/
│   ├── header_footer.css  # (~70 dòng): Header, Logo branding, Footer
│   ├── control_form.css   # (~120 dòng): Textarea prompt, options, chip buttons, generate button
│   ├── preview_panel.css  # (~100 dòng): Image preview canvas, overlay buttons, loading states
│   ├── modal.css          # (~120 dòng): Generic modals, lightbox, template manager modal
│   ├── history.css        # (~110 dòng): History grid, history table modal, selection toolbar
│   └── toast.css          # (~50 dòng): Toast notifications & rate limit banner
├── storyboard/
│   ├── storyboard_base.css     # (~100 dòng): Container layout, tabs, step wizard
│   ├── storyboard_upload.css   # (~120 dòng): Dropzones audio/srt, waveform preview, summary card
│   └── storyboard_timeline.css # (~150 dòng): Timeline cards, video segment player, status badges
└── style.css              # File tổng hợp hoặc import các CSS modules
```

---

## 3. Cách thức Load CSS
1. **Phương án A (Nhiều `<link>` tags trong `templates/base.html`)**: Trình duyệt nạp song song với HTTP/2, cache từng component độc lập khi có cập nhật nhỏ.
2. **Phương án B (`@import` trong `style.css`)**: Giữ nguyên thẻ `<link rel="stylesheet" href="/css/style.css">`, bên trong `style.css` chỉ chứa các dòng `@import` tới từng module.

---

## 4. Kế hoạch Thực hiện

- [ ] **Bước 1**: Tạo cấu trúc thư mục `templates/css/base/`, `templates/css/components/`, `templates/css/storyboard/`.
- [ ] **Bước 2**: Di chuyển và trích xuất từng khối style từ `style.css` và `storyboard.css` vào các file con.
- [ ] **Bước 3**: Cấu hình `templates/base.html` hoặc `style.css` để liên kết toàn bộ module.
- [ ] **Bước 4**: Kiểm tra trực quan giao diện (Visual verification) đảm bảo 100% không bị vỡ giao diện hoặc mất hiệu ứng.
- [ ] **Bước 5**: Cập nhật `docs/templates_base.md` và `DOCS_INDEX.md`.
