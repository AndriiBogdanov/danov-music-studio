// Main JavaScript file for Danov Music Studio

document.addEventListener('DOMContentLoaded', function() {
    // Optimized navbar scroll effect with throttling
    const navbar = document.querySelector('.navbar');
    let ticking = false;
    
    function updateNavbar() {
        if (navbar) {
            if (window.scrollY > 50) {
                navbar.style.background = 'rgba(0, 0, 0, 0.95)';
            } else {
                navbar.style.background = 'rgba(0, 0, 0, 0.9)';
            }
        }
        ticking = false;
    }
    
    window.addEventListener('scroll', function() {
        if (!ticking) {
            requestAnimationFrame(updateNavbar);
            ticking = true;
        }
    }, { passive: true });

    // Ensure navigation links are always clickable
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    navLinks.forEach(link => {
        link.style.pointerEvents = 'auto';
        link.style.position = 'relative';
        link.style.zIndex = '1001';
    });

    // Optimize video loading (simplified)
    const videos = document.querySelectorAll('video');
    videos.forEach(video => {
        // Only pause video when page is not visible (less aggressive)
        document.addEventListener('visibilitychange', function() {
            if (document.hidden && !video.paused) {
                video.pause();
            }
        });
        
        // Add error handling for video loading
        video.addEventListener('error', function() {
            console.log('Video loading error, continuing without video');
        });
    });

    // Smooth scrolling for anchor links (only on same page)
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            // Only prevent default for same-page anchors
            const href = this.getAttribute('href');
            if (href.startsWith('#') && href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });

    // Simplified fade-in animation - only for visible elements
    const cards = document.querySelectorAll('.feature-card, .service-card, .card');
    if (cards.length > 0) {
        try {
            const observerOptions = {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            };

            const observer = new IntersectionObserver(function(entries) {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('fade-in');
                        observer.unobserve(entry.target); // Stop observing once animated
                    }
                });
            }, observerOptions);

            // Only observe if there are elements to observe
            cards.forEach(el => observer.observe(el));
        } catch (error) {
            console.log('IntersectionObserver error:', error);
        }
    }

    // Optimized form validation - only for forms that exist
    const forms = document.querySelectorAll('form');
    if (forms.length > 0) {
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, textarea, select');
            
            inputs.forEach(input => {
                // Real-time validation
                input.addEventListener('blur', function() {
                    validateField(this);
                });
                
                input.addEventListener('input', function() {
                    if (this.classList.contains('is-invalid')) {
                        validateField(this);
                    }
                });
            });
        });
    }



    // Auto-hide alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.parentNode) {
                alert.style.opacity = '0';
                setTimeout(() => {
                    if (alert.parentNode) {
                        alert.remove();
                    }
                }, 300);
            }
        }, 5000);
    });

    // Optimized loading states for buttons
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('btn') && !e.target.disabled && !e.target.classList.contains('btn-success')) {
            e.target.style.transform = 'scale(0.95)';
            setTimeout(() => {
                e.target.style.transform = '';
            }, 150);
        }
    });

    // Tooltip initialization (only if Bootstrap tooltips exist)
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltipTriggerList.length > 0) {
        tooltipTriggerList.forEach(function (tooltipTriggerEl) {
            new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Modal enhancements (only if modals exist)
    const modals = document.querySelectorAll('.modal');
    if (modals.length > 0) {
        modals.forEach(modal => {
            modal.addEventListener('show.bs.modal', function() {
                this.querySelector('.modal-content').style.transform = 'scale(0.7)';
                setTimeout(() => {
                    this.querySelector('.modal-content').style.transform = 'scale(1)';
                }, 50);
            });
        });
    }
});

// Simple Mobile Menu
document.addEventListener('DOMContentLoaded', function() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        // Close menu when clicking on nav links
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth <= 991) {
                    // Use Bootstrap's collapse method
                    const bsCollapse = new bootstrap.Collapse(navbarCollapse, {
                        toggle: false
                    });
                    bsCollapse.hide();
                }
            });
        });
    }
});

// Form validation function
function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let errorMessage = '';

    // Remove existing validation classes
    field.classList.remove('is-valid', 'is-invalid');
    
    // Remove existing error message
    const existingError = field.parentNode.querySelector('.invalid-feedback');
    if (existingError) {
        existingError.remove();
    }

    // Validation rules
    switch (field.type) {
        case 'email':
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (value && !emailRegex.test(value)) {
                isValid = false;
                errorMessage = 'Пожалуйста, введите корректный email адрес';
            }
            break;
            
        case 'tel':
        case 'text':
            if (field.name === 'phone') {
                // Accept any international phone number format
                const phoneRegex = /^\+[\d\s\-\(\)]{10,20}$/;
                if (value && !phoneRegex.test(value)) {
                    isValid = false;
                    errorMessage = 'Пожалуйста, введите корректный номер телефона';
                }
            } else if (field.name === 'name') {
                if (value.length < 2) {
                    isValid = false;
                    errorMessage = 'Имя должно содержать минимум 2 символа';
                }
            }
            break;
            
        case 'date':
            const selectedDate = new Date(value);
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            
            if (value && selectedDate < today) {
                isValid = false;
                errorMessage = 'Нельзя выбрать прошедшую дату';
            }
            break;
            
        case 'time':
            if (value) {
                const [hours, minutes] = value.split(':').map(Number);
                if (hours < 9 || hours > 23) {
                    isValid = false;
                    errorMessage = 'Студия работает с 9:00 до 23:00';
                }
            }
            break;
    }

    // Apply validation result
    if (value) {
        if (isValid) {
            field.classList.add('is-valid');
        } else {
            field.classList.add('is-invalid');
            const errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            errorDiv.textContent = errorMessage;
            field.parentNode.appendChild(errorDiv);
        }
    }
}

// Utility functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

function formatPhoneNumber(phone) {
    const cleaned = phone.replace(/\D/g, '');
    const match = cleaned.match(/^(\d{1})(\d{3})(\d{3})(\d{2})(\d{2})$/);
    if (match) {
        return `+${match[1]} (${match[2]}) ${match[3]}-${match[4]}-${match[5]}`;
    }
    return phone;
}

// Language switcher functions
function toggleLanguageDropdown() {
    const dropdown = document.getElementById('languageDropdown');
    const btn = document.getElementById('languageBtn');
    
    if (dropdown && btn) {
        dropdown.classList.toggle('show');
        btn.classList.toggle('active');
    }
}

function changeLanguage(lang) {
    // Get current URL
    const currentUrl = window.location.pathname;
    
    // Language path mapping
    const langPaths = {
        'en': '/en',
        'ru': '/ru', 
        'uk': '/uk',
        'de': '/de'
    };
    
    // Build new URL
    let newUrl;
    if (lang === 'en') {
        // Remove language prefix for English
        newUrl = currentUrl.replace(/^\/(ru|uk|de)/, '');
        if (newUrl === '') newUrl = '/';
    } else {
        // Add or replace language prefix
        const langPrefix = langPaths[lang];
        if (currentUrl.match(/^\/(ru|uk|de)/)) {
            newUrl = currentUrl.replace(/^\/(ru|uk|de)/, langPrefix);
        } else {
            newUrl = langPrefix + currentUrl;
        }
    }
    
    // Navigate to new URL
    window.location.href = newUrl;
}

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    const dropdown = document.getElementById('languageDropdown');
    const btn = document.getElementById('languageBtn');
    
    if (dropdown && btn && !btn.contains(event.target) && !dropdown.contains(event.target)) {
        dropdown.classList.remove('show');
        btn.classList.remove('active');
    }
});

// Close dropdown on escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        const dropdown = document.getElementById('languageDropdown');
        const btn = document.getElementById('languageBtn');
        
        if (dropdown && btn) {
            dropdown.classList.remove('show');
            btn.classList.remove('active');
        }
    }
});

// Export functions for use in other scripts
window.DanovMusicStudio = {
    showNotification,
    formatPhoneNumber,
    validateField,
    toggleLanguageDropdown,
    changeLanguage
}; 