// app.js – Quản lý khởi tạo ảnh, thông số kỹ thuật, tab navigation và preview kết quả
const promptInput = document.getElementById('promptInput');
const randomPromptBtn = document.getElementById('randomPromptBtn');
const advancedToggle = document.getElementById('advancedToggle');
const aspectRatioSelect = document.getElementById('aspectRatioSelect');
const numStepsInput = document.getElementById('numStepsInput');
const stepsVal = document.getElementById('stepsVal');
const seedInput = document.getElementById('seedInput');
const apiKeyInput = document.getElementById('apiKeyInput');
const generateBtn = document.getElementById('generateBtn');

const placeholderState = document.getElementById('placeholderState');
const loadingState = document.getElementById('loadingState');
const imageWrapper = document.getElementById('imageWrapper');
const resultImage = document.getElementById('resultImage');
const downloadBtn = document.getElementById('downloadBtn');
const copyUrlBtn = document.getElementById('copyUrlBtn');
const fullscreenBtn = document.getElementById('fullscreenBtn');

const statusIndicator = document.getElementById('statusIndicator');
const statusDot = statusIndicator?.querySelector('.status-dot');
const statusText = document.getElementById('statusText');

const lightboxModal = document.getElementById('lightboxModal');
const modalImage = document.getElementById('modalImage');
const closeModalBtn = document.getElementById('closeModalBtn');
const modalBackdrop = document.getElementById('modalBackdrop');

document.addEventListener('DOMContentLoaded', () => {
    initNavigationTabs();

    advancedToggle?.addEventListener('click', () => advancedToggle.parentElement?.classList.toggle('active'));
    numStepsInput?.addEventListener('input', (e) => { if (stepsVal) stepsVal.textContent = e.target.value; });

    // Chọn ngẫu nhiên 1 template từ dropdown
    randomPromptBtn?.addEventListener('click', () => {
        const select = document.getElementById('promptTemplateSelect');
        if (select && select.options.length > 1) {
            const randIdx = Math.floor(Math.random() * (select.options.length - 1)) + 1;
            select.selectedIndex = randIdx;
            select.dispatchEvent(new Event('change'));
            if (promptInput) promptInput.value = '';
        }
    });

    // Mẫu phong cách nhanh
    document.querySelectorAll('.chip').forEach(chip => {
        chip.addEventListener('click', () => {
            const prompt = chip.getAttribute('data-prompt');
            const select = document.getElementById('promptTemplateSelect');
            if (select) {
                let found = false;
                for (let i = 0; i < select.options.length; i++) {
                    if (select.options[i].value === prompt) {
                        select.selectedIndex = i;
                        found = true;
                        break;
                    }
                }
                if (!found && prompt) {
                    const opt = document.createElement('option');
                    opt.value = prompt;
                    opt.textContent = chip.textContent.trim();
                    select.appendChild(opt);
                    select.value = prompt;
                }
                select.dispatchEvent(new Event('change'));
                if (promptInput) promptInput.value = '';
            }
        });
    });

    generateBtn?.addEventListener('click', handleGenerate);

    downloadBtn?.addEventListener('click', async () => {
        const url = resultImage?.src;
        if (!url) return;
        try {
            const res = await fetch(url);
            const blob = await res.blob();
            const blobUrl = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = blobUrl; a.download = `aura-logo-${Date.now()}.png`;
            document.body.appendChild(a); a.click(); document.body.removeChild(a);
            URL.revokeObjectURL(blobUrl);
        } catch { window.open(url, '_blank'); }
    });

    copyUrlBtn?.addEventListener('click', () => {
        if (!resultImage?.src) return;
        navigator.clipboard.writeText(resultImage.src).then(() => {
            const orig = copyUrlBtn.innerHTML;
            copyUrlBtn.innerHTML = '<i class="fa-solid fa-check"></i> Đã chép!';
            setTimeout(() => { copyUrlBtn.innerHTML = orig; }, 2000);
        });
    });

    fullscreenBtn?.addEventListener('click', () => {
        if (resultImage?.src) { modalImage.src = resultImage.src; lightboxModal?.classList.remove('hidden'); }
    });
    closeModalBtn?.addEventListener('click', () => lightboxModal?.classList.add('hidden'));
    modalBackdrop?.addEventListener('click', () => lightboxModal?.classList.add('hidden'));
});

/* ─── Tab Navigation (Chuyển đổi Menu chức năng) ────────────────────────── */
function switchView(targetViewId) {
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.target === targetViewId);
    });

    document.querySelectorAll('.view-section').forEach(view => {
        const isMatch = view.id === targetViewId;
        view.classList.toggle('hidden', !isMatch);
        view.classList.toggle('active', isMatch);
    });
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function initNavigationTabs() {
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.dataset.target;
            if (target) switchView(target);
        });
    });

    document.getElementById('goToGenerateViewBtn')?.addEventListener('click', () => {
        switchView('viewGenerate');
    });
}

window.switchView = switchView;

/* ─── Generator Logic ─────────────────────────────────────────────────── */
async function handleGenerate() {
    const customPrompt = promptInput?.value.trim() || '';
    const templateSelect = document.getElementById('promptTemplateSelect');
    const selectedTemplatePrompt = templateSelect ? templateSelect.value : '';

    const prompt = customPrompt || selectedTemplatePrompt;
    if (!prompt) {
        alert('Vui lòng chọn một Template hoặc tự nhập prompt mô tả!');
        promptInput?.focus();
        return;
    }

    const [width, height] = aspectRatioSelect.value.split('x').map(Number);
    const numSteps = parseInt(numStepsInput.value, 10);
    const seedVal = parseInt(seedInput.value, 10);
    const seed = isNaN(seedVal) || seedVal < 0 ? Math.floor(Math.random() * 1000000) : seedVal;
    const customApiKey = apiKeyInput.value.trim();

    setLoadingState(true);
    try {
        let imageUrl = '';
        if (customApiKey) {
            const res = await fetch('https://gateway.pixazo.ai/flux-1-schnell/v1/getData', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-cache', 'Ocp-Apim-Subscription-Key': customApiKey },
                body: JSON.stringify({ prompt, num_steps: numSteps, seed, height, width })
            });
            if (!res.ok) { const err = await res.json().catch(() => ({})); throw new Error(err.message || `Lỗi API (${res.status})`); }
            const data = await res.json();
            imageUrl = data.output;
        } else {
            const res = await fetch('/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt, num_steps: numSteps, seed, height, width })
            });
            if (await checkAndHandleRateLimit(res)) { setLoadingState(false); return; }
            if (!res.ok) { const err = await res.json().catch(() => ({})); throw new Error(err.detail?.message || err.message || 'Lỗi kết nối Backend'); }
            const data = await res.json();
            imageUrl = data.output;
        }

        if (imageUrl) {
            displayResult(imageUrl, prompt);
            if (typeof window.addToHistory === 'function') {
                window.addToHistory(imageUrl, prompt);
            }
        } else { throw new Error('API không trả về link ảnh hợp lệ!'); }
    } catch (err) {
        alert(`❌ Lỗi: ${err.message}`);
        if (statusText) statusText.textContent = 'Thất bại';
        if (statusDot) statusDot.className = 'status-dot';
    } finally {
        setLoadingState(false);
    }
}

function setLoadingState(isLoading) {
    if (generateBtn) generateBtn.disabled = isLoading;
    if (loadingState) loadingState.classList.toggle('hidden', !isLoading);

    if (isLoading) {
        placeholderState?.classList.add('hidden');
        imageWrapper?.classList.add('hidden');
        if (statusText) statusText.textContent = 'Đang xử lý AI...';
        if (statusDot) statusDot.className = 'status-dot loading';
    } else {
        const hasResult = resultImage && resultImage.src && resultImage.src.trim() !== '' && !resultImage.src.endsWith('/');
        placeholderState?.classList.toggle('hidden', Boolean(hasResult));
        imageWrapper?.classList.toggle('hidden', !hasResult);
    }
}

function displayResult(url, prompt) {
    if (resultImage) resultImage.src = url;
    imageWrapper?.classList.remove('hidden');
    placeholderState?.classList.add('hidden');
    loadingState?.classList.add('hidden');
    if (statusText) statusText.textContent = 'Hoàn thành';
    if (statusDot) statusDot.className = 'status-dot active';
}
