(function () {
  'use strict';

  function initTheme() {
    // Получаем элементы
    const html = document.documentElement;
    const toggleBtn = document.getElementById('theme-toggle');
    const iconSpan = document.getElementById('theme-toggle-icon');

    // Безопасная работа с localStorage
    function getStoredTheme() {
      try {
        return localStorage.getItem('theme');
      } catch (e) {
        console.warn('LocalStorage access denied', e);
        return null;
      }
    }

    function setStoredTheme(theme) {
      try {
        localStorage.setItem('theme', theme);
      } catch (e) {
        console.warn('LocalStorage access denied', e);
      }
    }

    // Функция для применения темы
    function applyTheme(theme) {
      if (theme === 'dark') {
        html.setAttribute('data-bs-theme', 'dark');
        if (iconSpan) iconSpan.textContent = '☀️';
      } else {
        html.setAttribute('data-bs-theme', 'light');
        if (iconSpan) iconSpan.textContent = '🌙';
      }
    }

    // Применяем сохраненную тему
    const savedTheme = getStoredTheme() || 'light';
    applyTheme(savedTheme);

    // Обработчик клика на кнопку переключения
    if (toggleBtn) {
      toggleBtn.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();

        const current = html.getAttribute('data-bs-theme') || 'light';
        const next = current === 'light' ? 'dark' : 'light';

        applyTheme(next);
        setStoredTheme(next);

        // Визуальная обратная связь
        toggleBtn.style.transform = 'scale(0.9)';
        setTimeout(() => {
          toggleBtn.style.transform = '';
        }, 150);
      });
    } else {
      console.warn('Theme toggle button not found');
    }
  }

  // Запускаем после загрузки DOM
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTheme);
  } else {
    initTheme();
  }
})();

