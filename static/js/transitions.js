// Create transition element with loading animation
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

// Function to start transition
function startTransition(url) {
    transitionElement.classList.add('active');
    setTimeout(() => {
        window.location.href = url;
    }, 700); // Match this with the CSS transition duration
}

// Handle all link clicks for page transitions
document.addEventListener('click', (e) => {
    const link = e.target.closest('a');
    if (!link) return;

    // Skip if it's an external link or has a specific target
    if (link.target || link.hasAttribute('download') || link.getAttribute('href').startsWith('#')) {
        return;
    }

    e.preventDefault();
    const href = link.getAttribute('href');
    startTransition(href);
});

// Handle form submissions
document.addEventListener('submit', (e) => {
    const form = e.target;
    if (form.method.toLowerCase() === 'get') {
        e.preventDefault();
        startTransition(form.action + '?' + new URLSearchParams(new FormData(form)));
    }
});

// Handle back/forward navigation
window.addEventListener('pageshow', (e) => {
    if (e.persisted) {
        transitionElement.classList.remove('active');
    }
});

// Remove transition class when page loads
window.addEventListener('load', () => {
    requestAnimationFrame(() => {
        transitionElement.style.display = 'none';
        requestAnimationFrame(() => {
            transitionElement.style.display = '';
            transitionElement.classList.remove('active');
        });
    });
});
