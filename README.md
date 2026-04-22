# 🖥️ ServerOS

**A modular, Umbrel-inspired dashboard for Raspberry Pi (and any Linux server)**

ServerOS is a lightweight Flask-based server operating system dashboard that auto-discovers and manages self-contained web applications. Originally inspired by [OmniHub](https://github.com/ithig124-hub/OmniHub), all modules have been ported and enhanced for a server-based architecture.

---

## ✨ Features

- **Auto-Discovery**: Drop an app folder into `/apps/` with a `manifest.json` and it's automatically registered
- **Umbrel-Style Dashboard**: Beautiful glassmorphic grid layout with smooth animations
- **12+ Built-in Apps**: All ported from OmniHub plus new additions
- **Real System Monitoring**: Uses `psutil` for live CPU, RAM, Disk, Temperature data
- **Wallpaper Manager**: Change dashboard backgrounds with gradients or images
- **World Clock**: 12+ timezone display with day/night indicators
- **Pi Zero 2 W Optimized**: Lightweight Flask backend, minimal resource usage

---

## 🚀 Quick Start

```bash
# 1. Clone / copy ServerOS to your Pi
cd /path/to/ServerOS

# 2. Run setup
chmod +x setup.sh
./setup.sh

# 3. Start the server
python3 server.py
```

Open `http://<your-pi-ip>:5000` in any browser.

---

## 📱 Apps Included

| # | App | Icon | Description | Source |
|---|-----|------|-------------|--------|
| 1 | **3D Globe** | 🌍 | Interactive Three.js globe with pins & labels | OmniHub |
| 2 | **SnackScout** | 🍿 | Food discovery & price comparison | OmniHub |
| 3 | **Library** | 📚 | Internet Archive book search & reader | OmniHub |
| 4 | **Map Explorer** | 🗺️ | Leaflet maps with routing & pins | OmniHub |
| 5 | **Universal Search** | 🔍 | Wikipedia & DuckDuckGo search | OmniHub |
| 6 | **Notes** | 📝 | Markdown note-taking with auto-save | OmniHub |
| 7 | **Smart Dashboard** | 📊 | Widgets: weather, stats, quick links | OmniHub |
| 8 | **GPS Tracker** | 📍 | Live GPS tracking with distance calc | OmniHub |
| 9 | **Wallpaper Manager** | 🎨 | Change dashboard background | **New** |
| 10 | **World Clock** | 🕐 | 12+ timezone display | **New** |
| 11 | **System Monitor** | 📈 | Real psutil CPU/RAM/Disk/Temp stats | **Enhanced** |
| 12 | **File Manager** | 📁 | Browse & view server files | **New** |

---

## 🏗 Architecture

```
ServerOS/
├── server.py              # Flask backend with auto-discovery
├── setup.sh               # One-command setup
├── requirements.txt       # Python dependencies
├── README.md
├── data/                  # Persistent data (notes, wallpaper prefs)
├── templates/
│   ├── dashboard.html     # Main dashboard
│   ├── app_base.html      # Shared app template
│   └── apps/              # Individual app pages
│       ├── globe.html
│       ├── snackscout.html
│       ├── library.html
│       ├── map.html
│       ├── search.html
│       ├── notes.html
│       ├── dashboard.html
│       ├── tracking.html
│       ├── wallpaper.html
│       ├── worldclock.html
│       ├── monitor.html
│       └── filemanager.html
├── static/
│   ├── css/dashboard.css  # Global styles
│   └── js/dashboard.js    # Dashboard JS
└── apps/                  # App modules (auto-discovered)
    ├── globe/
    │   ├── manifest.json
    │   └── routes.py
    ├── snackscout/
    ├── library/
    ├── map/
    ├── search/
    ├── notes/
    ├── dashboard/
    ├── tracking/
    ├── wallpaper/
    ├── worldclock/
    ├── monitor/
    └── filemanager/
```

### How Auto-Discovery Works

1. On startup, `server.py` scans `/apps/` for directories containing `manifest.json`
2. Each manifest defines the app's name, icon, description, category, and color
3. If `routes.py` exists, its `register(app, app_id)` function is called to add Flask blueprints
4. The dashboard template renders all discovered apps as an Umbrel-style grid

### Adding a New App

1. Create a folder: `apps/myapp/`
2. Add `manifest.json`:
   ```json
   {
     "id": "myapp",
     "name": "My App",
     "icon": "🚀",
     "description": "Does something cool",
     "category": "utility",
     "color": "#6366f1"
   }
   ```
3. Optionally add `routes.py` with a `register(app, app_id)` function
4. Create `templates/apps/myapp.html` extending `app_base.html`
5. Restart the server — your app appears on the dashboard!

---

## 🖥 System Monitor (psutil)

The System Monitor uses Python's `psutil` library to pull **real hardware data**:

- **CPU**: Usage %, core count, frequency, per-second history chart
- **RAM**: Total, used, available, swap stats
- **Disk**: Usage %, read/write bytes
- **Temperature**: Reads from hardware sensors (great for Pi Zero 2 W)
- **Network**: Bytes sent/received
- **Processes**: Top 15 by CPU usage

---

## 🎨 UI/UX Design

- **Glassmorphism**: Frosted glass panels with `backdrop-filter: blur()`
- **Umbrel-Style Grid**: Auto-sizing app cards with staggered entry animations
- **Welcome Messages**: Time-based greetings (Good morning/afternoon/evening)
- **Live Stats Bar**: CPU, RAM, temperature in the header
- **Responsive**: Works on desktop, tablet, and mobile
- **Smooth Transitions**: CSS hardware-accelerated animations

---

## ⚙️ Configuration

### Environment

- **Port**: Default 5000 (change in `server.py`)
- **Host**: Binds to `0.0.0.0` (accessible on LAN)
- **Debug**: Enabled by default for development

### Target Hardware

- **Primary**: Raspberry Pi Zero 2 W (ARM, 512MB RAM)
- **Also works**: Any Linux, macOS, or Windows with Python 3.7+

---

## 📄 License

MIT License — based on [OmniHub](https://github.com/ithig124-hub/OmniHub) by ithig124-hub
