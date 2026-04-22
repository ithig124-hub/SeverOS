/* ═══════════════════════════════════════════════════════════
   ServerOS Dashboard – Chad's Dashboard HiFi Edition
   Glassmorphism + Wallpaper + Floating Dock + Live Metrics
   Seamless Smooth Edition
   ═══════════════════════════════════════════════════════════ */
(function () {
    'use strict';

    // ── DOM refs ──
    var wallpaperBg   = document.getElementById('wallpaperBg');
    var greetingEl    = document.getElementById('greetingText');
    var clockEl       = document.getElementById('headerClock');
    var appGrid       = document.getElementById('appGrid');

    // Metric chips
    var cpuChip  = document.getElementById('cpuChip');
    var ramChip  = document.getElementById('ramChip');
    var diskChip = document.getElementById('diskChip');
    var cpuVal   = document.getElementById('cpuValue');
    var ramVal   = document.getElementById('ramValue');
    var diskVal  = document.getElementById('diskValue');

    // Storage widget
    var storageWidgetFill = document.getElementById('storageWidgetFill');
    var storageUsedLabel  = document.getElementById('storageUsedLabel');
    var storageTotalLabel = document.getElementById('storageTotalLabel');

    // Search
    var searchFloatBtn   = document.getElementById('searchFloatBtn');
    var searchOverlay    = document.getElementById('searchModalOverlay');
    var searchInput      = document.getElementById('searchInput');
    var searchCloseBtn   = document.getElementById('searchCloseBtn');
    var searchResults    = document.getElementById('searchResults');

    // Dock nav items
    var dockNavItems = document.querySelectorAll('.dock-icon[data-section]');

    // App frame overlay
    var appFrameOverlay = document.getElementById('appFrameOverlay');
    var appFrameIframe  = document.getElementById('appFrameIframe');
    var appFrameBackBtn = document.getElementById('appFrameBackBtn');
    var appFrameTitle   = document.getElementById('appFrameTitle');

    // Sections
    var sections = {
        home:     document.getElementById('sectionHome'),
        appstore: document.getElementById('sectionAppStore'),
        storage:  document.getElementById('sectionStorage'),
    };

    // Legacy sidebar nav items (kept for old test compat)
    var navItems = document.querySelectorAll('.nav-item[data-section]');

    // App data cache for search
    var _appCache = [];

    // ── Wallpaper ──
    function loadWallpaper() {
        fetch('/api/wallpaper')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (!wallpaperBg) return;
                if (data.type === 'image' && data.value) {
                    wallpaperBg.style.backgroundImage = 'url(' + data.value + ')';
                } else if (data.type === 'gradient' && data.value) {
                    wallpaperBg.style.backgroundImage = data.value;
                } else {
                    wallpaperBg.style.backgroundImage = 'url(https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1920&q=80)';
                }
            })
            .catch(function() {
                if (wallpaperBg) {
                    wallpaperBg.style.backgroundImage = 'url(https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1920&q=80)';
                }
            });
    }

    // ── Greeting ──
    function updateGreeting() {
        if (!greetingEl) return;
        var h = new Date().getHours();
        var g = 'Good evening';
        if (h < 12) g = 'Good morning';
        else if (h < 17) g = 'Good afternoon';
        greetingEl.textContent = g + ', StrawHaIthi.';
    }

    // ── Clock ──
    function tickClock() {
        if (!clockEl) return;
        clockEl.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    // ── Widget Stats (compact endpoint) ──
    function fetchWidgetStats() {
        fetch('/api/widget/stats')
            .then(function(r) { return r.json(); })
            .then(function(d) {
                if (d.error) return;
                if (cpuVal) {
                    cpuVal.textContent = d.cpu_percent + '%';
                    cpuChip.className = 'metric-chip' + (d.cpu_percent > 80 ? ' crit' : d.cpu_percent > 50 ? ' warn' : '');
                }
                if (ramVal) {
                    ramVal.textContent = d.ram_percent + '%';
                    ramChip.className = 'metric-chip' + (d.ram_percent > 85 ? ' crit' : d.ram_percent > 60 ? ' warn' : '');
                }
                if (diskVal) {
                    diskVal.textContent = d.disk_percent + '%';
                    diskChip.className = 'metric-chip' + (d.disk_percent > 90 ? ' crit' : d.disk_percent > 75 ? ' warn' : '');
                }
                if (storageWidgetFill) {
                    var pct = d.storage_percent || 0;
                    storageWidgetFill.style.width = pct + '%';
                    storageWidgetFill.className = 'storage-widget-fill' + (pct > 90 ? ' crit' : pct > 75 ? ' warn' : '');
                }
                if (storageUsedLabel) {
                    storageUsedLabel.textContent = d.storage_used_tb + ' TB';
                }
                if (storageTotalLabel) {
                    storageTotalLabel.textContent = d.storage_total_tb + ' TB';
                }
            })
            .catch(function() {});
    }

    // Fallback to /api/stats if widget endpoint not available
    function fetchStats() {
        fetch('/api/stats')
            .then(function(r) { return r.json(); })
            .then(function(d) {
                if (d.error) return;
                if (cpuVal && !cpuVal.textContent.includes('%') || cpuVal.textContent === '—%') {
                    cpuVal.textContent = d.cpu_percent + '%';
                }
            })
            .catch(function() {});
    }

    // ── Section Switching ──
    function switchSection(sectionKey) {
        Object.values(sections).forEach(function(s) { if (s) s.classList.remove('active'); });
        dockNavItems.forEach(function(n) { n.classList.remove('active'); });
        navItems.forEach(function(n) { n.classList.remove('active'); });

        if (sections[sectionKey]) {
            sections[sectionKey].classList.add('active');
        }
        dockNavItems.forEach(function(n) {
            if (n.dataset.section === sectionKey) n.classList.add('active');
        });
        navItems.forEach(function(n) {
            if (n.dataset.section === sectionKey) n.classList.add('active');
        });

        if (sectionKey === 'appstore') loadAppStore();
        if (sectionKey === 'storage') loadStorage();
    }

    // Dock navigation
    dockNavItems.forEach(function(nav) {
        nav.addEventListener('click', function(e) {
            var section = this.dataset.section;
            if (sections[section]) {
                e.preventDefault();
                switchSection(section);
            }
        });
    });

    // Legacy sidebar navigation
    navItems.forEach(function(nav) {
        nav.addEventListener('click', function(e) {
            var section = this.dataset.section;
            if (sections[section]) {
                e.preventDefault();
                switchSection(section);
            }
        });
    });

    // ── Seamless App Transitions ──
    function openAppInFrame(url, title) {
        if (!appFrameOverlay || !appFrameIframe) return false;
        appFrameIframe.src = url;
        if (appFrameTitle) appFrameTitle.textContent = title || '';
        appFrameOverlay.classList.remove('closing');
        appFrameOverlay.classList.add('visible');
        return true;
    }

    function closeAppFrame() {
        if (!appFrameOverlay) return;
        appFrameOverlay.classList.add('closing');
        appFrameOverlay.classList.remove('visible');
        setTimeout(function() {
            appFrameOverlay.classList.remove('closing');
            if (appFrameIframe) appFrameIframe.src = 'about:blank';
        }, 400);
    }

    if (appFrameBackBtn) {
        appFrameBackBtn.addEventListener('click', function(e) {
            e.preventDefault();
            closeAppFrame();
        });
    }

    // Intercept app tile clicks for seamless transition
    if (appGrid) {
        appGrid.addEventListener('click', function(e) {
            var tile = e.target.closest('.app-tile');
            if (!tile) return;
            var url = tile.getAttribute('href');
            if (!url || url === '#') return;
            var label = tile.querySelector('.app-label');
            var name = label ? label.textContent : '';
            if (openAppInFrame(url, name)) {
                e.preventDefault();
            }
        });
    }

    // Handle Escape key to close app frame
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            if (appFrameOverlay && appFrameOverlay.classList.contains('visible')) {
                closeAppFrame();
                return;
            }
            closeSearch();
        }
        if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
            e.preventDefault();
            openSearch();
        }
    });

    // ── Search ──
    function openSearch() {
        if (searchOverlay) {
            searchOverlay.classList.add('open');
            if (searchInput) {
                searchInput.value = '';
                searchInput.focus();
            }
            if (searchResults) searchResults.innerHTML = '';
            loadAppCache();

    // Listen for close-app messages from iframe children
    window.addEventListener("message", function(e) {
        if (e.data && e.data.type === "serveros-close-app") {
            closeAppFrame();
        }
    });
        }
    }
    function closeSearch() {
        if (searchOverlay) searchOverlay.classList.remove('open');
    }

    if (searchFloatBtn) searchFloatBtn.addEventListener('click', openSearch);
    if (searchCloseBtn) searchCloseBtn.addEventListener('click', closeSearch);
    if (searchOverlay) {
        searchOverlay.addEventListener('click', function(e) {
            if (e.target === searchOverlay) closeSearch();
        });
    }

    function loadAppCache() {
        if (_appCache.length > 0) return;
        fetch('/api/apps')
            .then(function(r) { return r.json(); })
            .then(function(apps) { _appCache = apps; })
            .catch(function() {});
    }

    if (searchInput) {
        searchInput.addEventListener('input', function() {
            var q = this.value.toLowerCase().trim();
            document.querySelectorAll('.app-tile').forEach(function(tile) {
                var name = (tile.dataset.name || '').toLowerCase();
                var cat  = (tile.dataset.category || '').toLowerCase();
                tile.classList.toggle('hidden', q && !name.includes(q) && !cat.includes(q));
            });
            document.querySelectorAll('.store-card').forEach(function(card) {
                var name = (card.dataset.name || '').toLowerCase();
                card.classList.toggle('hidden', q && !name.includes(q));
            });
            if (!searchResults) return;
            if (!q) { searchResults.innerHTML = ''; return; }
            var filtered = _appCache.filter(function(a) {
                return a.name.toLowerCase().includes(q) || (a.description || '').toLowerCase().includes(q);
            });
            searchResults.innerHTML = '';
            filtered.forEach(function(a) {
                var item = document.createElement('a');
                item.href = a.url;
                item.className = 'search-result-item';
                item.innerHTML =
                    '<div class="search-result-icon" style="background:' + a.color + '">' + a.icon + '</div>' +
                    '<div class="search-result-info">' +
                    '<div class="search-result-name">' + a.name + '</div>' +
                    '<div class="search-result-desc">' + (a.description || '') + '</div>' +
                    '</div>';
                searchResults.appendChild(item);
            });
        });
    }

    // ── Mobile sidebar (legacy compat) ──
    var sidebar = document.getElementById('sidebar');
    var sidebarOverlay = document.getElementById('sidebarOverlay');
    var mobileMenuBtn = document.getElementById('mobileMenuBtn');

    function openMobileSidebar() {
        if (sidebar) sidebar.classList.add('open');
        if (sidebarOverlay) sidebarOverlay.classList.add('visible');
    }
    function closeMobileSidebar() {
        if (sidebar) sidebar.classList.remove('open');
        if (sidebarOverlay) sidebarOverlay.classList.remove('visible');
    }
    if (mobileMenuBtn) mobileMenuBtn.addEventListener('click', openMobileSidebar);
    if (sidebarOverlay) sidebarOverlay.addEventListener('click', closeMobileSidebar);

    // ── App Store section ──
    function loadAppStore() {
        var grid = document.getElementById('appStoreGrid');
        if (!grid || grid.dataset.loaded) return;
        grid.dataset.loaded = '1';

        fetch('/api/apps')
            .then(function(r) { return r.json(); })
            .then(function(apps) {
                grid.innerHTML = '';
                apps.forEach(function(a) {
                    var card = document.createElement('a');
                    card.href = a.url;
                    card.className = 'store-card';
                    card.dataset.name = a.name;
                    card.innerHTML =
                        '<div class="store-icon" style="background:' + a.color + '">' +
                            a.icon +
                        '</div>' +
                        '<div class="store-info">' +
                            '<div class="store-name">' + a.name + '</div>' +
                            '<div class="store-desc">' + a.description + '</div>' +
                        '</div>' +
                        '<span class="store-badge">Installed</span>';
                    grid.appendChild(card);
                });
            });
    }

    // ── Storage section ──
    function loadStorage() {
        loadDiskHealth();
        loadExternalDrives();
    }

    function loadDiskHealth() {
        var el = document.getElementById('diskHealthList');
        if (!el) return;
        fetch('/api/storage/health')
            .then(function(r) { return r.json(); })
            .then(function(disks) {
                if (!disks.length) { el.innerHTML = '<div class="no-drives">No disk info available</div>'; return; }
                el.innerHTML = '';
                disks.forEach(function(d) {
                    var pct = d.percent_used || 0;
                    var cls = pct > 90 ? 'crit' : pct > 75 ? 'warn' : '';
                    var item = document.createElement('div');
                    item.className = 'disk-item';
                    item.innerHTML =
                        '<div class="disk-item-header">' +
                            '<span class="disk-item-name">' + d.device + '</span>' +
                            '<span class="disk-item-mount">' + d.mount + '</span>' +
                        '</div>' +
                        '<div class="disk-progress-bar">' +
                            '<div class="disk-progress-fill ' + cls + '" style="width:' + pct + '%"></div>' +
                        '</div>' +
                        '<div class="disk-item-stats">' +
                            '<span>' + d.used_human + ' / ' + d.total_human + '</span>' +
                            '<span>' + pct + '% used</span>' +
                        '</div>';
                    el.appendChild(item);
                });
            })
            .catch(function() { el.innerHTML = '<div class="no-drives">Could not load disk info</div>'; });
    }

    function loadExternalDrives() {
        var el = document.getElementById('externalDrivesList');
        if (!el) return;
        fetch('/api/storage/drives')
            .then(function(r) { return r.json(); })
            .then(function(drives) {
                if (!drives.length) {
                    el.innerHTML = '<div class="no-drives">🔌 No external drives detected</div>';
                    return;
                }
                el.innerHTML = '';
                drives.forEach(function(drv) {
                    var card = document.createElement('div');
                    card.className = 'drive-card';
                    var partsHtml = '';
                    if (drv.partitions && drv.partitions.length) {
                        partsHtml = '<div class="drive-partitions">' +
                            drv.partitions.map(function(p) {
                                return '<div class="drive-partition">' +
                                    '<span>' + p.name + ' (' + (p.fstype || 'unknown') + ')</span>' +
                                    '<span>' + p.size_human + (p.mountpoint ? ' → ' + p.mountpoint : '') + '</span>' +
                                '</div>';
                            }).join('') + '</div>';
                    }
                    card.innerHTML =
                        '<div class="drive-card-header">' +
                            '<span class="drive-card-icon">💾</span>' +
                            '<span class="drive-card-name">' + drv.model + '</span>' +
                            '<span class="drive-card-size">' + drv.size_human + '</span>' +
                        '</div>' +
                        partsHtml;
                    el.appendChild(card);
                });
            })
            .catch(function() { el.innerHTML = '<div class="no-drives">Could not scan drives</div>'; });
    }

    // ── Init ──
    loadWallpaper();
    updateGreeting();
    tickClock();
    setInterval(tickClock, 1000);
    fetchWidgetStats();
    setInterval(fetchWidgetStats, 4000);
    fetchStats();
    setInterval(fetchStats, 5000);
    loadAppCache();

    // Listen for close-app messages from iframe children
    window.addEventListener("message", function(e) {
        if (e.data && e.data.type === "serveros-close-app") {
            closeAppFrame();
        }
    });
})();
