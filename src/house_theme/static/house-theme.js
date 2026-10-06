// house-theme — decorative theme particles shared by every family app.
// Ambient emoji drift on every page (falling leaves in fall, bats and
// pumpkins in October, snow at Christmas, hearts + balloons on Valentine's
// Day, ...) plus a matching burst wherever you click.
// Config comes from window.HOUSE_THEME, injected by house_theme/scripts.html
// from the server-resolved theme (themes.py). Purely visual: everything is
// pointer-events:none so it never interferes with real clicks/links.
//
// An empty emoji list (e.g. Black History Month) means "no particle effect".

(function () {
    var config = window.HOUSE_THEME || {};
    var EMOJIS = config.emojis || [];
    var DIRECTION = config.direction === 'rise' ? 'rise' : 'fall';
    var AMBIENT_COUNT = 14;
    var BURST_COUNT = 9;

    if (!EMOJIS.length) return; // this theme has no particle effect

    var prefersReducedMotion = window.matchMedia &&
        window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) return;

    function randomEmoji() {
        return EMOJIS[Math.floor(Math.random() * EMOJIS.length)];
    }

    function initAmbientParticles() {
        var overlay = document.createElement('div');
        overlay.className = 'particle-overlay';
        overlay.setAttribute('aria-hidden', 'true');

        for (var i = 0; i < AMBIENT_COUNT; i++) {
            var particle = document.createElement('span');
            particle.className = 'particle particle-' + DIRECTION;
            particle.textContent = randomEmoji();

            var duration = 9 + Math.random() * 8; // 9-17s per pass
            var delay = -Math.random() * duration; // negative: already mid-flight on load
            var drift = Math.round(Math.random() * 140 - 70) + 'px'; // sideways sway
            var size = Math.round(14 + Math.random() * 14) + 'px';

            particle.style.left = (Math.random() * 100) + '%';
            particle.style.fontSize = size;
            particle.style.animationDuration = duration + 's';
            particle.style.animationDelay = delay + 's';
            particle.style.setProperty('--drift', drift);

            overlay.appendChild(particle);
        }

        document.body.appendChild(overlay);
    }

    function burstParticlesAt(x, y) {
        for (var i = 0; i < BURST_COUNT; i++) {
            var particle = document.createElement('span');
            particle.className = 'particle particle-burst';
            particle.textContent = randomEmoji();
            particle.setAttribute('aria-hidden', 'true');

            var angle = Math.random() * Math.PI * 2;
            var distance = 55 + Math.random() * 95;
            var dx = Math.round(Math.cos(angle) * distance) + 'px';
            var dy = Math.round(Math.sin(angle) * distance) + 'px';
            var size = Math.round(16 + Math.random() * 12) + 'px';

            particle.style.left = x + 'px';
            particle.style.top = y + 'px';
            particle.style.fontSize = size;
            particle.style.setProperty('--dx', dx);
            particle.style.setProperty('--dy', dy);

            document.body.appendChild(particle);

            (function (el) {
                var cleanup = function () { if (el.parentNode) el.remove(); };
                el.addEventListener('animationend', cleanup);
                setTimeout(cleanup, 1200); // safety net if animationend doesn't fire
            })(particle);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAmbientParticles);
    } else {
        initAmbientParticles();
    }

    document.addEventListener('click', function (event) {
        burstParticlesAt(event.clientX, event.clientY);
    });
})();
