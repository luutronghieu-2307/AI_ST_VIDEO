/**
 * test_storyboard_ui.js – Unit tests cho storyboard_ui.js
 *
 * @jest-environment jsdom
 */
const ui = require('../templates/js/storyboard_ui');

function setupDOM() {
    document.body.innerHTML = `
        <div id="toastContainer"></div>
        <div id="storyboardVideoModal" class="hidden">
            <video id="storyboardFullscreenVideo"><source src=""></video>
        </div>
        <div id="storyboardProgressBar"></div>
        <span id="storyboardProgressText"></span>
        <div id="fullMergedVideoSection" class="hidden">
            <div id="fullVideoPlayerContainer">
                <video id="fullMergedVideoPlayer"><source src=""></video>
            </div>
            <div id="stitchingLoader" class="hidden"></div>
            <a id="downloadFullVideoBtn"></a>
        </div>
        <div id="storyboardSegmentGrid"></div>
        <div id="storyboardEmptyState"></div>
        <span id="storyboardTitle"></span>
    `;
}

describe('Storyboard UI Module', () => {
    beforeEach(() => {
        setupDOM();
    });

    test('renderSegmentCard với timecode và status completed', () => {
        const html = ui.renderSegmentCard({
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

    test('renderMergedVideoSection hiển thị player khi có video_url', () => {
        ui.renderMergedVideoSection({
            merged_video_url: '/static/merged_videos/sb_1_final.mp4',
            is_stitching: false,
            completed: 2,
            total: 2
        });
        expect(document.getElementById('fullMergedVideoSection').classList.contains('hidden')).toBe(false);
        expect(document.getElementById('downloadFullVideoBtn').href).toContain('sb_1_final.mp4');
    });

    test('renderMergedVideoSection hiển thị loader khi đang stitching', () => {
        ui.renderMergedVideoSection({
            merged_video_url: null,
            is_stitching: true,
            completed: 2,
            total: 2
        });
        expect(document.getElementById('stitchingLoader').classList.contains('hidden')).toBe(false);
    });

    test('updateProgress tính toán thanh tiến trình', () => {
        ui.updateProgress({ total: 6, completed: 3 });
        expect(document.getElementById('storyboardProgressBar').style.width).toBe('50%');
        expect(document.getElementById('storyboardProgressText').textContent).toBe('3/6');
    });

    test('showToast hiển thị thông báo toast', () => {
        ui.showToast('Thông báo test', 'success');
        const toast = document.querySelector('.toast-success');
        expect(toast).not.toBeNull();
        expect(toast.textContent).toContain('Thông báo test');
    });

    test('openFullscreen mở modal xem video', () => {
        ui.openFullscreen('https://example.com/video.mp4');
        expect(document.getElementById('storyboardVideoModal').classList.contains('hidden')).toBe(false);
    });

    test('renderTimeline render danh sách phân đoạn', () => {
        const seg = { id: 's1', order: 1, text: 'Sample', status: 'pending', num_frames: 33, duration_sec: 2 };
        const callback = jest.fn();
        ui.renderTimeline({ title: 'Kịch bản A', segments: [seg], completed: 0, total: 1 }, callback);
        expect(document.getElementById('storyboardTitle').textContent).toBe('Kịch bản A');
        expect(callback).toHaveBeenCalled();
    });
});
