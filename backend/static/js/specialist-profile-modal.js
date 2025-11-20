/**
 * Улучшенное модальное окно профиля специалиста
 * С вкладками: Портфолио и Отзывы
 */

(function () {
    'use strict';

    let currentSpecialistId = null;
    let currentTab = 'portfolio'; // portfolio или reviews

    /**
     * Открывает модальное окно и загружает данные специалиста
     */
    window.openSpecialistModal = function (specialistId) {
        currentSpecialistId = specialistId;

        // Создаем модальное окно сразу
        showLoadingModal();

        // Загружаем данные с сервера
        fetch(`/marketplace/api/specialist/${specialistId}/`)
            .then(response => {
                if (!response.ok) throw new Error('Failed to load specialist data');
                return response.json();
            })
            .then(data => {
                renderModal(data);
            })
            .catch(error => {
                console.error('Error loading specialist:', error);
                closeSpecialistModal();
                alert('Ошибка при загрузке данных специалиста');
            });
    };

    /**
     * Показывает модалку с loader
     */
    function showLoadingModal() {
        const modal = document.createElement('div');
        modal.id = 'specialist-profile-modal';
        modal.className = 'fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6';

        modal.innerHTML = `
            <div class="absolute inset-0 bg-slate-900/60 backdrop-blur-sm dark:bg-slate-950/80" onclick="closeSpecialistModal()"></div>
            <div class="relative bg-white dark:bg-slate-800 rounded-2xl shadow-2xl w-full max-w-4xl p-12 text-center">
                <div class="flex items-center justify-center gap-3">
                    <div class="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
                    <span class="text-lg text-slate-600 dark:text-slate-300">Загрузка...</span>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        document.body.style.overflow = 'hidden';
    }

    /**
     * Отрисовывает модальное окно с данными
     */
    function renderModal(data) {
        const existing = document.getElementById('specialist-profile-modal');
        if (existing) existing.remove();

        const modal = document.createElement('div');
        modal.id = 'specialist-profile-modal';
        modal.className = 'fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6';
        modal.style.overflowY = 'auto';

        const stars = generateStars(data.rating);
        const reviewsText = getReviewsText(data.reviews_count);
        const portfolioHtml = renderPortfolio(data.portfolio);
        const reviewsHtml = renderReviews(data.reviews);

        modal.innerHTML = `
            <div class="absolute inset-0 bg-slate-900/60 backdrop-blur-sm dark:bg-slate-950/80" onclick="closeSpecialistModal()"></div>
            <div class="relative bg-white dark:bg-slate-800 rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
                <button onclick="closeSpecialistModal()" class="absolute top-4 right-4 z-10 p-2 bg-white/80 dark:bg-slate-700/80 rounded-full hover:bg-red-50 dark:hover:bg-red-900/30 hover:text-red-500 transition">
                    <i class="bi bi-x-lg text-slate-600 dark:text-slate-300"></i>
                </button>
                
                <div class="p-6 sm:p-8">
                    <!-- Header -->
                    <div class="flex flex-col sm:flex-row items-center sm:items-start gap-6 mb-6 pb-6 border-b border-slate-200 dark:border-slate-700">
                        <div class="relative flex-shrink-0">
                            <img src="${data.avatar_url}" 
                                 alt="${data.username}" 
                                 class="w-32 h-32 rounded-full object-cover border-4 border-white dark:border-slate-700 shadow-lg">
                            ${data.is_verified ? '<div class="absolute bottom-2 right-2 bg-green-500 w-5 h-5 rounded-full border-2 border-white dark:border-slate-700"></div>' : ''}
                        </div>
                        
                        <div class="flex-1 text-center sm:text-left">
                            <h2 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">${data.username}</h2>
                            <p class="text-indigo-600 dark:text-indigo-400 font-medium mb-4">${data.profession}</p>
                            
                            <div class="flex flex-wrap items-center gap-4 justify-center sm:justify-start">
                                <div class="flex items-center gap-2 bg-amber-50 dark:bg-amber-900/30 px-3 py-1.5 rounded-lg">
                                    ${stars}
                                    <span class="font-bold text-slate-900 dark:text-white">${data.rating.toFixed(1)}</span>
                                    <span class="text-slate-500 dark:text-slate-400 text-sm">${reviewsText}</span>
                                </div>
                                
                                ${data.years_of_experience ? `
                                <div class="flex items-center gap-2 text-slate-600 dark:text-slate-300">
                                    <i class="bi bi-calendar-check"></i>
                                    <span class="text-sm">${data.years_of_experience} лет опыта</span>
                                </div>
                                ` : ''}
                            </div>
                        </div>
                    </div>
                    
                    <!-- Description -->
                    <div class="mb-6">
                        <h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-3">О специалисте</h3>
                        <p class="text-slate-600 dark:text-slate-300 leading-relaxed">${data.description}</p>
                    </div>
                    
                    <!-- Tabs -->
                    <div class="mb-6">
                        <div class="flex gap-2 border-b border-slate-200 dark:border-slate-700">
                            <button onclick="switchTab('portfolio')" 
                                    id="tab-portfolio"
                                    class="tab-button px-6 py-3 font-medium transition border-b-2 border-indigo-600 text-indigo-600 dark:text-indigo-400">
                                <i class="bi bi-images mr-2"></i>Портфолио (${data.portfolio.length})
                            </button>
                            <button onclick="switchTab('reviews')" 
                                    id="tab-reviews"
                                    class="tab-button px-6 py-3 font-medium transition border-b-2 border-transparent text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300">
                                <i class="bi bi-star mr-2"></i>Отзывы (${data.reviews.length})
                            </button>
                        </div>
                        
                        <!-- Tab Content -->
                        <div id="tab-content-portfolio" class="mt-6">
                            ${portfolioHtml}
                        </div>
                        <div id="tab-content-reviews" class="mt-6 hidden">
                            ${reviewsHtml}
                        </div>
                    </div>
                    
                    <!-- Price & Actions -->
                    <div class="bg-slate-50 dark:bg-slate-700/50 rounded-xl p-6">
                        <div class="flex flex-col sm:flex-row items-center justify-between gap-4">
                            <div>
                                <p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Стоимость услуг</p>
                                <p class="text-2xl font-bold text-slate-900 dark:text-white">${data.price_range}</p>
                            </div>
                            <div class="flex gap-3 w-full sm:w-auto">
                                <button onclick="closeSpecialistModal()" 
                                        class="flex-1 sm:flex-none px-6 py-3 bg-white dark:bg-slate-600 border border-slate-300 dark:border-slate-500 text-slate-700 dark:text-white rounded-lg font-medium hover:bg-slate-50 dark:hover:bg-slate-500 transition">
                                    Написать
                                </button>
                                <a href="/marketplace/tasks/create/" 
                                   class="flex-1 sm:flex-none px-6 py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition shadow-md hover:shadow-lg text-center">
                                    Создать задачу
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        document.body.style.overflow = 'hidden';
    }

    /**
     * Отрисовка портфолио
     */
    function renderPortfolio(portfolio) {
        if (!portfolio || portfolio.length === 0) {
            return '<p class="text-slate-500 dark:text-slate-400 text-center py-8">Портфолио пока пусто</p>';
        }

        return `
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                ${portfolio.map(item => `
                    <div class="group relative bg-slate-50 dark:bg-slate-700/50 rounded-lg overflow-hidden hover:shadow-lg transition">
                        ${item.image_url ? `
                            <img src="${item.image_url}" 
                                 alt="${item.title}" 
                                 class="w-full h-48 object-cover">
                        ` : `
                            <div class="w-full h-48 bg-slate-200 dark:bg-slate-600 flex items-center justify-center">
                                <i class="bi bi-image text-4xl text-slate-400 dark:text-slate-500"></i>
                            </div>
                        `}
                        <div class="p-4">
                            <h4 class="font-semibold text-slate-900 dark:text-white mb-2">${item.title}</h4>
                            <p class="text-sm text-slate-600 dark:text-slate-300 line-clamp-2">${item.description || 'Без описания'}</p>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    /**
     * Отрисовка отзывов
     */
    function renderReviews(reviews) {
        if (!reviews || reviews.length === 0) {
            return '<p class="text-slate-500 dark:text-slate-400 text-center py-8">Отзывов пока нет</p>';
        }

        return `
            <div class="space-y-4">
                ${reviews.map(review => `
                    <div class="bg-slate-50 dark:bg-slate-700/50 rounded-lg p-4">
                        <div class="flex items-start justify-between mb-2">
                            <div class="flex items-center gap-2">
                                <span class="font-semibold text-slate-900 dark:text-white">${review.client_name}</span>
                                <div class="flex items-center gap-1">
                                    ${generateStars(review.rating)}
                                </div>
                            </div>
                            <span class="text-sm text-slate-500 dark:text-slate-400">${review.created_at}</span>
                        </div>
                        <p class="text-slate-600 dark:text-slate-300">${review.comment}</p>
                        ${review.task_title ? `
                            <p class="text-sm text-slate-500 dark:text-slate-400 mt-2">Задача: ${review.task_title}</p>
                        ` : ''}
                    </div>
                `).join('')}
            </div>
        `;
    }

    /**
     * Переключение вкладок
     */
    window.switchTab = function (tab) {
        currentTab = tab;

        // Переключаем стили кнопок
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('border-indigo-600', 'text-indigo-600', 'dark:text-indigo-400');
            btn.classList.add('border-transparent', 'text-slate-500', 'dark:text-slate-400');
        });

        const activeBtn = document.getElementById(`tab-${tab}`);
        activeBtn.classList.add('border-indigo-600', 'text-indigo-600', 'dark:text-indigo-400');
        activeBtn.classList.remove('border-transparent', 'text-slate-500', 'dark:text-slate-400');

        // Переключаем контент
        document.getElementById('tab-content-portfolio').classList.add('hidden');
        document.getElementById('tab-content-reviews').classList.add('hidden');
        document.getElementById(`tab-content-${tab}`).classList.remove('hidden');
    };

    /**
     * Генерирует HTML для звезд рейтинга
     */
    function generateStars(rating) {
        const fullStars = Math.floor(rating);
        const hasHalfStar = rating % 1 >= 0.5;
        let starsHtml = '';

        for (let i = 0; i < fullStars; i++) {
            starsHtml += '<i class="bi bi-star-fill text-amber-500 dark:text-amber-400"></i>';
        }

        if (hasHalfStar) {
            starsHtml += '<i class="bi bi-star-half text-amber-500 dark:text-amber-400"></i>';
        }

        const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
        for (let i = 0; i < emptyStars; i++) {
            starsHtml += '<i class="bi bi-star text-amber-500 dark:text-amber-400"></i>';
        }

        return starsHtml;
    }

    /**
     * Возвращает правильный текст для отзывов
     */
    function getReviewsText(count) {
        if (count % 10 === 1 && count % 100 !== 11) {
            return `(${count} отзыв)`;
        } else if ([2, 3, 4].includes(count % 10) && ![12, 13, 14].includes(count % 100)) {
            return `(${count} отзыва)`;
        } else {
            return `(${count} отзывов)`;
        }
    }

    /**
     * Закрывает модальное окно
     */
    window.closeSpecialistModal = function () {
        const modal = document.getElementById('specialist-profile-modal');
        if (modal) {
            modal.style.opacity = '0';
            document.body.style.overflow = '';
            setTimeout(() => modal.remove(), 300);
        }
    };

    // Закрытие по Escape
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            window.closeSpecialistModal();
        }
    });

    // Event delegation для карточек специалистов на главной
    document.addEventListener('click', function (e) {
        const card = e.target.closest('.specialist-card-clickable');
        if (card) {
            e.preventDefault();
            const specialistId = parseInt(card.dataset.specialistId);
            if (specialistId) {
                window.openSpecialistModal(specialistId);
            }
        }

        // Для триггеров в других местах
        const trigger = e.target.closest('.specialist-modal-trigger');
        if (trigger) {
            e.preventDefault();
            const specialistId = parseInt(trigger.dataset.specialistId);
            if (specialistId) {
                window.openSpecialistModal(specialistId);
            }
        }
    });
})();
