document.addEventListener('DOMContentLoaded', function () {
  const toggleBtn = document.getElementById('theme-toggle');
  const iconSpan = document.getElementById('theme-toggle-icon');
  const html = document.documentElement;
  const body = document.body;

  // Функция для применения темы с плавной анимацией
  function applyTheme(theme) {
    // Добавляем класс для плавного перехода
    body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
    
    if (theme === 'dark') {
      html.setAttribute('data-bs-theme', 'dark');
      html.classList.add('theme-dark');
      body.classList.add('theme-dark');
      if (iconSpan) {
        iconSpan.textContent = '☀️';
        iconSpan.style.transition = 'transform 0.3s ease';
        iconSpan.style.transform = 'rotate(180deg)';
        setTimeout(() => {
          iconSpan.style.transform = 'rotate(0deg)';
        }, 300);
      }
    } else {
      html.setAttribute('data-bs-theme', 'light');
      html.classList.remove('theme-dark');
      body.classList.remove('theme-dark');
      if (iconSpan) {
        iconSpan.textContent = '🌙';
        iconSpan.style.transition = 'transform 0.3s ease';
        iconSpan.style.transform = 'rotate(180deg)';
        setTimeout(() => {
          iconSpan.style.transform = 'rotate(0deg)';
        }, 300);
      }
    }
    
    // Убираем transition после применения темы
    setTimeout(() => {
      body.style.transition = '';
    }, 300);
  }

  // Применяем сохраненную тему при загрузке
  const savedTheme = localStorage.getItem('theme') || 'light';
  applyTheme(savedTheme);

  // Обработчик клика на кнопку
  if (toggleBtn) {
    toggleBtn.addEventListener('click', function (e) {
      e.preventDefault();
      const current = html.getAttribute('data-bs-theme') || 'light';
      const next = current === 'light' ? 'dark' : 'light';
      applyTheme(next);
      localStorage.setItem('theme', next);
      
      // Добавляем визуальную обратную связь
      toggleBtn.style.transform = 'scale(0.9)';
      setTimeout(() => {
        toggleBtn.style.transform = '';
      }, 150);
    });
  }
});

