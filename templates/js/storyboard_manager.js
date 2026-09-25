/**
 * storyboard_manager.js – Quản lý Storyboard Video Studio (SRT & Audio Muxing)
 */
let _currentStoryboardId = null;
let _pollingInterval = null;
let _audioFile = null;
let _srtFile = null;

const POLL_INTERVAL_MS = 8000;
const STORAGE_KEY = 'aura_active_storyboard';
const MAX_AUDIO_SIZE = 50 * 1024 * 1024;

const SAMPLE_SRT = `1
00:00:00,100 --> 00:00:04,292
Trí tuệ nhân tạo hay AI không phải là một thực thể có ý thức hay suy nghĩ độc lập như con người trong các bộ phim khoa học viễn tưởng

2
00:00:04,850 --> 00:00:08,383
Bản chất của AI thực chất là những thuật toán phức tạp được huấn luyện trên những tập dữ liệu khổng lồ để nhận diện mẫu

3
00:00:08,533 --> 00:00:09,883
dự đoán và tự động hóa các tác vụ

4
00:00:10,458 --> 00:00:14,025
Dù có khả năng xử lý thông tin với tốc độ chóng mặt và tạo ra các sản phẩm nghệ thuật hay văn bản giống con người

5
00:00:14,208 --> 00:00:16,775
AI vẫn hoàn toàn phụ thuộc vào dữ liệu đầu vào và sự định hướng của con người

6
00:00:17,350 --> 00:00:22,092
Hiểu đúng về AI giúp chúng ta tận dụng tối đa sức mạnh của công nghệ này làm công cụ hỗ trợ đắc lực thay vì lo sợ về một viễn cảnh viển vông`;

if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', () => {
        initStoryboardManager();
        resumeActiveStoryboard();
    });
}

function initStoryboardManager() {
    setupSrtUpload();
    setupAudioUpload();

    document.getElementById('pasteSampleSrtBtn')?.addEventListener('click', () => {
        const textInput = document.getElementById('storyboardTextInput');
        const titleInput = document.getElementById('storyboardTitleInput');
        if (textInput) textInput.value = SAMPLE_SRT;
        if (titleInput && !titleInput.value) titleInput.value = 'Khám phá Trí tuệ Nhân tạo';
        updateInfoFromText();
        showToast('Đã nạp phụ đề SRT mẫu!', 'success');
    });

    document.getElementById('storyboardTextInput')?.addEventListener('input', updateInfoFromText);
    document.getElementById('createStoryboardBtn')?.addEventListener('click', handleCreateStoryboard);
    document.getElementById('reStitchBtn')?.addEventListener('click', handleReStitch);

    document.getElementById('closeStoryboardVideoBtn')?.addEventListener('click', () => {
        document.getElementById('storyboardVideoModal')?.classList.add('hidden');
    });
    document.getElementById('storyboardVideoBackdrop')?.addEventListener('click', () => {
        document.getElementById('storyboardVideoModal')?.classList.add('hidden');
    });
}

function setupSrtUpload() {
    const srtZone = document.getElementById('srtUploadZone');
    const srtInput = document.getElementById('srtFileInput');
    srtZone?.addEventListener('click', (e) => {
        if (!e.target.closest('#removeSrtBtn')) srtInput?.click();
    });
    ['dragover', 'dragleave', 'drop'].forEach(evt => {
        srtZone?.addEventListener(evt, (e) => {
            e.preventDefault();
            srtZone.classList.toggle('drag-over', evt === 'dragover');
            if (evt === 'drop' && e.dataTransfer?.files[0]) handleSrtFile(e.dataTransfer.files[0]);
        });
    });
    srtInput?.addEventListener('change', () => {
        if (srtInput.files[0]) handleSrtFile(srtInput.files[0]);
    });
    document.getElementById('removeSrtBtn')?.addEventListener('click', (e) => {
        e.stopPropagation();
        resetSrtUpload();
    });
}

function handleSrtFile(file) {
    if (!file.name.toLowerCase().endsWith('.srt') && !file.name.toLowerCase().endsWith('.txt')) {
        return showToast('Chỉ chấp nhận file phụ đề (.srt)!', 'error');
    }
    _srtFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
        const textInput = document.getElementById('storyboardTextInput');
        if (textInput) textInput.value = e.target.result;
        updateInfoFromText();
    };
    reader.readAsText(file);
    document.getElementById('srtFileName').textContent = file.name;
    document.getElementById('srtUploadPlaceholder')?.classList.add('hidden');
    document.getElementById('srtUploadPreview')?.classList.remove('hidden');
}

function resetSrtUpload() {
    _srtFile = null;
    const input = document.getElementById('srtFileInput');
    if (input) input.value = '';
    document.getElementById('srtUploadPlaceholder')?.classList.remove('hidden');
    document.getElementById('srtUploadPreview')?.classList.add('hidden');
    updateInfoFromText();
}

function setupAudioUpload() {
    const zone = document.getElementById('audioUploadZone');
    const input = document.getElementById('audioFileInput');
    zone?.addEventListener('click', (e) => {
        if (!e.target.closest('#removeAudioBtn')) input?.click();
    });
    ['dragover', 'dragleave', 'drop'].forEach(evt => {
        zone?.addEventListener(evt, (e) => {
            e.preventDefault();
            zone.classList.toggle('drag-over', evt === 'dragover');
            if (evt === 'drop' && e.dataTransfer?.files[0]) handleAudioFile(e.dataTransfer.files[0]);
        });
    });
    input?.addEventListener('change', () => {
        if (input.files[0]) handleAudioFile(input.files[0]);
    });
    document.getElementById('removeAudioBtn')?.addEventListener('click', (e) => {
        e.stopPropagation();
        resetAudioUpload();
    });
}

function handleAudioFile(file) {
    if (file.size > MAX_AUDIO_SIZE) return showToast('File âm thanh quá lớn (tối đa 50MB)!', 'error');
    _audioFile = file;
    document.getElementById('audioFileName').textContent = file.name;
    document.getElementById('audioUploadPlaceholder')?.classList.add('hidden');
    document.getElementById('audioUploadPreview')?.classList.remove('hidden');
    document.getElementById('infoAudioStatus').textContent = `Đã đính kèm (${file.name})`;
}

function resetAudioUpload() {
    _audioFile = null;
    const input = document.getElementById('audioFileInput');
    if (input) input.value = '';
    document.getElementById('audioUploadPlaceholder')?.classList.remove('hidden');
    document.getElementById('audioUploadPreview')?.classList.add('hidden');
    document.getElementById('infoAudioStatus').textContent = 'Không đính kèm';
}

function updateInfoFromText() {
    const text = document.getElementById('storyboardTextInput')?.value || '';
    const timeMatches = text.match(/\d{1,2}:\d{2}:\d{2}[,\.]\d{1,3}\s*-->\s*(\d{1,2}:\d{2}:\d{2}[,\.]\d{1,3})/g) || [];
    const countEl = document.getElementById('infoSegmentCount');
    const durEl = document.getElementById('infoAudioDuration');
    if (countEl) countEl.textContent = timeMatches.length > 0 ? `${timeMatches.length} phân đoạn` : '--';
    if (timeMatches.length > 0) {
        const last = timeMatches[timeMatches.length - 1].split('-->')[1]?.trim();
        if (durEl && last) durEl.textContent = `~${last.split(',')[0]}s`;
    } else if (durEl) {
        durEl.textContent = '--';
    }
}

async function handleCreateStoryboard() {
    const text = document.getElementById('storyboardTextInput')?.value.trim();
    const title = document.getElementById('storyboardTitleInput')?.value.trim();
    const groqKey = document.getElementById('storyboardGroqKeyInput')?.value.trim();
    const modelId = document.getElementById('storyboardModelSelect')?.value;
    const aspect = document.getElementById('storyboardAspectSelect')?.value || '16:9';

    if (!text && !_srtFile) return showToast('Vui lòng nhập phụ đề SRT hoặc tải file .srt!', 'error');
    if (!title) return showToast('Vui lòng nhập tiêu đề storyboard!', 'error');

    const btn = document.getElementById('createStoryboardBtn');
    btn.disabled = true;

    try {
        const formData = new FormData();
        formData.append('title', title);
        if (_srtFile) formData.append('srt_file', _srtFile);
        else formData.append('srt_text', text);
        if (_audioFile) formData.append('audio_file', _audioFile);
        if (groqKey) formData.append('groq_api_key', groqKey);
        if (modelId) formData.append('model_id', modelId);
        formData.append('aspect', aspect);

        const resp = await fetch('/api/storyboard/create', { method: 'POST', body: formData });
        if (await checkAndHandleRateLimit(resp)) return;
        if (!resp.ok) {
            const err = await resp.json().catch(() => ({}));
            throw new Error(err.detail || `Lỗi ${resp.status}`);
        }
        const data = await resp.json();
        _currentStoryboardId = data.storyboard_id;
        localStorage.setItem(STORAGE_KEY, _currentStoryboardId);
        renderTimeline(data);
        startPolling(_currentStoryboardId);
        showToast('Đã bắt đầu tạo và render storyboard!', 'info');
    } catch (err) {
        showToast(`❌ ${err.message}`, 'error');
    } finally {
        btn.disabled = false;
    }
}

function renderTimeline(sb) {
    const grid = document.getElementById('storyboardSegmentGrid');
    const emptyState = document.getElementById('storyboardEmptyState');
    const titleEl = document.getElementById('storyboardTitle');
    if (!grid) return;
    emptyState?.classList.add('hidden');
    if (titleEl) titleEl.textContent = sb.title || 'Storyboard';
    grid.innerHTML = (sb.segments || []).map(renderSegmentCard).join('');
    updateProgress(sb);
    renderMergedVideoSection(sb);
    attachSegmentEvents();
}

function renderMergedVideoSection(sb) {
    const section = document.getElementById('fullMergedVideoSection');
    const playerContainer = document.getElementById('fullVideoPlayerContainer');
    const loader = document.getElementById('stitchingLoader');
    const video = document.getElementById('fullMergedVideoPlayer');
    const downloadBtn = document.getElementById('downloadFullVideoBtn');
    if (!section) return;

    if (sb.merged_video_url) {
        section.classList.remove('hidden');
        loader?.classList.add('hidden');
        playerContainer?.classList.remove('hidden');
        if (video && video.querySelector('source')) {
            if (video.querySelector('source').src !== sb.merged_video_url) {
                video.querySelector('source').src = sb.merged_video_url;
                try { video.load(); } catch (_) {}
            }
        }
        if (downloadBtn) downloadBtn.href = sb.merged_video_url;
    } else if (sb.is_stitching || (sb.completed === sb.total && sb.total > 0)) {
        section.classList.remove('hidden');
        loader?.classList.remove('hidden');
        playerContainer?.classList.add('hidden');
    } else {
        section.classList.add('hidden');
    }
}

function renderSegmentCard(seg) {
    const statusMap = {
        pending: { class: 'status-pending', icon: 'fa-clock', text: 'Chờ xử lý' },
        processing: { class: 'status-processing', icon: 'fa-spinner fa-spin', text: 'Đang tạo' },
        completed: { class: 'status-completed', icon: 'fa-check', text: 'Hoàn thành' },
        failed: { class: 'status-failed', icon: 'fa-xmark', text: 'Thất bại' }
    };
    const st = statusMap[seg.status] || statusMap.pending;
    const videoHtml = seg.video_url
        ? `<video controls preload="metadata" class="segment-video"><source src="${seg.video_url}" type="video/mp4"></video>`
        : `<div class="segment-video-placeholder"><i class="fa-solid fa-film"></i></div>`;

    return `
        <div class="storyboard-segment-card" data-segment-id="${seg.id}">
            <div class="segment-card-header">
                <span class="segment-order">#${seg.order}</span>
                <span class="segment-status-badge ${st.class}">
                    <i class="fa-solid ${st.icon}"></i> ${st.text}
                </span>
            </div>
            ${seg.timecode ? `<div class="segment-timecode-badge"><i class="fa-solid fa-stopwatch"></i> ${escapeHtml(seg.timecode)}</div>` : ''}
            <div class="segment-video-wrapper">${videoHtml}</div>
            <p class="segment-text">${escapeHtml(seg.text)}</p>
            ${seg.error ? `<div class="segment-error-msg" style="color: #ff6b6b; font-size: 0.8rem; margin: 4px 0; background: rgba(255,107,107,0.1); padding: 4px 8px; border-radius: 4px;"><i class="fa-solid fa-circle-exclamation"></i> ${escapeHtml(seg.error)}</div>` : ''}
            <div class="segment-meta">
                <span><i class="fa-solid fa-clock"></i> ${seg.duration_sec}s</span>
                <span><i class="fa-solid fa-film"></i> ${seg.num_frames} frames</span>
            </div>
            <div class="segment-actions">
                <button class="text-btn action-sm" data-action="regenerate" data-segment-id="${seg.id}">
                    <i class="fa-solid fa-rotate"></i> Tạo lại
                </button>
                ${seg.video_url ? `<button class="text-btn action-sm" data-action="fullscreen" data-url="${seg.video_url}"><i class="fa-solid fa-expand"></i></button>` : ''}
            </div>
        </div>`;
}

function updateProgress(sb) {
    const bar = document.getElementById('storyboardProgressBar');
    const text = document.getElementById('storyboardProgressText');
    const pct = sb.total > 0 ? (sb.completed / sb.total) * 100 : 0;
    if (bar) bar.style.width = `${pct}%`;
    if (text) text.textContent = `${sb.completed}/${sb.total}`;
}

function startPolling(id) {
    if (_pollingInterval) clearInterval(_pollingInterval);
    _pollingInterval = setInterval(() => pollStoryboardStatus(id), POLL_INTERVAL_MS);
}

async function pollStoryboardStatus(id) {
    try {
        const resp = await fetch(`/api/storyboard/${id}/status`);
        if (!resp.ok) return;
        const data = await resp.json();
        renderTimeline(data);
        if (data.merged_video_url) {
            clearInterval(_pollingInterval);
            _pollingInterval = null;
            showToast('🎬 Toàn bộ video đã được ghép nối & lồng tiếng hoàn tất!', 'success');
        }
    } catch (e) {
        console.warn('Polling error:', e);
    }
}

function attachSegmentEvents() {
    document.getElementById('storyboardSegmentGrid')?.querySelectorAll('[data-action]').forEach(btn => {
        btn.addEventListener('click', () => {
            if (btn.dataset.action === 'regenerate') handleRegenerateSegment(btn.dataset.segmentId);
            if (btn.dataset.action === 'fullscreen') openFullscreen(btn.dataset.url);
        });
    });
}

async function handleRegenerateSegment(segId) {
    if (!_currentStoryboardId || !confirm('Tạo lại phân đoạn này? Video tổng sẽ tự động cập nhật lại.')) return;
    try {
        const resp = await fetch(`/api/storyboard/${_currentStoryboardId}/segment/${segId}/retry`, { method: 'POST' });
        if (await checkAndHandleRateLimit(resp)) return;
        if (!resp.ok) throw new Error('Lỗi tạo lại phân đoạn');
        showToast('Đang render lại phân đoạn...', 'info');
        startPolling(_currentStoryboardId);
    } catch (err) {
        showToast(`❌ ${err.message}`, 'error');
    }
}

async function handleReStitch() {
    if (!_currentStoryboardId) return;
    try {
        showToast('Đang ghép nối lại video...', 'info');
        const resp = await fetch(`/api/storyboard/${_currentStoryboardId}/stitch`, { method: 'POST' });
        if (!resp.ok) throw new Error('Ghép video không thành công.');
        pollStoryboardStatus(_currentStoryboardId);
        showToast('Ghép nối video thành công!', 'success');
    } catch (err) {
        showToast(`❌ ${err.message}`, 'error');
    }
}

function openFullscreen(url) {
    const video = document.getElementById('storyboardFullscreenVideo');
    if (video) {
        video.querySelector('source').src = url;
        try { video.load(); } catch (_) {}
    }
    document.getElementById('storyboardVideoModal')?.classList.remove('hidden');
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    const icons = { success: 'fa-circle-check', error: 'fa-circle-xmark', warning: 'fa-triangle-exclamation', info: 'fa-circle-info' };
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<i class="fa-solid ${icons[type] || icons.info}"></i><div class="toast-content"><span>${message}</span></div><button class="toast-close"><i class="fa-solid fa-xmark"></i></button>`;
    container.appendChild(toast);
    toast.querySelector('.toast-close')?.addEventListener('click', () => toast.remove());
    setTimeout(() => toast.remove(), 5000);
}

function resumeActiveStoryboard() {
    const activeId = localStorage.getItem(STORAGE_KEY);
    if (!activeId) return;
    fetch(`/api/storyboard/${activeId}`)
        .then(r => r.ok ? r.json() : null)
        .then(data => {
            if (!data) return localStorage.removeItem(STORAGE_KEY);
            _currentStoryboardId = activeId;
            renderTimeline(data);
            if (!data.merged_video_url) startPolling(activeId);
        })
        .catch(() => localStorage.removeItem(STORAGE_KEY));
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str || '';
    return div.innerHTML;
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initStoryboardManager, handleSrtFile, resetSrtUpload,
        handleAudioFile, resetAudioUpload, updateInfoFromText,
        handleCreateStoryboard, renderTimeline, renderSegmentCard,
        renderMergedVideoSection, updateProgress, startPolling,
        pollStoryboardStatus, handleRegenerateSegment, handleReStitch,
        openFullscreen, showToast, resumeActiveStoryboard, escapeHtml,
        getState: () => ({ storyboardId: _currentStoryboardId, srtFile: _srtFile, audioFile: _audioFile })
    };
}
