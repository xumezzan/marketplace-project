document.addEventListener('DOMContentLoaded', function () {
    let currentStep = 1;
    const totalSteps = 3;

    const form = document.getElementById('wizard-form');
    const nextBtn = document.getElementById('next-btn');
    const prevBtn = document.getElementById('prev-btn');
    const submitBtn = document.getElementById('submit-btn');
    const progressBar = document.getElementById('progress-bar');
    const stepNumber = document.getElementById('step-number');
    const stepTitle = document.getElementById('step-title');
    const aiHelpBtn = document.getElementById('ai-help-btn');

    const stepTitles = {
        1: 'Основная информация',
        2: 'Опишите задачу',
        3: 'Бюджет и сроки'
    };

    // Navigation
    nextBtn.addEventListener('click', () => {
        if (validateStep(currentStep)) {
            currentStep++;
            updateUI();
        }
    });

    prevBtn.addEventListener('click', () => {
        currentStep--;
        updateUI();
    });

    // AI Generation
    if (aiHelpBtn) {
        aiHelpBtn.addEventListener('click', async () => {
            const title = form.querySelector('[name="title"]').value;
            const categoryId = form.querySelector('[name="category"]').value;
            const descriptionField = form.querySelector('[name="description"]');
            const loadingOverlay = document.getElementById('ai-loading');

            if (!title) {
                alert('Пожалуйста, сначала укажите название задания на первом шаге');
                currentStep = 1;
                updateUI();
                return;
            }

            loadingOverlay.classList.remove('hidden');

            try {
                const formData = new FormData();
                formData.append('title', title);
                formData.append('category_id', categoryId);

                const response = await fetch('/api/tasks/generate-description/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: formData
                });

                const data = await response.json();

                if (data.success) {
                    // Typewriter effect
                    const text = data.description;
                    descriptionField.value = '';
                    let i = 0;
                    const typeWriter = setInterval(() => {
                        if (i < text.length) {
                            descriptionField.value += text.charAt(i);
                            i++;
                        } else {
                            clearInterval(typeWriter);
                        }
                    }, 10);
                } else {
                    alert(data.error || 'Ошибка генерации');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Произошла ошибка при обращении к AI');
            } finally {
                loadingOverlay.classList.add('hidden');
            }
        });
    }

    // Form Submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(form);

        try {
            const response = await fetch(window.location.href, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                window.location.href = data.redirect_url;
            } else {
                alert(data.error || 'Ошибка при создании задания');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Произошла ошибка');
        }
    });

    function updateUI() {
        // Show/Hide Steps
        document.querySelectorAll('.wizard-step').forEach(step => step.classList.add('hidden'));
        document.getElementById(`step-${currentStep}`).classList.remove('hidden');

        // Update Progress
        const progress = (currentStep / totalSteps) * 100;
        progressBar.style.width = `${progress}%`;
        stepNumber.textContent = currentStep;
        stepTitle.textContent = stepTitles[currentStep];

        // Update Buttons
        prevBtn.classList.toggle('hidden', currentStep === 1);

        if (currentStep === totalSteps) {
            nextBtn.classList.add('hidden');
            submitBtn.classList.remove('hidden');
        } else {
            nextBtn.classList.remove('hidden');
            submitBtn.classList.add('hidden');
        }
    }

    function validateStep(step) {
        const stepEl = document.getElementById(`step-${step}`);
        const inputs = stepEl.querySelectorAll('input[required], select[required], textarea[required]');
        let isValid = true;

        inputs.forEach(input => {
            if (!input.value.trim()) {
                isValid = false;
                input.classList.add('border-red-500');
                input.addEventListener('input', () => input.classList.remove('border-red-500'), { once: true });
            }
        });

        if (!isValid) {
            // Shake animation
            stepEl.classList.add('animate-shake');
            setTimeout(() => stepEl.classList.remove('animate-shake'), 500);
        }

        return isValid;
    }

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
