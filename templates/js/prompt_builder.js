/**
 * prompt_builder.js – AI Prompt Builder (Phân tích ảnh & tạo template với Groq Vision + GPT-120B)
 */
const MAX_FILE_SIZE = 5 * 1024 * 1024;
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];
let _currentImageBase64 = '', _currentImageMime = '';

document.addEventListener('DOMContentLoaded', () => {
    initPromptBuilder();
    loadGroqModels();
});

function initPromptBuilder() {
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('imageFileInput');
    const groqKeyIn = document.getElementById('groqApiKeyInput');

    uploadZone?.addEventListener('click', (e) => {
        if (!e.target.closest('#removeImageBtn')) fileInput?.click();
    });

    ['dragover', 'dragleave', 'drop'].forEach(evt => {
        uploadZone?.addEventListener(evt, (e) => {
            e.preventDefault();
            uploadZone.classList.toggle('drag-over', evt === 'dragover');
            if (evt === 'drop' && e.dataTransfer?.files[0]) handleImageUpload(e.dataTransfer.files[0]);
        });
    });

    fileInput?.addEventListener('change', () => fileInput.files[0] && handleImageUpload(fileInput.files[0]));
    document.getElementById('removeImageBtn')?.addEventListener('click', (e) => { e.stopPropagation(); resetUpload(); });
    document.getElementById('suggestPromptBtn')?.addEventListener('click', handleSuggestPrompt);

    let keyTimer = null;
    const fetchModels = () => loadGroqModels(groqKeyIn?.value.trim());
    groqKeyIn?.addEventListener('input', () => { clearTimeout(keyTimer); keyTimer = setTimeout(fetchModels, 400); });
    groqKeyIn?.addEventListener('change', fetchModels);

    initModeSelector();
}

function initModeSelector() {
    const stdCard = document.getElementById('modeStandardCard');
    const advCard = document.getElementById('modeAdvancedCard');
    const badge = document.getElementById('modeLimitBadge');

    const setMode = (mode) => {
        const isAdv = mode === 'advanced';
        stdCard?.classList.toggle('active', !isAdv);
        advCard?.classList.toggle('active', isAdv);
        const radio = (isAdv ? advCard : stdCard)?.querySelector('input[type="radio"]');
        if (radio) radio.checked = true;
        if (badge) badge.innerHTML = `<i class="fa-solid fa-gauge-high"></i> ${isAdv ? '10' : '20'} req/phút`;
    };

    stdCard?.addEventListener('click', () => setMode('standard'));
    advCard?.addEventListener('click', () => setMode('advanced'));
}

function handleImageUpload(file) {
    if (!ALLOWED_TYPES.includes(file.type)) return alert('Chỉ chấp nhận JPG, PNG hoặc WEBP!');
    if (file.size > MAX_FILE_SIZE) return alert('Ảnh quá lớn! Tối đa 5MB.');

    const reader = new FileReader();
    reader.onload = (e) => {
        _currentImageBase64 = e.target.result.split(',')[1];
        _currentImageMime = file.type;
        document.getElementById('previewImg').src = e.target.result;
        document.getElementById('uploadPlaceholder')?.classList.add('hidden');
        document.getElementById('uploadPreview')?.classList.remove('hidden');
        document.getElementById('suggestPromptBtn').disabled = false;
        document.getElementById('templateSavedCard')?.classList.add('hidden');
    };
    reader.readAsDataURL(file);
}

function resetUpload() {
    _currentImageBase64 = ''; _currentImageMime = '';
    document.getElementById('imageFileInput').value = '';
    document.getElementById('uploadPlaceholder')?.classList.remove('hidden');
    document.getElementById('uploadPreview')?.classList.add('hidden');
    document.getElementById('suggestPromptBtn').disabled = true;
    document.getElementById('templateSavedCard')?.classList.add('hidden');
}

async function loadGroqModels(apiKey = '') {
    const select = document.getElementById('groqModelSelect');
    const badge = document.getElementById('modelCountBadge');
    if (!select) return;
    if (!apiKey) {
        select.innerHTML = '<option value="">-- Nhập Groq API Key ở trên để tải model --</option>';
        if (badge) badge.innerHTML = '<i class="fa-solid fa-eye"></i> Nhập key để tải model';
        return;
    }

    const currentVal = select.value;
    select.innerHTML = '<option value="">Đang tải danh sách model Vision...</option>';
    try {
        const resp = await fetch(`/api/groq-models?groq_api_key=${encodeURIComponent(apiKey)}`);
        if (!resp.ok) {
            const err = await resp.json().catch(() => ({}));
            select.innerHTML = `<option value="">❌ ${err.detail || 'Lỗi tải model'}</option>`;
            if (badge) badge.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> Lỗi key';
            return;
        }
        const models = await resp.json();
        if (!models?.length) {
            select.innerHTML = '<option value="">Không tìm thấy model Vision nào</option>';
            if (badge) badge.innerHTML = '<i class="fa-solid fa-circle-xmark"></i> 0 model';
            return;
        }
        select.innerHTML = '';
        let found = false;
        models.forEach((m, idx) => {
            const opt = document.createElement('option');
            opt.value = m.id;
            opt.textContent = `${m.name}${m.context_window ? ` (${Math.round(m.context_window / 1024)}k ctx)` : ''}`;
            if (m.id === currentVal) { opt.selected = true; found = true; }
            else if (!found && idx === 0) opt.selected = true;
            select.appendChild(opt);
        });
        if (!found && select.options.length > 0) select.options[0].selected = true;
        if (badge) badge.innerHTML = `<i class="fa-solid fa-check"></i> ${models.length} model Vision`;
    } catch {
        select.innerHTML = '<option value="">❌ Lỗi kết nối khi tải model</option>';
    }
}

async function handleSuggestPrompt() {
    const nameInput = document.getElementById('promptNameInput');
    const name = nameInput?.value.trim();
    if (!name) return alert('Vui lòng nhập tên cho Prompt Template!');
    if (!_currentImageBase64) return alert('Vui lòng chọn ảnh mẫu!');

    const groqKey = document.getElementById('groqApiKeyInput')?.value.trim();
    const modelId = document.getElementById('groqModelSelect')?.value || null;
    const mode = document.querySelector('input[name="promptMode"]:checked')?.value || 'standard';
    const suggestBtn = document.getElementById('suggestPromptBtn');
    const btnText = document.getElementById('suggestBtnText');

    suggestBtn.disabled = true;
    btnText.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> ${mode === 'advanced' ? 'Đang phân tích & nâng cấp GPT-120B...' : 'Đang phân tích và tạo template...'}`;

    try {
        const resp = await fetch('/api/suggest-prompt', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                image_base64: _currentImageBase64, image_mime: _currentImageMime,
                prompt_name: name, groq_api_key: groqKey || null,
                model_id: modelId, mode: mode
            })
        });

        if (await checkAndHandleRateLimit(resp)) return;
        if (!resp.ok) {
            const err = await resp.json().catch(() => ({}));
            throw new Error(err?.detail?.message || err?.detail || `Lỗi ${resp.status}`);
        }

        const data = await resp.json();
        
        // Cập nhật thông báo thành công (không hiển thị prompt content)
        const savedCard = document.getElementById('templateSavedCard');
        const savedSub = document.getElementById('templateSavedSub');
        if (savedSub) savedSub.textContent = `Template "${name}" đã được lưu vào danh sách.`;
        savedCard?.classList.remove('hidden');

        // Tải lại danh sách templates
        if (typeof window.loadPromptTemplates === 'function') {
            await window.loadPromptTemplates();
            const select = document.getElementById('promptTemplateSelect');
            if (select && data.prompt) {
                select.value = data.prompt;
                select.dispatchEvent(new Event('change'));
            }
        }
        if (nameInput) nameInput.value = '';
    } catch (err) {
        alert(`❌ ${err.message}`);
    } finally {
        suggestBtn.disabled = !_currentImageBase64;
        btnText.innerHTML = 'Phân tích và tạo template';
    }
}
