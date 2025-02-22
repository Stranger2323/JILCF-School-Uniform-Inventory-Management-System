document.addEventListener('DOMContentLoaded', () => {
    // Password visibility toggle
    const toggleButtons = document.querySelectorAll('.toggle-password');
    
    toggleButtons.forEach(toggleButton => {
        const input = toggleButton.parentElement.querySelector('input');
        const eyeIcon = toggleButton.querySelector('img');
        
        toggleButton.addEventListener('click', () => {
            // Add blink animation classes
            input.classList.add('password-blink');
            eyeIcon.classList.add('eye-blink');
            
            // Toggle password visibility
            const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
            input.setAttribute('type', type);
            eyeIcon.src = type === 'password' ? '/static/img/eye.svg' : '/static/img/eye-off.svg';
            
            // Remove animation classes after animation completes
            setTimeout(() => {
                input.classList.remove('password-blink');
                eyeIcon.classList.remove('eye-blink');
            }, 200); // Match the animation duration
        });
    });

    // Form submission
    const loginForm = document.querySelector('.login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const email = loginForm.querySelector('input[type="email"]').value;
            const password = loginForm.querySelector('input[type="password"]').value;
            const remember = loginForm.querySelector('input[type="checkbox"]')?.checked || false;
            
            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email, password, remember })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    // Show success message
                    showMessage(data.message, 'success');
                    
                    // Redirect after successful login
                    setTimeout(() => {
                        window.location.href = '/dashboard';  // Change this to your dashboard URL
                    }, 1500);
                } else {
                    showMessage(data.message, 'error');
                }
            } catch (error) {
                showMessage('An error occurred. Please try again.', 'error');
                console.error('Login error:', error);
            }
        });
    }

    // Social login buttons
    const googleBtn = document.querySelector('.google-login');
    const facebookBtn = document.querySelector('.facebook-login');
    
    if (googleBtn) {
        googleBtn.addEventListener('click', () => {
            // Implement Google OAuth login
            console.log('Google login clicked');
        });
    }
    
    if (facebookBtn) {
        facebookBtn.addEventListener('click', () => {
            // Implement Facebook OAuth login
            console.log('Facebook login clicked');
        });
    }
});

// Helper function to show messages
function showMessage(message, type = 'info') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;
    
    // Remove any existing messages
    const existingMessages = document.querySelectorAll('.message');
    existingMessages.forEach(msg => msg.remove());
    
    // Add new message
    document.body.appendChild(messageDiv);
    
    // Remove message after 5 seconds
    setTimeout(() => {
        messageDiv.remove();
    }, 5000);
}

// Add message styles to the page
const style = document.createElement('style');
style.textContent = `
.message {
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 15px 25px;
    border-radius: 8px;
    color: white;
    font-weight: 500;
    z-index: 1000;
    animation: slideIn 0.3s ease-out;
}

.message.success {
    background-color: #4CAF50;
}

.message.error {
    background-color: #f44336;
}

.message.info {
    background-color: #2196F3;
}

@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

.password-blink {
    animation: blink 0.2s ease-out;
}

.eye-blink {
    animation: blink 0.2s ease-out;
}

@keyframes blink {
    from {
        opacity: 1;
    }
    to {
        opacity: 0;
    }
}
`;
