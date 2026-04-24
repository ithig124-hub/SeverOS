/* ══════
   ServerOS Dashboard – Chad's Dashboard HiFi Edition
   ══════ */
(function () {
    'use strict';
    // JS logic...
})();

// ── Theme Engineering ──
function loadThemes() {
    fetch('/api/themes')
        .then(r => r.json())
        .then(themes => {
            window.serverosThemes = themes;
            const savedTheme = localStorage.getItem('serveros-theme');
            if (savedTheme && themes[savedTheme]) applyTheme(savedTheme);
        });
}

function applyTheme(themeName) {
    const theme = window.serverosThemes[themeName];
    if (!theme) return;
    for (const [key, value] of Object.entries(theme)) {
        document.documentElement.style.setProperty(key, value);
    }
    localStorage.setItem('serveros-theme', themeName);
}
