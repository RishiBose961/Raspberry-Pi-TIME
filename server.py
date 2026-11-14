#!/usr/bin/env python3
"""
PiClock Web Remote & Clock Server.
Runs the lightweight HTTP server for the Remote Control dashboard and live web clock.
Accessible from any phone, tablet, or PC on the same Wi-Fi network.
"""

import sys
import time
import socket
from piclock.config import ConfigManager
from piclock.web_remote import start_web_remote, get_local_ip

def main():
    config_file = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    config_mgr = ConfigManager(config_file)
    port = config_mgr.get("web_remote", "port") or 8080
    host = config_mgr.get("web_remote", "bind_address") or "0.0.0.0"

    local_ip = get_local_ip()

    print("\n" + "=" * 70)
    print("  ⏰ PICLOCK REMOTE CONTROL & CLOCK SERVER")
    print("=" * 70)
    print(f"  💻 Local PC Dashboard:   http://localhost:{port}")
    print(f"  📱 Phone / LAN Remote:   http://{local_ip}:{port}")
    print(f"  🌐 Clock Web Simulator:  http://{local_ip}:{port}/preview")
    print("=" * 70)
    print("  HOW TO CONNECT YOUR PHONE:")
    print("  1. Connect your phone to the SAME Wi-Fi network as this PC.")
    print(f"  2. Open Safari / Chrome on your phone and go to: http://{local_ip}:{port}")
    print("  3. If your phone cannot connect, run 'allow_firewall.bat' once as Admin.")
    print("=" * 70 + "\n")
    print("Server running... Press Ctrl+C to stop.\n")

    # Start in blocking mode
    start_web_remote(config_mgr, port=port, host=host, blocking=True)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[PiClock] Server stopped.")
        sys.exit(0)
