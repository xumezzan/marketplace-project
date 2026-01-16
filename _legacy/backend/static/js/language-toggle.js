/**
 * Переключение языка через AJAX
 */
(function() {
    'use strict';

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

    document.addEventListener('DOMContentLoaded', function() {
        // Находим все формы переключения языка
        const languageForms = document.querySelectorAll('form[action*="set_language"]');
        
        languageForms.forEach(function(form) {
            const submitBtn = form.querySelector('button[type="submit"]');
            
            if (submitBtn) {
                submitBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    const formData = new FormData(form);
                    const language = formData.get('language');
                    const nextUrl = formData.get('next') || window.location.pathname;
                    const csrfToken = formData.get('csrfmiddlewaretoken') || getCookie('csrftoken');
                    
                    if (!csrfToken) {
                        console.error('CSRF token not found');
                        if (typeof showNotification === 'function') {
                            showNotification('Ошибка безопасности. Перезагрузите страницу.', 'error');
                        }
                        return;
                    }
                    
                    // Отправляем AJAX запрос
                    fetch(form.action, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': csrfToken,
                            'Content-Type': 'application/x-www-form-urlencoded',
                        },
                        body: new URLSearchParams(formData),
                        credentials: 'same-origin'
                    })
                    .then(response => {
                        if (response.ok || response.redirected) {
                            // Перезагружаем страницу для применения языка
                            window.location.href = nextUrl;
                        } else {
                            console.error('Ошибка при смене языка:', response.status);
                            if (typeof showNotification === 'function') {
                                showNotification('Не удалось изменить язык', 'error');
                            } else {
                                alert('Не удалось изменить язык');
                            }
                        }
                    })
                    .catch(error => {
                        console.error('Ошибка:', error);
                        if (typeof showNotification === 'function') {
                            showNotification('Не удалось изменить язык', 'error');
                        } else {
                            alert('Не удалось изменить язык');
                        }
                    });
                });
            }
        });
    });
})();

