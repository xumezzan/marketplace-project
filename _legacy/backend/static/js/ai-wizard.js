/**
 * AI-мастер создания задач (TaskWizard) для Profimatch
 */

(function() {
    'use strict';

    /**
     * Инициализация AI-мастера
     */
    function initAIWizard() {
        const wizardForm = document.getElementById('task-wizard-form');
        if (!wizardForm) return;

        const rawInput = document.getElementById('raw-task-input');
        const analyzeBtn = document.getElementById('analyze-task-btn');
        const language = document.documentElement.lang || 'ru';

        if (!rawInput || !analyzeBtn) return;

        analyzeBtn.addEventListener('click', async function(e) {
            e.preventDefault();
            
            const description = rawInput.value.trim();
            if (!description) {
                showNotification('Введите описание задачи', 'warning');
                return;
            }

            // Показываем индикатор загрузки
            analyzeBtn.disabled = true;
            const originalText = analyzeBtn.innerHTML;
            analyzeBtn.innerHTML = '<i class="bi bi-hourglass-split animate-spin"></i> Анализируем...';

            try {
                const response = await fetch('/api/ai/analyze-task/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        description: description,
                        language: language
                    })
                });

                const data = await response.json();

                if (response.ok && data.suggested_title) {
                    // Заполняем форму результатами анализа
                    fillFormWithAIResults(data);
                    showNotification('Задача успешно проанализирована! Заполните детали ниже.', 'success');
                    
                    // Скрываем AI-секцию и показываем форму
                    const step1 = document.getElementById('wizard-step-1');
                    const step2 = document.getElementById('wizard-step-2');
                    if (step1 && step2) {
                        step1.style.display = 'none';
                        step2.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }
                } else {
                    showNotification(data.error || 'Не удалось проанализировать задачу', 'error');
                }
            } catch (error) {
                console.error('Ошибка при анализе задачи:', error);
                showNotification('Произошла ошибка при анализе задачи', 'error');
            } finally {
                analyzeBtn.disabled = false;
                analyzeBtn.innerHTML = originalText;
            }
        });
    }

    /**
     * Заполняет форму результатами AI-анализа
     */
    function fillFormWithAIResults(data) {
        const titleInput = document.getElementById('id_title');
        const descriptionInput = document.getElementById('id_description');
        const budgetMinInput = document.getElementById('id_budget_min');
        const budgetMaxInput = document.getElementById('id_budget_max');
        const categorySelect = document.getElementById('id_category');

        if (titleInput && data.suggested_title) {
            titleInput.value = data.suggested_title;
        }

        if (descriptionInput && data.refined_description) {
            descriptionInput.value = data.refined_description;
        }

        if (budgetMinInput && data.estimated_budget_min) {
            budgetMinInput.value = data.estimated_budget_min;
        }

        if (budgetMaxInput && data.estimated_budget_max) {
            budgetMaxInput.value = data.estimated_budget_max;
        }

        // Пытаемся найти категорию по названию
        if (categorySelect && data.suggested_category) {
            const options = Array.from(categorySelect.options);
            const matchingOption = options.find(opt => 
                opt.text.toLowerCase().includes(data.suggested_category.toLowerCase())
            );
            if (matchingOption) {
                categorySelect.value = matchingOption.value;
            }
        }
    }

    /**
     * Получает значение cookie
     */
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

    // Инициализация при загрузке DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAIWizard);
    } else {
        initAIWizard();
    }
})();

