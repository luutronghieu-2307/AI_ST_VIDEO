# 📋 Kế hoạch Tối ưu & Phân tách: `templates/js/history_manager.js`

> **Trạng thái**: ✅ Đã hoàn thành  
> **File gốc**: `templates/js/history_manager.js` (Trước: 313 dòng -> Sau: 164 dòng)  
> **Kết quả**: Phân tách thành 3 sub-module (`history_store.js`: 83 dòng, `history_ui.js`: 138 dòng, `history_manager.js`: 164 dòng), Test coverage Jest đạt 97–100%.

---

## 1. Phân tích Hiện trạng
File `templates/js/history_manager.js` hiện đang chịu trách nhiệm quá nhiều vai trò:
1. **Quản lý dữ liệu (Storage & State)**: `_loadHistory`, `_saveHistory`, `addToHistory`, `_deleteSelected`, `_clearAll`, `_toggleSelect`, `_toggleSelectAll`.
2. **Render giao diện (DOM & UI)**: `_renderGrid`, `_renderModalList`, `_syncToolbar`, `_renderAll`.
3. **Sự kiện & Điều khiển (Event Delegation & Actions)**: `_setupDelegation`, `_previewImage`, `_usePrompt`, `initHistoryManager`.

---

## 2. Phương án Phân tách (Modular Architecture)

Tách `templates/js/history_manager.js` thành 3 module chuyên biệt:

```
templates/js/
├── history_store.js         # (~60-80 dòng): Quản lý localStorage, State và Data operations
├── history_ui.js            # (~100-120 dòng): Render HTML grid & modal list, DOM helpers
└── history_manager.js       # (~80-100 dòng): Entry point, Event delegation, Orchestration
```

### Chi tiết phân chia nhiệm vụ:

#### 1. `templates/js/history_store.js`
- **Nhiệm vụ**: Độc lập với DOM, chỉ xử lý dữ liệu và `localStorage`.
- **Hàm dự kiến**:
  - `loadHistory()`: Đọc và parse JSON từ `localStorage`.
  - `saveHistory(items)`: Lưu mảng items vào `localStorage`.
  - `addToHistory(url, prompt)`: Thêm item mới vào đầu danh sách (tối đa `MAX_HISTORY = 50`).
  - `deleteSelected(selectedIds)`: Xóa các item theo mảng ID.
  - `clearAll()`: Xóa toàn bộ lịch sử.
  - `getSelectedIds()` / `toggleSelect(id)` / `toggleSelectAll(isSelectAll)`: Quản lý tập `Set` các item được chọn.

#### 2. `templates/js/history_ui.js`
- **Nhiệm vụ**: Chỉ phụ trách sinh HTML string và cập nhật các element DOM.
- **Hàm dự kiến**:
  - `renderGrid(items)`: Render danh sách ảnh dạng grid ở giao diện chính.
  - `renderModalList(items, selectedIds)`: Render bảng danh sách lịch sử trong modal quản lý.
  - `syncToolbar(selectedCount, totalCount)`: Cập nhật trạng thái nút "Chọn tất cả", "Xóa đã chọn", text số lượng.
  - `escapeHtml(str)`: Helper chống XSS.

#### 3. `templates/js/history_manager.js`
- **Nhiệm vụ**: Kết nối Store và UI, lắng nghe và xử lý sự kiện người dùng (click, modal show/hide, use prompt, preview).
- **Hàm dự kiến**:
  - `initHistoryManager()`: Khởi tạo, render ban đầu và gán event delegation.
  - `setupDelegation()`: Bắt các event click (use prompt, preview, delete, checkbox).
  - `previewImage(url)`: Hiển thị lightbox.
  - `usePrompt(promptText)`: Điền prompt vào ô input chính.

---

## 3. Kế hoạch Thực hiện

- [ ] **Bước 1**: Tạo file `templates/js/history_store.js` và export module chuẩn (hỗ trợ cả ES module / Window global / Jest CommonJS).
- [ ] **Bước 2**: Tạo file `templates/js/history_ui.js` chứa các hàm render.
- [ ] **Bước 3**: Rút gọn `templates/js/history_manager.js` làm controller trung tâm.
- [ ] **Bước 4**: Cập nhật `templates/base.html` để nạp các file script theo đúng thứ tự (`history_store.js` -> `history_ui.js` -> `history_manager.js`).
- [ ] **Bước 5**: Cập nhật và chạy lại test `test/test_history_manager.js`, bổ sung `test/test_history_store.js` và `test/test_history_ui.js` đạt độ phủ ≥ 90%.
- [ ] **Bước 6**: Cập nhật tài liệu `docs/templates_components.md` và `DOCS_INDEX.md`.
