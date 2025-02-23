// Create transition element
const transitionElement = document.createElement('div');
transitionElement.className = 'page-transition';
document.body.appendChild(transitionElement);

// Handle all link clicks for page transitions
document.addEventListener('click', (e) => {
    const link = e.target.closest('a');
    if (link && !link.target && link.href) {
        e.preventDefault();
        
        // Start transition animation
        transitionElement.classList.add('active');
        
        // Navigate to new page after transition
        setTimeout(() => {
            window.location.href = link.href;
        }, 300);
    }
});

// Handle back/forward navigation
window.addEventListener('pageshow', (e) => {
    if (e.persisted) {
        transitionElement.classList.remove('active');
    }
});

// Remove transition class when page loads
window.addEventListener('DOMContentLoaded', () => {
    transitionElement.classList.remove('active');
});
