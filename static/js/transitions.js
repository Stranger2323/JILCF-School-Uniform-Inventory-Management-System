document.addEventListener('DOMContentLoaded', () => {
    // Create transition element
    const transitionElement = document.createElement('div');
    transitionElement.className = 'page-transition';
    transitionElement.innerHTML = `
        <div class="page-transition__icon">
            <svg viewBox="0 0 50 50">
                <circle cx="25" cy="25" r="20" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round"/>
            </svg>
        </div>
        <div class="page-transition__tile"></div>
        <div class="page-transition__tile"></div>
        <div class="page-transition__tile"></div>
        <div class="page-transition__tile"></div>
        <div class="page-transition__tile"></div>
    `;
    document.body.appendChild(transitionElement);

    // Handle all link clicks
    document.addEventListener('click', (e) => {
        const link = e.target.closest('a');
        if (!link) return;

        // Skip external links and special cases
        if (link.target || link.hasAttribute('download') || 
            link.getAttribute('href').startsWith('#') || 
            link.getAttribute('href').startsWith('tel:') || 
            link.getAttribute('href').startsWith('mailto:')) {
            return;
        }

        e.preventDefault();
        startTransition(link.getAttribute('href'));
    });

    // Handle form submissions
    document.addEventListener('submit', (e) => {
        const form = e.target;
        if (form.method.toLowerCase() === 'get') {
            e.preventDefault();
            startTransition(form.action + '?' + new URLSearchParams(new FormData(form)));
        }
    });

    function startTransition(targetUrl) {
        transitionElement.classList.add('active');
        
        // Navigate after animation starts but before it ends
        setTimeout(() => {
            window.location.href = targetUrl;
        }, 400);
    }

    // Clean up transition on page load
    window.addEventListener('pageshow', (e) => {
        transitionElement.classList.remove('active');
    });

    // Initial page load
    document.addEventListener('DOMContentLoaded', () => {
        transitionElement.classList.remove('active');
    });
});
