/**
 * test_storyboard_api.js – Unit tests cho templates/js/storyboard_api.js
 */
const api = require('../templates/js/storyboard_api');

describe('Storyboard API Client', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    test('createStoryboardApi success', async () => {
        global.fetch = jest.fn().mockResolvedValue({
            ok: true,
            json: async () => ({ storyboard_id: 'sb_123', status: 'pending' })
        });
        global.checkAndHandleRateLimit = jest.fn().mockResolvedValue(false);

        const formData = new FormData();
        const res = await api.createStoryboardApi(formData);
        expect(res.storyboard_id).toBe('sb_123');
        expect(global.fetch).toHaveBeenCalledWith('/api/storyboard/create', expect.objectContaining({ method: 'POST' }));
    });

    test('createStoryboardApi rate limited', async () => {
        global.fetch = jest.fn().mockResolvedValue({ ok: false, status: 429 });
        global.checkAndHandleRateLimit = jest.fn().mockResolvedValue(true);

        const res = await api.createStoryboardApi(new FormData());
        expect(res).toBeNull();
    });

    test('createStoryboardApi error', async () => {
        global.fetch = jest.fn().mockResolvedValue({
            ok: false,
            status: 400,
            json: async () => ({ detail: 'Dữ liệu không hợp lệ' })
        });
        global.checkAndHandleRateLimit = jest.fn().mockResolvedValue(false);

        await expect(api.createStoryboardApi(new FormData())).rejects.toThrow('Dữ liệu không hợp lệ');
    });

    test('fetchStoryboardStatus success and error', async () => {
        global.fetch = jest.fn()
            .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'completed' }) })
            .mockResolvedValueOnce({ ok: false, status: 404 });

        const ok = await api.fetchStoryboardStatus('sb_1');
        expect(ok.status).toBe('completed');

        const fail = await api.fetchStoryboardStatus('sb_2');
        expect(fail).toBeNull();
    });

    test('fetchStoryboard success and error', async () => {
        global.fetch = jest.fn()
            .mockResolvedValueOnce({ ok: true, json: async () => ({ storyboard_id: 'sb_1' }) })
            .mockResolvedValueOnce({ ok: false, status: 404 });

        const ok = await api.fetchStoryboard('sb_1');
        expect(ok.storyboard_id).toBe('sb_1');

        const fail = await api.fetchStoryboard('sb_2');
        expect(fail).toBeNull();
    });

    test('regenerateSegmentApi success, rate limit, and error', async () => {
        global.fetch = jest.fn()
            .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'processing' }) })
            .mockResolvedValueOnce({ ok: false, status: 429 })
            .mockResolvedValueOnce({ ok: false, status: 500 });
        global.checkAndHandleRateLimit = jest.fn()
            .mockResolvedValueOnce(false)
            .mockResolvedValueOnce(true)
            .mockResolvedValueOnce(false);

        const ok = await api.regenerateSegmentApi('sb_1', 'seg_1');
        expect(ok.status).toBe('processing');

        const limited = await api.regenerateSegmentApi('sb_1', 'seg_1');
        expect(limited).toBeNull();

        await expect(api.regenerateSegmentApi('sb_1', 'seg_1')).rejects.toThrow('Lỗi tạo lại phân đoạn');
    });

    test('reStitchStoryboardApi success and error', async () => {
        global.fetch = jest.fn()
            .mockResolvedValueOnce({ ok: true, json: async () => ({ merged_video_url: '/v.mp4' }) })
            .mockResolvedValueOnce({ ok: false, status: 500 });

        const ok = await api.reStitchStoryboardApi('sb_1');
        expect(ok.merged_video_url).toBe('/v.mp4');

        await expect(api.reStitchStoryboardApi('sb_1')).rejects.toThrow('Ghép video không thành công.');
    });
});
