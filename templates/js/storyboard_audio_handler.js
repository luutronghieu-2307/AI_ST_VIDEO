/**
 * storyboard_audio_handler.js – Quản lý Tải lên & Phân tích Subtitle SRT và Audio
 */

const MAX_AUDIO_SIZE = 50 * 1024 * 1024;
const SAMPLE_SRT = `1\n00:00:00,100 --> 00:00:04,292\nTrí tuệ nhân tạo hay AI không phải là một thực thể có ý thức hay suy nghĩ độc lập\n\n2\n00:00:04,850 --> 00:00:08,383\nBản chất của AI thực chất là những thuật toán phức tạp được huấn luyện trên dữ liệu lớn\n\n3\n00:00:08,533 --> 00:00:09,883\ndự đoán và tự động hóa các tác vụ\n\n4\n00:00:10,458 --> 00:00:14,025\nDù có khả năng xử lý thông tin với tốc độ chóng mặt và tạo ra các tác phẩm ấn tượng\n\n5\n00:00:14,208 --> 00:00:16,775\nAI vẫn hoàn toàn phụ thuộc vào dữ liệu đầu vào và sự định hướng của con người\n\n6\n00:00:17,350 --> 00:00:22,092\nHiểu đúng về AI giúp chúng ta tận dụng tối đa sức mạnh của công nghệ này`;

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

function handleSrtFile(file, showToast) {
    if (!file.name.toLowerCase().endsWith('.srt') && !file.name.toLowerCase().endsWith('.txt')) {
        if (showToast) showToast('Chỉ chấp nhận file phụ đề (.srt)!', 'error');
        return null;
    }
    const reader = new FileReader();
    reader.onload = (e) => {
        const textInput = document.getElementById('storyboardTextInput');
        if (textInput) textInput.value = e.target.result;
        updateInfoFromText();
    };
    reader.readAsText(file);
    const fileNameEl = document.getElementById('srtFileName');
    if (fileNameEl) fileNameEl.textContent = file.name;
    document.getElementById('srtUploadPlaceholder')?.classList.add('hidden');
    document.getElementById('srtUploadPreview')?.classList.remove('hidden');
    return file;
}

function resetSrtUpload() {
    const input = document.getElementById('srtFileInput');
    if (input) input.value = '';
    document.getElementById('srtUploadPlaceholder')?.classList.remove('hidden');
    document.getElementById('srtUploadPreview')?.classList.add('hidden');
    updateInfoFromText();
    return null;
}

function handleAudioFile(file, showToast) {
    if (file.size > MAX_AUDIO_SIZE) {
        if (showToast) showToast('File âm thanh quá lớn (tối đa 50MB)!', 'error');
        return null;
    }
    const nameEl = document.getElementById('audioFileName');
    if (nameEl) nameEl.textContent = file.name;
    document.getElementById('audioUploadPlaceholder')?.classList.add('hidden');
    document.getElementById('audioUploadPreview')?.classList.remove('hidden');
    const statusEl = document.getElementById('infoAudioStatus');
    if (statusEl) statusEl.textContent = `Đã đính kèm (${file.name})`;
    return file;
}

function resetAudioUpload() {
    const input = document.getElementById('audioFileInput');
    if (input) input.value = '';
    document.getElementById('audioUploadPlaceholder')?.classList.remove('hidden');
    document.getElementById('audioUploadPreview')?.classList.add('hidden');
    const statusEl = document.getElementById('infoAudioStatus');
    if (statusEl) statusEl.textContent = 'Không đính kèm';
    return null;
}

const StoryboardAudioHandler = {
    MAX_AUDIO_SIZE,
    SAMPLE_SRT,
    updateInfoFromText,
    handleSrtFile,
    resetSrtUpload,
    handleAudioFile,
    resetAudioUpload
};

if (typeof window !== 'undefined') {
    window.StoryboardAudioHandler = StoryboardAudioHandler;
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = StoryboardAudioHandler;
}
