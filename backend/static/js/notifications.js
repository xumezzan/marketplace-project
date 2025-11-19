/**
 * Система уведомлений (Toast Notifications) для Profimatch
 */

(function() {
    'use strict';

    /**
     * Показывает toast-уведомление
     * @param {string} message - Текст уведомления
     * @param {string} type - Тип: 'success', 'error', 'info', 'warning'
     * @param {number} duration - Длительность в миллисекундах (по умолчанию 4000)
     */
    function showNotification(message, type = 'success', duration = 4000) {
        // Создаем контейнер для уведомлений, если его еще нет
        let container = document.getElementById('notifications-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notifications-container';
            container.className = 'fixed top-20 right-4 z-50 space-y-2';
            document.body.appendChild(container);
        }

        // Создаем элемент уведомления
        const notification = document.createElement('div');
        notification.className = `notification notification-${type} animate-bounce-in`;
        
        // Иконки для разных типов
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };

        // Цвета для разных типов
        const colors = {
            success: 'bg-green-600',
            error: 'bg-red-600',
            warning: 'bg-yellow-600',
            info: 'bg-blue-600'
        };

        notification.className = `${colors[type] || colors.success} text-white px-6 py-3 rounded-lg shadow-xl flex items-center gap-2 min-w-[300px] max-w-[500px]`;
        notification.innerHTML = `
            <span class="text-xl">${icons[type] || icons.success}</span>
            <span class="flex-1">${message}</span>
            <button class="notification-close text-white hover:text-gray-200 transition" onclick="this.parentElement.remove()">
                <i class="bi bi-x-lg"></i>
            </button>
        `;

        // Добавляем в контейнер
        container.appendChild(notification);

        // Автоматически удаляем через указанное время
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            notification.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, duration);
    }

    // Экспортируем функцию глобально
    window.showNotification = showNotification;

    // Обработка Django messages
    document.addEventListener('DOMContentLoaded', function() {
        // Ищем Django messages и преобразуем их в toast-уведомления
        const messages = document.querySelectorAll('.alert-modern, .alert');
        messages.forEach(function(messageEl) {
            const text = messageEl.textContent.trim();
            if (!text) return;

            // Определяем тип по классам
            let type = 'info';
            if (messageEl.classList.contains('alert-success')) {
                type = 'success';
            } else if (messageEl.classList.contains('alert-danger') || messageEl.classList.contains('alert-error')) {
                type = 'error';
            } else if (messageEl.classList.contains('alert-warning')) {
                type = 'warning';
            }

            // Показываем уведомление
            showNotification(text, type);

            // Удаляем оригинальное сообщение
            setTimeout(() => {
                messageEl.remove();
            }, 100);
        });
    });

    // Обработка AJAX-ответов с уведомлениями
    document.body.addEventListener('htmx:afterRequest', function(event) {
        const response = event.detail.xhr.response;
        try {
            const data = JSON.parse(response);
            if (data.notification) {
                showNotification(data.notification.message, data.notification.type || 'success');
            }
        } catch (e) {
            // Не JSON ответ, игнорируем
        }
    });
})();

