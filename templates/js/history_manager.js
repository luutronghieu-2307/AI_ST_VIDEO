/**
 * history_manager.js – Quản lý lịch sử ảnh tạo & Modal chọn nhiều để xóa
 * Tương thích và đồng bộ với template_manager.js
 */

/* ─── State ───────────────────────────────────────────────────────────── */
let _history = [];
let _selectedHistoryIds = new Set();

/* ─── Storage ─────────────────────────────────────────────────────────── */
function _loadHistory() {
    try {
        const raw = JSON.parse(localStorage.getItem('aura_ai_history') || '[]');
        return raw.map((item, idx) => ({
            id: item.id || `hist_${Date.now()}_${idx}_${Math.random().toString(36).slice(2, 6)}`,
            url: item.url || '',
            prompt: item.prompt || '',
            timestamp: item.timestamp || 'Gần đây'
        }));
    } catch { return []; }
}

function _saveHistory() {
    try {
        localStorage.setItem('aura_ai_history', JSON.stringify(_history));
    } catch (e) {
        console.warn('Không thể lưu localStorage:', e);
    }
}

/* ─── Public API ──────────────────────────────────────────────────────── */
function addToHistory(url, prompt) {
    if (!url) return;
    const newItem = {
        id: `hist_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
        url,
        prompt: prompt || '',
        timestamp: new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })
    };
    _history.unshift(newItem);
    if (_history.length > 25) _history.pop();
    _selectedHistoryIds.clear();
    _saveHistory();
    _renderAll();
}

/* ─── Render ──────────────────────────────────────────────────────────── */
function _renderAll() {
    _renderGrid();
    _renderModalList();
    _syncToolbar();
}

function _renderGrid() {
    const grid = document.getElementById('historyGrid');
    if (!grid) return;

    if (!_history.length) {
        grid.innerHTML = '<span class="history-empty">Chưa có lịch sử tạo ảnh nào.</span>';
        return;
    }

    grid.innerHTML = _history.map(item => {
        const sel = _selectedHistoryIds.has(item.id);
        return `
            <div class="history-card ${sel ? 'selected' : ''}" data-id="${item.id}"
                 title="${(item.prompt || '').replace(/"/g, '&quot;')}">
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

function _renderModalList() {
    const container = document.getElementById('historyListModalContainer');
    if (!container) return;

    if (!_history.length) {
        container.innerHTML = '<div class="empty-hint">Chưa có ảnh nào trong lịch sử.</div>';
        return;
    }

    container.innerHTML = _history.map(item => {
        const sel = _selectedHistoryIds.has(item.id);
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
                           title="${(item.prompt || '').replace(/"/g, '&quot;')}">${item.prompt || ''}</p>
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

    container.querySelectorAll('.history-modal-cb').forEach(cb => {
        cb.addEventListener('change', (e) => {
            const id = e.target.dataset.id;
            if (id) {
                e.target.checked ? _selectedHistoryIds.add(id) : _selectedHistoryIds.delete(id);
                _renderAll();
            }
        });
    });
}

function _syncToolbar() {
    const hasItems = _history.length > 0;
    const selCount = _selectedHistoryIds.size;

    /* Count badge */
    const badge = document.getElementById('historyCountBadge');
    if (badge) {
        badge.classList.toggle('hidden', !hasItems);
        badge.textContent = `${_history.length} ảnh`;
    }

    /* Manage + Clear buttons */
    document.getElementById('manageHistoryBtn')?.classList.toggle('hidden', !hasItems);
    document.getElementById('clearHistoryBtn')?.classList.toggle('hidden', !hasItems);

    /* Select-all outside grid */
    const saBtn = document.getElementById('selectAllHistoryBtn');
    if (saBtn) {
        saBtn.classList.toggle('hidden', !hasItems);
        const isAll = hasItems && selCount === _history.length;
        saBtn.innerHTML = isAll
            ? '<i class="fa-solid fa-square-minus"></i> Bỏ chọn'
            : '<i class="fa-solid fa-check-double"></i> Chọn tất cả';
    }

    /* Delete-selected outside grid */
    const delBtn = document.getElementById('deleteSelectedHistoryBtn');
    const delCount = document.getElementById('selectedHistoryCount');
    if (delBtn) delBtn.classList.toggle('hidden', selCount === 0);
    if (delCount) delCount.textContent = selCount;

    /* Modal toolbar */
    const delModalBtn = document.getElementById('deleteSelectedHistoryModalBtn');
    const delModalCount = document.getElementById('selectedHistoryModalCount');
    const selectAllCb = document.getElementById('selectAllHistoryModalCb');
    if (delModalBtn) delModalBtn.classList.toggle('hidden', selCount === 0);
    if (delModalCount) delModalCount.textContent = selCount;
    if (selectAllCb) {
        selectAllCb.checked = hasItems && selCount === _history.length;
        selectAllCb.indeterminate = selCount > 0 && selCount < _history.length;
        selectAllCb.disabled = !hasItems;
    }
}

/* ─── Actions ──────────────────────────────────────────────────────────── */
function _toggleSelect(id) {
    if (!id) return;
    _selectedHistoryIds.has(id) ? _selectedHistoryIds.delete(id) : _selectedHistoryIds.add(id);
    _renderAll();
}

function _toggleSelectAll() {
    if (!_history.length) return;
    const isAll = _selectedHistoryIds.size === _history.length;
    _selectedHistoryIds = isAll ? new Set() : new Set(_history.map(i => i.id));
    _renderAll();
}

function _deleteSelected() {
    if (!_selectedHistoryIds.size) return;
    if (!confirm(`Xóa ${_selectedHistoryIds.size} ảnh đã chọn khỏi lịch sử?`)) return;
    _history = _history.filter(i => !_selectedHistoryIds.has(i.id));
    _selectedHistoryIds.clear();
    _saveHistory();
    _renderAll();
}

function _clearAll() {
    if (!_history.length || !confirm('Bạn có chắc muốn xóa TOÀN BỘ lịch sử ảnh?')) return;
    _history = [];
    _selectedHistoryIds.clear();
    localStorage.removeItem('aura_ai_history');
    _renderAll();
}

function _previewImage(url) {
    if (!url) return;
    const resultImg = document.getElementById('resultImage');
    const imageWrapper = document.getElementById('imageWrapper');
    const placeholder = document.getElementById('placeholderState');
    if (resultImg) resultImg.src = url;
    imageWrapper?.classList.remove('hidden');
    placeholder?.classList.add('hidden');
    document.getElementById('historyManagerModal')?.classList.add('hidden');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function _usePrompt(encoded) {
    const input = document.getElementById('promptInput');
    if (input) { input.value = decodeURIComponent(encoded); input.focus(); }
    document.getElementById('historyManagerModal')?.classList.add('hidden');
}

/* ─── Event Delegation ────────────────────────────────────────────────── */
function _setupDelegation() {
    /* Grid (history section) */
    const grid = document.getElementById('historyGrid');
    grid?.addEventListener('click', e => {
        const btn = e.target.closest('[data-action]');
        if (!btn) return;
        e.stopPropagation();
        const action = btn.dataset.action;
        if (action === 'toggle-select') _toggleSelect(btn.dataset.id);
        if (action === 'preview') _previewImage(btn.dataset.url);
    });

    /* Modal list */
    const modalList = document.getElementById('historyListModalContainer');
    modalList?.addEventListener('click', e => {
        const btn = e.target.closest('[data-action]');
        if (!btn) return;
        e.stopPropagation();
        const action = btn.dataset.action;
        if (action === 'preview') _previewImage(btn.dataset.url);
        if (action === 'use-prompt') _usePrompt(btn.dataset.prompt);
    });

    /* Toolbar buttons */
    document.getElementById('selectAllHistoryBtn')
        ?.addEventListener('click', (e) => { e.preventDefault(); _toggleSelectAll(); });

    document.getElementById('deleteSelectedHistoryBtn')
        ?.addEventListener('click', (e) => { e.preventDefault(); _deleteSelected(); });

    document.getElementById('clearHistoryBtn')
        ?.addEventListener('click', (e) => { e.preventDefault(); _clearAll(); });

    /* Modal controls */
    const modal = document.getElementById('historyManagerModal');
    document.getElementById('manageHistoryBtn')
        ?.addEventListener('click', () => modal?.classList.remove('hidden'));

    document.getElementById('closeHistoryModalBtn')
        ?.addEventListener('click', () => modal?.classList.add('hidden'));

    document.getElementById('doneHistoryModalBtn')
        ?.addEventListener('click', () => modal?.classList.add('hidden'));

    document.getElementById('historyModalBackdrop')
        ?.addEventListener('click', () => modal?.classList.add('hidden'));

    document.getElementById('selectAllHistoryModalCb')
        ?.addEventListener('change', (e) => {
            _selectedHistoryIds = e.target.checked
                ? new Set(_history.map(i => i.id))
                : new Set();
            _renderAll();
        });

    document.getElementById('deleteSelectedHistoryModalBtn')
        ?.addEventListener('click', (e) => { e.preventDefault(); _deleteSelected(); });
}

/* ─── Init ─────────────────────────────────────────────────────────────── */
function initHistoryManager() {
    _history = _loadHistory();
    _saveHistory();
    _setupDelegation();
    _renderAll();
}

if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initHistoryManager);
    } else {
        initHistoryManager();
    }
}

/* ─── Exports for Window and CommonJS / Jest ────────────────────────────── */
if (typeof window !== 'undefined') {
    window.addToHistory = addToHistory;
    window.previewHistoryImage = _previewImage;
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        _loadHistory, _saveHistory, addToHistory, _renderAll, _renderGrid,
        _renderModalList, _syncToolbar, _toggleSelect, _toggleSelectAll,
        _deleteSelected, _clearAll, _previewImage, _usePrompt, _setupDelegation,
        initHistoryManager,
        getState: () => ({ history: _history, selectedIds: _selectedHistoryIds }),
        setState: (h, s) => { _history = h; _selectedHistoryIds = s || new Set(); }
    };
}
