/**
 * rate_limit_ui.js – Xử lý UI khi backend trả về HTTP 429 Rate Limit
 * Dùng sessionStorage để countdown tiếp tục ngay cả khi user reload trang.
 */

const RATE_LIMIT_KEY = 'aura_rate_limit_reset';
let _countdownInterval = null;

/** Gọi khi nhận HTTP 429, retryAfter = số giây cần chờ */
function handleRateLimitError(retryAfter) {
    const resetAt = Date.now() + retryAfter * 1000;
    sessionStorage.setItem(RATE_LIMIT_KEY, String(resetAt));
    _showRateLimitBanner(retryAfter);
}

/** Hiện banner đếm ngược và disable các nút */
function _showRateLimitBanner(seconds) {
    _disableActionButtons(true);
    const banner = document.getElementById('rateLimitBanner');
    if (banner) banner.classList.remove('hidden');
    _startCountdown(seconds);
}

/** Bắt đầu đếm ngược realtime */
function _startCountdown(seconds) {
    if (_countdownInterval) clearInterval(_countdownInterval);
    let remaining = Math.max(seconds, 1);
    _updateCountdownDisplay(remaining);

    _countdownInterval = setInterval(() => {
        remaining -= 1;
        _updateCountdownDisplay(remaining);
        if (remaining <= 0) {
            _clearRateLimit();
        }
    }, 1000);
}

function _updateCountdownDisplay(seconds) {
    const el = document.getElementById('rateLimitTimer');
    if (el) el.textContent = seconds;
}

/** Ẩn banner, enable nút, clear storage */
function _clearRateLimit() {
    clearInterval(_countdownInterval);
    _countdownInterval = null;
    sessionStorage.removeItem(RATE_LIMIT_KEY);
    _disableActionButtons(false);
    const banner = document.getElementById('rateLimitBanner');
    if (banner) banner.classList.add('hidden');
}

/** Disable/enable generateBtn + suggestPromptBtn */
function _disableActionButtons(disabled) {
    ['generateBtn', 'suggestPromptBtn'].forEach(id => {
        const btn = document.getElementById(id);
        if (btn) btn.disabled = disabled;
    });
}

/** Khôi phục countdown khi user reload trang */
function restoreRateLimitOnLoad() {
    const resetAt = parseInt(sessionStorage.getItem(RATE_LIMIT_KEY) || '0', 10);
    if (!resetAt) return;
    const remaining = Math.ceil((resetAt - Date.now()) / 1000);
    if (remaining > 0) {
        _showRateLimitBanner(remaining);
    } else {
        sessionStorage.removeItem(RATE_LIMIT_KEY);
    }
}

/** Kiểm tra response 429 và trả về retryAfter (giây) hoặc 0 nếu không phải 429 */
async function checkAndHandleRateLimit(response) {
    if (response.status !== 429) return false;
    try {
        const data = await response.json();
        const retryAfter = data?.detail?.retry_after || 60;
        handleRateLimitError(retryAfter);
    } catch {
        handleRateLimitError(60);
    }
    return true;
}

// Tự khôi phục khi trang load
document.addEventListener('DOMContentLoaded', restoreRateLimitOnLoad);
