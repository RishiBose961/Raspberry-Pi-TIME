#!/usr/bin/env bash
# ==============================================================================
# PiClock Uninstaller for Raspberry Pi 3
# ==============================================================================

echo "Uninstalling PiClock autostart & services..."

# Stop and disable systemd service
if systemctl is-active --quiet piclock 2>/dev/null; then
    sudo systemctl stop piclock
fi
if systemctl is-enabled --quiet piclock 2>/dev/null; then
    sudo systemctl disable piclock
fi

# Remove systemd service file
if [ -f "/etc/systemd/system/piclock.service" ]; then
    sudo rm -f "/etc/systemd/system/piclock.service"
    sudo systemctl daemon-reload
    echo "✓ Removed systemd service"
fi

# Remove desktop autostart
CURRENT_USER="$(id -u -n)"
USER_HOME="$(getent passwd "$CURRENT_USER" | cut -d: -f6)"
AUTOSTART_FILE="$USER_HOME/.config/autostart/piclock.desktop"

if [ -f "$AUTOSTART_FILE" ]; then
    rm -f "$AUTOSTART_FILE"
    echo "✓ Removed desktop autostart entry"
fi

echo "PiClock uninstallation complete."
