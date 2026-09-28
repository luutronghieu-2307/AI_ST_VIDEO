/**
 * test_storyboard_audio_handler.js – Unit tests cho storyboard_audio_handler.js
 *
 * @jest-environment jsdom
 */
const handler = require('../templates/js/storyboard_audio_handler');

function setupDOM() {
    document.body.innerHTML = `
        <div id="srtUploadPlaceholder"></div>
        <div id="srtUploadPreview" class="hidden">
            <span id="srtFileName"></span>
        </div>
        <input type="file" id="srtFileInput">
        <div id="audioUploadPlaceholder"></div>
        <div id="audioUploadPreview" class="hidden">
            <span id="audioFileName"></span>
        </div>
        <input type="file" id="audioFileInput">
        <textarea id="storyboardTextInput"></textarea>
        <div id="infoAudioDuration"></div>
        <div id="infoSegmentCount"></div>
        <div id="infoAudioStatus"></div>
    `;
}

describe('Storyboard Audio & SRT Handler', () => {
    beforeEach(() => {
        setupDOM();
        global.FileReader = class {
            readAsText(file) {
                setTimeout(() => {
                    this.onload({ target: { result: '1\n00:00:00,100 --> 00:00:04,292\nText sample' } });
                }, 0);
            }
        };
    });

    test('handleSrtFile từ chối định dạng sai', () => {
        const toastMock = jest.fn();
        const res = handler.handleSrtFile({ name: 'image.png', size: 100 }, toastMock);
        expect(res).toBeNull();
        expect(toastMock).toHaveBeenCalledWith(expect.stringContaining('Chỉ chấp nhận file phụ đề'), 'error');
    });

    test('handleSrtFile đọc file .srt hợp lệ', async () => {
        const file = { name: 'subtitle.srt', size: 1024 };
        const res = handler.handleSrtFile(file);
        expect(res).toBe(file);
        expect(document.getElementById('srtFileName').textContent).toBe('subtitle.srt');
        await new Promise(r => setTimeout(r, 10));
        expect(document.getElementById('storyboardTextInput').value).toContain('00:00:00,100');
    });

    test('resetSrtUpload reset UI và input', () => {
        handler.handleSrtFile({ name: 'sub.srt', size: 100 });
        const res = handler.resetSrtUpload();
        expect(res).toBeNull();
        expect(document.getElementById('srtUploadPlaceholder').classList.contains('hidden')).toBe(false);
    });

    test('handleAudioFile từ chối file > 50MB', () => {
        const toastMock = jest.fn();
        const res = handler.handleAudioFile({ name: 'big.mp3', size: 60 * 1024 * 1024 }, toastMock);
        expect(res).toBeNull();
        expect(toastMock).toHaveBeenCalledWith(expect.stringContaining('quá lớn'), 'error');
    });

    test('handleAudioFile chấp nhận file audio hợp lệ', () => {
        const file = { name: 'voice.mp3', size: 1024 * 1024 };
        const res = handler.handleAudioFile(file);
        expect(res).toBe(file);
        expect(document.getElementById('infoAudioStatus').textContent).toContain('voice.mp3');
    });

    test('resetAudioUpload reset audio state & UI', () => {
        handler.handleAudioFile({ name: 'v.mp3', size: 100 });
        const res = handler.resetAudioUpload();
        expect(res).toBeNull();
        expect(document.getElementById('infoAudioStatus').textContent).toBe('Không đính kèm');
    });

    test('updateInfoFromText cập nhật số phân đoạn và thời lượng', () => {
        document.getElementById('storyboardTextInput').value = `1\n00:00:00,100 --> 00:00:04,292\nHello\n\n2\n00:00:05,000 --> 00:00:09,000\nWorld`;
        handler.updateInfoFromText();
        expect(document.getElementById('infoSegmentCount').textContent).toBe('2 phân đoạn');
    });
});
