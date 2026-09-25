# templates/components/ – Tất cả UI Components

## Mục đích
Các component Jinja2 modular, mỗi file độc lập và được include vào trang qua `{% include %}`.

---

## header.html
**ID elements**: `.app-header`, `.logo-brand`, `.brand-icon`, `.brand-text`, `.header-badges`, `.badge-pill`, `.pulse-dot`
- Hiển thị: Logo AURA, brand name, tagline, badge "Flux.1 Schnell Engine"
- **Keywords**: `header`, `brand`, `logo-brand`, `tagline`, `badge`, `pulse-dot`

---

## control_form.html
**ID elements**: `#promptInput`, `#randomPromptBtn`, `#promptTemplateSelect`, `#manageTemplatesBtn`, `#deleteTemplateBtn`, `#aspectRatioSelect`, `#numStepsInput`, `#stepsVal`, `#seedInput`, `#apiKeyInput`, `#generateBtn`, `#advancedToggle`, `#advancedContent`

**Form fields**:
| ID | Kiểu | Mô tả |
|---|---|---|
| `#promptTemplateSelect` | `select` | Chọn template prompt đã lưu |
| `#manageTemplatesBtn` | `button` | Mở modal quản lý & xóa nhiều prompt template |
| `#promptInput` | `textarea` | Nhập prompt mô tả logo |
| `#aspectRatioSelect` | `select` | Kích thước: 512x512, 768x768, 512x768, 768x512, 1024x1024 |
| `#numStepsInput` | `range` | Steps 1–10, mặc định 4 |
| `#seedInput` | `number` | Seed, mặc định 15, -1 = ngẫu nhiên |
| `#apiKeyInput` | `password` | API Key phía client (tuỳ chọn) |
| `#generateBtn` | `button` | Nút kích hoạt sinh ảnh |

**Preset chips**: 4 mẫu prompt nhanh (Fox Logo, Mecha Samurai, Luxury Monogram, 3D Glass Orb)

**Keywords**: `control-panel`, `glass-card`, `promptInput`, `promptTemplateSelect`, `manageTemplatesBtn`, `generateBtn`, `aspectRatioSelect`, `numStepsInput`, `seedInput`, `apiKeyInput`, `randomPromptBtn`, `preset-chips`, `chip`, `accordion`, `advancedToggle`

---

## preview_panel.html
**ID elements**: `#displayContainer`, `#placeholderState`, `#loadingState`, `#imageWrapper`, `#resultImage`, `#downloadBtn`, `#copyUrlBtn`, `#fullscreenBtn`, `#statusIndicator`, `#statusText`

**3 trạng thái UI**:
1. `#placeholderState` – Chưa có ảnh (mặc định hiện)
2. `#loadingState` – Đang tải (class `hidden` toggle bởi JS)
3. `#imageWrapper` – Hiển thị ảnh kết quả + action buttons

Bao gồm: `{% include "components/history.html" %}`

**Keywords**: `preview-panel`, `displayContainer`, `placeholderState`, `loadingState`, `imageWrapper`, `resultImage`, `downloadBtn`, `copyUrlBtn`, `fullscreenBtn`, `statusIndicator`, `scanner-spinner`

---

## ai_prompt_builder.html
**ID elements**: `#uploadZone`, `#imageFileInput`, `#uploadPlaceholder`, `#uploadPreview`, `#previewImg`, `#removeImageBtn`, `#promptNameInput`, `#groqApiKeyInput`, `#groqModelSelect`, `#modelCountBadge`, `#modeLimitBadge`, `#modeStandardCard`, `#modeAdvancedCard`, `#suggestPromptBtn`, `#suggestBtnText`, `#templateSavedCard`, `#templateSavedSub`

**Mô tả**:
- Drag & drop upload ảnh mẫu
- Nhập tên template + Groq API key
- Dropdown `#groqModelSelect` tự động tải các model Vision (đọc ảnh) từ Groq API
- **Bộ chọn 2 chế độ sinh prompt**:
  - `Cơ bản (Standard)`: Phân tích bám sát ảnh gốc (20 req/phút)
  - `Nâng cao (Advanced)`: Chuyển tiếp qua GPT-120B nâng cấp biến tấu sáng tạo (10 req/phút)
- Nút "Phân tích và tạo template" (`#suggestPromptBtn`) gọi API Groq LLM và tự động lưu template vào danh sách
- Không hiển thị nội dung prompt trực tiếp ra ngoài để giữ tính bảo mật/tinh gọn cho giao diện, hiển thị thẻ thông báo lưu template thành công (`#templateSavedCard`).
- Hiển thị kết quả prompt (có cơ chế thu gọn / Xem thêm khi prompt dài) và nút "Dùng prompt này"

**Keywords**: `ai_prompt_builder`, `uploadZone`, `imageFileInput`, `previewImg`, `removeImageBtn`, `promptNameInput`, `groqApiKeyInput`, `groqModelSelect`, `modeStandardCard`, `modeAdvancedCard`, `modeLimitBadge`, `promptMode`, `suggestPromptBtn`, `suggestedResult`, `toggleExpandPromptBtn`, `useThisPromptBtn`

---

## history.html
**ID elements**: `#historyGrid`, `#manageHistoryBtn`, `#selectAllHistoryBtn`, `#deleteSelectedHistoryBtn`, `#selectedHistoryCount`, `#clearHistoryBtn`, `#historyCountBadge`
- Gallery hiển thị các ảnh đã tạo gần đây
- Hỗ trợ **tích chọn nhiều ảnh** (checkbox trên thumbnail) và nút "Quản lý" mở modal chuyên dụng để xóa chỉ định hoặc xóa tất cả.
- **Keywords**: `history`, `recent creations`, `gallery`, `manageHistoryBtn`, `selectAllHistoryBtn`, `deleteSelectedHistoryBtn`, `selectedHistoryCount`

---

## history_modal.html
**ID elements**: `#historyManagerModal`, `#historyModalBackdrop`, `#closeHistoryModalBtn`, `#selectAllHistoryModalCb`, `#deleteSelectedHistoryModalBtn`, `#selectedHistoryModalCount`, `#historyListModalContainer`, `#doneHistoryModalBtn`
- Modal quản lý Lịch sử Tạo ảnh: hiển thị danh sách ảnh kèm prompt, thời gian tạo
- Hỗ trợ **tích chọn nhiều ảnh** để xóa hàng loạt hoặc xem/dùng lại prompt.
- **Keywords**: `history_modal`, `historyManagerModal`, `deleteSelectedHistoryModalBtn`, `selectAllHistoryModalCb`, `batch delete history`

---

## template_modal.html
**ID elements**: `#templateManagerModal`, `#templateModalBackdrop`, `#closeTemplateModalBtn`, `#selectAllTemplatesCb`, `#deleteSelectedTemplatesBtn`, `#selectedTemplatesCount`, `#templateListContainer`, `#doneTemplateModalBtn`
- Modal quản lý Prompt Templates: hiển thị danh sách toàn bộ templates (mặc định + do người dùng tạo)
- Hỗ trợ **tích chọn nhiều template** để xóa hàng loạt qua API `POST /api/prompt-templates/batch-delete`.
- Template hệ thống có badge "Hệ thống" và bị khóa không cho xóa.
- **Keywords**: `template_modal`, `templateManagerModal`, `deleteSelectedTemplatesBtn`, `selectAllTemplatesCb`, `batch delete templates`

---

## modal.html
- Lightbox modal xem ảnh fullscreen
- **Keywords**: `modal`, `lightbox`, `fullscreen viewer`

---

## footer.html
- Thông tin footer
- **Keywords**: `footer`

## Phụ thuộc
- Include bởi: `templates/index.html`, `templates/components/preview_panel.html`, `templates/components/control_form.html`
- Tương tác với: `templates/js/app.js`, `templates/js/template_manager.js`, `templates/js/prompt_builder.js`, `templates/js/rate_limit_ui.js`
- Style bởi: `templates/css/style.css`

