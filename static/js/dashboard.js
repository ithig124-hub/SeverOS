// ── Resource Guard ──
let lastNotificationTime = 0;
function checkResourceGuard(stats) {
    if (!("Notification" in window) || Notification.permission !== "granted") return;
    const now = Date.now();
    if (now - lastNotificationTime < 300000) return;
    let msg = "";
    if (stats.temperature > 75) msg = "🌡️ High Temp: " + stats.temperature + "°C";
    else if (stats.storage_percent > 95) msg = "💾 Storage Low: " + stats.storage_percent + "%";
    if (msg) {
        new Notification("SeverOS Alert", { body: msg });
        lastNotificationTime = now;
    }
}
document.addEventListener('click', () => { if (Notification.permission === "default") Notification.requestPermission(); }, { once: true });
