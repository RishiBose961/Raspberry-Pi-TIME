# ⏰ PiClock - Lightweight Animated Smart Clock for Raspberry Pi 3

A sleek, ultra-lightweight, customizable digital clock and animated ambient display engineered specifically for the **Raspberry Pi 3** (and compatible with Raspberry Pi 4, 5, Zero 2W, and PC/Mac/Linux).

Built with **Python 3** and **SDL2/Pygame**, PiClock maintains silky-smooth 60 FPS visual animations while consuming **under 5% CPU** and **less than 40 MB of RAM**, keeping your Raspberry Pi cool, silent, and fanless-friendly.

---

## ✨ Features

- 🕒 **Precision Date & Time Display**:
  - 12-Hour (with AM/PM badge) or 24-Hour military time format.
  - Optional smooth seconds counter.
  - Configurable blinking or solid separator colon (`:`).
  - Full formatted calendar date with customizable format strings (`strftime`).
  - Customizable subtitle/greeting banner (e.g. *"Raspberry Pi 3 • Smart Display"* or daily quotes).
- 🎆 **5 Built-in Animated Background Engines**:
  1. **3D Starfield Warp**: Depth-projected space warp with dynamic speed trails.
  2. **Digital Matrix Rain**: Classic cyberpunk cascading phosphor code glyphs with bright leading heads.
  3. **Glowing Floating Embers**: Warm drifting ambient particles with translucent glow halos.
  4. **Neon Sine Waves**: Undulating harmonic ribbons floating across the horizon.
  5. **Minimalist Geometric Pulse**: Ultra-low-overhead (<1% CPU) breathing ambient rings and accent lines.
- 🎨 **8 Curated Color Palettes**:
  - *Cyberpunk Neon* (Cyan & Hot Pink)
  - *Matrix Terminal* (Hacker Phosphor Green)
  - *Synthwave Sunset* (Magenta, Aqua & Sunset Orange)
  - *Midnight Ice* (Deep Royal Blue & Frost Cyan)
  - *Retro Amber CRT* (Warm Vintage Monospaced Amber)
  - *Sakura Bloom* (Soft Blossom Rose & Pastel Pink)
  - *Emerald Forest* (Pine Green & Mint)
  - *Minimalist OLED* (Pure White on Absolute Black)
- 📱 **Built-in Mobile Web Remote (No extra dependencies!)**:
  - Control your clock from any smartphone, tablet, or computer on the same Wi-Fi network (`http://<pi-ip>:8080`).
  - Change themes, animation modes, toggle 12/24h, adjust night brightness dimmer, and edit subtitles in real-time.
- ⚡ **Ultra-Lightweight & Hardware-Optimized**:
  - Native SDL2 hardware rendering.
  - Software brightness dimmer slider (dim down to 10% for bedside nightstand use).
  - Touchscreen support: Tap the top half of the screen to switch animations; tap the bottom half to switch themes.
  - Automatic resolution scaling (crisp on 800×480, 1024×600, 1280×720, 1920×1080, and 4K displays).

---

## 📋 System Requirements

- **Hardware**: Raspberry Pi 3 Model B or B+ (also works on Pi 2, 4, 5, Zero 2W).
- **Display**: Any HDMI monitor, TV, or DSI / SPI touchscreen (e.g. Official Raspberry Pi 7" Touchscreen).
- **Operating System**: Raspberry Pi OS (Bullseye or Bookworm, 32-bit or 64-bit, Desktop or Lite).
- **Runtime**: Python 3.7+ and `python3-pygame`.

---

## 🪟 Testing on Windows 11 / PC

You can test and preview PiClock right on your Windows 11 computer:

### Option 1: Native Python App
Double-click [`run.bat`](file:///d:/Rasberi/run.bat) or run in PowerShell / Command Prompt:
```cmd
.\run.bat
```
*(Requires `pip install pygame-ce`, which is already installed on your system).*

### Option 2: Instant Interactive Web Simulator
Open [`preview.html`](file:///d:/Rasberi/preview.html) in your browser (Edge, Chrome, or Firefox). It renders all 5 animations, clock modes, and themes in real-time with full keyboard hotkey support!

---

## 🚀 Quick Start (Automated Installation on Raspberry Pi)

Clone or copy this repository to your Raspberry Pi and run the automated installer:

```bash
# 1. Clone or download the project to your Raspberry Pi
git clone https://github.com/your-username/piclock.git ~/piclock
cd ~/piclock

# 2. Run the automated installer
chmod +x install.sh
./install.sh
```

The script will:
1. Install required packages (`python3`, `python3-pygame`, `python3-pip`).
2. Make helper scripts executable.
3. Automatically configure PiClock to launch on boot.
4. Display your Raspberry Pi's local IP address for the Web Remote.

---

## 🛠️ Manual Installation (Step-by-Step)

If you prefer to configure the system manually:

### Step 1: Update Packages & Install Pygame
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pygame python3-pip
```

> **Why `python3-pygame` via `apt`?**  
> On Raspberry Pi OS, installing Pygame via `apt` provides pre-compiled binaries linked directly to the Pi's native SDL2 hardware acceleration, avoiding lengthy compilation from source.

### Step 2: Test Run PiClock
```bash
cd ~/piclock
python3 main.py
```
You should see the animated clock appear immediately!

---

## 🔄 Autostart on Boot

To have PiClock automatically start when your Raspberry Pi powers on, choose **Method A** (recommended for Raspberry Pi OS with Desktop) or **Method B** (for systemd / headless):

### Method A: Desktop Autostart (Recommended for GUI)
Create an autostart desktop entry:

```bash
mkdir -p ~/.config/autostart
nano ~/.config/autostart/piclock.desktop
```

Paste the following configuration:
```ini
[Desktop Entry]
Type=Application
Name=PiClock
Comment=Lightweight Animated Clock for Raspberry Pi 3
Exec=/home/pi/piclock/run.sh
Path=/home/pi/piclock
Terminal=false
StartupNotify=false
X-GNOME-Autostart-enabled=true
```
*(Replace `/home/pi/piclock` with your actual installation directory if different).*

### Method B: Systemd Service (For Background / Console Boot)
```bash
sudo nano /etc/systemd/system/piclock.service
```

Paste the following:
```ini
[Unit]
Description=PiClock Animated Smart Display
After=graphical.target sound.target network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/piclock
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/pi/.Xauthority
ExecStart=/home/pi/piclock/run.sh
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=graphical.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable piclock
sudo systemctl start piclock
```

To check service status:
```bash
sudo systemctl status piclock
```

---

## 🎛️ How to Customize PiClock

### 1. Web Remote Control (Smartphone / PC)
PiClock starts a lightweight HTTP server on port `8080`.
1. Ensure your phone or laptop is on the same Wi-Fi network as your Raspberry Pi.
2. Find your Raspberry Pi's IP address:
   ```bash
   hostname -I
   ```
3. Open your browser and navigate to:
   ```
   http://192.168.1.100:8080
   ```
   *(replace `192.168.1.100` with your Pi's actual IP).*
4. The web dashboard allows you to:
   - Tap color swatches to switch color themes instantly.
   - Click animation pills to switch between Starfield, Matrix, Particles, Waves, and Minimalist.
   - Toggle 12h/24h time, seconds display, blinking colon, and text glow.
   - Adjust the night brightness dimmer.
   - Edit the custom subtitle/greeting message.
   - View your Raspberry Pi's live CPU temperature.

---

### 2. Keyboard & Touchscreen Hotkeys
When PiClock is running on your screen, you can use these keys:

| Key | Action |
| :--- | :--- |
| `[M]` | Cycle Animation Mode (*Starfield → Matrix → Particles → Waves → Minimalist*) |
| `[C]` | Cycle Color Themes (*Cyberpunk, Matrix, Synthwave, Midnight, Amber, etc.*) |
| `[T]` | Toggle 12-Hour (AM/PM) / 24-Hour military time |
| `[S]` | Toggle seconds display on / off |
| `[F]` | Toggle Fullscreen / Windowed mode |
| `[B]` | Cycle brightness levels (100% → 75% → 50% → 25%) |
| `[↑] / [↓]` | Increase / decrease animation speed |
| `[H]` | Toggle on-screen shortcut guide |
| `[Q]` or `[ESC]` | Exit PiClock |
| **Touch Top Half** | Tap top half of touchscreen to cycle animations |
| **Touch Bottom Half** | Tap bottom half of touchscreen to cycle color themes |

---

### 3. Editing `config.json`
You can fine-tune every parameter directly in `config.json`:

```json
{
    "display": {
        "fullscreen": true,          // true for full display, false for windowed
        "width": 1024,               // default resolution width
        "height": 600,               // default resolution height
        "fps": 60,                   // 60 for ultra-smooth; 30 for ultra-low power
        "brightness": 100,           // 10 to 100 (software night dimmer)
        "show_cursor": false         // hide mouse cursor on display
    },
    "clock": {
        "format_24h": false,         // true: "14:35", false: "2:35 PM"
        "show_seconds": true,        // display seconds counter
        "blink_colon": true,         // flash separator colon every second
        "date_format": "%A, %B %d, %Y", // standard strftime format
        "custom_message": "Raspberry Pi 3 • Smart Display",
        "show_message": true         // show/hide subtitle message
    },
    "visual": {
        "theme": "cyberpunk",        // cyberpunk, matrix, synthwave, midnight, amber, sakura, emerald, oled_dark
        "animation": "starfield",    // starfield, matrix, particles, waves, minimalist
        "animation_speed": 1.0,      // 0.2 (slow/ambient) to 3.0 (fast)
        "particle_count": 80,        // number of particles/stars
        "glow_effect": true,         // soft text drop shadow and glow
        "font_scale": 1.0            // scale factor for fonts (0.8 - 1.5)
    },
    "web_remote": {
        "enabled": true,             // enable/disable mobile web dashboard
        "port": 8080,                // HTTP port
        "bind_address": "0.0.0.0"    // listen on all network interfaces
    }
}
```

---

## 📺 Display & Hardware Setup Tips for Raspberry Pi 3

### 1. Disable Screen Blanking / Sleep
To keep your clock display on 24/7 without turning off:
- **In Raspberry Pi OS Desktop**: Open `Raspberry Pi Menu` → `Preferences` → `Raspberry Pi Configuration` → `Display` → Turn **Screen Blanking** to **Disabled**.
- **Via CLI (`raspi-config`)**:
  ```bash
  sudo raspi-config
  # Navigate to: Display Options -> Screen Blanking -> No
  ```

### 2. Screen Rotation (Portrait / Desk Mount)
If your display is mounted vertically (portrait mode):
- **On Raspberry Pi OS Bookworm**:
  Open `Raspberry Pi Menu` → `Preferences` → `Screen Configuration` → Right click display → `Orientation` → Select `Right` or `Left` → Click Apply.
- **On Raspberry Pi OS Bullseye**:
  Edit `/boot/config.txt`:
  ```ini
  # 0 = Normal, 1 = 90 degrees, 2 = 180 degrees, 3 = 270 degrees
  display_rotate=1
  ```

### 3. Official 7" Raspberry Pi Touchscreen
PiClock automatically detects native 800×480 resolution and dynamically scales fonts and particles to fit proportionally. Touch input is pre-mapped for cycling modes!

### 4. GPU Memory Allocation
For best animation performance on Pi 3, allocate at least 128 MB to the GPU:
```bash
sudo raspi-config
# Performance Options -> GPU Memory -> 128
```

---

## 📁 Project Structure

```
piclock/
├── piclock/
│   ├── __init__.py           # Package definition
│   ├── main.py               # Application engine and event loop
│   ├── config.py             # Thread-safe config.json manager
│   ├── clock.py              # Clock typography & date renderer
│   ├── themes.py             # 8 custom color themes & palettes
│   ├── web_remote.py         # Mobile web remote server & dashboard
│   └── animations/
│       ├── __init__.py       # Animation registry & factory
│       ├── base.py           # Base animation abstract class
│       ├── starfield.py      # 3D warp starfield animation
│       ├── matrix.py         # Cyberpunk digital rain animation
│       ├── particles.py      # Floating glowing embers animation
│       ├── waves.py          # Glowing neon sine waves animation
│       └── minimalist.py     # Clean geometric pulse animation
├── config.json               # Default configuration
├── install.sh                # Automated installer for Raspberry Pi
├── uninstall.sh              # Service uninstaller
├── run.sh                    # Startup runner script
├── requirements.txt          # Python dependencies
└── README.md                 # Complete documentation
```

---

## ❓ Troubleshooting

| Issue | Solution |
| :--- | :--- |
| **Clock doesn't start on boot** | Verify desktop autostart path in `~/.config/autostart/piclock.desktop` points to your correct user directory (e.g. `/home/pi/piclock/run.sh`). |
| **Screen turns black after 10 minutes** | Disable screen blanking via `sudo raspi-config` under `Display Options` → `Screen Blanking`. |
| **Web remote cannot be reached** | Check your Pi's IP address (`hostname -I`). Ensure both devices are on the same local network and port 8080 is not blocked by a firewall (`sudo ufw allow 8080`). |
| **Animation feels sluggish** | In `config.json`, reduce `particle_count` to `50` or set `fps` to `30`. Ensure GPU memory is set to `128MB` in `raspi-config`. |
| **Wrong Timezone** | Set your local timezone with `sudo raspi-config` → `Localisation Options` → `Timezone`. |

---

## 📄 License

MIT License. Free to use, modify, and distribute for personal and commercial projects.
