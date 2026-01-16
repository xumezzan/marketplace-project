function toggleFavorite(event, specialistId) {
    event.preventDefault();
    event.stopPropagation();

    const btn = event.currentTarget;
    const icon = btn.querySelector('i');

    fetch(`/api/favorites/toggle/${specialistId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
        .then(response => {
            if (response.status === 401) {
                window.location.href = '/accounts/login/';
                return;
            }
            return response.json();
        })
        .then(data => {
            if (data && data.success) {
                if (data.is_favorite) {
                    icon.classList.remove('bi-heart', 'text-slate-400', 'group-hover:text-red-500');
                    icon.classList.add('bi-heart-fill', 'text-red-500');
                } else {
                    icon.classList.remove('bi-heart-fill', 'text-red-500');
                    icon.classList.add('bi-heart', 'text-slate-400', 'group-hover:text-red-500');

                    // If on favorites page, remove the card
                    if (window.location.pathname.includes('/favorites/')) {
                        const card = btn.closest('.specialist-card');
                        if (card) {
                            card.remove();
                            // Check if list is empty and show empty state if needed
                            const grid = document.querySelector('.grid');
                            if (grid && grid.children.length === 0) {
                                window.location.reload();
                            }
                        }
                    }
                }
            }
        })
        .catch(error => console.error('Error:', error));
}

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
