class SearchAutocomplete {
    constructor(inputId, resultsId) {
        this.input = document.getElementById(inputId);
        this.results = document.getElementById(resultsId);
        this.debounceTimer = null;
        this.init();
    }
    
    init() {
        if (!this.input || !this.results) return;

        this.input.addEventListener('input', (e) => {
            clearTimeout(this.debounceTimer);
            this.debounceTimer = setTimeout(() => {
                this.search(e.target.value);
            }, 300);
        });
        
        // Close on click outside
        document.addEventListener('click', (e) => {
            if (!this.input.contains(e.target) && !this.results.contains(e.target)) {
                this.results.classList.add('hidden');
            }
        });

        // Focus input to show results if query exists
        this.input.addEventListener('focus', () => {
            if (this.input.value.length >= 2) {
                this.results.classList.remove('hidden');
            }
        });
    }
    
    async search(query) {
        if (query.length < 2) {
            this.results.classList.add('hidden');
            return;
        }
        
        try {
            const response = await fetch(`/api/search/suggestions/?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            this.displayResults(data);
        } catch (error) {
            console.error('Search error:', error);
        }
    }
    
    displayResults(data) {
        let html = '';
        let hasResults = false;
        
        // Specialists
        if (data.specialists && data.specialists.length > 0) {
            hasResults = true;
            html += '<div class="p-2"><p class="text-xs font-semibold text-slate-500 uppercase dark:text-slate-400">Специалисты</p></div>';
            data.specialists.forEach(specialist => {
                html += `
                    <a href="/specialists/${specialist.id}/" class="block px-4 py-2 hover:bg-slate-100 dark:hover:bg-slate-700 no-underline transition-colors">
                        <div class="flex items-center gap-3">
                            <img src="${specialist.avatar_url}" class="w-10 h-10 rounded-full object-cover" />
                            <div>
                                <p class="font-semibold text-slate-900 dark:text-white">${specialist.username}</p>
                                <p class="text-sm text-slate-500 dark:text-slate-400">${specialist.profession || 'Специалист'}</p>
                            </div>
                        </div>
                    </a>
                `;
            });
        }
        
        // Categories
        if (data.categories && data.categories.length > 0) {
            hasResults = true;
            html += '<div class="p-2 mt-2"><p class="text-xs font-semibold text-slate-500 uppercase dark:text-slate-400">Категории</p></div>';
            data.categories.forEach(category => {
                html += `
                    <a href="/tasks/?category=${category.slug}" class="block px-4 py-2 hover:bg-slate-100 dark:hover:bg-slate-700 no-underline transition-colors">
                        <div class="flex items-center gap-2">
                            <i class="bi bi-grid text-slate-400"></i>
                            <p class="text-slate-900 dark:text-white">${category.name}</p>
                        </div>
                    </a>
                `;
            });
        }

        // Tasks
        if (data.tasks && data.tasks.length > 0) {
            hasResults = true;
            html += '<div class="p-2 mt-2"><p class="text-xs font-semibold text-slate-500 uppercase dark:text-slate-400">Задачи</p></div>';
            data.tasks.forEach(task => {
                html += `
                    <a href="/tasks/${task.id}/" class="block px-4 py-2 hover:bg-slate-100 dark:hover:bg-slate-700 no-underline transition-colors">
                        <div class="flex items-center gap-2">
                            <i class="bi bi-card-text text-slate-400"></i>
                            <div>
                                <p class="text-slate-900 dark:text-white font-medium">${task.title}</p>
                                <p class="text-xs text-slate-500 dark:text-slate-400">${task.budget_display}</p>
                            </div>
                        </div>
                    </a>
                `;
            });
        }
        
        if (!hasResults) {
            html = '<div class="p-4 text-center text-slate-500 dark:text-slate-400">Ничего не найдено</div>';
        }
        
        this.results.innerHTML = html;
        this.results.classList.remove('hidden');
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    new SearchAutocomplete('searchInput', 'searchResults');
});
