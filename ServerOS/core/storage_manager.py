"""
Storage Manager – Detects and manages external USB drives.
Uses lsblk to enumerate block devices and identify removable/USB storage.
"""

import json
import os
import subprocess
import shutil


def _run(cmd):
    """Run a command and return stdout or empty string on failure."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip()
    except Exception:
        return ""


def list_block_devices():
    """Return structured list of block devices from lsblk."""
    raw = _run([
        "lsblk", "-J", "-b", "-o",
        "NAME,SIZE,TYPE,MOUNTPOINT,FSTYPE,RM,TRAN,MODEL,SERIAL,LABEL,HOTPLUG"
    ])
    if not raw:
        return []
    try:
        data = json.loads(raw)
        return data.get("blockdevices", [])
    except (json.JSONDecodeError, KeyError):
        return []


def get_external_drives():
    """
    Identify external/removable USB drives.
    Returns a list of dicts with drive info.
    """
    devices = list_block_devices()
    drives = []
    for dev in devices:
        is_removable = dev.get("rm") in (True, "1", 1)
        transport = (dev.get("tran") or "").lower()
        is_usb = transport == "usb"
        is_hotplug = dev.get("hotplug") in (True, "1", 1)
        dev_type = dev.get("type", "")

        if dev_type == "disk" and (is_removable or is_usb or is_hotplug):
            size_bytes = int(dev.get("size", 0) or 0)
            partitions = []
            for child in dev.get("children", []):
                part_size = int(child.get("size", 0) or 0)
                partitions.append({
                    "name": child.get("name", ""),
                    "size_bytes": part_size,
                    "size_human": _human_size(part_size),
                    "fstype": child.get("fstype", ""),
                    "mountpoint": child.get("mountpoint", ""),
                    "label": child.get("label", ""),
                })

            drives.append({
                "name": dev.get("name", ""),
                "model": (dev.get("model") or "Unknown Device").strip(),
                "serial": dev.get("serial", ""),
                "size_bytes": size_bytes,
                "size_human": _human_size(size_bytes),
                "transport": transport,
                "removable": is_removable,
                "partitions": partitions,
            })
    return drives


def get_disk_health():
    """
    Return disk usage info for all mounted filesystems.
    Works even without external drives.
    """
    disks = []
    try:
        raw = _run(["df", "-B1", "--output=source,size,used,avail,pcent,target"])
        if not raw:
            return _fallback_disk_health()
        lines = raw.strip().split("\n")[1:]  # skip header
        for line in lines:
            parts = line.split()
            if len(parts) >= 6 and not parts[0].startswith("tmpfs"):
                source = parts[0]
                total = int(parts[1])
                used = int(parts[2])
                avail = int(parts[3])
                percent_str = parts[4].replace("%", "")
                mount = parts[5]
                if total > 0:
                    disks.append({
                        "device": source,
                        "mount": mount,
                        "total_bytes": total,
                        "used_bytes": used,
                        "avail_bytes": avail,
                        "total_human": _human_size(total),
                        "used_human": _human_size(used),
                        "avail_human": _human_size(avail),
                        "percent_used": int(percent_str) if percent_str.isdigit() else 0,
                    })
    except Exception:
        return _fallback_disk_health()
    return disks


def _fallback_disk_health():
    """Fallback using shutil for at least the root partition."""
    try:
        usage = shutil.disk_usage("/")
        return [{
            "device": "/dev/root",
            "mount": "/",
            "total_bytes": usage.total,
            "used_bytes": usage.used,
            "avail_bytes": usage.free,
            "total_human": _human_size(usage.total),
            "used_human": _human_size(usage.used),
            "avail_human": _human_size(usage.free),
            "percent_used": round(usage.used / usage.total * 100) if usage.total else 0,
        }]
    except Exception:
        return []


def mount_drive(device_path, mount_point=None):
    """
    Attempt to mount an external drive partition.
    Returns (success: bool, message: str).
    """
    if not device_path.startswith("/dev/"):
        device_path = f"/dev/{device_path}"

    if mount_point is None:
        name = os.path.basename(device_path)
        mount_point = f"/mnt/{name}"

    try:
        os.makedirs(mount_point, exist_ok=True)
        result = subprocess.run(
            ["mount", device_path, mount_point],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            return True, f"Mounted {device_path} at {mount_point}"
        return False, result.stderr.strip() or "Mount failed"
    except Exception as e:
        return False, str(e)


def unmount_drive(mount_point):
    """
    Attempt to unmount a drive.
    Returns (success: bool, message: str).
    """
    try:
        result = subprocess.run(
            ["umount", mount_point],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            return True, f"Unmounted {mount_point}"
        return False, result.stderr.strip() or "Unmount failed"
    except Exception as e:
        return False, str(e)


def _human_size(size_bytes):
    """Convert bytes to human-readable string."""
    if not size_bytes or size_bytes == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(size_bytes)
    for unit in units:
        if abs(size) < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"
