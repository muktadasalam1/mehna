/* ============================================================
   Mehna Admin — Micro-interactions
   Keep lightweight; no frameworks.
   ============================================================ */

document.addEventListener("DOMContentLoaded", () => {
    /* ── Animate stat numbers on load ── */
    document.querySelectorAll(".admin-stat-number").forEach((el) => {
        const target = parseInt(el.textContent.trim(), 10);
        if (isNaN(target)) return;

        el.textContent = "0";
        const duration = 600;
        const start = performance.now();

        function tick(now) {
            const elapsed = now - start;
            const progress = Math.min(elapsed / duration, 1);
            // ease-out cubic
            const eased = 1 - Math.pow(1 - progress, 3);
            el.textContent = Math.round(eased * target);
            if (progress < 1) requestAnimationFrame(tick);
        }

        // delay each card slightly
        const delay = [...document.querySelectorAll(".admin-stat-number")].indexOf(el) * 120;
        setTimeout(() => requestAnimationFrame(tick), 300 + delay);
    });

    /* ── Card tilt on mouse move (subtle) ── */
    document.querySelectorAll(".admin-stat-card").forEach((card) => {
        card.addEventListener("mousemove", (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const cx = rect.width / 2;
            const cy = rect.height / 2;
            const rotateX = ((y - cy) / cy) * -3; // max 3deg
            const rotateY = ((x - cx) / cx) * 3;
            card.style.transform = `perspective(600px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
        });

        card.addEventListener("mouseleave", () => {
            card.style.transform = "";
        });
    });

    /* ── Ripple on button click ── */
    document.querySelectorAll(".admin-btn").forEach((btn) => {
        btn.addEventListener("click", function (e) {
            const ripple = document.createElement("span");
            ripple.style.cssText = `
                position:absolute;border-radius:50%;
                background:currentColor;opacity:0.25;
                width:0;height:0;
                pointer-events:none;
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
                    { width: "0px", height: "0px", opacity: 0.3 },
                    { width: size + "px", height: size + "px", opacity: 0 },
                ],
                { duration: 500, easing: "ease-out" }
            );
            setTimeout(() => ripple.remove(), 500);
        });
    });

    /* ── Nav button active state tracking ── */
    document.querySelectorAll(".admin-nav-btn").forEach((btn) => {
        btn.addEventListener("mousedown", function () {
            this.style.transform = "scale(0.97)";
        });
        btn.addEventListener("mouseup", function () {
            this.style.transform = "";
        });
        btn.addEventListener("mouseleave", function () {
            this.style.transform = "";
        });
    });
});
