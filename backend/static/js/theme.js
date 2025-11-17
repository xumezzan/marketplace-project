(function() {
  'use strict';
  
  // Получаем элементы
  const html = document.documentElement;
  const toggleBtn = document.getElementById('theme-toggle');
  const iconSpan = document.getElementById('theme-toggle-icon');
  
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
  
  // Применяем сохраненную тему при загрузке (до рендера страницы)
  const savedTheme = localStorage.getItem('theme') || 'light';
  applyTheme(savedTheme);
  
  // Обработчик клика на кнопку переключения
  if (toggleBtn) {
    toggleBtn.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      
      const current = html.getAttribute('data-bs-theme') || 'light';
      const next = current === 'light' ? 'dark' : 'light';
      
      applyTheme(next);
      localStorage.setItem('theme', next);
      
      // Визуальная обратная связь
      toggleBtn.style.transform = 'scale(0.9)';
      setTimeout(() => {
        toggleBtn.style.transform = '';
      }, 150);
    });
  }
})();

