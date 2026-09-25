/**
 * template_manager.js – Quản lý Prompt Templates & Xóa hàng loạt (Modal Management)
 */
let _cachedTemplates = [];
let _selectedTemplateIds = new Set();

document.addEventListener('DOMContentLoaded', () => {
    initTemplateManager();
    loadPromptTemplates();
});

async function loadPromptTemplates() {
    try {
        const resp = await fetch('/api/prompt-templates');
        if (!resp.ok) return;
        _cachedTemplates = await resp.json();
        const select = document.getElementById('promptTemplateSelect');
        if (!select) return;
        const current = select.value;
        select.innerHTML = '<option value="">-- Chọn template hoặc tự nhập prompt bên dưới --</option>';
        _cachedTemplates.forEach(t => {
            const opt = document.createElement('option');
            opt.value = t.prompt;
            opt.textContent = t.name;
            opt.dataset.id = t.id;
            opt.dataset.isDefault = t.is_default;
            if (t.prompt === current) opt.selected = true;
            select.appendChild(opt);
        });
        renderTemplateModalList();
    } catch (e) { console.warn('Không tải được templates:', e); }
}

function initTemplateManager() {
    const tplSelect = document.getElementById('promptTemplateSelect');
    const deleteBtn = document.getElementById('deleteTemplateBtn');
    const modal = document.getElementById('templateManagerModal');
    const openBtn = document.getElementById('manageTemplatesBtn');
    const closeBtn = document.getElementById('closeTemplateModalBtn');
    const doneBtn = document.getElementById('doneTemplateModalBtn');
    const backdrop = document.getElementById('templateModalBackdrop');
    const selectAllCb = document.getElementById('selectAllTemplatesCb');
    const deleteBatchBtn = document.getElementById('deleteSelectedTemplatesBtn');

    tplSelect?.addEventListener('change', () => {
        const val = tplSelect.value;
        if (!val) return deleteBtn?.classList.add('hidden');
        const opt = tplSelect.options[tplSelect.selectedIndex];
        deleteBtn?.classList.toggle('hidden', opt?.dataset.isDefault === 'true');
    });

    deleteBtn?.addEventListener('click', handleDeleteSingleTemplate);

    const toggleModal = (show) => modal?.classList.toggle('hidden', !show);
    openBtn?.addEventListener('click', () => { _selectedTemplateIds.clear(); renderTemplateModalList(); toggleModal(true); });
    closeBtn?.addEventListener('click', () => toggleModal(false));
    doneBtn?.addEventListener('click', () => toggleModal(false));
    backdrop?.addEventListener('click', () => toggleModal(false));

    selectAllCb?.addEventListener('change', (e) => {
        const userTpls = _cachedTemplates.filter(t => !t.is_default);
        _selectedTemplateIds = e.target.checked ? new Set(userTpls.map(t => t.id)) : new Set();
        renderTemplateModalList();
    });

    deleteBatchBtn?.addEventListener('click', async () => {
        if (!_selectedTemplateIds.size) return;
        if (!confirm(`Bạn có chắc muốn xóa ${_selectedTemplateIds.size} template đã chọn?`)) return;
        try {
            const res = await fetch('/api/prompt-templates/batch-delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ids: Array.from(_selectedTemplateIds) })
            });
            if (!res.ok) { const err = await res.json(); throw new Error(err.detail || 'Lỗi xóa hàng loạt'); }
            _selectedTemplateIds.clear();
            await loadPromptTemplates();
        } catch (err) { alert(`❌ ${err.message}`); }
    });
}

function renderTemplateModalList() {
    const container = document.getElementById('templateListContainer');
    const deleteBatchBtn = document.getElementById('deleteSelectedTemplatesBtn');
    const selCountEl = document.getElementById('selectedTemplatesCount');
    const selectAllCb = document.getElementById('selectAllTemplatesCb');
    if (!container) return;

    const userTpls = _cachedTemplates.filter(t => !t.is_default);
    const selCount = _selectedTemplateIds.size;
    if (deleteBatchBtn) deleteBatchBtn.classList.toggle('hidden', selCount === 0);
    if (selCountEl) selCountEl.textContent = selCount;
    if (selectAllCb) {
        selectAllCb.checked = userTpls.length > 0 && selCount === userTpls.length;
        selectAllCb.disabled = userTpls.length === 0;
    }

    if (!_cachedTemplates.length) {
        container.innerHTML = '<div class="empty-hint">Chưa có template nào được lưu.</div>';
        return;
    }

    container.innerHTML = _cachedTemplates.map(t => {
        const isChecked = _selectedTemplateIds.has(t.id);
        return `
            <div class="template-item-row ${isChecked ? 'selected' : ''}" data-id="${t.id}">
                <div class="template-item-left">
                    ${t.is_default 
                        ? `<span class="badge-tag protected" title="Template mặc định (không thể xóa)"><i class="fa-solid fa-lock"></i></span>`
                        : `<label class="custom-checkbox-label" onclick="event.stopPropagation()">
                             <input type="checkbox" class="tpl-checkbox" data-id="${t.id}" ${isChecked ? 'checked' : ''}>
                             <span class="custom-checkmark"><i class="fa-solid fa-check"></i></span>
                           </label>`
                    }
                    <div class="template-info">
                        <div class="template-name-row">
                            <strong class="template-name">${t.name}</strong>
                            ${t.is_default ? '<span class="badge-tag default">Hệ thống</span>' : ''}
                        </div>
                    </div>
                </div>
                <button type="button" class="text-btn action-sm accent use-tpl-btn" data-prompt="${encodeURIComponent(t.prompt)}">
                    <i class="fa-solid fa-check"></i> Chọn
                </button>
            </div>
        `;
    }).join('');

    container.querySelectorAll('.tpl-checkbox').forEach(cb => {
        cb.addEventListener('change', (e) => {
            const id = e.target.dataset.id;
            e.target.checked ? _selectedTemplateIds.add(id) : _selectedTemplateIds.delete(id);
            renderTemplateModalList();
        });
    });

    container.querySelectorAll('.use-tpl-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const prompt = decodeURIComponent(btn.dataset.prompt);
            const select = document.getElementById('promptTemplateSelect');
            if (select) {
                select.value = prompt;
                select.dispatchEvent(new Event('change'));
            }
            document.getElementById('templateManagerModal')?.classList.add('hidden');
        });
    });
}

async function handleDeleteSingleTemplate() {
    const select = document.getElementById('promptTemplateSelect');
    const opt = select?.options[select.selectedIndex];
    if (!opt?.dataset.id || !confirm(`Xóa template "${opt.textContent}"?`)) return;
    try {
        const resp = await fetch(`/api/prompt-templates/${opt.dataset.id}`, { method: 'DELETE' });
        if (!resp.ok) { const e = await resp.json(); throw new Error(e.detail || 'Lỗi xóa'); }
        select.value = '';
        document.getElementById('deleteTemplateBtn')?.classList.add('hidden');
        await loadPromptTemplates();
    } catch (e) { alert(`❌ ${e.message}`); }
}

window.loadPromptTemplates = loadPromptTemplates;
