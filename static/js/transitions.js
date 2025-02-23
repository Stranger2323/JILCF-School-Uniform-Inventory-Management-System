// Create transition element with loading animation
const transitionElement = document.createElement('div');
transitionElement.className = 'page-transition';

// Create loading icon
const iconElement = document.createElement('div');
iconElement.className = 'page-transition__icon';
iconElement.innerHTML = `
    <svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" 
         x="0px" y="0px" width="40px" height="40px" viewBox="0 0 40 40" enable-background="new 0 0 40 40" xml:space="preserve">
        <path opacity="0.2" fill="#fff" d="M20.201,5.169c-8.254,0-14.946,6.692-14.946,14.946c0,8.255,6.692,14.946,14.946,14.946s14.946-6.691,14.946-14.946C35.146,11.861,28.455,5.169,20.201,5.169z M20.201,31.749c-6.425,0-11.634-5.208-11.634-11.634c0-6.425,5.209-11.634,11.634-11.634c6.425,0,11.633,5.209,11.633,11.634C31.834,26.541,26.626,31.749,20.201,31.749z"/>
        <path fill="#fff" d="M26.013,10.047l1.654-2.866c-2.198-1.272-4.743-2.012-7.466-2.012h0v3.312h0C22.32,8.481,24.301,9.057,26.013,10.047z">
            <animateTransform attributeType="xml" attributeName="transform" type="rotate" from="0 20 20" to="360 20 20" dur="0.5s" repeatCount="indefinite"/>
        </path>
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
    }, 1000);
}

// Handle all link clicks for page transitions
document.addEventListener('click', (e) => {
    // Check for any link or element with href
    const link = e.target.closest('a');
    if (link && !link.target && link.href) {
        e.preventDefault();
        startTransition(link.href);
    }
    
    // Check for forgot password link specifically
    const forgotPassword = e.target.closest('.forgot-password');
    if (forgotPassword && forgotPassword.href) {
        e.preventDefault();
        startTransition(forgotPassword.href);
    }
});

// Handle form submissions
document.addEventListener('submit', (e) => {
    const form = e.target;
    if (form.id === 'loginForm' || form.id === 'signupForm' || form.id === 'resetForm') {
        // Don't prevent default here, let the form handle its own submission
        startTransition(window.location.href);
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
