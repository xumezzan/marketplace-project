document.addEventListener('DOMContentLoaded', function () {
  const toggleBtn = document.getElementById('theme-toggle');
  const html = document.documentElement;

  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'dark') {
    html.setAttribute('data-bs-theme', 'dark');
    html.classList.add('theme-dark');
    document.body.classList.add('theme-dark');
  } else {
    html.setAttribute('data-bs-theme', 'light');
    html.classList.remove('theme-dark');
    document.body.classList.remove('theme-dark');
  }

  if (toggleBtn) {
    const iconSpan = document.getElementById('theme-toggle-icon');
    
    toggleBtn.addEventListener('click', function () {
      const current = html.getAttribute('data-bs-theme') || 'light';
      const next = current === 'light' ? 'dark' : 'light';
      
      html.setAttribute('data-bs-theme', next);
      localStorage.setItem('theme', next);
      
      if (next === 'dark') {
        html.classList.add('theme-dark');
        document.body.classList.add('theme-dark');
        if (iconSpan) iconSpan.textContent = '☀️';
      } else {
        html.classList.remove('theme-dark');
        document.body.classList.remove('theme-dark');
        if (iconSpan) iconSpan.textContent = '🌙';
      }
    });
  }
});

