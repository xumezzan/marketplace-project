(function () {
  'use strict';

  // Применяем тему сразу при загрузке скрипта (до DOMContentLoaded)
  (function applyThemeEarly() {
    try {
      const savedTheme = localStorage.getItem('theme') || 'light';
      const html = document.documentElement;
      html.setAttribute('data-bs-theme', savedTheme);
      if (savedTheme === 'dark') {
        html.classList.add('dark-theme');
      }
    } catch (e) {
      // Игнорируем ошибки localStorage
    }
  })();

  function initTheme() {
    // Получаем элементы
    const html = document.documentElement;
    const toggleBtn = document.getElementById('theme-toggle');
    const icon = document.getElementById('theme-icon');

    if (!toggleBtn) {
      console.warn('Theme toggle button not found');
      return;
    }

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
        html.classList.add('dark-theme');
        if (icon) {
          icon.className = 'bi bi-sun-fill text-lg';
        }
      } else {
        html.setAttribute('data-bs-theme', 'light');
        html.classList.remove('dark-theme');
        if (icon) {
          icon.className = 'bi bi-moon-fill text-lg';
        }
      }
    }

    // Применяем сохраненную тему при загрузке
    const savedTheme = getStoredTheme() || 'light';
    applyTheme(savedTheme);

    // Обработчик клика на кнопку переключения
    toggleBtn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();

      const current = html.getAttribute('data-bs-theme') || 'light';
      const next = current === 'light' ? 'dark' : 'light';

      console.log('Switching theme from', current, 'to', next); // Debug

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
  }

  // Запускаем после загрузки DOM
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTheme);
  } else {
    // DOM уже загружен
    initTheme();
  }
})();

