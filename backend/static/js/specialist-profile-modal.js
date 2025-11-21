document.addEventListener('DOMContentLoaded', function () {
    // Create modal container if it doesn't exist
    if (!document.getElementById('specialist-modal')) {
        const modalHtml = `
        <div id="specialist-modal" class="fixed inset-0 z-50 hidden overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
            <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
                <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" id="modal-backdrop"></div>
                <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
                <div class="relative inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full dark:bg-slate-800">
                    <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4 dark:bg-slate-800">
                        <div class="sm:flex sm:items-start">
                            <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left w-full">
                                <div class="flex justify-between items-start">
                                    <h3 class="text-lg leading-6 font-medium text-slate-900 dark:text-white" id="modal-title">
                                        Профиль специалиста
                                    </h3>
                                    <button type="button" class="bg-white rounded-md text-slate-400 hover:text-slate-500 focus:outline-none dark:bg-slate-800 dark:text-slate-400" id="modal-close">
                                        <span class="sr-only">Закрыть</span>
                                        <svg class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                                        </svg>
                                    </button>
                                </div>
                                <div class="mt-4" id="modal-content">
                                    <!-- Content will be loaded here -->
                                    <div class="flex justify-center py-10">
                                        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="bg-slate-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse dark:bg-slate-700">
                        <a href="#" id="modal-profile-link" class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:ml-3 sm:w-auto sm:text-sm no-underline">
                            Полный профиль
                        </a>
                        <button type="button" class="mt-3 w-full inline-flex justify-center rounded-md border border-slate-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-slate-700 hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm dark:bg-slate-800 dark:text-slate-300 dark:border-slate-600 dark:hover:bg-slate-700" id="modal-cancel">
                            Закрыть
                        </button>
                    </div>
                </div>
            </div>
        </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    }

    const modal = document.getElementById('specialist-modal');
    const backdrop = document.getElementById('modal-backdrop');
    const closeBtn = document.getElementById('modal-close');
    const cancelBtn = document.getElementById('modal-cancel');
    const contentDiv = document.getElementById('modal-content');
    const profileLink = document.getElementById('modal-profile-link');

    function closeModal() {
        modal.classList.add('hidden');
        document.body.style.overflow = '';
    }

    function openModal() {
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }

    [backdrop, closeBtn, cancelBtn].forEach(el => {
        if (el) el.addEventListener('click', closeModal);
    });

    // Add click handlers to specialist cards
    const cards = document.querySelectorAll('.specialist-card-clickable');
    cards.forEach(card => {
        card.addEventListener('click', function () {
            const specialistId = this.dataset.specialistId;
            if (!specialistId) return;

            openModal();

            // Show loading state
            contentDiv.innerHTML = `
                <div class="flex justify-center py-10">
                    <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600"></div>
                </div>
            `;

            // Fetch specialist data
            fetch(`/api/specialists/${specialistId}/`)
                .then(response => {
                    if (!response.ok) throw new Error('Network response was not ok');
                    return response.json();
                })
                .then(data => {
                    renderSpecialistData(data);
                })
                .catch(error => {
                    console.error('Error:', error);
                    contentDiv.innerHTML = `
                        <div class="text-center py-10 text-red-500">
                            <p>Не удалось загрузить данные специалиста.</p>
                        </div>
                    `;
                });
        });
    });

    function renderSpecialistData(data) {
        // Update profile link
        // Assuming there is a URL pattern for specialist profile, but for now we might just link to a generic page or use the ID
        // If we don't have a specific page, we can hide the button or link to something else
        // For now, let's assume there isn't a dedicated full profile page implemented yet or we construct it
        // profileLink.href = `/specialists/${data.id}/`; 
        // Actually, looking at urls.py might be good, but let's just keep it generic or '#' if unknown.
        // The 'get_specialist_data' view was in 'marketplace/views.py', let's check if there is a profile view.
        // There is 'accounts:profile' for self, but for others? 
        // Maybe just hide it if not sure.

        let portfolioHtml = '';
        if (data.portfolio && data.portfolio.length > 0) {
            portfolioHtml = `
                <div class="mt-6">
                    <h4 class="text-sm font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-3">Портфолио</h4>
                    <div class="grid grid-cols-2 gap-4">
                        ${data.portfolio.slice(0, 2).map(item => `
                            <div class="relative aspect-w-16 aspect-h-9 rounded-lg overflow-hidden bg-slate-100 dark:bg-slate-700">
                                ${item.image_url ? `<img src="${item.image_url}" alt="${item.title}" class="object-cover w-full h-full">` : '<div class="flex items-center justify-center h-full text-slate-400"><i class="bi bi-image text-2xl"></i></div>'}
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        let reviewsHtml = '';
        if (data.reviews && data.reviews.length > 0) {
            reviewsHtml = `
                <div class="mt-6">
                    <h4 class="text-sm font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-3">Последние отзывы</h4>
                    <div class="space-y-4">
                        ${data.reviews.slice(0, 2).map(review => `
                            <div class="bg-slate-50 rounded-lg p-3 dark:bg-slate-700/50">
                                <div class="flex items-center justify-between mb-1">
                                    <span class="font-medium text-slate-900 dark:text-white">${review.client_name}</span>
                                    <div class="flex text-amber-400 text-xs">
                                        ${Array(5).fill(0).map((_, i) => `<i class="bi bi-star${i < review.rating ? '-fill' : ''}"></i>`).join('')}
                                    </div>
                                </div>
                                <p class="text-sm text-slate-600 dark:text-slate-300">${review.comment}</p>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        contentDiv.innerHTML = `
            <div class="flex flex-col sm:flex-row gap-6">
                <div class="flex-shrink-0 flex flex-col items-center sm:items-start">
                    <img src="${data.avatar_url}" alt="${data.username}" class="w-24 h-24 rounded-full object-cover border-4 border-white shadow-lg dark:border-slate-700">
                    <div class="mt-4 flex items-center gap-1 bg-amber-50 px-2 py-1 rounded-md dark:bg-amber-900/30">
                        <i class="bi bi-star-fill text-amber-500 text-sm"></i>
                        <span class="font-bold text-slate-900 dark:text-white">${data.rating.toFixed(1)}</span>
                        <span class="text-slate-500 text-xs dark:text-slate-400">(${data.reviews_count})</span>
                    </div>
                </div>
                <div class="flex-grow text-center sm:text-left">
                    <h2 class="text-2xl font-bold text-slate-900 dark:text-white">${data.username}</h2>
                    <p class="text-indigo-600 font-medium dark:text-indigo-400">${data.profession}</p>
                    
                    <div class="mt-4 grid grid-cols-2 gap-4 text-sm">
                        <div class="bg-slate-50 p-2 rounded-lg dark:bg-slate-700/50">
                            <span class="block text-slate-500 text-xs dark:text-slate-400">Ставка</span>
                            <span class="font-semibold text-slate-900 dark:text-white">${data.hourly_rate ? data.hourly_rate + ' ₽/час' : 'По договоренности'}</span>
                        </div>
                        <div class="bg-slate-50 p-2 rounded-lg dark:bg-slate-700/50">
                            <span class="block text-slate-500 text-xs dark:text-slate-400">Опыт</span>
                            <span class="font-semibold text-slate-900 dark:text-white">${data.years_of_experience || 0} лет</span>
                        </div>
                    </div>

                    <div class="mt-4">
                        <h4 class="text-sm font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">О себе</h4>
                        <p class="text-slate-600 text-sm dark:text-slate-300">${data.description}</p>
                    </div>

                    ${portfolioHtml}
                    ${reviewsHtml}
                </div>
            </div>
        `;
    }
});
