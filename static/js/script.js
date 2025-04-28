document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const errorMessage = document.getElementById('error-message');
    const loginBox = document.querySelector('.login-box');
    
    // Send POST request to Flask backend
    fetch('/validate_login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `email=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`
    })
    .then(response => response.json())
    .then(data => {
        if(data.success) {
            // Success animation
            loginBox.classList.add('success');
            errorMessage.style.opacity = '0';
            
            // Show success message
            errorMessage.style.color = '#4CAF50';
            errorMessage.textContent = 'Login successful! Redirecting...';
            errorMessage.style.opacity = '1';
            
            // Redirect to home page after 1.5 seconds
            setTimeout(() => {
                window.location.href = '/home';
            }, 1500);
        } else {
            // Error animation
            loginBox.classList.add('shake');
            
            // Show error message
            errorMessage.style.color = '#ff3333';
            errorMessage.textContent = 'Invalid email or password!';
            errorMessage.style.opacity = '1';
            
            // Remove shake class after animation
            setTimeout(() => {
                loginBox.classList.remove('shake');
            }, 500);
        }
    });
});

// Remove success class after animation
document.querySelector('.login-box').addEventListener('animationend', function(e) {
    if(e.animationName === 'success') {
        this.classList.remove('success');
    }
}); 