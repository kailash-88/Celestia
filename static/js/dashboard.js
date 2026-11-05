/**
 * MediMitra – Dashboard JavaScript
 * Handles dashboard-specific interactivity and charts.
 */

document.addEventListener('DOMContentLoaded', () => {
    animateStatValues();
    animateAdherenceRing();
});


/* ============================================================
   Animate stat card values on load
   ============================================================ */
function animateStatValues() {
    const statValues = document.querySelectorAll('.stat-value');
    statValues.forEach(el => {
        const target = parseInt(el.textContent, 10);
        if (isNaN(target)) return;

        const suffix = el.textContent.replace(/\d/g, ''); // Capture % or other suffix
        let current = 0;
        const duration = 800;
        const step = Math.max(1, Math.ceil(target / (duration / 16)));
        const startTime = performance.now();

        function tick(now) {
            const elapsed = now - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
            current = Math.round(target * eased);
            el.textContent = current + suffix;
            if (progress < 1) {
                requestAnimationFrame(tick);
            }
        }

        el.textContent = '0' + suffix;
        requestAnimationFrame(tick);
    });
}


/* ============================================================
   Animate the SVG adherence ring on load
   ============================================================ */
function animateAdherenceRing() {
    const ring = document.querySelector('.ring-fill');
    if (!ring) return;

    const circumference = 326.73;
    const targetOffset = parseFloat(ring.getAttribute('stroke-dashoffset'));

    // Start fully hidden
    ring.style.strokeDashoffset = circumference;

    // Animate after a brief delay
    setTimeout(() => {
        ring.style.transition = 'stroke-dashoffset 1.2s ease-out';
        ring.style.strokeDashoffset = targetOffset;
    }, 300);
}
