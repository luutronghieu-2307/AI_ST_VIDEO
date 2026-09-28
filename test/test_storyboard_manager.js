/**
 * test_storyboard_manager.js – Unit tests cho templates/js/storyboard_manager.js
 *
 * @jest-environment jsdom
 */
const path = require('path');
const SRC = path.join(__dirname, '..', 'templates', 'js', 'storyboard_manager.js');

function setupDOM() {
    document.body.innerHTML = `
        <div id="srtUploadZone"><input type="file" id="srtFileInput"></div>
        <div id="audioUploadZone"><input type="file" id="audioFileInput"></div>
        <textarea id="storyboardTextInput"></textarea>
        <input id="storyboardTitleInput">
        <input id="storyboardGroqKeyInput">
        <select id="storyboardModelSelect"><option value="openai/gpt-oss-120b"></option></select>
        <select id="storyboardAspectSelect"><option value="16:9"></option></select>
        <button id="pasteSampleSrtBtn"></button>
        <button id="createStoryboardBtn"></button>
        <button id="reStitchBtn"></button>
        <div id="infoAudioDuration"></div>
        <div id="infoSegmentCount"></div>
        <div id="infoAudioStatus"></div>
        <div id="storyboardSegmentGrid"></div>
        <div id="storyboardEmptyState"></div>
        <span id="storyboardTitle"></span>
        <div id="storyboardProgressBar"></div>
        <span id="storyboardProgressText"></span>
        <div id="toastContainer"></div>
        <div id="fullMergedVideoSection" class="hidden">
            <div id="fullVideoPlayerContainer"><video id="fullMergedVideoPlayer"><source src=""></video></div>
            <div id="stitchingLoader" class="hidden"></div>
            <a id="downloadFullVideoBtn"></a>
        </div>
        <div id="storyboardVideoModal" class="hidden">
            <video id="storyboardFullscreenVideo"><source src=""></video>
        </div>
        <div id="closeStoryboardVideoBtn"></div>
        <div id="storyboardVideoBackdrop"></div>
    `;
}

let mod;
function loadModule() {
    jest.resetModules();
    setupDOM();
    global.checkAndHandleRateLimit = jest.fn().mockResolvedValue(false);
    global.confirm = jest.fn().mockReturnValue(true);
    mod = require(SRC);
    return mod;
}

beforeEach(() => {
    localStorage.clear();
    loadModule();
});

describe('Storyboard Manager Controller', () => {
    test('init and paste sample SRT', () => {
        mod.initStoryboardManager();
        document.getElementById('pasteSampleSrtBtn').click();
        expect(document.getElementById('storyboardTextInput').value).toContain('Trí tuệ nhân tạo');
        expect(document.getElementById('storyboardTitleInput').value).toBe('Khám phá Trí tuệ Nhân tạo');
    });

    test('handleCreateStoryboard validation error when empty', async () => {
        await mod.handleCreateStoryboard();
        expect(document.querySelector('.toast-error')).not.toBeNull();
    });

    test('handleCreateStoryboard success', async () => {
        document.getElementById('storyboardTextInput').value = '1\n00:00:00,000 --> 00:00:02,000\nHi';
        document.getElementById('storyboardTitleInput').value = 'Title Test';
        
        global.fetch = jest.fn().mockResolvedValue({
            ok: true,
            json: async () => ({
                storyboard_id: 'sb_test',
                title: 'Title Test',
                segments: []
            })
        });

        await mod.handleCreateStoryboard();
        expect(mod.getState().storyboardId).toBe('sb_test');
        expect(localStorage.getItem('aura_active_storyboard')).toBe('sb_test');
    });

    test('handleRegenerateSegment and pollStoryboardStatus', async () => {
        global.fetch = jest.fn().mockResolvedValue({
            ok: true,
            json: async () => ({
                storyboard_id: 'sb_123',
                title: 'Test',
                merged_video_url: '/v.mp4',
                segments: []
            })
        });

        localStorage.setItem('aura_active_storyboard', 'sb_123');
        mod.resumeActiveStoryboard();
        await new Promise(r => setTimeout(r, 0));

        await mod.handleRegenerateSegment('seg_1');
        await mod.pollStoryboardStatus('sb_123');
        expect(document.querySelector('.toast-success')).not.toBeNull();
    });

    test('handleReStitch calls api', async () => {
        global.fetch = jest.fn().mockResolvedValue({
            ok: true,
            json: async () => ({ success: true, merged_video_url: '/static/merged_videos/test.mp4' })
        });
        localStorage.setItem('aura_active_storyboard', 'sb_123');
        mod.resumeActiveStoryboard();
        await new Promise(r => setTimeout(r, 0));

        await mod.handleReStitch();
        expect(global.fetch).toHaveBeenCalled();
    });

    test('close modal buttons and backdrop', () => {
        mod.initStoryboardManager();
        const modal = document.getElementById('storyboardVideoModal');
        modal.classList.remove('hidden');
        document.getElementById('closeStoryboardVideoBtn').click();
        expect(modal.classList.contains('hidden')).toBe(true);

        modal.classList.remove('hidden');
        document.getElementById('storyboardVideoBackdrop').click();
        expect(modal.classList.contains('hidden')).toBe(true);
    });

    test('attachSegmentEvents triggers action buttons', () => {
        const seg = { id: 'seg_1', order: 1, text: 'Hello', status: 'completed', video_url: 'https://v.mp4', num_frames: 65, duration_sec: 4.0 };
        mod.renderTimeline({ title: 'Test', segments: [seg], completed: 1, total: 1 });
        
        const fullscreenBtn = document.querySelector('[data-action="fullscreen"]');
        expect(fullscreenBtn).not.toBeNull();
        fullscreenBtn.click();
        expect(document.getElementById('storyboardVideoModal').classList.contains('hidden')).toBe(false);
    });
});
