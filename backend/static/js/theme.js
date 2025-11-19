(function () {
  'use strict';

  function initTheme() {
    // Получаем элементы
    const html = document.documentElement;
    const toggleBtn = document.getElementById('theme-toggle');
    const icon = document.getElementById('theme-icon');

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
        if (icon) {
          icon.classList.remove('bi-moon-fill');
          icon.classList.add('bi-sun-fill');
        }
      } else {
        html.setAttribute('data-bs-theme', 'light');
        if (icon) {
          icon.classList.remove('bi-sun-fill');
          icon.classList.add('bi-moon-fill');
        }
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

        // Анимация иконки
        if (icon) {
          icon.style.transform = 'rotate(360deg)';
          icon.style.transition = 'transform 0.5s ease';
          setTimeout(() => {
            icon.style.transform = '';
            icon.style.transition = '';
          }, 500);
        }
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

