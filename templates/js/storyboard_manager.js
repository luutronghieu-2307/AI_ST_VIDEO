/**
 * storyboard_manager.js – Điều phối Storyboard Video Studio
 */
const api = (typeof StoryboardApi !== 'undefined') ? StoryboardApi : (typeof require !== 'undefined' ? require('./storyboard_api') : {});
const ui = (typeof StoryboardUI !== 'undefined') ? StoryboardUI : (typeof require !== 'undefined' ? require('./storyboard_ui') : {});
const audioHandler = (typeof StoryboardAudioHandler !== 'undefined') ? StoryboardAudioHandler : (typeof require !== 'undefined' ? require('./storyboard_audio_handler') : {});

let _currentStoryboardId = null;
let _pollingInterval = null;
let _audioFile = null;
let _srtFile = null;

const POLL_INTERVAL_MS = 8000;
const STORAGE_KEY = 'aura_active_storyboard';

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
        if (textInput) textInput.value = audioHandler.SAMPLE_SRT;
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
    const res = audioHandler.handleSrtFile ? audioHandler.handleSrtFile(file, showToast) : file;
    if (res) _srtFile = res;
    return res;
}

function resetSrtUpload() {
    _srtFile = audioHandler.resetSrtUpload ? audioHandler.resetSrtUpload() : null;
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
    const res = audioHandler.handleAudioFile ? audioHandler.handleAudioFile(file, showToast) : file;
    if (res) _audioFile = res;
    return res;
}

function resetAudioUpload() {
    _audioFile = audioHandler.resetAudioUpload ? audioHandler.resetAudioUpload() : null;
}

function updateInfoFromText() {
    if (audioHandler.updateInfoFromText) audioHandler.updateInfoFromText();
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

        const data = await (api.createStoryboardApi ? api.createStoryboardApi(formData) : null);
        if (!data) return;
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
    ui.renderTimeline(sb, attachSegmentEvents);
}

function startPolling(id) {
    if (_pollingInterval) clearInterval(_pollingInterval);
    _pollingInterval = setInterval(() => pollStoryboardStatus(id), POLL_INTERVAL_MS);
}

async function pollStoryboardStatus(id) {
    try {
        const data = await (api.fetchStoryboardStatus ? api.fetchStoryboardStatus(id) : null);
        if (!data) return;
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
        await (api.regenerateSegmentApi ? api.regenerateSegmentApi(_currentStoryboardId, segId) : null);
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
        await (api.reStitchStoryboardApi ? api.reStitchStoryboardApi(_currentStoryboardId) : null);
        pollStoryboardStatus(_currentStoryboardId);
        showToast('Ghép nối video thành công!', 'success');
    } catch (err) {
        showToast(`❌ ${err.message}`, 'error');
    }
}

function resumeActiveStoryboard() {
    const activeId = localStorage.getItem(STORAGE_KEY);
    if (!activeId) return;
    (api.fetchStoryboard ? api.fetchStoryboard(activeId) : fetch(`/api/storyboard/${activeId}`).then(r => r.ok ? r.json() : null))
        .then(data => {
            if (!data) return localStorage.removeItem(STORAGE_KEY);
            _currentStoryboardId = activeId;
            renderTimeline(data);
            if (!data.merged_video_url) startPolling(activeId);
        })
        .catch(() => localStorage.removeItem(STORAGE_KEY));
}

// Shortcuts for UI helpers
const showToast = ui.showToast || function() {};
const openFullscreen = ui.openFullscreen || function() {};
const renderSegmentCard = ui.renderSegmentCard || function() {};
const renderMergedVideoSection = ui.renderMergedVideoSection || function() {};
const updateProgress = ui.updateProgress || function() {};
const escapeHtml = ui.escapeHtml || function() {};

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
