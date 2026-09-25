/**
 * storyboard_history.js – Quản lý lịch sử storyboard trong localStorage
 *
 * Lưu, hiển thị, xóa, chọn nhiều storyboard.
 */

const HISTORY_KEY = 'aura_storyboard_history';
const MAX_HISTORY = 20;

let _storyboardHistory = [];

/* ─── Init ────────────────────────────────────────────────────────────── */
if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', () => {
        initStoryboardHistory();
    });
}

function initStoryboardHistory() {
    _storyboardHistory = loadStoryboardHistory();
    renderStoryboardHistory();
}

/* ─── Storage ─────────────────────────────────────────────────────────── */
function loadStoryboardHistory() {
    try {
        const raw = JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]');
        return raw.map((item, idx) => ({
            id: item.id || `sb_hist_${Date.now()}_${idx}`,
            storyboardId: item.storyboardId || '',
            title: item.title || 'Không có tiêu đề',
            total: item.total || 0,
            completed: item.completed || 0,
            status: item.status || 'pending',
            createdAt: item.createdAt || 'Gần đây'
        }));
    } catch {
        return [];
    }
}

function saveStoryboardHistory() {
    try {
        localStorage.setItem(HISTORY_KEY, JSON.stringify(_storyboardHistory));
    } catch (e) {
        console.warn('Không thể lưu storyboard history:', e);
    }
}

/* ─── Public API ──────────────────────────────────────────────────────── */
function addStoryboardToHistory(storyboard) {
    if (!storyboard || !storyboard.storyboard_id) return;

    const newItem = {
        id: `sb_hist_${Date.now()}`,
        storyboardId: storyboard.storyboard_id,
        title: storyboard.title || 'Không có tiêu đề',
        total: storyboard.total || 0,
        completed: storyboard.completed || 0,
        status: storyboard.status || 'pending',
        createdAt: new Date().toLocaleString('vi-VN', {
            hour: '2-digit', minute: '2-digit',
            day: '2-digit', month: '2-digit'
        })
    };

    // Xóa entry cũ nếu trùng storyboardId
    _storyboardHistory = _storyboardHistory.filter(
        item => item.storyboardId !== storyboard.storyboard_id
    );

    _storyboardHistory.unshift(newItem);
    if (_storyboardHistory.length > MAX_HISTORY) _storyboardHistory.pop();

    saveStoryboardHistory();
    renderStoryboardHistory();
}

function updateStoryboardInHistory(storyboard) {
    const item = _storyboardHistory.find(s => s.storyboardId === storyboard.storyboard_id);
    if (!item) return;

    item.completed = storyboard.completed || 0;
    item.status = storyboard.status || 'pending';
    saveStoryboardHistory();
    renderStoryboardHistory();
}

/* ─── Render ──────────────────────────────────────────────────────────── */
function renderStoryboardHistory() {
    const container = document.getElementById('storyboardHistoryList');
    if (!container) return;

    if (!_storyboardHistory.length) {
        container.innerHTML = '<div class="empty-hint">Chưa có storyboard nào.</div>';
        return;
    }

    container.innerHTML = _storyboardHistory.map(item => {
        const pct = item.total > 0 ? Math.round((item.completed / item.total) * 100) : 0;
        const statusClass = `status-${item.status}`;

        return `
            <div class="storyboard-history-item" data-id="${item.id}">
                <div class="history-item-info">
                    <strong class="history-item-title">${escapeHtml(item.title)}</strong>
                    <span class="history-item-meta">
                        <span class="segment-status-badge ${statusClass}">${item.status}</span>
                        <span>${item.completed}/${item.total} video</span>
                        <span>${item.createdAt}</span>
                    </span>
                    <div class="history-item-progress">
                        <div class="history-item-progress-fill" style="width: ${pct}%"></div>
                    </div>
                </div>
                <div class="history-item-actions">
                    <button class="text-btn action-sm" data-action="load" data-storyboard-id="${item.storyboardId}">
                        <i class="fa-solid fa-folder-open"></i> Mở
                    </button>
                    <button class="text-btn danger action-sm" data-action="delete" data-id="${item.id}">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </div>
            </div>`;
    }).join('');

    attachHistoryEvents();
}

function attachHistoryEvents() {
    const container = document.getElementById('storyboardHistoryList');
    container?.querySelectorAll('[data-action]').forEach(btn => {
        btn.addEventListener('click', () => {
            const action = btn.dataset.action;
            if (action === 'load') loadStoryboardFromHistory(btn.dataset.storyboardId);
            if (action === 'delete') deleteStoryboardFromHistory(btn.dataset.id);
        });
    });
}

/* ─── Actions ─────────────────────────────────────────────────────────── */
function deleteStoryboardFromHistory(id) {
    if (!confirm('Xóa storyboard này khỏi lịch sử?')) return;
    _storyboardHistory = _storyboardHistory.filter(item => item.id !== id);
    saveStoryboardHistory();
    renderStoryboardHistory();
}

function clearStoryboardHistory() {
    if (!_storyboardHistory.length) return;
    if (!confirm('Xóa TOÀN BỘ lịch sử storyboard?')) return;
    _storyboardHistory = [];
    localStorage.removeItem(HISTORY_KEY);
    renderStoryboardHistory();
}

function loadStoryboardFromHistory(storyboardId) {
    if (!storyboardId) return;

    fetch(`/api/storyboard/${storyboardId}`)
        .then(r => r.ok ? r.json() : null)
        .then(data => {
            if (!data) {
                alert('Không tìm thấy storyboard.');
                return;
            }
            // Chuyển sang view Storyboard
            if (typeof window.switchView === 'function') {
                window.switchView('viewStoryboard');
            }
            // Render timeline
            if (typeof window.renderTimeline === 'function') {
                window.renderTimeline(data);
            }
            // Bắt đầu polling nếu chưa xong
            if (data.status !== 'completed' && typeof window.startPolling === 'function') {
                window.startPolling(storyboardId);
            }
        })
        .catch(() => alert('Lỗi tải storyboard.'));
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str || '';
    return div.innerHTML;
}

/* ─── Exports for Jest ────────────────────────────────────────────────── */
if (typeof window !== 'undefined') {
    window.addStoryboardToHistory = addStoryboardToHistory;
    window.updateStoryboardInHistory = updateStoryboardInHistory;
    window.clearStoryboardHistory = clearStoryboardHistory;
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initStoryboardHistory, loadStoryboardHistory, saveStoryboardHistory,
        addStoryboardToHistory, updateStoryboardInHistory, renderStoryboardHistory,
        deleteStoryboardFromHistory, clearStoryboardHistory, loadStoryboardFromHistory,
        escapeHtml,
        getState: () => ({ history: _storyboardHistory }),
        setState: (h) => { _storyboardHistory = h || []; }
    };
}
