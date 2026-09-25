# templates/ – Storyboard Video Components

## Mục đích
Các component Jinja2 + JS + CSS cho tính năng Storyboard Video.

## Components

### storyboard_input.html
**ID elements**: `#storyboardTextInput`, `#audioUploadZone`, `#audioFileInput`, `#audioUploadPlaceholder`, `#audioUploadPreview`, `#audioFileName`, `#audioDuration`, `#removeAudioBtn`, `#storyboardTitleInput`, `#storyboardGroqKeyInput`, `#storyboardModelSelect`, `#storyboardAspectSelect`, `#infoAudioDuration`, `#infoSegmentCount`, `#infoEstimatedTime`, `#createStoryboardBtn`

### storyboard_timeline.html
**ID elements**: `#storyboardTitle`, `#storyboardStatusBadge`, `#storyboardStatusText`, `#storyboardProgressBar`, `#storyboardProgressText`, `#storyboardSegmentGrid`, `#storyboardEmptyState`, `#toastContainer`

### storyboard_modal.html
**ID elements**: `#storyboardVideoModal`, `#storyboardVideoBackdrop`, `#closeStoryboardVideoBtn`, `#storyboardFullscreenVideo`, `#storyboardPromptModal`, `#storyboardPromptBackdrop`, `#closeStoryboardPromptBtn`, `#editSegmentText`, `#editVideoPrompt`, `#cancelEditPromptBtn`, `#saveEditPromptBtn`

## JavaScript

### storyboard_manager.js
- `initStoryboardManager()`, `handleAudioUpload()`, `handleCreateStoryboard()`
- `renderTimeline()`, `renderSegmentCard()`, `updateProgress()`
- `pollStoryboardStatus()` – polling 10s
- `showToast()` – 4 loại toast
- `resumeActiveStoryboard()` – localStorage

### storyboard_history.js
- `addStoryboardToHistory()`, `updateStoryboardInHistory()`
- `renderStoryboardHistory()`, `deleteStoryboardFromHistory()`
- `loadStoryboardFromHistory()`

## CSS
### storyboard.css
- Input panel, upload zone, info card
- Timeline panel, progress bar, segment grid
- Status badges (4 loại), video player
- Toast notifications, history items
- Responsive: 3 cột → 2 cột → 1 cột

## Keywords
`storyboard_input`, `storyboard_timeline`, `storyboard_modal`, `storyboard_manager`, `storyboard_history`, `storyboard.css`, `audioUploadZone`, `storyboardSegmentGrid`, `toastContainer`, `pollStoryboardStatus`, `showToast`, `resumeActiveStoryboard`

## Phụ thuộc
- Include bởi: `templates/index.html`
- Tương tác với: `templates/js/rate_limit_ui.js`, `templates/js/app.js`
- Style bởi: `templates/css/storyboard.css`
