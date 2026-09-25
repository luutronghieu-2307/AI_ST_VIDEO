/**
 * test_storyboard_manager.js – Unit tests cho templates/js/storyboard_manager.js
 */
const fs = require('fs');
const path = require('path');

const SRC = path.join(__dirname, '..', 'templates', 'js', 'storyboard_manager.js');

/* ─── DOM Setup ───────────────────────────────────────────────────────── */
function setupDOM() {
    document.body.innerHTML = `
        <div id="srtUploadZone">
            <input type="file" id="srtFileInput">
            <div id="srtUploadPlaceholder"></div>
            <div id="srtUploadPreview" class="hidden">
                <span id="srtFileName"></span>
            </div>
            <button id="removeSrtBtn"></button>
        </div>
        <div id="audioUploadZone">
            <input type="file" id="audioFileInput">
            <div id="audioUploadPlaceholder"></div>
            <div id="audioUploadPreview" class="hidden">
                <span id="audioFileName"></span>
            </div>
            <button id="removeAudioBtn"></button>
        </div>
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
        
        <!-- Full Merged Video -->
        <div id="fullMergedVideoSection" class="hidden">
            <div id="fullVideoPlayerContainer">
                <video id="fullMergedVideoPlayer"><source src=""></video>
            </div>
            <div id="stitchingLoader" class="hidden"></div>
            <a id="downloadFullVideoBtn"></a>
        </div>

        <div id="storyboardVideoModal" class="hidden">
            <video id="storyboardFullscreenVideo"><source src=""></video>
        </div>
    `;
}

/* ─── Load module ─────────────────────────────────────────────────────── */
let mod;
function loadModule() {
    jest.resetModules();
    setupDOM();
    global.checkAndHandleRateLimit = jest.fn().mockResolvedValue(false);
    global.confirm = jest.fn().mockReturnValue(true);
    global.FileReader = class {
        readAsText(file) {
            setTimeout(() => {
                this.onload({ target: { result: '1\n00:00:00,100 --> 00:00:04,292\nText sample' } });
            }, 0);
        }
    };
    mod = require(SRC);
    return mod;
}

beforeEach(() => {
    loadModule();
});

/* ─── Tests ───────────────────────────────────────────────────────────── */
describe('SRT Upload and Parsing', () => {
    test('handleSrtFile wrong extension', () => {
        mod.handleSrtFile({ name: 'image.png', size: 100 });
        const toast = document.querySelector('.toast-error');
        expect(toast).not.toBeNull();
        expect(toast.textContent).toContain('Chỉ chấp nhận file phụ đề');
    });

    test('handleSrtFile valid srt', async () => {
        const file = { name: 'subtitle.srt', size: 1024 };
        mod.handleSrtFile(file);
        expect(mod.getState().srtFile).toBe(file);
        expect(document.getElementById('srtFileName').textContent).toBe('subtitle.srt');
        await new Promise(r => setTimeout(r, 10));
        expect(document.getElementById('storyboardTextInput').value).toContain('00:00:00,100');
    });

    test('resetSrtUpload', () => {
        mod.handleSrtFile({ name: 'sub.srt', size: 100 });
        mod.resetSrtUpload();
        expect(mod.getState().srtFile).toBeNull();
        expect(document.getElementById('srtUploadPlaceholder').classList.contains('hidden')).toBe(false);
    });

    test('updateInfoFromText', () => {
        document.getElementById('storyboardTextInput').value = `1\n00:00:00,100 --> 00:00:04,292\nHello\n\n2\n00:00:05,000 --> 00:00:09,000\nWorld`;
        mod.updateInfoFromText();
        expect(document.getElementById('infoSegmentCount').textContent).toBe('2 phân đoạn');
    });
});

describe('Audio Upload', () => {
    test('handleAudioFile too large', () => {
        mod.handleAudioFile({ name: 'big.mp3', size: 60 * 1024 * 1024 });
        const toast = document.querySelector('.toast-error');
        expect(toast).not.toBeNull();
        expect(toast.textContent).toContain('quá lớn');
    });

    test('handleAudioFile ok', () => {
        const file = { name: 'voice.mp3', size: 1024 * 1024 };
        mod.handleAudioFile(file);
        expect(mod.getState().audioFile).toBe(file);
        expect(document.getElementById('infoAudioStatus').textContent).toContain('voice.mp3');
    });

    test('resetAudioUpload', () => {
        mod.handleAudioFile({ name: 'v.mp3', size: 100 });
        mod.resetAudioUpload();
        expect(mod.getState().audioFile).toBeNull();
        expect(document.getElementById('infoAudioStatus').textContent).toBe('Không đính kèm');
    });
});

describe('Rendering & UI', () => {
    test('renderSegmentCard with timecode', () => {
        const html = mod.renderSegmentCard({
            id: 'seg_1',
            order: 1,
            text: 'Hello',
            timecode: '00:00:00,100 --> 00:00:04,292',
            duration_sec: 4.19,
            num_frames: 65,
            status: 'completed',
            video_url: 'https://example.com/v.mp4'
        });
        expect(html).toContain('00:00:00,100 --&gt; 00:00:04,292');
        expect(html).toContain('65 frames');
        expect(html).toContain('status-completed');
    });

    test('renderMergedVideoSection when completed with URL', () => {
        mod.renderMergedVideoSection({
            merged_video_url: '/static/merged_videos/sb_1_final.mp4',
            is_stitching: false,
            completed: 2,
            total: 2
        });
        expect(document.getElementById('fullMergedVideoSection').classList.contains('hidden')).toBe(false);
        expect(document.getElementById('downloadFullVideoBtn').href).toContain('sb_1_final.mp4');
    });

    test('renderMergedVideoSection when stitching', () => {
        mod.renderMergedVideoSection({
            merged_video_url: null,
            is_stitching: true,
            completed: 2,
            total: 2
        });
        expect(document.getElementById('stitchingLoader').classList.contains('hidden')).toBe(false);
    });

    test('updateProgress', () => {
        mod.updateProgress({ total: 6, completed: 3 });
        expect(document.getElementById('storyboardProgressBar').style.width).toBe('50%');
        expect(document.getElementById('storyboardProgressText').textContent).toBe('3/6');
    });
});

describe('Toast & Modal', () => {
    test('showToast', () => {
        mod.showToast('Thông báo test', 'success');
        const toast = document.querySelector('.toast-success');
        expect(toast).not.toBeNull();
        expect(toast.textContent).toContain('Thông báo test');
    });

    test('openFullscreen', () => {
        mod.openFullscreen('https://example.com/video.mp4');
        expect(document.getElementById('storyboardVideoModal').classList.contains('hidden')).toBe(false);
    });
});

describe('ReStitch action', () => {
    test('handleReStitch calls api', async () => {
        global.fetch = jest.fn().mockResolvedValue({
            ok: true,
            json: async () => ({ success: true, merged_video_url: '/static/merged_videos/test.mp4' })
        });
        // Set storyboard id
        localStorage.setItem('aura_active_storyboard', 'sb_123');
        mod.resumeActiveStoryboard();
        await new Promise(r => setTimeout(r, 0));

        await mod.handleReStitch();
        expect(global.fetch).toHaveBeenCalled();
    });
});
