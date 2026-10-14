/**
 * NovaStore — Core Client-Side Interactions
 * Implements Apple-style banner carousel, search toggle, and mobile drawer.
 */

document.addEventListener("DOMContentLoaded", () => {
    initHeaderSearch();
    initMobileNav();
    initHeroCarousel();
});

/* ==========================================================================
   1. Header Quick Search Toggle
   ========================================================================== */
function initHeaderSearch() {
    const searchBtn = document.getElementById("search-toggle-btn");
    const searchBar = document.getElementById("header-search-bar");
    const searchClose = document.getElementById("search-close-btn");
    const searchInput = document.getElementById("header-search-input");

    if (!searchBtn || !searchBar) return;

    searchBtn.addEventListener("click", () => {
        const isOpen = searchBar.classList.toggle("open");
        if (isOpen && searchInput) {
            setTimeout(() => searchInput.focus(), 100);
        }
    });

    if (searchClose) {
        searchClose.addEventListener("click", () => {
            searchBar.classList.remove("open");
        });
    }

    // Dismiss search bar on Escape key
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && searchBar.classList.contains("open")) {
            searchBar.classList.remove("open");
        }
    });
}

/* ==========================================================================
   2. Mobile Drawer Navigation
   ========================================================================== */
function initMobileNav() {
    const hamburgerBtn = document.getElementById("nav-hamburger-btn");
    const mobileDrawer = document.getElementById("mobile-nav-drawer");

    if (!hamburgerBtn || !mobileDrawer) return;

    hamburgerBtn.addEventListener("click", () => {
        const isOpen = mobileDrawer.classList.toggle("open");
        hamburgerBtn.setAttribute("aria-expanded", isOpen ? "true" : "false");
        document.body.style.overflow = isOpen ? "hidden" : "";
    });

    // Close mobile drawer when clicking links inside
    const drawerLinks = mobileDrawer.querySelectorAll("a");
    drawerLinks.forEach((link) => {
        link.addEventListener("click", () => {
            mobileDrawer.classList.remove("open");
            hamburgerBtn.setAttribute("aria-expanded", "false");
            document.body.style.overflow = "";
        });
    });
}

/* ==========================================================================
   3. Dynamic Hero Carousel Slider
   ========================================================================== */
function initHeroCarousel() {
    const carousel = document.getElementById("hero-carousel");
    if (!carousel) return;

    const slides = carousel.querySelectorAll(".carousel-slide");
    const dots = carousel.querySelectorAll(".carousel-dot");
    const prevBtn = document.getElementById("carousel-prev-btn");
    const nextBtn = document.getElementById("carousel-next-btn");

    if (slides.length <= 1) return;

    let currentIndex = 0;
    let autoPlayTimer = null;
    const intervalMs = 6000;

    function goToSlide(index) {
        slides[currentIndex].classList.remove("active");
        if (dots[currentIndex]) {
            dots[currentIndex].classList.remove("active");
        }

        currentIndex = (index + slides.length) % slides.length;

        slides[currentIndex].classList.add("active");
        if (dots[currentIndex]) {
            dots[currentIndex].classList.add("active");
        }
    }

    function nextSlide() {
        goToSlide(currentIndex + 1);
    }

    function prevSlide() {
        goToSlide(currentIndex - 1);
    }

    function startAutoPlay() {
        stopAutoPlay();
        autoPlayTimer = setInterval(nextSlide, intervalMs);
    }

    function stopAutoPlay() {
        if (autoPlayTimer) {
            clearInterval(autoPlayTimer);
            autoPlayTimer = null;
        }
    }

    // Attach event listeners
    if (nextBtn) {
        nextBtn.addEventListener("click", () => {
            nextSlide();
            startAutoPlay();
        });
    }

    if (prevBtn) {
        prevBtn.addEventListener("click", () => {
            prevSlide();
            startAutoPlay();
        });
    }

    dots.forEach((dot, idx) => {
        dot.addEventListener("click", () => {
            goToSlide(idx);
            startAutoPlay();
        });
    });

    // Pause on hover
    carousel.addEventListener("mouseenter", stopAutoPlay);
    carousel.addEventListener("mouseleave", startAutoPlay);

    // Keyboard navigation when user is interacting
    carousel.setAttribute("tabindex", "0");
    carousel.addEventListener("keydown", (e) => {
        if (e.key === "ArrowLeft") {
            prevSlide();
            startAutoPlay();
        } else if (e.key === "ArrowRight") {
            nextSlide();
            startAutoPlay();
        }
    });

    // Start auto-advance
    startAutoPlay();
}
