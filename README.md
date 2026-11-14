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
- 🌍 **National & Global Holidays (100% Offline)**:
  - Built-in multi-country holiday calendar: **India (IN)**, **United States (US)**, **United Kingdom (UK)**, **Canada (CA)**, **Australia (AU)**, **Global**, or **All Countries**.
  - Highlights today's holiday with a festive glowing badge (e.g. *🎉 Holiday: Diwali* or *🎉 Holiday: Christmas Day*).
  - Shows days remaining countdown for upcoming holidays (e.g. *✨ Tomorrow: Children's Day* or *📅 Next: Thanksgiving Day (Nov 26 • in 13d)*).
  - Support for custom user-defined dates (Birthdays, Anniversaries, Company events).
- 🎆 **9 Built-in Animated Visual Engines**:
  1. **3D Starfield Warp**: Depth-projected space warp with dynamic speed trails.
  2. **Digital Matrix Rain**: Classic cyberpunk cascading phosphor code glyphs with bright leading heads.
  3. **Glowing Floating Embers**: Warm drifting ambient particles with translucent glow halos.
  4. **Neon Sine Waves**: Undulating harmonic ribbons floating across the horizon.
  5. **Minimalist Geometric Pulse**: Ultra-low-overhead (<1% CPU) breathing ambient rings and accent lines.
  6. **Cozy Rain & Ripples**: Diagonal falling raindrops with wind sway and ground splash ripples.
  7. **Enchanted Fireflies**: Organic wandering fireflies with breathing luminescence and bokeh halos.
  8. **Northern Lights (Aurora)**: Ethereal polar aurora borealis celestial curtains flowing across the sky.
  9. **80s Retro Grid**: Synthwave outrun 3D perspective wireframe ground grid scrolling towards the viewer.
- 🖼️ **Online Image & Looping Video Wallpapers**:
  - Load online background images (Unsplash, nature, sci-fi) or local wallpapers and MP4 video loops.
  - Looping video wallpaper support in browser simulator (`.mp4`, `.webm`) with local offline video loops included (`backgrounds/oceans.mp4`, `backgrounds/flower.mp4`).
  - Local media picker button to load your own video clips or photos directly from your device.
  - Multi-tier fallback architecture: Local Video → Online CDN → Curated Wallpaper Poster (screen is NEVER blank!).
  - Asynchronous background downloader with local caching (`backgrounds_cache/`) so clock animations never stutter.
  - Built-in presets: *Deep Ocean Waves*, *Blooming Flowers*, *Cyberpunk City*, *Cozy Lofi Room*, *Cosmic Nebula*, *Misty Forest*, *Northern Lights Sky*.
  - Configurable darkening dimmer overlay (10% to 90%) to guarantee 100% clock readability over any background image or video.
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
Open [`preview.html`](file:///d:/Rasberi/preview.html) directly in your browser (Edge, Chrome, or Firefox), or via the built-in server at `http://localhost:8080/preview`. It renders all 9 animations, video loops, online wallpapers, holiday countdowns, and themes in real-time with full keyboard hotkey support!

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

### 1. Web Remote Control (Smartphone / Tablet / PC)
PiClock includes a zero-dependency, mobile-responsive web dashboard running on port `8080`.

#### Connecting From Your Smartphone:
1. Ensure your smartphone is connected to the **same Wi-Fi network** as your Raspberry Pi or PC.
2. Launch the server:
   - **On Windows 11**: Double-click [`run_remote.bat`](file:///d:/Rasberi/run_remote.bat) or [`run.bat`](file:///d:/Rasberi/run.bat).
   - **On Raspberry Pi**: Start PiClock via `./run.sh` or systemd service.
3. Your terminal and remote header will display the exact phone link (e.g. `http://192.168.29.67:8080`).
4. **Instant QR Code Scan**: Open `http://localhost:8080` on your PC, point your phone's camera at the on-screen QR code, and tap the link to connect!
5. **Windows Firewall Troubleshooting**: If your phone cannot connect on Windows, double-click [`allow_firewall.bat`](file:///d:/Rasberi/allow_firewall.bat) once (click 'Yes' on the administrator prompt) to allow inbound TCP port 8080.

#### Phone Media Gallery & Slideshow Controls:
- **Upload Any Photo or Video**: Tap **📷 Choose Photo or Video** to upload directly from your phone's camera roll or files (`.jpg`, `.png`, `.mp4`, `.mov`, `.webm`).
- **Live Video Playback in `run.bat`**: Uploaded MP4 and video files now decode and play smoothly in high-resolution, hardware-accelerated loops on your Pygame desktop and Raspberry Pi screen!
- **Manage Media Directly from Phone**: View your stored gallery on the phone dashboard. Tap **✓ Apply** on any picture/video to immediately switch to it, or tap **🗑️ Delete** to remove unwanted items from storage.
- **Automated Slideshow Mode**: Turn on **📸 Photo Slideshow Mode** and choose an interval (5s, 10s, 15s, 30s, 60s) to automatically cycle through all your uploaded gallery pictures and videos!

#### What You Can Control From the Dashboard:
- **Instant Photo/Video Upload & Gallery Management**: Add or remove photos and videos directly from your mobile browser.
- **Automated Slideshow**: Toggle automatic wallpaper slideshow cycling with configurable intervals.
- **Palette & Animation Pickers**: Tap any of the 8 curated themes or 9 procedural animations.
- **Time & Clock Options**: Toggle 12h/24h format, show/hide seconds, blinking colon, and text glow.
- **Holidays & Countdown**: Switch country holidays and upcoming event alerts.
- **Night Brightness & Dimmer**: Adjust the screen brightness down to 10% for bedside nightstand use.
- **Live System Telemetry**: View live CPU temperature, hostname, and holiday status.

---

### 2. Keyboard & Touchscreen Hotkeys
When PiClock is running on your screen, you can use these keys:

| Key | Action |
| :--- | :--- |
| `[M]` | Cycle Animation Mode (*Starfield → Matrix → Particles → Waves → Minimalist → Rain → Fireflies → Aurora → Retro Grid*) |
| `[C]` | Cycle Color Themes (*Cyberpunk, Matrix, Synthwave, Midnight, Amber, etc.*) |
| `[L]` | Cycle Country Holidays (*India → United States → UK → Canada → Australia → Global → All*) |
| `[G]` | Toggle Background Wallpaper on / off |
| `[O]` | Toggle Photo Slideshow mode on / off |
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
        "fullscreen": false,         // true for full display, false for windowed
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
    "holiday": {
        "enabled": true,             // show/hide holidays on clock
        "country": "IN",              // "IN" (India), "US", "UK", "CA", "AU", "GLOBAL", "ALL"
        "show_upcoming": true,        // show upcoming countdown if today is not a holiday
        "custom_holidays": [         // optional personal events
            { "name": "Mom's Birthday", "month": 5, "day": 12 },
            { "name": "Anniversary", "month": 11, "day": 20 }
        ]
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
