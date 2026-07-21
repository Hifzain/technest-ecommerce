document.addEventListener('DOMContentLoaded', function () {
    // Mobile nav toggle
    const hamburger = document.getElementById('hamburger');
    const navLinks = document.getElementById('navLinks');

    if (hamburger && navLinks) {
        hamburger.addEventListener('click', function () {
            navLinks.classList.toggle('active');
        });
    }

    // Navbar shrink/shadow on scroll
    const navbar = document.getElementById('navbar');
    window.addEventListener('scroll', function () {
        if (window.scrollY > 20) {
            navbar.style.boxShadow = '0 4px 20px rgba(0,0,0,0.15)';
        } else {
            navbar.style.boxShadow = 'none';
        }
    });

    // Auto-dismiss toast messages after 4 seconds
    const toasts = document.querySelectorAll('.toast-message');
    toasts.forEach(function (toast) {
        setTimeout(function () {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(120%)';
            setTimeout(() => toast.remove(), 400);
        }, 4000);
    });
});
document.addEventListener('DOMContentLoaded', function () {
    // Scroll-to-top button visibility + click handler
    const scrollBtn = document.getElementById('scrollTopBtn');
    if (scrollBtn) {
        window.addEventListener('scroll', function () {
            if (window.scrollY > 400) {
                scrollBtn.classList.add('visible');
            } else {
                scrollBtn.classList.remove('visible');
            }
        });

        scrollBtn.addEventListener('click', function () {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // Fade out shimmer skeleton once each product image actually loads
    document.querySelectorAll('.product-img-link img, .main-product-img').forEach(function (img) {
        if (img.complete) {
            img.style.animation = 'none';
            img.style.background = 'none';
        } else {
            img.addEventListener('load', function () {
                img.style.animation = 'none';
                img.style.background = 'none';
            });
        }
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const dropdown = document.getElementById('categoryDropdown');
    const toggle = document.getElementById('categoryDropdownToggle');

    if (dropdown && toggle) {
        toggle.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            dropdown.classList.toggle('open');
        });

        // Close when clicking anywhere else on the page
        document.addEventListener('click', function (e) {
            if (!dropdown.contains(e.target)) {
                dropdown.classList.remove('open');
            }
        });

        // Close after clicking an actual category link
        dropdown.querySelectorAll('.nav-dropdown-menu a').forEach(function (link) {
            link.addEventListener('click', function () {
                dropdown.classList.remove('open');
            });
        });

        // Close on Escape key
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                dropdown.classList.remove('open');
            }
        });
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const searchToggle = document.getElementById('searchToggle');
    const searchOverlay = document.getElementById('searchOverlay');
    const searchInput = document.getElementById('searchInput');
    const searchClose = document.getElementById('searchClose');

    function openSearch() {
        searchOverlay.classList.add('active');
        setTimeout(() => searchInput.focus(), 100);
    }

    function closeSearch() {
        searchOverlay.classList.remove('active');
        searchInput.value = '';
    }

    if (searchToggle && searchOverlay) {
        searchToggle.addEventListener('click', openSearch);
        searchClose.addEventListener('click', closeSearch);

        searchOverlay.addEventListener('click', function (e) {
            if (e.target === searchOverlay) closeSearch();
        });

        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && searchOverlay.classList.contains('active')) {
                closeSearch();
            }
        });
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const slides = document.querySelectorAll('.hero-slide');
    const dots = document.querySelectorAll('.hero-dot');
    const prevBtn = document.getElementById('heroPrev');
    const nextBtn = document.getElementById('heroNext');

    if (slides.length > 1) {
        let currentSlide = 0;
        let autoplayTimer;

        function goToSlide(index) {
            slides[currentSlide].classList.remove('active');
            dots[currentSlide]?.classList.remove('active');

            currentSlide = (index + slides.length) % slides.length;

            slides[currentSlide].classList.add('active');
            dots[currentSlide]?.classList.add('active');
        }

        function nextSlide() {
            goToSlide(currentSlide + 1);
        }

        function prevSlide() {
            goToSlide(currentSlide - 1);
        }

        function startAutoplay() {
            autoplayTimer = setInterval(nextSlide, 6000);
        }

        function resetAutoplay() {
            clearInterval(autoplayTimer);
            startAutoplay();
        }

        nextBtn?.addEventListener('click', () => { nextSlide(); resetAutoplay(); });
        prevBtn?.addEventListener('click', () => { prevSlide(); resetAutoplay(); });

        dots.forEach((dot, i) => {
            dot.addEventListener('click', () => { goToSlide(i); resetAutoplay(); });
        });

        startAutoplay();
    }
});