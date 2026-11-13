#!/usr/bin/env bash
# ==============================================================================
# PiClock Runner Script for Raspberry Pi 3
# ==============================================================================

# Move to the script directory
cd "$(dirname "$0")"

# Check if running under X11 or Wayland or console
if [ -z "$DISPLAY" ] && [ -z "$WAYLAND_DISPLAY" ]; then
    # Headless / Framebuffer / KMSDRM fallback if running from raw console
    export SDL_VIDEODRIVER=kmsdrm
fi

# Execute PiClock using Python 3
exec python3 main.py "$@"
