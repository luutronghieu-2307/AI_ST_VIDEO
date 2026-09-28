/**
 * test_history_store.js – Unit tests cho templates/js/history_store.js
 *
 * @jest-environment jsdom
 */

const Store = require('../templates/js/history_store');

describe('history_store module', () => {
    let mockStorage = {};

    beforeEach(() => {
        mockStorage = {};
        Object.defineProperty(window, 'localStorage', {
            value: {
                getItem: (k) => mockStorage[k] || null,
                setItem: (k, v) => { mockStorage[k] = String(v); },
                removeItem: (k) => { delete mockStorage[k]; },
                clear: () => { mockStorage = {}; }
            },
            writable: true
        });
    });

    test('loadHistory trả về mảng rỗng khi không có dữ liệu hoặc json lỗi', () => {
        expect(Store.loadHistory()).toEqual([]);
        mockStorage['aura_ai_history'] = '{invalid json}';
        expect(Store.loadHistory()).toEqual([]);
    });

    test('loadHistory gán ID mặc định nếu item thiếu ID', () => {
        mockStorage['aura_ai_history'] = JSON.stringify([{ url: 'http://test.png' }]);
        const items = Store.loadHistory();
        expect(items.length).toBe(1);
        expect(items[0].id).toContain('hist_');
        expect(items[0].timestamp).toBe('Gần đây');
    });

    test('saveHistory lưu JSON vào localStorage và bắt lỗi nếu quota full', () => {
        const spyWarn = jest.spyOn(console, 'warn').mockImplementation(() => {});
        Store.saveHistory([{ id: '1', url: 'test' }]);
        expect(mockStorage['aura_ai_history']).toContain('test');

        // Test exception branch
        window.localStorage.setItem = () => { throw new Error('Quota exceeded'); };
        Store.saveHistory([]);
        expect(spyWarn).toHaveBeenCalled();
        spyWarn.mockRestore();
    });

    test('createHistoryItem trả về null nếu url rỗng', () => {
        expect(Store.createHistoryItem('', 'prompt')).toBeNull();
    });

    test('addHistoryItem thêm phần tử và giới hạn MAX_HISTORY = 25', () => {
        let history = [];
        for (let i = 0; i < 30; i++) {
            history = Store.addHistoryItem(history, `http://img${i}.png`, `p${i}`);
        }
        expect(history.length).toBe(25);
        expect(history[0].prompt).toBe('p29');

        // Thêm với url rỗng không làm thay đổi history
        expect(Store.addHistoryItem(history, '', 'abc')).toBe(history);
    });

    test('removeHistoryByIds lọc bỏ các ID được chỉ định', () => {
        const history = [
            { id: '1', url: 'u1' },
            { id: '2', url: 'u2' },
            { id: '3', url: 'u3' }
        ];
        const res = Store.removeHistoryByIds(history, new Set(['1', '3']));
        expect(res.map(i => i.id)).toEqual(['2']);
    });

    test('clearAllHistory xóa key localStorage', () => {
        mockStorage['aura_ai_history'] = 'data';
        Store.clearAllHistory();
        expect(mockStorage['aura_ai_history']).toBeUndefined();

        const spyWarn = jest.spyOn(console, 'warn').mockImplementation(() => {});
        window.localStorage.removeItem = () => { throw new Error('Storage error'); };
        Store.clearAllHistory();
        expect(spyWarn).toHaveBeenCalled();
        spyWarn.mockRestore();
    });
});
