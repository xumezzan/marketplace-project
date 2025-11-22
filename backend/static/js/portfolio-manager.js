/**
 * Portfolio Manager - Handles drag-and-drop upload and reordering
 */

document.addEventListener('DOMContentLoaded', function () {
    // Bulk upload modal
    const uploadModal = document.getElementById('upload-modal');
    const bulkUploadBtn = document.getElementById('bulk-upload-btn');
    const closeModalBtn = document.getElementById('close-modal');
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const previewContainer = document.getElementById('preview-container');
    const uploadBtn = document.getElementById('upload-btn');
    const uploadProgress = document.getElementById('upload-progress');
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');

    let selectedFiles = [];

    // Open modal
    if (bulkUploadBtn) {
        bulkUploadBtn.addEventListener('click', () => {
            uploadModal.classList.remove('hidden');
        });
    }

    // Close modal
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', () => {
            uploadModal.classList.add('hidden');
            selectedFiles = [];
            previewContainer.innerHTML = '';
            previewContainer.classList.add('hidden');
            uploadBtn.classList.add('hidden');
        });
    }

    // Click to select files
    if (dropZone) {
        dropZone.addEventListener('click', () => {
            fileInput.click();
        });
    }

    // Drag and drop
    if (dropZone) {
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('border-indigo-500', 'bg-indigo-50', 'dark:bg-indigo-900/20');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('border-indigo-500', 'bg-indigo-50', 'dark:bg-indigo-900/20');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('border-indigo-500', 'bg-indigo-50', 'dark:bg-indigo-900/20');
            handleFiles(e.dataTransfer.files);
        });
    }

    // File input change
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            handleFiles(e.target.files);
        });
    }

    // Handle selected files
    function handleFiles(files) {
        selectedFiles = Array.from(files).filter(file => file.type.startsWith('image/'));

        if (selectedFiles.length === 0) {
            alert('Пожалуйста, выберите изображения');
            return;
        }

        // Show previews
        previewContainer.innerHTML = '';
        previewContainer.classList.remove('hidden');
        uploadBtn.classList.remove('hidden');

        selectedFiles.forEach((file, index) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                const div = document.createElement('div');
                div.className = 'relative aspect-square rounded-lg overflow-hidden border-2 border-slate-200 dark:border-slate-600';
                div.innerHTML = `
                    <img src="${e.target.result}" class="w-full h-full object-cover">
                    <button class="absolute top-1 right-1 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center hover:bg-red-600" data-index="${index}">
                        <i class="bi bi-x text-sm"></i>
                    </button>
                `;

                // Remove file on click
                div.querySelector('button').addEventListener('click', (e) => {
                    e.preventDefault();
                    const idx = parseInt(e.currentTarget.dataset.index);
                    selectedFiles.splice(idx, 1);
                    handleFiles(selectedFiles);
                });

                previewContainer.appendChild(div);
            };
            reader.readAsDataURL(file);
        });
    }

    // Upload files
    if (uploadBtn) {
        uploadBtn.addEventListener('click', async () => {
            if (selectedFiles.length === 0) return;

            const formData = new FormData();
            selectedFiles.forEach(file => {
                formData.append('images', file);
            });

            uploadBtn.disabled = true;
            uploadProgress.classList.remove('hidden');
            progressText.textContent = 'Загрузка...';

            try {
                const response = await fetch('/api/portfolio/bulk-upload/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: formData
                });

                const data = await response.json();

                if (data.success) {
                    progressBar.style.width = '100%';
                    progressText.textContent = `Загружено ${data.created} изображений`;

                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                } else {
                    alert('Ошибка загрузки: ' + (data.error || 'Неизвестная ошибка'));
                    uploadBtn.disabled = false;
                }
            } catch (error) {
                console.error('Upload error:', error);
                alert('Ошибка загрузки файлов');
                uploadBtn.disabled = false;
            }
        });
    }

    // Sortable for reordering
    const portfolioGrid = document.getElementById('portfolio-grid');
    if (portfolioGrid) {
        new Sortable(portfolioGrid, {
            animation: 150,
            handle: '.portfolio-item',
            ghostClass: 'opacity-50',
            onEnd: async function (evt) {
                // Get new order
                const items = [];
                document.querySelectorAll('.portfolio-item').forEach((item, index) => {
                    items.push({
                        id: parseInt(item.dataset.id),
                        order: index
                    });
                });

                // Send to server
                try {
                    const response = await fetch('/api/portfolio/reorder/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        },
                        body: JSON.stringify({ items })
                    });

                    const data = await response.json();
                    if (!data.success) {
                        console.error('Reorder failed:', data.error);
                        // Reload to restore original order
                        window.location.reload();
                    }
                } catch (error) {
                    console.error('Reorder error:', error);
                    window.location.reload();
                }
            }
        });
    }

    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
