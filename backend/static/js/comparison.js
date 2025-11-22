function toggleCompare(specialistId) {
    fetch(`/api/compare/toggle/${specialistId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update UI if on comparison page
                if (window.location.pathname.includes('/compare/')) {
                    window.location.reload();
                } else {
                    // Update button state
                    const btns = document.querySelectorAll(`.compare-btn[data-specialist-id="${specialistId}"]`);
                    btns.forEach(btn => {
                        const icon = btn.querySelector('i');
                        if (data.is_in_comparison) {
                            icon.classList.remove('bi-arrow-left-right', 'text-slate-400');
                            icon.classList.add('bi-check-lg', 'text-indigo-600');
                            btn.classList.add('bg-indigo-50', 'dark:bg-indigo-900/30');
                        } else {
                            icon.classList.remove('bi-check-lg', 'text-indigo-600');
                            icon.classList.add('bi-arrow-left-right', 'text-slate-400');
                            btn.classList.remove('bg-indigo-50', 'dark:bg-indigo-900/30');
                        }
                    });

                    // Show toast or notification
                    const message = data.is_in_comparison
                        ? 'Специалист добавлен к сравнению'
                        : 'Специалист удален из сравнения';
                    // You could implement a toast notification here
                }
            } else {
                alert(data.error || 'Произошла ошибка');
            }
        })
        .catch(error => console.error('Error:', error));
}
