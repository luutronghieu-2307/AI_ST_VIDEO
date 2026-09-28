/**
 * history_manager.js – Điều phối lịch sử ảnh & Modal quản lý
 * Modularized with history_store.js and history_ui.js
 */

const _Store = (typeof require !== 'undefined') ? require('./history_store') : (window.HistoryStore || {});
const _UI = (typeof require !== 'undefined') ? require('./history_ui') : (window.HistoryUI || {});

let _history = [];
let _selectedHistoryIds = new Set();

function _loadHistory() { return _Store.loadHistory ? _Store.loadHistory() : []; }
function _saveHistory() { if (_Store.saveHistory) _Store.saveHistory(_history); }

function addToHistory(url, prompt) {
    if (!url) return;
    _history = _Store.addHistoryItem ? _Store.addHistoryItem(_history, url, prompt) : _history;
    _selectedHistoryIds.clear();
    _saveHistory();
    _renderAll();
}

function _renderAll() {
    _renderGrid();
    _renderModalList();
    _syncToolbar();
}

function _renderGrid() {
    if (_UI.renderHistoryGrid) _UI.renderHistoryGrid(_history, _selectedHistoryIds);
}

function _renderModalList() {
    if (_UI.renderHistoryModalList) {
        _UI.renderHistoryModalList(_history, _selectedHistoryIds, (id, checked) => {
            if (id) {
                checked ? _selectedHistoryIds.add(id) : _selectedHistoryIds.delete(id);
                _renderAll();
            }
        });
    }
}

function _syncToolbar() {
    if (_UI.syncHistoryToolbar) _UI.syncHistoryToolbar(_history, _selectedHistoryIds);
}

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
    _history = _Store.removeHistoryByIds ? _Store.removeHistoryByIds(_history, _selectedHistoryIds) : _history;
    _selectedHistoryIds.clear();
    _saveHistory();
    _renderAll();
}

function _clearAll() {
    if (!_history.length || !confirm('Bạn có chắc muốn xóa TOÀN BỘ lịch sử ảnh?')) return;
    _history = [];
    _selectedHistoryIds.clear();
    if (_Store.clearAllHistory) _Store.clearAllHistory();
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

function _setupDelegation() {
    const grid = document.getElementById('historyGrid');
    grid?.addEventListener('click', e => {
        const btn = e.target.closest('[data-action]');
        if (!btn) return;
        e.stopPropagation();
        const action = btn.dataset.action;
        if (action === 'toggle-select') _toggleSelect(btn.dataset.id);
        if (action === 'preview') _previewImage(btn.dataset.url);
    });

    const modalList = document.getElementById('historyListModalContainer');
    modalList?.addEventListener('click', e => {
        const btn = e.target.closest('[data-action]');
        if (!btn) return;
        e.stopPropagation();
        const action = btn.dataset.action;
        if (action === 'preview') _previewImage(btn.dataset.url);
        if (action === 'use-prompt') _usePrompt(btn.dataset.prompt);
    });

    document.getElementById('selectAllHistoryBtn')?.addEventListener('click', (e) => { e.preventDefault(); _toggleSelectAll(); });
    document.getElementById('deleteSelectedHistoryBtn')?.addEventListener('click', (e) => { e.preventDefault(); _deleteSelected(); });
    document.getElementById('clearHistoryBtn')?.addEventListener('click', (e) => { e.preventDefault(); _clearAll(); });

    const modal = document.getElementById('historyManagerModal');
    document.getElementById('manageHistoryBtn')?.addEventListener('click', () => modal?.classList.remove('hidden'));
    document.getElementById('closeHistoryModalBtn')?.addEventListener('click', () => modal?.classList.add('hidden'));
    document.getElementById('doneHistoryModalBtn')?.addEventListener('click', () => modal?.classList.add('hidden'));
    document.getElementById('historyModalBackdrop')?.addEventListener('click', () => modal?.classList.add('hidden'));

    document.getElementById('selectAllHistoryModalCb')?.addEventListener('change', (e) => {
        _selectedHistoryIds = e.target.checked ? new Set(_history.map(i => i.id)) : new Set();
        _renderAll();
    });

    document.getElementById('deleteSelectedHistoryModalBtn')?.addEventListener('click', (e) => { e.preventDefault(); _deleteSelected(); });
}

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
