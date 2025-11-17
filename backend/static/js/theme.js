document.addEventListener('DOMContentLoaded', function () {
  const toggleBtn = document.getElementById('theme-toggle');
  const iconSpan = document.getElementById('theme-toggle-icon');
  const html = document.documentElement;
  const body = document.body;

  // Функция для применения темы
  function applyTheme(theme) {
    if (theme === 'dark') {
      html.setAttribute('data-bs-theme', 'dark');
      html.classList.add('theme-dark');
      body.classList.add('theme-dark');
      if (iconSpan) iconSpan.textContent = '☀️';
    } else {
      html.setAttribute('data-bs-theme', 'light');
      html.classList.remove('theme-dark');
      body.classList.remove('theme-dark');
      if (iconSpan) iconSpan.textContent = '🌙';
    }
  }

  // Применяем сохраненную тему при загрузке
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'dark') {
    applyTheme('dark');
  } else {
    applyTheme('light');
  }

  // Обработчик клика на кнопку
  if (toggleBtn) {
    toggleBtn.addEventListener('click', function () {
      const current = html.getAttribute('data-bs-theme') || 'light';
      const next = current === 'light' ? 'dark' : 'light';
      applyTheme(next);
      localStorage.setItem('theme', next);
    });
  }
});

