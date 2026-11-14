#!/usr/bin/env bash
# ==============================================================================
# PiClock Runner & Watchdog Script for Raspberry Pi 3
# ==============================================================================

cd "$(dirname "$0")"

# If DISPLAY not set, check for local X11 desktop session (:0)
if [ -z "$DISPLAY" ] && [ -e /tmp/.X11-unix/X0 ]; then
    export DISPLAY=:0
    if [ -f "$HOME/.Xauthority" ]; then
        export XAUTHORITY="$HOME/.Xauthority"
    fi
fi

# Fallback to KMSDRM only if absolutely no window server found
if [ -z "$DISPLAY" ] && [ -z "$WAYLAND_DISPLAY" ]; then
    export SDL_VIDEODRIVER=kmsdrm
fi

# Disable screen blanking / power management
if [ -n "$DISPLAY" ]; then
    xset s off -dpms s noblank 2>/dev/null || true
fi

# Watchdog execution loop: auto-restarts if process ever crashes, exits cleanly on user quit
echo "[PiClock] Starting smart display engine..."

while true; do
    python3 main.py "$@"
    EXIT_CODE=$?

    # Exit code 0 means user intentionally quit ([Q] key or remote Quit button)
    if [ $EXIT_CODE -eq 0 ]; then
        echo "[PiClock] Clean exit requested. Goodbye!"
        break
    else
        echo "[PiClock Watchdog] App stopped with exit code $EXIT_CODE. Automatically restarting in 2 seconds..."
        sleep 2
    fi
done
