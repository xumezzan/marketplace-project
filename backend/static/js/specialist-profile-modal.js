/**
 * Модальное окно профиля специалиста для Profimatch
 */

(function() {
    'use strict';

    /**
     * Показывает модальное окно профиля специалиста
     */
    function showSpecialistProfile(specialistId) {
        // Загружаем данные специалиста через API
        fetch(`/api/users/${specialistId}/`)
            .then(response => response.json())
            .then(data => {
                createModal(data);
            })
            .catch(error => {
                console.error('Ошибка загрузки профиля:', error);
                showNotification('Не удалось загрузить профиль специалиста', 'error');
            });
    }

    /**
     * Создает модальное окно
     */
    function createModal(specialist) {
        // Удаляем существующее модальное окно если есть
        const existing = document.getElementById('specialist-profile-modal');
        if (existing) {
            existing.remove();
        }

        // Создаем модальное окно
        const modal = document.createElement('div');
        modal.id = 'specialist-profile-modal';
        modal.className = 'fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6';
        modal.innerHTML = `
            <div class="absolute inset-0 bg-slate-900/60 backdrop-blur-sm" onclick="closeSpecialistModal()"></div>
            <div class="relative bg-white dark:bg-slate-900 rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col md:flex-row animate-fade-in-up transition-colors duration-300">
                <button onclick="closeSpecialistModal()" class="absolute top-4 right-4 z-10 p-2 bg-white/80 dark:bg-slate-800/80 rounded-full hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-red-500 transition">
                    <i class="bi bi-x-lg text-slate-600 dark:text-slate-300"></i>
                </button>
                <!-- Содержимое будет загружено динамически -->
                <div class="p-6 text-center">
                    <div class="animate-spin text-indigo-600 dark:text-indigo-400">
                        <i class="bi bi-hourglass-split text-2xl"></i>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Загружаем полные данные профиля
        loadProfileContent(specialist.id, modal);
    }

    /**
     * Загружает содержимое профиля
     */
    function loadProfileContent(specialistId, modal) {
        // Здесь можно загрузить дополнительные данные (портфолио, отзывы)
        // Пока используем базовые данные
        const content = modal.querySelector('.p-6');
        if (content) {
            content.innerHTML = `
                <div class="flex flex-col items-center text-center mb-6">
                    <img src="${specialist.avatar || '/static/img/default-avatar.png'}" 
                         alt="${specialist.username}" 
                         class="w-32 h-32 rounded-full object-cover border-4 border-white dark:border-slate-700 shadow-lg mb-4">
                    <h2 class="text-xl font-bold text-slate-900 dark:text-white">${specialist.username}</h2>
                    <p class="text-indigo-600 dark:text-indigo-400 font-medium mb-2">Специалист</p>
                </div>
                <p class="text-slate-600 dark:text-slate-300">Профиль загружается...</p>
            `;
        }
    }

    /**
     * Закрывает модальное окно
     */
    window.closeSpecialistModal = function() {
        const modal = document.getElementById('specialist-profile-modal');
        if (modal) {
            modal.style.opacity = '0';
            setTimeout(() => modal.remove(), 300);
        }
    };

    // Инициализация: добавляем обработчики на кнопки "Профиль"
    document.addEventListener('DOMContentLoaded', function() {
        document.body.addEventListener('click', function(e) {
            const profileBtn = e.target.closest('[data-specialist-id]');
            if (profileBtn) {
                e.preventDefault();
                const specialistId = profileBtn.getAttribute('data-specialist-id');
                if (specialistId) {
                    showSpecialistProfile(specialistId);
                }
            }
        });
    });
})();

