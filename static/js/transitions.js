document.addEventListener('DOMContentLoaded', () => {
    // Create transition element
    const transitionElement = document.createElement('div');
    transitionElement.className = 'page-transition';

    // Create loading icon
    const iconElement = document.createElement('div');
    iconElement.className = 'page-transition__icon';
    iconElement.innerHTML = `
        <svg width="40" height="40" viewBox="0 0 40 40">
            <circle cx="20" cy="20" r="18" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" />
        </svg>
    `;
    transitionElement.appendChild(iconElement);

    // Create tiles
    for (let i = 0; i < 5; i++) {
        const tile = document.createElement('div');
        tile.className = 'page-transition__tile';
        transitionElement.appendChild(tile);
    }

    document.body.appendChild(transitionElement);

    function startTransition(url) {
        transitionElement.classList.add('active');
        setTimeout(() => {
            window.location.href = url;
        }, 500);
    }

    // Handle link clicks
    document.addEventListener('click', (e) => {
        const link = e.target.closest('a');
        if (!link) return;

        // Skip external links and special cases
        if (link.target || 
            link.hasAttribute('download') || 
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

    // Remove transition on page load and navigation
    window.addEventListener('pageshow', () => {
        requestAnimationFrame(() => {
            transitionElement.classList.remove('active');
        });
    });
});
