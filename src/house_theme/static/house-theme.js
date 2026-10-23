// house-theme — decorative theme particles shared by every family app.
// Ambient emoji drift on every page (falling leaves in fall, bats and
// pumpkins in October, snow at Christmas, hearts + balloons on Valentine's
// Day, ...) plus a matching burst wherever you click.
// Config comes from data- attributes on the script tag, written by
// house_theme/scripts.html from the server-resolved theme (themes.py). Purely visual: everything is
// pointer-events:none so it never interferes with real clicks/links.
//
// An empty emoji list (e.g. Black History Month) means "no particle effect".
//
// On/off toggle (v1.3.0): a small round button in the bottom-left corner
// turns the particles (ambient + click bursts) off and on. The choice is
// saved in localStorage, so it's remembered per device, per app. An app can
// place the button itself: any element with a data-house-particles-toggle
// attribute is used instead of the floating one. HOUSE_THEME_PARTICLES=off
// in the app's .env turns particles off entirely (no button).

(function () {
    // Config comes from data- attributes on this <script> tag
    // (house_theme/scripts.html); window.HOUSE_THEME still works if set.
    var el = document.currentScript;
    var config = window.HOUSE_THEME || {};
    if (!window.HOUSE_THEME && el && el.dataset.emojis) {
        try {
            config = {
                key: el.dataset.themeKey,
                emojis: JSON.parse(el.dataset.emojis),
                direction: el.dataset.direction,
                particles: el.dataset.particles
            };
        } catch (e) { config = {}; }
    }
    var EMOJIS = config.emojis || [];
    var DIRECTION = config.direction === 'rise' ? 'rise' : 'fall';
    var AMBIENT_COUNT = 14;
    var BURST_COUNT = 9;
    var STORAGE_KEY = 'house-theme-particles';

    if (config.particles === 'off') return; // turned off for this app (.env)
    if (!EMOJIS.length) return; // this theme has no particle effect

    var prefersReducedMotion = window.matchMedia &&
        window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) return;

    // localStorage can throw (private mode, blocked storage); default to on.
    function loadEnabled() {
        try { return window.localStorage.getItem(STORAGE_KEY) !== 'off'; }
        catch (e) { return true; }
    }
    function saveEnabled(on) {
        try {
            if (on) window.localStorage.removeItem(STORAGE_KEY);
            else window.localStorage.setItem(STORAGE_KEY, 'off');
        } catch (e) { /* not remembered; still toggles for this page */ }
    }

    var enabled = loadEnabled();
    var overlay = null;
    var toggles = [];

    function randomEmoji() {
        return EMOJIS[Math.floor(Math.random() * EMOJIS.length)];
    }

    function buildOverlay() {
        overlay = document.createElement('div');
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

    function render() {
        if (enabled && !overlay) buildOverlay();
        if (overlay) overlay.hidden = !enabled;
        var label = enabled ? 'Turn off falling decorations'
                            : 'Turn on falling decorations';
        toggles.forEach(function (btn) {
            btn.setAttribute('aria-pressed', enabled ? 'true' : 'false');
            btn.setAttribute('aria-label', label);
            btn.title = label;
            btn.classList.toggle('is-off', !enabled);
        });
    }

    function onToggle(event) {
        event.preventDefault();
        enabled = !enabled;
        saveEnabled(enabled);
        render();
    }

    function setUpToggles() {
        var custom = document.querySelectorAll('[data-house-particles-toggle]');
        if (custom.length) {
            toggles = Array.prototype.slice.call(custom);
        } else {
            var btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'house-particles-toggle';
            var icon = document.createElement('span');
            icon.setAttribute('aria-hidden', 'true');
            icon.textContent = EMOJIS[0];
            btn.appendChild(icon);
            document.body.appendChild(btn);
            toggles = [btn];
        }
        toggles.forEach(function (btn) {
            btn.addEventListener('click', onToggle);
        });
    }

    function start() {
        setUpToggles();
        render();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', start);
    } else {
        start();
    }

    document.addEventListener('click', function (event) {
        if (!enabled) return;
        var t = event.target;
        if (t && t.closest && t.closest(
            '.house-particles-toggle, [data-house-particles-toggle]')) return;
        burstParticlesAt(event.clientX, event.clientY);
    });
})();
