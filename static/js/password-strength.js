document.addEventListener('DOMContentLoaded', function() {
    const passwordInput = document.getElementById('password');
    const requirements = document.querySelectorAll('.requirement');
    
    // Password validation patterns
    const patterns = {
        length: password => password.length >= 8,
        uppercase: password => /[A-Z]/.test(password),
        lowercase: password => /[a-z]/.test(password),
        number: password => /[0-9]/.test(password),
        special: password => /[!@#$%^&*(),.?":{}|<>]/.test(password)
    };

    function validatePassword(password) {
        requirements.forEach(req => {
            const type = req.dataset.requirement;
            const isValid = patterns[type](password);
            
            req.classList.remove('valid');
            if (isValid) {
                // Remove and re-add the class to restart the animation
                void req.offsetWidth; // Trigger reflow
                req.classList.add('valid');
            }
        });
    }

    passwordInput.addEventListener('input', (e) => {
        validatePassword(e.target.value);
    });
});
