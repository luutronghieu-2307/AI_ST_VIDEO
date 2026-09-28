/**
 * storyboard_ui.js – Giao diện & Render UI cho Storyboard Video Studio
 */

function escapeHtml(str) {
    if (typeof document === 'undefined') return str || '';
    const div = document.createElement('div');
    div.textContent = str || '';
    return div.innerHTML;
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    const icons = {
        success: 'fa-circle-check',
        error: 'fa-circle-xmark',
        warning: 'fa-triangle-exclamation',
        info: 'fa-circle-info'
    };
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<i class="fa-solid ${icons[type] || icons.info}"></i><div class="toast-content"><span>${message}</span></div><button class="toast-close"><i class="fa-solid fa-xmark"></i></button>`;
    container.appendChild(toast);
    toast.querySelector('.toast-close')?.addEventListener('click', () => toast.remove());
    setTimeout(() => toast.remove(), 5000);
}

function openFullscreen(url) {
    const video = document.getElementById('storyboardFullscreenVideo');
    if (video) {
        video.querySelector('source').src = url;
        try { video.load(); } catch (_) {}
    }
    document.getElementById('storyboardVideoModal')?.classList.remove('hidden');
}

function updateProgress(sb) {
    const bar = document.getElementById('storyboardProgressBar');
    const text = document.getElementById('storyboardProgressText');
    const pct = sb.total > 0 ? (sb.completed / sb.total) * 100 : 0;
    if (bar) bar.style.width = `${pct}%`;
    if (text) text.textContent = `${sb.completed}/${sb.total}`;
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

function renderTimeline(sb, onAttachEvents) {
    const grid = document.getElementById('storyboardSegmentGrid');
    const emptyState = document.getElementById('storyboardEmptyState');
    const titleEl = document.getElementById('storyboardTitle');
    if (!grid) return;
    emptyState?.classList.add('hidden');
    if (titleEl) titleEl.textContent = sb.title || 'Storyboard';
    grid.innerHTML = (sb.segments || []).map(renderSegmentCard).join('');
    updateProgress(sb);
    renderMergedVideoSection(sb);
    if (typeof onAttachEvents === 'function') {
        onAttachEvents();
    }
}

const StoryboardUI = {
    escapeHtml,
    showToast,
    openFullscreen,
    updateProgress,
    renderSegmentCard,
    renderMergedVideoSection,
    renderTimeline
};

if (typeof window !== 'undefined') {
    window.StoryboardUI = StoryboardUI;
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = StoryboardUI;
}
