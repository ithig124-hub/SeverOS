# 🖥️ ServerOS

**A modular, Umbrel-inspired dashboard for Raspberry Pi Zero 2 W**

ServerOS is a lightweight, mobile-first command center for your server. It’s designed to run lean on the Pi Zero 2 W while giving you full control over your homelab, learning, and daily tasks.

---

## ✨ Key Features

- **🚀 Auto-Discovery**: Drop any folder into `/apps/` with a `manifest.json` and it appears instantly on the dashboard.
- **📟 Web Terminal**: A stateful, full-command terminal in your browser. Tracks CWD and supports complex commands.
- **🧪 Chem Suite**: A full chemistry learning assistant with Experiment Generators, Year 10 Ions Database, and Smart Revision modes.
- **🛰️ Phone Beacon**: Live GPS tracking that syncs your phone's location to a real-time map on the dashboard.
- **📂 DropShare**: Wireless file transfer directly to a connected USB drive or local storage.
- **🎨 Theme Engine**: Engineered CSS-variable system with **Midnight**, **Glassic**, and **Cyberpunk** styles.
- **🌡️ Resource Guard**: Automatic browser notifications for high CPU temperature or low storage.
- **🛠️ App Smith**: Create and add new apps or web-links visually directly from the dashboard UI.

---

## 🚀 Quick Start

```bash
# 1. Clone to your Pi
git clone https://github.com/ithig124-hub/SeverOS.git
cd SeverOS

# 2. Run the all-in-one setup (Installs Avahi, Tailscale, Python deps)
chmod +x setup.sh
sudo ./setup.sh

# 3. Start the dashboard (or let the auto-boot service handle it!)
python3 server.py
```

---

## 🛰️ Connection Modes

SeverOS is designed to be accessible wherever you are:

### 1. Local Mode (Home/Hotspot)
- **URL**: `http://severos.local:5000`
- **Hotspot SSID**: `ServerOS` | **Pass**: `SeRVEROS`
- **Use Case**: When you are in the same room or traveling with the Pi.

### 2. Remote Mode (Global)
- **URL**: `http://<your-tailscale-ip>:5000`
- **Setup**: Choose 'y' for Tailscale during `setup.sh`. Install the Tailscale app on your phone/laptop.
- **Use Case**: Access your terminal, files, and tracker from anywhere in the world on 5G.

---

## 📱 Apps Included

| App | Icon | Description |
|---|---|---|
| **Chem Suite** | 🧪 | Experiment generator, Ions DB, and Quiz mode. |
| **Terminal** | 📟 | Browser-based SSH replacement. |
| **DropShare** | 📂 | Easy file uploads to USB. |
| **Phone Beacon** | 📍 | Live GPS tracking & mapping. |
| **Mealie Lite** | 🍲 | RAM-optimized recipe manager. |
| **Grocery List** | 📝 | Smart checklist synced with recipes. |
| **Speed Checker** | 🚀 | Real-time internet performance monitoring. |
| **Power Control** | ⚡ | Safe reboot, shutdown, and one-click updates. |
| **System Monitor** | 📈 | Live CPU, RAM, Disk, and Temp stats. |

---

## 🛠️ Maintenance & Backups

### One-Click Update
Go to **Power Control** -> **One-Click Update**. This will pull the latest code and update dependencies automatically.

### Data Backups
To back up your recipes, notes, and logs:
```bash
zip -r severos_backup_$(date +%F).zip data/
```

---

## 📄 License
MIT License — Inspired by Umbrel. Built for the Pi Zero 2 W community.