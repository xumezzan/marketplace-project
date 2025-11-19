/**
 * Модальное окно профиля специалиста для Profimatch
 */

(function() {
    'use strict';

    /**
     * Показывает модальное окно профиля специалиста с данными
     * @param {number} id - ID специалиста
     * @param {string} name - Имя специалиста
     * @param {string} profession - Профессия
     * @param {number} rating - Рейтинг
     * @param {number} reviewsCount - Количество отзывов
     * @param {string} description - Описание
     * @param {string} avatarUrl - URL аватара
     * @param {string} price - Цена
     * @param {number} portfolioCount - Количество работ в портфолио
     */
    window.openSpecialistModal = function(id, name, profession, rating, reviewsCount, description, avatarUrl, price, portfolioCount) {
        // Удаляем существующее модальное окно если есть
        const existing = document.getElementById('specialist-profile-modal');
        if (existing) {
            existing.remove();
        }

        // Создаем модальное окно
        const modal = document.createElement('div');
        modal.id = 'specialist-profile-modal';
        modal.className = 'fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 animate-fade-in';
        modal.style.overflowY = 'auto';
        
        const stars = generateStars(rating);
        const reviewsText = getReviewsText(reviewsCount);
        const portfolioText = getPortfolioText(portfolioCount);
        
        modal.innerHTML = `
            <div class="absolute inset-0 bg-slate-900/60 backdrop-blur-sm" onclick="closeSpecialistModal()"></div>
            <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto animate-fade-in-up transition-colors duration-300">
                <button onclick="closeSpecialistModal()" class="absolute top-4 right-4 z-10 p-2 bg-white/80 rounded-full hover:bg-red-50 hover:text-red-500 transition">
                    <i class="bi bi-x-lg text-slate-600"></i>
                </button>
                
                <div class="p-6 sm:p-8">
                    <!-- Header -->
                    <div class="flex flex-col sm:flex-row items-center sm:items-start gap-6 mb-6 pb-6 border-b border-slate-200">
                        <div class="relative flex-shrink-0">
                            <img src="${avatarUrl}" 
                                 alt="${name}" 
                                 class="w-32 h-32 rounded-full object-cover border-4 border-white shadow-lg">
                            <div class="absolute bottom-2 right-2 bg-green-500 w-5 h-5 rounded-full border-2 border-white"></div>
                        </div>
                        
                        <div class="flex-1 text-center sm:text-left">
                            <h2 class="text-2xl font-bold text-slate-900 mb-2">${name}</h2>
                            <p class="text-indigo-600 font-medium mb-4">${profession}</p>
                            
                            <div class="flex flex-wrap items-center gap-4 justify-center sm:justify-start">
                                <div class="flex items-center gap-2 bg-amber-50 px-3 py-1.5 rounded-lg">
                                    ${stars}
                                    <span class="font-bold text-slate-900">${rating}</span>
                                    <span class="text-slate-500 text-sm">${reviewsText}</span>
                                </div>
                                
                                <div class="flex items-center gap-2 text-slate-600">
                                    <i class="bi bi-briefcase-fill"></i>
                                    <span class="text-sm">${portfolioText}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Description -->
                    <div class="mb-6">
                        <h3 class="text-lg font-semibold text-slate-900 mb-3">О специалисте</h3>
                        <p class="text-slate-600 leading-relaxed">${description}</p>
                    </div>
                    
                    <!-- Price & Actions -->
                    <div class="bg-slate-50 rounded-xl p-6 mb-6">
                        <div class="flex flex-col sm:flex-row items-center justify-between gap-4">
                            <div>
                                <p class="text-sm text-slate-500 mb-1">Стоимость услуг</p>
                                <p class="text-2xl font-bold text-slate-900">${price}</p>
                            </div>
                            <div class="flex gap-3 w-full sm:w-auto">
                                <button onclick="closeSpecialistModal()" class="flex-1 sm:flex-none px-6 py-3 bg-white border border-slate-300 text-slate-700 rounded-lg font-medium hover:bg-slate-50 transition">
                                    Написать
                                </button>
                                <button onclick="closeSpecialistModal()" class="flex-1 sm:flex-none px-6 py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition shadow-md hover:shadow-lg">
                                    Создать задачу
                                </button>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Additional Info -->
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div class="bg-slate-50 rounded-lg p-4">
                            <div class="flex items-center gap-3 mb-2">
                                <div class="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
                                    <i class="bi bi-shield-check text-indigo-600"></i>
                                </div>
                                <div>
                                    <p class="text-sm font-semibold text-slate-900">Проверенный профиль</p>
                                    <p class="text-xs text-slate-500">Верифицирован администрацией</p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="bg-slate-50 rounded-lg p-4">
                            <div class="flex items-center gap-3 mb-2">
                                <div class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                                    <i class="bi bi-clock-history text-green-600"></i>
                                </div>
                                <div>
                                    <p class="text-sm font-semibold text-slate-900">Быстрый отклик</p>
                                    <p class="text-xs text-slate-500">Обычно отвечает в течение часа</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        document.body.style.overflow = 'hidden'; // Блокируем скролл фона
        
        // Плавное появление
        setTimeout(() => {
            modal.style.opacity = '1';
        }, 10);
    };

    /**
     * Генерирует HTML для звезд рейтинга
     */
    function generateStars(rating) {
        const fullStars = Math.floor(rating);
        const hasHalfStar = rating % 1 >= 0.5;
        let starsHtml = '';
        
        for (let i = 0; i < fullStars; i++) {
            starsHtml += '<i class="bi bi-star-fill text-amber-500"></i>';
        }
        
        if (hasHalfStar) {
            starsHtml += '<i class="bi bi-star-half text-amber-500"></i>';
        }
        
        const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
        for (let i = 0; i < emptyStars; i++) {
            starsHtml += '<i class="bi bi-star text-amber-500"></i>';
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
     * Возвращает правильный текст для портфолио
     */
    function getPortfolioText(count) {
        if (count === 1) {
            return `${count} работа`;
        } else if ([2, 3, 4].includes(count)) {
            return `${count} работы`;
        } else {
            return `${count} работ`;
        }
    }

    /**
     * Закрывает модальное окно
     */
    window.closeSpecialistModal = function() {
        const modal = document.getElementById('specialist-profile-modal');
        if (modal) {
            modal.style.opacity = '0';
            document.body.style.overflow = ''; // Восстанавливаем скролл
            setTimeout(() => modal.remove(), 300);
        }
    };

    // Закрытие по Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            window.closeSpecialistModal();
        }
    });
})();

