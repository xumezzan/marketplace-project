document.addEventListener('DOMContentLoaded', function () {
    // Create button if it doesn't exist
    if (!document.getElementById('scroll-to-top')) {
        const buttonHtml = `
            <button id="scroll-to-top" class="fixed bottom-8 right-8 bg-indigo-600 text-white p-3 rounded-full shadow-lg transform translate-y-20 transition-all duration-300 hover:bg-indigo-700 focus:outline-none z-40 opacity-0" aria-label="Scroll to top">
                <i class="bi bi-arrow-up text-xl"></i>
            </button>
        `;
        document.body.insertAdjacentHTML('beforeend', buttonHtml);
    }

    const scrollToTopBtn = document.getElementById('scroll-to-top');

    if (scrollToTopBtn) {
        // Show button when scrolling down
        window.addEventListener('scroll', function () {
            if (window.pageYOffset > 300) {
                scrollToTopBtn.classList.remove('translate-y-20', 'opacity-0');
                scrollToTopBtn.classList.add('translate-y-0', 'opacity-100');
            } else {
                scrollToTopBtn.classList.add('translate-y-20', 'opacity-0');
                scrollToTopBtn.classList.remove('translate-y-0', 'opacity-100');
            }
        });

        // Scroll to top when clicked
        scrollToTopBtn.addEventListener('click', function () {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
});
