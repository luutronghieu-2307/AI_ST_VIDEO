/**
 * test_history_manager.js – Unit tests cho templates/js/history_manager.js
 * Dùng Jest + JSDOM để simulate browser environment
 *
 * @jest-environment jsdom
 */

function setupDOM() {
    document.body.innerHTML = `
        <div id="historyGrid"></div>
        <span id="historyCountBadge" class="hidden">0 ảnh</span>
        <button id="manageHistoryBtn" class="hidden">Quản lý</button>
        <button id="selectAllHistoryBtn" class="hidden">Chọn tất cả</button>
        <button id="deleteSelectedHistoryBtn" class="hidden">Xóa (<span id="selectedHistoryCount">0</span>)</button>
        <button id="clearHistoryBtn" class="hidden">Xóa tất cả</button>
        <div id="historyManagerModal" class="hidden">
            <div id="historyModalBackdrop"></div>
            <div id="historyListModalContainer"></div>
            <input type="checkbox" id="selectAllHistoryModalCb">
            <button id="deleteSelectedHistoryModalBtn" class="hidden">
                Xóa (<span id="selectedHistoryModalCount">0</span>)
            </button>
            <button id="closeHistoryModalBtn">Đóng</button>
            <button id="doneHistoryModalBtn">Xong</button>
        </div>
        <img id="resultImage" src="">
        <div id="imageWrapper" class="hidden"></div>
        <div id="placeholderState"></div>
        <input id="promptInput" type="text">
    `;
}

// Mock localStorage
const localStorageMock = (() => {
    let store = {};
    return {
        getItem: (key) => store[key] || null,
        setItem: (key, value) => { store[key] = String(value); },
        removeItem: (key) => { delete store[key]; },
        clear: () => { store = {}; },
    };
})();

Object.defineProperty(window, 'localStorage', { value: localStorageMock });

window.confirm = jest.fn(() => true);
window.scrollTo = jest.fn();

let hm;

beforeEach(() => {
    setupDOM();
    localStorageMock.clear();
    window.confirm.mockReturnValue(true);
    jest.resetModules();

    hm = require('../templates/js/history_manager');
});

describe('addToHistory()', () => {
    test('thêm item mới vào đầu danh sách', () => {
        hm.addToHistory('https://example.com/img1.png', 'Test prompt 1');
        hm.addToHistory('https://example.com/img2.png', 'Test prompt 2');
        const stored = JSON.parse(localStorage.getItem('aura_ai_history') || '[]');
        expect(stored[0].url).toBe('https://example.com/img2.png');
        expect(stored[1].url).toBe('https://example.com/img1.png');
    });

    test('bỏ qua nếu url rỗng', () => {
        hm.addToHistory('', 'Test prompt');
        const state = hm.getState();
        expect(state.history.length).toBe(0);
    });

    test('mỗi item phải có ID duy nhất', () => {
        hm.addToHistory('https://example.com/img1.png', 'prompt 1');
        hm.addToHistory('https://example.com/img2.png', 'prompt 2');
        const stored = JSON.parse(localStorage.getItem('aura_ai_history') || '[]');
        expect(stored[0].id).not.toBe(stored[1].id);
    });

    test('giới hạn tối đa 25 items', () => {
        for (let i = 0; i < 30; i++) {
            hm.addToHistory(`https://example.com/img${i}.png`, `prompt ${i}`);
        }
        const stored = JSON.parse(localStorage.getItem('aura_ai_history') || '[]');
        expect(stored.length).toBeLessThanOrEqual(25);
    });

    test('render grid sau khi thêm', () => {
        hm.addToHistory('https://example.com/img1.png', 'Test prompt');
        const grid = document.getElementById('historyGrid');
        expect(grid.innerHTML).toContain('history-card');
    });

    test('hiển thị badge với số lượng đúng', () => {
        hm.addToHistory('https://example.com/img1.png', 'prompt 1');
        hm.addToHistory('https://example.com/img2.png', 'prompt 2');
        const badge = document.getElementById('historyCountBadge');
        expect(badge.textContent).toBe('2 ảnh');
        expect(badge.classList.contains('hidden')).toBe(false);
    });
});

describe('Chọn ảnh lịch sử', () => {
    test('click history-check-btn chọn ảnh', () => {
        hm.addToHistory('https://example.com/img1.png', 'prompt 1');
        const checkBtn = document.querySelector('.history-check-btn[data-action="toggle-select"]');
        expect(checkBtn).not.toBeNull();
        checkBtn.dispatchEvent(new MouseEvent('click', { bubbles: true }));
        const updatedBtn = document.querySelector('.history-check-btn[data-action="toggle-select"]');
        expect(updatedBtn.classList.contains('checked')).toBe(true);
    });

    test('click lần 2 bỏ chọn ảnh', () => {
        hm.addToHistory('https://example.com/img1.png', 'prompt 1');
        let checkBtn = document.querySelector('.history-check-btn[data-action="toggle-select"]');
        checkBtn.dispatchEvent(new MouseEvent('click', { bubbles: true }));
        checkBtn = document.querySelector('.history-check-btn[data-action="toggle-select"]');
        checkBtn.dispatchEvent(new MouseEvent('click', { bubbles: true }));
        const updatedBtn = document.querySelector('.history-check-btn[data-action="toggle-select"]');
        expect(updatedBtn.classList.contains('checked')).toBe(false);
    });

    test('hiện nút deleteSelected khi có ảnh được chọn', () => {
        hm.addToHistory('https://example.com/img1.png', 'prompt 1');
        const checkBtn = document.querySelector('.history-check-btn[data-action="toggle-select"]');
        checkBtn.dispatchEvent(new MouseEvent('click', { bubbles: true }));
        const delBtn = document.getElementById('deleteSelectedHistoryBtn');
        expect(delBtn.classList.contains('hidden')).toBe(false);
    });

    test('selectAllHistoryBtn chọn tất cả', () => {
        hm.addToHistory('https://example.com/img1.png', 'prompt 1');
        hm.addToHistory('https://example.com/img2.png', 'prompt 2');
        const saBtn = document.getElementById('selectAllHistoryBtn');
        saBtn.dispatchEvent(new MouseEvent('click', { bubbles: true }));
        const allChecked = document.querySelectorAll('.history-card.selected');
        expect(allChecked.length).toBe(2);
    });

    test('selectAllHistoryBtn lần 2 bỏ chọn tất cả', () => {
        hm.addToHistory('https://example.com/img1.png', 'prompt 1');
        hm.addToHistory('https://example.com/img2.png', 'prompt 2');
        const saBtn = document.getElementById('selectAllHistoryBtn');
        saBtn.dispatchEvent(new MouseEvent('click', { bubbles: true })); // Chọn tất cả
        saBtn.dispatchEvent(new MouseEvent('click', { bubbles: true })); // Bỏ chọn tất cả
        const allChecked = document.querySelectorAll('.history-card.selected');
        expect(allChecked.length).toBe(0);
    });
});

describe('Xóa lịch sử', () => {
    test('xóa các ảnh đã chọn', () => {
        hm.addToHistory('https://example.com/img1.png', 'prompt 1');
        hm.addToHistory('https://example.com/img2.png', 'prompt 2');

        const checkBtn = document.querySelector('.history-check-btn[data-action="toggle-select"]');
        checkBtn.dispatchEvent(new MouseEvent('click', { bubbles: true }));
        document.getElementById('deleteSelectedHistoryBtn').dispatchEvent(new MouseEvent('click', { bubbles: true }));

        const stored = JSON.parse(localStorage.getItem('aura_ai_history') || '[]');
        expect(stored.length).toBe(1);
    });

    test('xóa tất cả lịch sử', () => {
        hm.addToHistory('https://example.com/img1.png', 'prompt 1');
        hm.addToHistory('https://example.com/img2.png', 'prompt 2');
        document.getElementById('clearHistoryBtn').dispatchEvent(new MouseEvent('click', { bubbles: true }));
        const stored = localStorage.getItem('aura_ai_history');
        expect(stored).toBeNull();
        const grid = document.getElementById('historyGrid');
        expect(grid.innerHTML).toContain('history-empty');
    });

    test('không xóa nếu user hủy confirm', () => {
        window.confirm.mockReturnValue(false);
        hm.addToHistory('https://example.com/img1.png', 'prompt 1');
        const checkBtn = document.querySelector('.history-check-btn[data-action="toggle-select"]');
        checkBtn.dispatchEvent(new MouseEvent('click', { bubbles: true }));
        document.getElementById('deleteSelectedHistoryBtn').dispatchEvent(new MouseEvent('click', { bubbles: true }));
        const stored = JSON.parse(localStorage.getItem('aura_ai_history') || '[]');
        expect(stored.length).toBe(1);
    });
});

describe('Modal Quản lý Lịch sử', () => {
    test('click manageHistoryBtn mở modal', () => {
        hm.addToHistory('https://example.com/img1.png', 'prompt 1');
        document.getElementById('manageHistoryBtn').dispatchEvent(new MouseEvent('click', { bubbles: true }));
        const modal = document.getElementById('historyManagerModal');
        expect(modal.classList.contains('hidden')).toBe(false);
    });

    test('click closeHistoryModalBtn đóng modal', () => {
        document.getElementById('manageHistoryBtn').dispatchEvent(new MouseEvent('click', { bubbles: true }));
        document.getElementById('closeHistoryModalBtn').dispatchEvent(new MouseEvent('click', { bubbles: true }));
        const modal = document.getElementById('historyManagerModal');
        expect(modal.classList.contains('hidden')).toBe(true);
    });

    test('selectAllHistoryModalCb chọn tất cả trong modal', () => {
        hm.addToHistory('https://example.com/img1.png', 'prompt 1');
        hm.addToHistory('https://example.com/img2.png', 'prompt 2');
        document.getElementById('manageHistoryBtn').dispatchEvent(new MouseEvent('click', { bubbles: true }));
        const cb = document.getElementById('selectAllHistoryModalCb');
        cb.checked = true;
        cb.dispatchEvent(new Event('change'));
        const allChecked = document.querySelectorAll('.history-modal-cb:checked');
        expect(allChecked.length).toBe(2);
    });

    test('chọn checkbox trong modal toggle item', () => {
        hm.addToHistory('https://example.com/img1.png', 'prompt 1');
        const itemCb = document.querySelector('.history-modal-cb');
        expect(itemCb).not.toBeNull();
        itemCb.checked = true;
        itemCb.dispatchEvent(new Event('change'));
        expect(hm.getState().selectedIds.size).toBe(1);
    });

    test('nút dùng prompt điền vào promptInput', () => {
        hm.addToHistory('https://example.com/img1.png', 'Dùng prompt này nhé');
        const useBtn = document.querySelector('[data-action="use-prompt"]');
        expect(useBtn).not.toBeNull();
        useBtn.dispatchEvent(new MouseEvent('click', { bubbles: true }));
        expect(document.getElementById('promptInput').value).toBe('Dùng prompt này nhé');
    });

    test('click thumbnail mở preview', () => {
        hm.addToHistory('https://example.com/img1.png', 'prompt 1');
        const img = document.querySelector('.history-modal-thumb');
        img.dispatchEvent(new MouseEvent('click', { bubbles: true }));
        expect(document.getElementById('resultImage').src).toContain('img1.png');
    });
});
