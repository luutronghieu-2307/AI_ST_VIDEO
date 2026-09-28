/**
 * history_store.js – Quản lý dữ liệu lịch sử ảnh & localStorage
 */

const MAX_HISTORY = 25;
const STORAGE_KEY = 'aura_ai_history';

function loadHistory() {
    try {
        const raw = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
        return raw.map((item, idx) => ({
            id: item.id || `hist_${Date.now()}_${idx}_${Math.random().toString(36).slice(2, 6)}`,
            url: item.url || '',
            prompt: item.prompt || '',
            timestamp: item.timestamp || 'Gần đây'
        }));
    } catch {
        return [];
    }
}

function saveHistory(history) {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
    } catch (e) {
        console.warn('Không thể lưu localStorage:', e);
    }
}

function createHistoryItem(url, prompt) {
    if (!url) return null;
    return {
        id: `hist_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
        url,
        prompt: prompt || '',
        timestamp: new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })
    };
}

function addHistoryItem(history, url, prompt) {
    const item = createHistoryItem(url, prompt);
    if (!item) return history;
    const next = [item, ...history];
    if (next.length > MAX_HISTORY) next.pop();
    return next;
}

function removeHistoryByIds(history, idsSet) {
    return history.filter(item => !idsSet.has(item.id));
}

function clearAllHistory() {
    try {
        localStorage.removeItem(STORAGE_KEY);
    } catch (e) {
        console.warn('Không thể xóa localStorage:', e);
    }
}

/* ─── Window & CommonJS Exports ────────────────────────────────────────── */
if (typeof window !== 'undefined') {
    window.HistoryStore = {
        loadHistory,
        saveHistory,
        createHistoryItem,
        addHistoryItem,
        removeHistoryByIds,
        clearAllHistory,
        MAX_HISTORY
    };
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        loadHistory,
        saveHistory,
        createHistoryItem,
        addHistoryItem,
        removeHistoryByIds,
        clearAllHistory,
        MAX_HISTORY
    };
}
