(() => {
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    const initHeader = () => {
        const header = document.querySelector(".site-header");
        const navLinks = document.querySelectorAll(".nav-links a[href^='#']");
        const sections = [...document.querySelectorAll("main section[id]")];

        if (!header) return;

        const updateHeader = () => {
            header.classList.toggle("is-scrolled", window.scrollY > 24);
        };

        const updateActiveLink = () => {
            const current = sections
                .filter((section) => section.getBoundingClientRect().top <= 150)
                .pop();

            navLinks.forEach((link) => {
                link.classList.toggle("is-active", current && link.hash === `#${current.id}`);
            });
        };

        updateHeader();
        updateActiveLink();
        window.addEventListener("scroll", () => {
            updateHeader();
            updateActiveLink();
        }, { passive: true });
    };

    const initRevealAnimations = () => {
        const animatedItems = document.querySelectorAll("[data-animate]");

        if (!animatedItems.length) return;

        if (prefersReducedMotion || !("IntersectionObserver" in window)) {
            animatedItems.forEach((item) => item.classList.add("is-visible"));
            return;
        }

        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) return;
                entry.target.classList.add("is-visible");
                observer.unobserve(entry.target);
            });
        }, {
            rootMargin: "0px 0px -12% 0px",
            threshold: 0.16,
        });

        animatedItems.forEach((item) => observer.observe(item));
    };

    const initCounters = () => {
        const counters = document.querySelectorAll("[data-counter]");

        if (!counters.length) return;

        const renderValue = (counter, value) => {
            const prefix = counter.dataset.prefix || "";
            const suffix = counter.dataset.suffix || "";
            counter.textContent = `${prefix}${Math.round(value)}${suffix}`;
        };

        const animateCounter = (counter) => {
            if (counter.dataset.counted === "true") return;

            counter.dataset.counted = "true";
            const target = Number(counter.dataset.target || "0");
            const duration = prefersReducedMotion ? 0 : 1300;
            const start = performance.now();

            if (!duration) {
                renderValue(counter, target);
                return;
            }

            const tick = (now) => {
                const progress = Math.min((now - start) / duration, 1);
                const eased = 1 - Math.pow(1 - progress, 3);
                renderValue(counter, target * eased);

                if (progress < 1) {
                    requestAnimationFrame(tick);
                }
            };

            requestAnimationFrame(tick);
        };

        if (!("IntersectionObserver" in window)) {
            counters.forEach(animateCounter);
            return;
        }

        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) return;
                animateCounter(entry.target);
                observer.unobserve(entry.target);
            });
        }, { threshold: 0.45 });

        counters.forEach((counter) => observer.observe(counter));
    };

    const initTestimonials = () => {
        const carousel = document.querySelector(".testimonial-carousel");
        if (!carousel) return;

        const cards = [...carousel.querySelectorAll(".testimonial-card")];
        const dotsContainer = carousel.querySelector(".testimonial-dots");
        const prevButton = carousel.querySelector("[data-testimonial-prev]");
        const nextButton = carousel.querySelector("[data-testimonial-next]");
        let currentIndex = Math.max(cards.findIndex((card) => card.classList.contains("is-active")), 0);
        let rotation;

        if (!cards.length || !dotsContainer) return;

        const setSlide = (index) => {
            currentIndex = (index + cards.length) % cards.length;

            cards.forEach((card, cardIndex) => {
                const active = cardIndex === currentIndex;
                card.classList.toggle("is-active", active);
                card.setAttribute("aria-hidden", String(!active));
            });

            dotsContainer.querySelectorAll(".testimonial-dot").forEach((dot, dotIndex) => {
                const active = dotIndex === currentIndex;
                dot.classList.toggle("is-active", active);
                dot.setAttribute("aria-pressed", String(active));
            });
        };

        const stopRotation = () => {
            if (rotation) window.clearInterval(rotation);
        };

        const startRotation = () => {
            if (prefersReducedMotion || cards.length < 2) return;
            stopRotation();
            rotation = window.setInterval(() => setSlide(currentIndex + 1), 5200);
        };

        cards.forEach((_, index) => {
            const dot = document.createElement("button");
            dot.className = "testimonial-dot";
            dot.type = "button";
            dot.setAttribute("aria-label", `Ver testimonio ${index + 1}`);
            dot.addEventListener("click", () => {
                setSlide(index);
                startRotation();
            });
            dotsContainer.appendChild(dot);
        });

        prevButton?.addEventListener("click", () => {
            setSlide(currentIndex - 1);
            startRotation();
        });

        nextButton?.addEventListener("click", () => {
            setSlide(currentIndex + 1);
            startRotation();
        });

        carousel.addEventListener("mouseenter", stopRotation);
        carousel.addEventListener("mouseleave", startRotation);
        carousel.addEventListener("focusin", stopRotation);
        carousel.addEventListener("focusout", startRotation);

        setSlide(currentIndex);
        startRotation();
    };

    const initLightbox = () => {
        const lightbox = document.querySelector(".lightbox");
        const items = [...document.querySelectorAll(".gallery-item img")];

        if (!lightbox || !items.length) return;

        const image = lightbox.querySelector("img");
        const caption = lightbox.querySelector("figcaption");
        const closeButton = lightbox.querySelector(".lightbox-close");
        const prevButton = lightbox.querySelector(".lightbox-prev");
        const nextButton = lightbox.querySelector(".lightbox-next");
        let currentIndex = 0;
        let lastFocusedElement = null;

        const showImage = (index) => {
            currentIndex = (index + items.length) % items.length;
            const selected = items[currentIndex];
            image.src = selected.currentSrc || selected.src;
            image.alt = selected.alt;
            caption.textContent = selected.alt;
        };

        const openLightbox = (index) => {
            lastFocusedElement = document.activeElement;
            showImage(index);
            lightbox.classList.add("is-open");
            lightbox.setAttribute("aria-hidden", "false");
            document.body.classList.add("has-lightbox");
            closeButton?.focus();
        };

        const closeLightbox = () => {
            lightbox.classList.remove("is-open");
            lightbox.setAttribute("aria-hidden", "true");
            document.body.classList.remove("has-lightbox");
            lastFocusedElement?.focus();
        };

        items.forEach((item, index) => {
            item.closest(".gallery-item")?.addEventListener("click", () => openLightbox(index));
        });

        closeButton?.addEventListener("click", closeLightbox);
        prevButton?.addEventListener("click", () => showImage(currentIndex - 1));
        nextButton?.addEventListener("click", () => showImage(currentIndex + 1));

        lightbox.addEventListener("click", (event) => {
            if (event.target === lightbox) closeLightbox();
        });

        document.addEventListener("keydown", (event) => {
            if (!lightbox.classList.contains("is-open")) return;

            if (event.key === "Escape") closeLightbox();
            if (event.key === "ArrowLeft") showImage(currentIndex - 1);
            if (event.key === "ArrowRight") showImage(currentIndex + 1);
        });
    };

    const initWhatsapp = () => {
        const button = document.querySelector(".whatsapp-float");
        if (!button) return;

        const enabled = document.body.dataset.whatsappEnabled !== "false";
        const phone = document.body.dataset.whatsappNumber;

        button.classList.toggle("is-hidden", !enabled);

        if (phone) {
            button.href = `https://wa.me/${phone}?text=Hola%20Hoppets%2C%20quiero%20conocer%20sus%20productos`;
        }
    };

    document.addEventListener("DOMContentLoaded", () => {
        initHeader();
        initRevealAnimations();
        initCounters();
        initTestimonials();
        initLightbox();
        initWhatsapp();
    });
})();
