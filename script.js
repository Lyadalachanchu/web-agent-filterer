// ===================================
// Mobile Menu Toggle
// ===================================
document.addEventListener('DOMContentLoaded', () => {
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
            
            // Animate hamburger
            const hamburger = mobileMenuToggle.querySelector('.hamburger');
            hamburger.style.transform = navMenu.classList.contains('active') 
                ? 'rotate(45deg)' 
                : 'rotate(0)';
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!mobileMenuToggle.contains(e.target) && !navMenu.contains(e.target)) {
                navMenu.classList.remove('active');
                const hamburger = mobileMenuToggle.querySelector('.hamburger');
                hamburger.style.transform = 'rotate(0)';
            }
        });
    }
});

// ===================================
// Animated Counter for Stats
// ===================================
const animateCounters = () => {
    const counters = document.querySelectorAll('.stat-number');
    
    counters.forEach(counter => {
        const target = parseInt(counter.getAttribute('data-target'));
        const duration = 2000; // 2 seconds
        const increment = target / (duration / 16); // 60fps
        let current = 0;
        
        const updateCounter = () => {
            current += increment;
            if (current < target) {
                counter.textContent = Math.floor(current);
                requestAnimationFrame(updateCounter);
            } else {
                counter.textContent = target;
            }
        };
        
        // Start animation when element is in viewport
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    updateCounter();
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });
        
        observer.observe(counter);
    });
};

// Initialize counters
animateCounters();

// ===================================
// FAQ Accordion
// ===================================
const faqQuestions = document.querySelectorAll('.faq-question');

faqQuestions.forEach(question => {
    question.addEventListener('click', () => {
        const faqItem = question.parentElement;
        const isActive = faqItem.classList.contains('active');
        
        // Close all other FAQ items
        document.querySelectorAll('.faq-item').forEach(item => {
            item.classList.remove('active');
        });
        
        // Toggle current item
        if (!isActive) {
            faqItem.classList.add('active');
        }
    });
});

// ===================================
// Portfolio Filter
// ===================================
const filterButtons = document.querySelectorAll('.filter-btn');
const portfolioItems = document.querySelectorAll('.portfolio-item');

filterButtons.forEach(button => {
    button.addEventListener('click', () => {
        // Remove active class from all buttons
        filterButtons.forEach(btn => btn.classList.remove('active'));
        // Add active class to clicked button
        button.classList.add('active');
        
        const filter = button.getAttribute('data-filter');
        
        portfolioItems.forEach(item => {
            if (filter === 'all' || item.getAttribute('data-category') === filter) {
                item.style.display = 'block';
                // Fade in animation
                item.style.opacity = '0';
                setTimeout(() => {
                    item.style.transition = 'opacity 0.5s ease';
                    item.style.opacity = '1';
                }, 10);
            } else {
                item.style.display = 'none';
            }
        });
    });
});

// ===================================
// Contact Form Submission
// ===================================
const contactForm = document.getElementById('contactForm');
const formSuccess = document.getElementById('formSuccess');

if (contactForm) {
    contactForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        // Simulate form submission
        // In a real application, you would send this data to a server
        const formData = new FormData(contactForm);
        const data = Object.fromEntries(formData);
        
        console.log('Form submitted with data:', data);
        
        // Hide form and show success message
        contactForm.style.display = 'none';
        formSuccess.style.display = 'block';
        
        // Scroll to success message
        formSuccess.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        // Optional: Reset form after a delay
        setTimeout(() => {
            contactForm.reset();
        }, 2000);
    });
}

// ===================================
// Smooth Scroll for Anchor Links
// ===================================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        
        // Don't prevent default for empty hashes or just "#"
        if (href === '#' || href === '') {
            e.preventDefault();
            return;
        }
        
        const target = document.querySelector(href);
        if (target) {
            e.preventDefault();
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ===================================
// Header Scroll Effect
// ===================================
let lastScroll = 0;
const header = document.querySelector('.main-header');

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    
    // Add shadow when scrolled
    if (currentScroll > 0) {
        header.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)';
    } else {
        header.style.boxShadow = '0 1px 2px 0 rgba(0, 0, 0, 0.05)';
    }
    
    lastScroll = currentScroll;
});

// ===================================
// Scroll Reveal Animations
// ===================================
const observeElements = () => {
    const elements = document.querySelectorAll(
        '.feature-card, .testimonial-card, .service-card-large, .portfolio-item, .blog-card, .team-card, .timeline-item, .process-step'
    );
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, index * 100); // Stagger animation
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    elements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(30px)';
        element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(element);
    });
};

// Initialize scroll reveal
observeElements();

// ===================================
// Pagination
// ===================================
const paginationNumbers = document.querySelectorAll('.pagination-number');

paginationNumbers.forEach(button => {
    button.addEventListener('click', () => {
        // Remove active class from all
        paginationNumbers.forEach(btn => btn.classList.remove('active'));
        // Add to clicked
        button.classList.add('active');
        
        // Scroll to top of blog section
        const blogSection = document.querySelector('.blog-section');
        if (blogSection) {
            blogSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});

// ===================================
// Newsletter Form
// ===================================
const newsletterForm = document.querySelector('.newsletter-form');

if (newsletterForm) {
    newsletterForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const emailInput = newsletterForm.querySelector('input[type="email"]');
        const email = emailInput.value;
        
        console.log('Newsletter subscription:', email);
        
        // Show success feedback
        const submitButton = newsletterForm.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        submitButton.textContent = '✓ Subscribed!';
        submitButton.style.background = '#10b981';
        
        // Reset after delay
        setTimeout(() => {
            submitButton.textContent = originalText;
            submitButton.style.background = '';
            emailInput.value = '';
        }, 3000);
    });
}

// ===================================
// Search Form
// ===================================
const searchForm = document.querySelector('.search-form');

if (searchForm) {
    searchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const searchInput = searchForm.querySelector('.search-input');
        const query = searchInput.value;
        
        console.log('Search query:', query);
        
        // In a real application, this would trigger a search
        alert(`Searching for: ${query}`);
    });
}

// ===================================
// Dynamic Year in Footer
// ===================================
const updateFooterYear = () => {
    const footerYear = document.querySelector('.footer-bottom p');
    if (footerYear) {
        const currentYear = new Date().getFullYear();
        footerYear.innerHTML = `&copy; ${currentYear} TechVision. All rights reserved.`;
    }
};

updateFooterYear();

// ===================================
// Loading Animation for Images
// ===================================
const imagePlaceholders = document.querySelectorAll('.image-placeholder');

imagePlaceholders.forEach(placeholder => {
    // Add a subtle pulse animation
    placeholder.style.animation = 'pulse 2s ease-in-out infinite';
});

// Add pulse animation to CSS dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.8;
        }
    }
`;
document.head.appendChild(style);

// ===================================
// Tooltip Functionality (for enhanced UX)
// ===================================
const addTooltips = () => {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = element.getAttribute('data-tooltip');
        tooltip.style.cssText = `
            position: absolute;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-size: 0.875rem;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.3s ease;
            z-index: 10000;
            white-space: nowrap;
        `;
        
        element.addEventListener('mouseenter', (e) => {
            document.body.appendChild(tooltip);
            const rect = element.getBoundingClientRect();
            tooltip.style.left = rect.left + rect.width / 2 - tooltip.offsetWidth / 2 + 'px';
            tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
            setTimeout(() => tooltip.style.opacity = '1', 10);
        });
        
        element.addEventListener('mouseleave', () => {
            tooltip.style.opacity = '0';
            setTimeout(() => tooltip.remove(), 300);
        });
    });
};

addTooltips();

// ===================================
// Lazy Loading for Performance
// ===================================
const lazyLoadElements = () => {
    const lazyElements = document.querySelectorAll('[data-lazy]');
    
    const lazyObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const element = entry.target;
                const src = element.getAttribute('data-lazy');
                element.src = src;
                element.removeAttribute('data-lazy');
                lazyObserver.unobserve(element);
            }
        });
    });
    
    lazyElements.forEach(element => lazyObserver.observe(element));
};

lazyLoadElements();

// ===================================
// Dark Mode Toggle (Optional Enhancement)
// ===================================
const initDarkMode = () => {
    const darkModeToggle = document.getElementById('darkModeToggle');
    
    if (darkModeToggle) {
        const isDarkMode = localStorage.getItem('darkMode') === 'true';
        
        if (isDarkMode) {
            document.body.classList.add('dark-mode');
        }
        
        darkModeToggle.addEventListener('click', () => {
            document.body.classList.toggle('dark-mode');
            const isDark = document.body.classList.contains('dark-mode');
            localStorage.setItem('darkMode', isDark);
        });
    }
};

initDarkMode();

// ===================================
// Console Welcome Message
// ===================================
console.log('%c👋 Welcome to TechVision!', 'font-size: 20px; color: #6366f1; font-weight: bold;');
console.log('%cBuilding the future of technology, one solution at a time.', 'font-size: 14px; color: #6b7280;');
console.log('%cInterested in joining our team? Visit /contact', 'font-size: 12px; color: #9ca3af;');

