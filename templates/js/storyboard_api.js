/**
 * storyboard_api.js – API Client cho module Storyboard Video
 */

async function createStoryboardApi(formData) {
    const resp = await fetch('/api/storyboard/create', { method: 'POST', body: formData });
    if (typeof checkAndHandleRateLimit === 'function' && await checkAndHandleRateLimit(resp)) {
        return null;
    }
    if (!resp.ok) {
        const err = await resp.json().catch(() => ({}));
        throw new Error(err.detail || `Lỗi ${resp.status}`);
    }
    return await resp.json();
}

async function fetchStoryboardStatus(id) {
    const resp = await fetch(`/api/storyboard/${id}/status`);
    if (!resp.ok) return null;
    return await resp.json();
}

async function fetchStoryboard(id) {
    const resp = await fetch(`/api/storyboard/${id}`);
    if (!resp.ok) return null;
    return await resp.json();
}

async function regenerateSegmentApi(storyboardId, segmentId) {
    const resp = await fetch(`/api/storyboard/${storyboardId}/segment/${segmentId}/retry`, { method: 'POST' });
    if (typeof checkAndHandleRateLimit === 'function' && await checkAndHandleRateLimit(resp)) {
        return null;
    }
    if (!resp.ok) throw new Error('Lỗi tạo lại phân đoạn');
    return await resp.json();
}

async function reStitchStoryboardApi(storyboardId) {
    const resp = await fetch(`/api/storyboard/${storyboardId}/stitch`, { method: 'POST' });
    if (!resp.ok) throw new Error('Ghép video không thành công.');
    return await resp.json();
}

const StoryboardApi = {
    createStoryboardApi,
    fetchStoryboardStatus,
    fetchStoryboard,
    regenerateSegmentApi,
    reStitchStoryboardApi
};

if (typeof window !== 'undefined') {
    window.StoryboardApi = StoryboardApi;
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = StoryboardApi;
}
