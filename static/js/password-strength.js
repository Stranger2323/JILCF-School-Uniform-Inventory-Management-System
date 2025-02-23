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

    // Keep track of requirement states
    const requirementStates = new Map();
    requirements.forEach(req => {
        requirementStates.set(req.dataset.requirement, false);
    });

    function validatePassword(password) {
        requirements.forEach(req => {
            const type = req.dataset.requirement;
            const isValid = patterns[type](password);
            
            // Only update if the state has changed
            if (isValid !== requirementStates.get(type)) {
                requirementStates.set(type, isValid);
                
                if (isValid) {
                    // Remove and re-add for animation
                    req.classList.remove('valid');
                    // Force browser reflow
                    void req.offsetWidth;
                    req.classList.add('valid');
                } else {
                    req.classList.remove('valid');
                }
            }
        });
    }

    // Debounce to prevent too frequent updates
    let timeout;
    passwordInput.addEventListener('input', (e) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            validatePassword(e.target.value);
        }, 150); // Slightly longer delay for smoother highlighting
    });
});
