/* ============================================================
   Mehna Admin Layout — Sidebar, Theme, Interactions
   ============================================================ */

document.addEventListener("DOMContentLoaded", () => {
    /* ──────────────────────────────────────────────────────────
       THEME TOGGLE
       ────────────────────────────────────────────────────────── */
    const html = document.documentElement;
    const themeBtn = document.getElementById("theme-toggle");
    const THEME_KEY = "mehna-admin-theme";

    // Load saved theme or default to dark
    const savedTheme = localStorage.getItem(THEME_KEY) || "dark";
    html.setAttribute("data-theme", savedTheme);

    if (themeBtn) {
        themeBtn.addEventListener("click", () => {
            const current = html.getAttribute("data-theme");
            const next = current === "dark" ? "light" : "dark";
            html.setAttribute("data-theme", next);
            localStorage.setItem(THEME_KEY, next);
        });
    }

    /* ──────────────────────────────────────────────────────────
       SIDEBAR TOGGLE (mobile/tablet)
       ────────────────────────────────────────────────────────── */
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("sidebar-overlay");
    const toggleBtn = document.getElementById("sidebar-toggle");
    const closeBtn = document.getElementById("sidebar-close");

    function openSidebar() {
        sidebar.classList.add("open");
        overlay.classList.add("active");
        document.body.style.overflow = "hidden";
    }

    function closeSidebar() {
        sidebar.classList.remove("open");
        overlay.classList.remove("active");
        document.body.style.overflow = "";
    }

    if (toggleBtn) toggleBtn.addEventListener("click", openSidebar);
    if (closeBtn) closeBtn.addEventListener("click", closeSidebar);
    if (overlay) overlay.addEventListener("click", closeSidebar);

    // Close sidebar on Escape
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && sidebar.classList.contains("open")) {
            closeSidebar();
        }
    });

    /* ──────────────────────────────────────────────────────────
       STAT NUMBER COUNTER ANIMATION
       ────────────────────────────────────────────────────────── */
    document.querySelectorAll(".stat-card-value").forEach((el) => {
        const raw = el.textContent.trim();
        const target = parseInt(raw, 10);
        if (isNaN(target)) return;

        el.textContent = "0";
        const duration = 700;
        const start = performance.now();

        function tick(now) {
            const elapsed = now - start;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            el.textContent = Math.round(eased * target);
            if (progress < 1) requestAnimationFrame(tick);
        }

        const delay = [...document.querySelectorAll(".stat-card-value")].indexOf(el) * 80;
        setTimeout(() => requestAnimationFrame(tick), 300 + delay);
    });

    /* ──────────────────────────────────────────────────────────
       CARD TILT ON HOVER (subtle 3D)
       ────────────────────────────────────────────────────────── */
    document.querySelectorAll(".stat-card").forEach((card) => {
        card.addEventListener("mousemove", (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const cx = rect.width / 2;
            const cy = rect.height / 2;
            const rotateX = ((y - cy) / cy) * -2;
            const rotateY = ((x - cx) / cx) * 2;
            card.style.transform = `perspective(800px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-2px)`;
        });

        card.addEventListener("mouseleave", () => {
            card.style.transform = "";
        });
    });

    /* ──────────────────────────────────────────────────────────
       RIPPLE ON BUTTONS
       ────────────────────────────────────────────────────────── */
    document.querySelectorAll(".btn").forEach((btn) => {
        btn.addEventListener("click", function (e) {
            const ripple = document.createElement("span");
            ripple.style.cssText = `
                position:absolute;border-radius:50%;
                background:currentColor;opacity:0.2;
                width:0;height:0;pointer-events:none;
                transform:translate(-50%,-50%);
            `;
            this.style.position = "relative";
            this.style.overflow = "hidden";
            const rect = this.getBoundingClientRect();
            ripple.style.left = (e.clientX - rect.left) + "px";
            ripple.style.top = (e.clientY - rect.top) + "px";
            this.appendChild(ripple);

            const size = Math.max(rect.width, rect.height) * 2;
            ripple.animate(
                [
                    { width: "0px", height: "0px", opacity: 0.25 },
                    { width: size + "px", height: size + "px", opacity: 0 },
                ],
                { duration: 450, easing: "ease-out" }
            );
            setTimeout(() => ripple.remove(), 450);
        });
    });

    /* ──────────────────────────────────────────────────────────
       SEARCH INPUT EXPAND
       ────────────────────────────────────────────────────────── */
    const searchInput = document.querySelector(".topbar-search-input");
    if (searchInput) {
        searchInput.addEventListener("focus", () => {
            searchInput.style.width = "260px";
        });
        searchInput.addEventListener("blur", () => {
            searchInput.style.width = "";
        });
    }

    /* ──────────────────────────────────────────────────────────
       STAGGERED ROW ANIMATIONS
       ────────────────────────────────────────────────────────── */
    document.querySelectorAll(".row-item, .data-table tbody tr").forEach((row, i) => {
        row.style.opacity = "0";
        row.style.animation = `fadeSlideUp 0.35s var(--ease) ${i * 40}ms forwards`;
    });
});
