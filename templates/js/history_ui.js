/**
 * history_ui.js – Phụ trách render HTML & cập nhật giao diện Lịch sử ảnh
 */

function escapeHtml(str) {
    return (str || '').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function renderHistoryGrid(history, selectedIds) {
    const grid = document.getElementById('historyGrid');
    if (!grid) return;

    if (!history.length) {
        grid.innerHTML = '<span class="history-empty">Chưa có lịch sử tạo ảnh nào.</span>';
        return;
    }

    grid.innerHTML = history.map(item => {
        const sel = selectedIds.has(item.id);
        const escapedPrompt = escapeHtml(item.prompt);
        return `
            <div class="history-card ${sel ? 'selected' : ''}" data-id="${item.id}"
                 title="${escapedPrompt}">
                <button type="button"
                        class="history-check-btn ${sel ? 'checked' : ''}"
                        data-action="toggle-select"
                        data-id="${item.id}"
                        title="${sel ? 'Bỏ chọn' : 'Chọn ảnh'}">
                    <i class="fa-solid fa-check"></i>
                </button>
                <img src="${item.url}" alt="History Item"
                     data-action="preview" data-url="${item.url}">
            </div>`;
    }).join('');
}

function renderHistoryModalList(history, selectedIds, onSelectionChange) {
    const container = document.getElementById('historyListModalContainer');
    if (!container) return;

    if (!history.length) {
        container.innerHTML = '<div class="empty-hint">Chưa có ảnh nào trong lịch sử.</div>';
        return;
    }

    container.innerHTML = history.map(item => {
        const sel = selectedIds.has(item.id);
        const escapedPrompt = escapeHtml(item.prompt);
        return `
            <div class="template-item-row ${sel ? 'selected' : ''}" data-id="${item.id}">
                <div class="template-item-left">
                    <label class="custom-checkbox-label" onclick="event.stopPropagation()">
                        <input type="checkbox" class="history-modal-cb" data-id="${item.id}" ${sel ? 'checked' : ''}>
                        <span class="custom-checkmark"><i class="fa-solid fa-check"></i></span>
                    </label>
                    <img src="${item.url}" alt="Thumbnail" class="history-modal-thumb"
                         data-action="preview" data-url="${item.url}">
                    <div class="template-info">
                        <div class="template-name-row">
                            <span class="badge-tag default">${item.timestamp || 'Gần đây'}</span>
                        </div>
                        <p class="template-preview-text"
                           title="${escapedPrompt}">${item.prompt || ''}</p>
                    </div>
                </div>
                <button type="button"
                        class="text-btn action-sm accent"
                        data-action="use-prompt"
                        data-prompt="${encodeURIComponent(item.prompt || '')}">
                    <i class="fa-solid fa-arrow-turn-down"></i> Dùng prompt
                </button>
            </div>`;
    }).join('');

    if (typeof onSelectionChange === 'function') {
        container.querySelectorAll('.history-modal-cb').forEach(cb => {
            cb.addEventListener('change', (e) => onSelectionChange(e.target.dataset.id, e.target.checked));
        });
    }
}

function syncHistoryToolbar(history, selectedIds) {
    const hasItems = history.length > 0;
    const selCount = selectedIds.size;

    const badge = document.getElementById('historyCountBadge');
    if (badge) {
        badge.classList.toggle('hidden', !hasItems);
        badge.textContent = `${history.length} ảnh`;
    }

    document.getElementById('manageHistoryBtn')?.classList.toggle('hidden', !hasItems);
    document.getElementById('clearHistoryBtn')?.classList.toggle('hidden', !hasItems);

    const saBtn = document.getElementById('selectAllHistoryBtn');
    if (saBtn) {
        saBtn.classList.toggle('hidden', !hasItems);
        const isAll = hasItems && selCount === history.length;
        saBtn.innerHTML = isAll
            ? '<i class="fa-solid fa-square-minus"></i> Bỏ chọn'
            : '<i class="fa-solid fa-check-double"></i> Chọn tất cả';
    }

    const delBtn = document.getElementById('deleteSelectedHistoryBtn');
    const delCount = document.getElementById('selectedHistoryCount');
    if (delBtn) delBtn.classList.toggle('hidden', selCount === 0);
    if (delCount) delCount.textContent = selCount;

    const delModalBtn = document.getElementById('deleteSelectedHistoryModalBtn');
    const delModalCount = document.getElementById('selectedHistoryModalCount');
    const selectAllCb = document.getElementById('selectAllHistoryModalCb');
    if (delModalBtn) delModalBtn.classList.toggle('hidden', selCount === 0);
    if (delModalCount) delModalCount.textContent = selCount;
    if (selectAllCb) {
        selectAllCb.checked = hasItems && selCount === history.length;
        selectAllCb.indeterminate = selCount > 0 && selCount < history.length;
        selectAllCb.disabled = !hasItems;
    }
}

/* ─── Window & CommonJS Exports ────────────────────────────────────────── */
if (typeof window !== 'undefined') {
    window.HistoryUI = {
        escapeHtml,
        renderHistoryGrid,
        renderHistoryModalList,
        syncHistoryToolbar
    };
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        escapeHtml,
        renderHistoryGrid,
        renderHistoryModalList,
        syncHistoryToolbar
    };
}
