# templates/base.html

## Mục đích
Template gốc (layout skeleton) mà tất cả trang đều kế thừa qua `{% extends "base.html" %}`.

## Cấu trúc HTML
- `<head>`: charset, viewport, `{% block title %}`, Google Fonts (Outfit, Plus Jakarta Sans), Font Awesome, `/css/style.css`
- `<body>`:
  - `.background-glow` → 3 `glow-sphere` (ambient effect)
  - `.app-container` → `{% block content %}`
  - `{% block modals %}` → chỗ render modal
  - `<script src="/js/app.js">` → JS chính
  - `{% block extra_scripts %}`

## Jinja2 Blocks
| Block | Mô tả |
|---|---|
| `title` | Tiêu đề trang, mặc định "AURA - AI Logo & Visual Creator" |
| `extra_head` | Thêm CSS/meta vào `<head>` |
| `content` | Nội dung chính của trang |
| `modals` | Modal/dialog overlay |
| `extra_scripts` | Script thêm cuối body |

## Keywords
`base.html`, `extends`, `block title`, `block content`, `block modals`, `background-glow`, `glow-sphere`, `app-container`, `Outfit`, `Font Awesome`, `style.css`, `app.js`

## Phụ thuộc
- Extended bởi: `templates/index.html`
- Dùng: `/css/style.css`, `/js/app.js` (mount bởi `main.py`)
