#!/usr/bin/env bash
# ==============================================================================
# PiClock Automated Installer for Raspberry Pi 3
# Compatible with Raspberry Pi OS (Bullseye & Bookworm, 32-bit & 64-bit)
# ==============================================================================

set -e

# ANSI Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}"
echo "=========================================================="
echo "         PiClock Setup - Raspberry Pi 3 Edition           "
echo "=========================================================="
echo -e "${NC}"

INSTALL_DIR="$(cd "$(dirname "$0")" && pwd)"
CURRENT_USER="$(id -u -n)"
USER_HOME="$(getent passwd "$CURRENT_USER" | cut -d: -f6)"

echo -e "${YELLOW}[1/4] Checking and installing system packages...${NC}"
if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update -y
    sudo apt-get install -y python3 python3-pygame python3-opencv python3-pip x11-xserver-utils
else
    echo -e "${RED}apt-get not found. Please ensure you are running Raspberry Pi OS or Debian.${NC}"
    exit 1
fi

echo -e "${YELLOW}[2/4] Making scripts executable...${NC}"
chmod +x "$INSTALL_DIR/run.sh"
chmod +x "$INSTALL_DIR/main.py"

echo -e "${YELLOW}[3/4] Configuring Autostart on Boot...${NC}"

# A. Desktop Autostart (.config/autostart)
AUTOSTART_DIR="$USER_HOME/.config/autostart"
mkdir -p "$AUTOSTART_DIR"

cat <<EOF > "$AUTOSTART_DIR/piclock.desktop"
[Desktop Entry]
Type=Application
Name=PiClock
Comment=Lightweight Animated Clock for Raspberry Pi 3
Exec=$INSTALL_DIR/run.sh
Path=$INSTALL_DIR
Terminal=false
StartupNotify=false
X-GNOME-Autostart-enabled=true
EOF

chown -R "$CURRENT_USER:$CURRENT_USER" "$AUTOSTART_DIR"
chmod +x "$AUTOSTART_DIR/piclock.desktop"
echo -e "  ${GREEN}✓ Desktop autostart configured ($AUTOSTART_DIR/piclock.desktop)${NC}"

# B. Systemd Service (Optional for headless/console or system-level)
SYSTEMD_SERVICE_FILE="/etc/systemd/system/piclock.service"

sudo bash -c "cat <<EOF > $SYSTEMD_SERVICE_FILE
[Unit]
Description=PiClock Animated Smart Display
After=graphical.target sound.target network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$INSTALL_DIR
Environment=DISPLAY=:0
Environment=XAUTHORITY=$USER_HOME/.Xauthority
ExecStart=$INSTALL_DIR/run.sh
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=graphical.target
EOF"

sudo systemctl daemon-reload
echo -e "  ${GREEN}✓ Systemd service created ($SYSTEMD_SERVICE_FILE)${NC}"

echo -e "${YELLOW}[4/4] Getting IP address for Web Remote...${NC}"
LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP="<raspberry-pi-ip>"
fi

echo -e "${GREEN}"
echo "=========================================================="
echo "          Installation Completed Successfully!            "
echo "=========================================================="
echo -e "${NC}"
echo "You can now run PiClock manually:"
echo "  cd $INSTALL_DIR && ./run.sh"
echo ""
echo "Or start it as a system background service:"
echo "  sudo systemctl start piclock"
echo "  sudo systemctl enable piclock  # Enable auto-start at boot"
echo ""
echo "Web Remote Control:"
echo -e "  Open your phone/PC browser: ${CYAN}http://${LOCAL_IP}:8080${NC}"
echo ""
echo "Interactive Hotkeys (when active on screen):"
echo "  [M] Cycle Animation Mode (Starfield, Matrix, Waves, Particles, Minimalist)"
echo "  [C] Cycle Color Theme"
echo "  [T] Toggle 12h / 24h Time"
echo "  [S] Toggle Seconds"
echo "  [F] Toggle Fullscreen"
echo "  [B] Cycle Brightness (100%, 75%, 50%, 25%)"
echo "  [H] Toggle Help Overlay"
echo "  [Q / ESC] Quit"
echo "=========================================================="
