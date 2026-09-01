// menu.js
document.addEventListener('DOMContentLoaded', () => {
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    const navOverlay = document.querySelector('.nav-overlay');
    const navItems = document.querySelectorAll('.nav-item');

    function openMenu() {
        menuToggle.classList.add('active');
        navLinks.classList.add('active');
        navOverlay.classList.add('active');
        menuToggle.setAttribute('aria-expanded', 'true');
        menuToggle.setAttribute('aria-label', 'Fechar menu');
        document.body.style.overflow = 'hidden';
    }

    function closeMenu() {
        menuToggle.classList.remove('active');
        navLinks.classList.remove('active');
        navOverlay.classList.remove('active');
        menuToggle.setAttribute('aria-expanded', 'false');
        menuToggle.setAttribute('aria-label', 'Abrir menu');
        document.body.style.overflow = '';
    }

    if (menuToggle && navLinks) {
        menuToggle.addEventListener('click', () => {
            if (navLinks.classList.contains('active')) {
                closeMenu();
            } else {
                openMenu();
            }
        });

        if (navOverlay) {
            navOverlay.addEventListener('click', closeMenu);
        }

        navItems.forEach((link) => {
            link.addEventListener('click', () => {
                if (window.innerWidth <= 768) closeMenu();
            });
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && navLinks.classList.contains('active')) {
                closeMenu();
            }
        });

        window.addEventListener('resize', () => {
            if (window.innerWidth > 768 && navLinks.classList.contains('active')) {
                closeMenu();
            }
        });
    }
});
