# templates/index.html

## Mục đích
Trang chủ chính, kế thừa `base.html` và include toàn bộ component UI.

## Cấu trúc
```
{% extends "base.html" %}
└── block content
    ├── {% include "components/header.html" %} (Navbar Tabs: Tạo ảnh vs Tạo Template)
    ├── <main id="viewGenerate" class="main-content view-section active">
    │   ├── {% include "components/control_form.html" %} (Gọn gàng)
    │   └── {% include "components/preview_panel.html" %}
    ├── <main id="viewTemplate" class="main-content view-section hidden">
    │   └── {% include "components/ai_prompt_builder.html" %} (Studio riêng biệt)
    └── {% include "components/footer.html" %}
└── block modals
    ├── {% include "components/modal.html" %}
    ├── {% include "components/template_modal.html" %}
    └── {% include "components/history_modal.html" %}
```

## Keywords
`index.html`, `extends base.html`, `viewGenerate`, `viewTemplate`, `nav-tab`, `main-content`, `include header`, `include control_form`, `include preview_panel`, `include ai_prompt_builder`, `include footer`, `include modal`, `homepage`

## Phụ thuộc
- Extends: `base.html`
- Includes: `header.html`, `control_form.html`, `preview_panel.html`, `ai_prompt_builder.html`, `footer.html`, `modal.html`
- Render bởi: `routers/views_router.py`
