/**
 * MediMitra – Core Application JavaScript
 * GSAP 3D Transitions, Web Audio Synthesizer, Sidebar Toggle & Utilities
 */

document.addEventListener('DOMContentLoaded', () => {
    initStartupSplashScreen();
    initGSAP3DTransitions();
    initGSAP3DCardTilt();
    initSidebar();
    initFlashMessages();
});


/* ============================================================
   GSAP 3D Transitions & Card Tilt
   "have some 3d transitions gsap"
   ============================================================ */

function initGSAP3DTransitions() {
    if (typeof gsap === 'undefined') return;

    // 1. Topbar 3D slide-in
    gsap.from('.topbar', {
        duration: 0.65,
        y: -30,
        opacity: 0,
        ease: 'power3.out'
    });

    // 2. Welcome Banner 3D entrance
    const welcome = document.querySelector('.welcome-banner');
    if (welcome) {
        gsap.from(welcome, {
            duration: 0.85,
            y: 35,
            rotationX: 10,
            transformPerspective: 1000,
            opacity: 0,
            ease: 'power3.out',
            delay: 0.1
        });
    }

    // 3. Staggered 3D entrance for Stat Cards
    const statCards = document.querySelectorAll('.stat-card');
    if (statCards.length > 0) {
        gsap.from(statCards, {
            duration: 0.7,
            y: 30,
            rotationX: -12,
            transformPerspective: 900,
            opacity: 0,
            stagger: 0.08,
            ease: 'back.out(1.4)',
            delay: 0.18
        });
    }

    // 4. Staggered 3D entrance for Content Cards
    const cards = document.querySelectorAll('.dashboard-grid .card, .dashboard-sidebar .card, .chat-container, .upload-card, .result-card');
    if (cards.length > 0) {
        gsap.from(cards, {
            duration: 0.8,
            y: 38,
            rotationX: -8,
            transformPerspective: 1000,
            opacity: 0,
            stagger: 0.1,
            ease: 'power2.out',
            delay: 0.28
        });
    }

    // 5. List items cascade (doses, activities, medicines)
    const listItems = document.querySelectorAll('.dose-item, .activity-item, .medicine-item');
    if (listItems.length > 0) {
        gsap.from(listItems, {
            duration: 0.5,
            x: -18,
            opacity: 0,
            stagger: 0.035,
            ease: 'power2.out',
            delay: 0.38
        });
    }
}

function initGSAP3DCardTilt() {
    if (typeof gsap === 'undefined') return;

    // Apply interactive 3D tilt on desktop and tablet
    const tiltTargets = document.querySelectorAll('.stat-card, .dashboard-grid .card, .welcome-banner, .quick-action-btn');

    tiltTargets.forEach(card => {
        let bounds = null;

        function onMouseEnter() {
            bounds = card.getBoundingClientRect();
        }

        function onMouseMove(e) {
            if (!bounds) bounds = card.getBoundingClientRect();
            const mouseX = e.clientX - bounds.left;
            const mouseY = e.clientY - bounds.top;

            const xPct = (mouseX / bounds.width) - 0.5; // -0.5 to 0.5
            const yPct = (mouseY / bounds.height) - 0.5;

            const rotateX = -yPct * 10; // tilt angle
            const rotateY = xPct * 10;

            gsap.to(card, {
                rotationX: rotateX,
                rotationY: rotateY,
                transformPerspective: 1000,
                scale: 1.015,
                duration: 0.35,
                ease: 'power1.out',
                overwrite: 'auto'
            });
        }

        function onMouseLeave() {
            gsap.to(card, {
                rotationX: 0,
                rotationY: 0,
                scale: 1,
                duration: 0.65,
                ease: 'power2.out',
                overwrite: 'auto'
            });
            bounds = null;
        }

        card.addEventListener('mouseenter', onMouseEnter);
        card.addEventListener('mousemove', onMouseMove);
        card.addEventListener('mouseleave', onMouseLeave);
    });

    // Button micro-press 3D feedback
    const buttons = document.querySelectorAll('.btn, .icon-btn, .bottom-nav-item');
    buttons.forEach(btn => {
        btn.addEventListener('mousedown', () => {
            gsap.to(btn, { scale: 0.94, duration: 0.1, ease: 'power1.in' });
        });
        btn.addEventListener('mouseup', () => {
            gsap.to(btn, { scale: 1, duration: 0.25, ease: 'back.out(2)' });
        });
        btn.addEventListener('mouseleave', () => {
            gsap.to(btn, { scale: 1, duration: 0.2, ease: 'power1.out' });
        });
    });
}


/* ============================================================
   3D Cinematic Startup Sound & Splash Screen Handler
   Synthesizes crystal-clear acoustic medical startup chime (Web Audio API)
   Zero external audio files, zero network delay, 100% offline
   ============================================================ */

let splashAudioCtx = null;

function getAudioContext() {
    if (!splashAudioCtx) {
        const AudioContextClass = window.AudioContext || window.webkitAudioContext;
        if (AudioContextClass) {
            splashAudioCtx = new AudioContextClass();
        }
    }
    return splashAudioCtx;
}

function playMediMitraStartupSound() {
    try {
        const ctx = getAudioContext();
        if (!ctx) return;

        if (ctx.state === 'suspended') {
            ctx.resume();
        }

        const now = ctx.currentTime;

        // Master Gain Node
        const masterGain = ctx.createGain();
        masterGain.gain.setValueAtTime(0.28, now);
        masterGain.connect(ctx.destination);

        // Warm Low-pass Filter
        const filter = ctx.createBiquadFilter();
        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(2800, now);
        filter.connect(masterGain);

        // 1. Sub-bass Warmth Pulse (Grounding frequency: 72 Hz -> 54 Hz)
        const subOsc = ctx.createOscillator();
        const subGain = ctx.createGain();
        subOsc.type = 'sine';
        subOsc.frequency.setValueAtTime(72, now);
        subOsc.frequency.exponentialRampToValueAtTime(54, now + 0.6);

        subGain.gain.setValueAtTime(0.001, now);
        subGain.gain.linearRampToValueAtTime(0.35, now + 0.05);
        subGain.gain.exponentialRampToValueAtTime(0.0001, now + 0.8);

        subOsc.connect(subGain);
        subGain.connect(masterGain);
        subOsc.start(now);
        subOsc.stop(now + 0.85);

        // 2. Chime Note 1: E5 (659.25 Hz) - Gentle bell attack
        playChimeNote(ctx, filter, 659.25, now + 0.04, 0.9, 0.25);

        // 3. Chime Note 2: A5 (880.00 Hz) - Harmonic uplifting rise
        playChimeNote(ctx, filter, 880.00, now + 0.18, 1.1, 0.28);

        // 4. Chime Note 3: C#6 (1108.73 Hz) - Crystal clinical chime
        playChimeNote(ctx, filter, 1108.73, now + 0.36, 1.4, 0.32);

        // 5. High Sparkle Shimmer (E6, 1318.5 Hz) - Delicate overtone
        playChimeNote(ctx, filter, 1318.51, now + 0.48, 1.5, 0.16);

    } catch (err) {
        console.warn('[MediMitra Audio] Startup chime muted:', err);
    }
}

function playChimeNote(ctx, destination, freq, startTime, duration, peakGain) {
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.type = 'sine';
    osc.frequency.setValueAtTime(freq, startTime);

    gain.gain.setValueAtTime(0.0001, startTime);
    gain.gain.linearRampToValueAtTime(peakGain, startTime + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.0001, startTime + duration);

    osc.connect(gain);
    gain.connect(destination);

    osc.start(startTime);
    osc.stop(startTime + duration + 0.05);
}

function initStartupSplashScreen() {
    const splash = document.getElementById('medimitraSplash');
    if (!splash) return;

    // Check if already shown in this session
    const hasShown = sessionStorage.getItem('medimitra_splash_played');
    if (hasShown) {
        splash.style.display = 'none';
        return;
    }

    // Try playing sound immediately
    playMediMitraStartupSound();

    // If browser blocked sound until interaction, catch first touch/click
    const unlockSound = () => {
        playMediMitraStartupSound();
        document.removeEventListener('click', unlockSound);
        document.removeEventListener('touchstart', unlockSound);
    };
    document.addEventListener('click', unlockSound, { once: true });
    document.addEventListener('touchstart', unlockSound, { once: true });

    // Mark as played for session
    sessionStorage.setItem('medimitra_splash_played', '1');

    // Run GSAP 3D entrance and exit timeline if GSAP is available
    if (typeof gsap !== 'undefined') {
        const tl = gsap.timeline();
        tl.fromTo('#splashCube',
            { rotationY: -280, rotationX: 35, scale: 0.3, opacity: 0 },
            { rotationY: 0, rotationX: 0, scale: 1, opacity: 1, duration: 1.1, ease: 'back.out(1.5)' }
        )
        .fromTo('.splash-brand-wrap',
            { opacity: 0, y: 25 },
            { opacity: 1, y: 0, duration: 0.6, ease: 'power3.out' },
            '-=0.5'
        )
        .to(splash, {
            opacity: 0,
            scale: 1.04,
            duration: 0.6,
            ease: 'power2.inOut',
            delay: 0.4,
            onComplete: () => {
                splash.style.display = 'none';
                splash.classList.add('fade-out');
            }
        });
    } else {
        setTimeout(() => {
            splash.classList.add('fade-out');
            setTimeout(() => {
                splash.style.display = 'none';
            }, 600);
        }, 1800);
    }
}

// Function to replay 3D splash & sound anytime user clicks the sparkle button
window.playSplashAnimation = function(forceSound = true) {
    const splash = document.getElementById('medimitraSplash');
    if (!splash) return;

    splash.style.display = 'flex';
    splash.classList.remove('fade-out');
    splash.style.opacity = '1';

    if (forceSound) {
        playMediMitraStartupSound();
    }

    if (typeof gsap !== 'undefined') {
        const tl = gsap.timeline();

        // 3D Cube Spin Entrance
        tl.fromTo('#splashCube', 
            { rotationY: -360, rotationX: 45, scale: 0.25, opacity: 0 },
            { rotationY: 0, rotationX: 0, scale: 1, opacity: 1, duration: 1.1, ease: 'back.out(1.5)' }
        )
        // Typography 3D slide
        .fromTo('.splash-brand-wrap',
            { opacity: 0, y: 25, rotationX: -15, transformPerspective: 800 },
            { opacity: 1, y: 0, rotationX: 0, duration: 0.7, ease: 'power3.out' },
            '-=0.6'
        )
        // Progress bar expansion
        .fromTo('.splash-loader-bar',
            { width: '0%' },
            { width: '100%', duration: 1.1, ease: 'power2.inOut' },
            '-=0.5'
        )
        // Smooth 3D exit fade
        .to(splash, {
            opacity: 0,
            scale: 1.04,
            duration: 0.6,
            ease: 'power2.inOut',
            delay: 0.35,
            onComplete: () => {
                splash.style.display = 'none';
                splash.classList.add('fade-out');
            }
        });
    } else {
        setTimeout(() => {
            splash.classList.add('fade-out');
            setTimeout(() => {
                splash.style.display = 'none';
            }, 600);
        }, 2000);
    }
};


/* ============================================================
   Sidebar Toggle (Mobile)
   ============================================================ */
function initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const menuToggle = document.getElementById('menuToggle');
    const sidebarClose = document.getElementById('sidebarClose');

    if (!sidebar || !menuToggle) return;

    // Create overlay
    let overlay = document.querySelector('.sidebar-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.className = 'sidebar-overlay';
        document.body.appendChild(overlay);
    }

    menuToggle.addEventListener('click', () => {
        sidebar.classList.add('open');
        overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    });

    function closeSidebar() {
        sidebar.classList.remove('open');
        overlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    if (sidebarClose) {
        sidebarClose.addEventListener('click', closeSidebar);
    }
    overlay.addEventListener('click', closeSidebar);
}


/* ============================================================
   Flash Messages — Auto-dismiss
   ============================================================ */
function initFlashMessages() {
    const flashes = document.querySelectorAll('.flash');
    flashes.forEach((flash, i) => {
        setTimeout(() => {
            if (typeof gsap !== 'undefined') {
                gsap.to(flash, {
                    opacity: 0,
                    y: -15,
                    duration: 0.4,
                    ease: 'power2.in',
                    onComplete: () => flash.remove()
                });
            } else {
                flash.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
                flash.style.opacity = '0';
                flash.style.transform = 'translateY(-8px)';
                setTimeout(() => flash.remove(), 400);
            }
        }, 4000 + i * 800);  // stagger removal
    });
}


/* ============================================================
   Utility: Format Date/Time
   ============================================================ */
function formatTime(timeStr) {
    if (!timeStr) return '';
    const [hours, minutes] = timeStr.split(':');
    const h = parseInt(hours, 10);
    const ampm = h >= 12 ? 'PM' : 'AM';
    const h12 = h % 12 || 12;
    return `${h12}:${minutes} ${ampm}`;
}


/* ============================================================
   Utility: API helper
   ============================================================ */
async function apiFetch(url, options = {}) {
    try {
        const defaults = {
            headers: { 'Content-Type': 'application/json' },
        };
        const res = await fetch(url, { ...defaults, ...options });
        if (!res.ok) {
            const err = await res.json().catch(() => ({ error: 'Request failed' }));
            throw new Error(err.error || `HTTP ${res.status}`);
        }
        return await res.json();
    } catch (error) {
        console.error('[MediMitra API]', error);
        showToast(error.message, 'error');
        throw error;
    }
}


/* ============================================================
   Toast Notifications
   ============================================================ */
function showToast(message, type = 'info') {
    const container = document.querySelector('.flash-container') || createToastContainer();
    const iconMap = {
        success: 'check-circle',
        error: 'alert-circle',
        warning: 'alert-triangle',
        info: 'info',
    };

    const toast = document.createElement('div');
    toast.className = `flash flash-${type}`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <i data-lucide="${iconMap[type] || 'info'}"></i>
        <span>${message}</span>
        <button class="flash-close" onclick="this.parentElement.remove()" aria-label="Dismiss">
            <i data-lucide="x"></i>
        </button>
    `;
    container.appendChild(toast);
    lucide.createIcons();

    if (typeof gsap !== 'undefined') {
        gsap.from(toast, {
            y: -20,
            rotationX: 15,
            opacity: 0,
            duration: 0.5,
            ease: 'back.out(1.5)'
        });
    }

    // Auto-dismiss
    setTimeout(() => {
        if (typeof gsap !== 'undefined') {
            gsap.to(toast, {
                opacity: 0,
                y: -15,
                duration: 0.4,
                ease: 'power2.in',
                onComplete: () => toast.remove()
            });
        } else {
            toast.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(-8px)';
            setTimeout(() => toast.remove(), 400);
        }
    }, 5000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.className = 'flash-container';
    const pageContent = document.querySelector('.page-content') || document.body;
    pageContent.parentElement.insertBefore(container, pageContent);
    return container;
}
