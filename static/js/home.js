document.addEventListener('DOMContentLoaded', () => {
    // Profile Modal Functionality
    const profileBtn = document.querySelector('.profile-btn');
    const profileModal = document.getElementById('profileModal');
    const closeModal = document.querySelector('.close-modal');

    if (profileBtn && profileModal && closeModal) {
        profileBtn.addEventListener('click', () => {
            profileModal.classList.add('show');
            document.body.style.overflow = 'hidden';
            
            // Add entrance animation
            profileModal.querySelector('.modal-content').style.transform = 'translateY(0)';
            profileModal.querySelector('.modal-content').style.opacity = '1';
        });

        closeModal.addEventListener('click', () => {
            closeModalWithAnimation();
        });

        profileModal.addEventListener('click', (e) => {
            if (e.target === profileModal) {
                closeModalWithAnimation();
            }
        });
    }

    function closeModalWithAnimation() {
        const modalContent = profileModal.querySelector('.modal-content');
        modalContent.style.transform = 'translateY(20px)';
        modalContent.style.opacity = '0';
        
        setTimeout(() => {
            profileModal.classList.remove('show');
            document.body.style.overflow = '';
        }, 300);
    }

    // Card Hover Effects
    const cards = document.querySelectorAll('.dashboard-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-5px)';
            card.style.boxShadow = '0 8px 16px rgba(0,0,0,0.1)';
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
            card.style.boxShadow = '0 4px 6px rgba(0,0,0,0.05)';
        });
    });

    // Notification Badge Animation
    const notificationBadge = document.querySelector('.notification-badge');
    if (notificationBadge) {
        notificationBadge.addEventListener('animationend', () => {
            notificationBadge.classList.remove('pulse');
        });

        // Simulate new notification
        setInterval(() => {
            notificationBadge.classList.add('pulse');
        }, 10000);
    }

    // Stats Counter Animation
    const statValues = document.querySelectorAll('.stat-value');
    statValues.forEach(stat => {
        const finalValue = parseInt(stat.textContent);
        animateValue(stat, 0, finalValue, 1500);
    });

    function animateValue(element, start, end, duration) {
        const range = end - start;
        const increment = range / (duration / 16);
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            element.textContent = Math.floor(current);
            
            if (current >= end) {
                element.textContent = end;
                clearInterval(timer);
            }
        }, 16);
    }

    // Activity List Animation
    const activityItems = document.querySelectorAll('.activity-item');
    activityItems.forEach((item, index) => {
        item.style.animation = `slideIn 0.5s ease forwards ${index * 0.1}s`;
    });
});
