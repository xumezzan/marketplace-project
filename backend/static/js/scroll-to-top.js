/**
 * Scroll to Top Button
 * Плавная прокрутка к верху страницы
 */

(function() {
    'use strict';
    
    // Создаем кнопку
    const scrollButton = document.createElement('button');
    scrollButton.innerHTML = '<i class="bi bi-arrow-up"></i>';
    scrollButton.className = 'scroll-to-top';
    scrollButton.setAttribute('aria-label', 'Наверх');
    scrollButton.style.cssText = `
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        width: 3rem;
        height: 3rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 50%;
        cursor: pointer;
        display: none;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
        z-index: 1000;
    `;
    
    // Добавляем hover эффект
    scrollButton.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-4px)';
        this.style.boxShadow = '0 8px 20px rgba(102, 126, 234, 0.6)';
    });
    
    scrollButton.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0)';
        this.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.4)';
    });
    
    // Добавляем кнопку в body
    document.body.appendChild(scrollButton);
    
    // Показываем/скрываем кнопку при прокрутке
    function toggleScrollButton() {
        if (window.pageYOffset > 300) {
            scrollButton.style.display = 'flex';
        } else {
            scrollButton.style.display = 'none';
        }
    }
    
    // Плавная прокрутка к верху
    scrollButton.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    // Слушаем событие прокрутки
    window.addEventListener('scroll', toggleScrollButton);
    
    // Проверяем при загрузке страницы
    toggleScrollButton();
    
    // Поддержка темной темы
    function updateButtonTheme() {
        const isDark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
        if (isDark) {
            scrollButton.style.background = 'linear-gradient(135deg, #818cf8 0%, #6366f1 100%)';
        } else {
            scrollButton.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
        }
    }
    
    // Обновляем тему при изменении
    const observer = new MutationObserver(updateButtonTheme);
    observer.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['data-bs-theme']
    });
    
    // Инициализация темы
    updateButtonTheme();
})();

