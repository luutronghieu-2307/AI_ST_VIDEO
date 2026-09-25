/**
 * test_storyboard_history.js – Unit tests cho templates/js/storyboard_history.js
 */
const fs = require('fs');
const path = require('path');

const SRC = path.join(__dirname, '..', 'templates', 'js', 'storyboard_history.js');

function setupDOM() {
    document.body.innerHTML = `<div id="storyboardHistoryList"></div>`;
}

let mod;
function loadModule() {
    jest.resetModules();
    setupDOM();
    global.confirm = jest.fn().mockReturnValue(true);
    global.alert = jest.fn();
    mod = require(SRC);
    return mod;
}

beforeEach(() => {
    localStorage.clear();
    loadModule();
});

describe('loadStoryboardHistory', () => {
    test('test_load_empty_history', () => {
        expect(mod.loadStoryboardHistory()).toEqual([]);
    });

    test('test_load_corrupt_history', () => {
        localStorage.setItem('aura_storyboard_history', '{bad json');
        expect(mod.loadStoryboardHistory()).toEqual([]);
    });

    test('test_load_normalizes_items', () => {
        localStorage.setItem(
            'aura_storyboard_history',
            JSON.stringify([{ storyboardId: 'sb-1' }])
        );
        const result = mod.loadStoryboardHistory();
        expect(result[0].title).toBe('Không có tiêu đề');
        expect(result[0].status).toBe('pending');
    });
});

describe('addStoryboardToHistory', () => {
    test('test_add_storyboard_ok', () => {
        mod.addStoryboardToHistory({
            storyboard_id: 'sb-1', title: 'T1', total: 5, completed: 0, status: 'pending'
        });
        const { history } = mod.getState();
        expect(history.length).toBe(1);
        expect(history[0].storyboardId).toBe('sb-1');
    });

    test('test_add_duplicate_replaces', () => {
        mod.addStoryboardToHistory({ storyboard_id: 'sb-1', title: 'Old', total: 1 });
        mod.addStoryboardToHistory({ storyboard_id: 'sb-1', title: 'New', total: 2 });
        const { history } = mod.getState();
        expect(history.length).toBe(1);
        expect(history[0].title).toBe('New');
    });

    test('test_add_exceeds_max', () => {
        for (let i = 0; i < 25; i++) {
            mod.addStoryboardToHistory({ storyboard_id: `sb-${i}`, title: `T${i}` });
        }
        expect(mod.getState().history.length).toBe(20);
    });

    test('test_add_ignores_invalid', () => {
        mod.addStoryboardToHistory(null);
        mod.addStoryboardToHistory({});
        expect(mod.getState().history.length).toBe(0);
    });
});

describe('updateStoryboardInHistory', () => {
    test('test_update_in_history', () => {
        mod.addStoryboardToHistory({ storyboard_id: 'sb-1', title: 'T', total: 5, completed: 0 });
        mod.updateStoryboardInHistory({ storyboard_id: 'sb-1', completed: 3, status: 'processing' });
        const item = mod.getState().history[0];
        expect(item.completed).toBe(3);
        expect(item.status).toBe('processing');
    });

    test('test_update_not_found', () => {
        mod.addStoryboardToHistory({ storyboard_id: 'sb-1', title: 'T', total: 5 });
        mod.updateStoryboardInHistory({ storyboard_id: 'nope', completed: 9 });
        expect(mod.getState().history[0].completed).toBe(0);
    });
});

describe('renderStoryboardHistory', () => {
    test('test_render_empty', () => {
        mod.setState([]);
        mod.renderStoryboardHistory();
        expect(document.getElementById('storyboardHistoryList').innerHTML)
            .toContain('Chưa có storyboard nào');
    });

    test('test_render_with_items', () => {
        mod.setState([{
            id: 'h1', storyboardId: 'sb-1', title: 'My SB',
            total: 10, completed: 5, status: 'processing', createdAt: 'now'
        }]);
        mod.renderStoryboardHistory();
        const html = document.getElementById('storyboardHistoryList').innerHTML;
        expect(html).toContain('My SB');
        expect(html).toContain('5/10 video');
        expect(html).toContain('width: 50%');
    });
});

describe('deleteStoryboardFromHistory', () => {
    test('test_delete_storyboard', () => {
        mod.setState([{ id: 'h1', storyboardId: 'sb-1', title: 'T' }]);
        mod.deleteStoryboardFromHistory('h1');
        expect(mod.getState().history.length).toBe(0);
    });

    test('test_delete_cancelled', () => {
        global.confirm = jest.fn().mockReturnValue(false);
        mod.setState([{ id: 'h1', storyboardId: 'sb-1', title: 'T' }]);
        mod.deleteStoryboardFromHistory('h1');
        expect(mod.getState().history.length).toBe(1);
    });
});

describe('clearStoryboardHistory', () => {
    test('test_clear_all', () => {
        mod.setState([{ id: 'h1', storyboardId: 'sb-1', title: 'T' }]);
        mod.clearStoryboardHistory();
        expect(mod.getState().history.length).toBe(0);
        expect(localStorage.getItem('aura_storyboard_history')).toBeNull();
    });

    test('test_clear_cancelled', () => {
        global.confirm = jest.fn().mockReturnValue(false);
        mod.setState([{ id: 'h1', storyboardId: 'sb-1', title: 'T' }]);
        mod.clearStoryboardHistory();
        expect(mod.getState().history.length).toBe(1);
    });

    test('test_clear_empty_noop', () => {
        mod.setState([]);
        mod.clearStoryboardHistory();
        expect(global.confirm).not.toHaveBeenCalled();
    });
});

describe('loadStoryboardFromHistory', () => {
    test('test_load_storyboard_from_history', async () => {
        global.fetch = jest.fn().mockResolvedValue({
            ok: true,
            json: async () => ({ storyboard_id: 'sb-1', status: 'pending' })
        });
        window.switchView = jest.fn();
        window.renderTimeline = jest.fn();
        window.startPolling = jest.fn();

        mod.loadStoryboardFromHistory('sb-1');
        await new Promise(r => setTimeout(r, 0));

        expect(global.fetch).toHaveBeenCalledWith('/api/storyboard/sb-1');
        expect(window.switchView).toHaveBeenCalledWith('viewStoryboard');
        expect(window.renderTimeline).toHaveBeenCalled();
        expect(window.startPolling).toHaveBeenCalledWith('sb-1');
    });

    test('test_load_storyboard_not_found', async () => {
        global.fetch = jest.fn().mockResolvedValue({ ok: false });
        mod.loadStoryboardFromHistory('nope');
        await new Promise(r => setTimeout(r, 0));
        expect(global.alert).toHaveBeenCalled();
    });

    test('test_load_storyboard_no_id', () => {
        global.fetch = jest.fn();
        mod.loadStoryboardFromHistory('');
        expect(global.fetch).not.toHaveBeenCalled();
    });
});

describe('escapeHtml', () => {
    test('test_escape_html', () => {
        expect(mod.escapeHtml('<b>x</b>')).not.toContain('<');
        expect(mod.escapeHtml('')).toBe('');
    });
});
