"""
Lightweight Web Remote control panel for PiClock.
Built using Python standard library http.server (no extra pip dependencies!).
Allows customizing colors, animations, clock settings, and messages from any phone or PC.
"""

import json
import os
import datetime
import platform
import socket
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Callable, Optional
from .themes import THEMES, THEME_KEYS
from .animations import ANIMATION_NAMES
from .holidays import HolidayManager

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PiClock Remote Control</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #0b0f19;
            --card-bg: rgba(22, 29, 47, 0.75);
            --card-border: rgba(255, 255, 255, 0.08);
            --primary: #00f0ff;
            --accent: #ff007f;
            --text-main: #f0f4fc;
            --text-muted: #8b9bb4;
            --radius: 16px;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background: var(--bg);
            background-image: radial-gradient(circle at 10% 20%, rgba(0, 240, 255, 0.08) 0%, transparent 40%),
                              radial-gradient(circle at 90% 80%, rgba(255, 0, 127, 0.08) 0%, transparent 40%);
            color: var(--text-main);
            padding: 24px 16px;
            min-height: 100vh;
            display: flex;
            justify-content: center;
        }
        .container {
            max-width: 680px;
            width: 100%;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 4px;
        }
        .brand {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .logo-badge {
            background: linear-gradient(135deg, #00f0ff, #ff007f);
            width: 40px;
            height: 40px;
            border-radius: 12px;
            display: grid;
            place-items: center;
            font-weight: 700;
            font-size: 20px;
            color: #0b0813;
        }
        h1 { font-size: 22px; font-weight: 700; }
        .version { font-size: 12px; color: var(--text-muted); font-family: 'JetBrains Mono', monospace; }
        .sys-badge {
            background: rgba(0, 240, 255, 0.12);
            color: var(--primary);
            border: 1px solid rgba(0, 240, 255, 0.25);
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 13px;
            font-family: 'JetBrains Mono', monospace;
        }
        .card {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            backdrop-filter: blur(12px);
            border-radius: var(--radius);
            padding: 22px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        .card-title {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
            color: var(--primary);
        }
        .grid-2 {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 16px;
        }
        .control-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        label {
            font-size: 13px;
            font-weight: 500;
            color: var(--text-muted);
        }
        select, input[type="text"], input[type="number"] {
            background: rgba(11, 15, 25, 0.85);
            border: 1px solid var(--card-border);
            color: var(--text-main);
            padding: 12px 14px;
            border-radius: 10px;
            font-size: 14px;
            font-family: inherit;
            outline: none;
            transition: border-color 0.2s, box-shadow 0.2s;
        }
        select:focus, input[type="text"]:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 2px rgba(0, 240, 255, 0.2);
        }
        .themes-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
            gap: 10px;
            margin-top: 6px;
        }
        .theme-btn {
            background: rgba(11, 15, 25, 0.6);
            border: 1px solid var(--card-border);
            padding: 10px;
            border-radius: 12px;
            cursor: pointer;
            text-align: left;
            transition: all 0.2s;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }
        .theme-btn:hover {
            border-color: rgba(255,255,255,0.25);
            transform: translateY(-2px);
        }
        .theme-btn.active {
            border-color: var(--primary);
            box-shadow: 0 0 12px rgba(0, 240, 255, 0.3);
            background: rgba(0, 240, 255, 0.08);
        }
        .theme-swatches {
            display: flex;
            gap: 5px;
        }
        .swatch {
            width: 14px;
            height: 14px;
            border-radius: 50%;
        }
        .theme-name {
            font-size: 12px;
            font-weight: 600;
            color: var(--text-main);
        }
        .anim-pills {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 6px;
        }
        .anim-pill {
            background: rgba(11, 15, 25, 0.6);
            border: 1px solid var(--card-border);
            padding: 8px 14px;
            border-radius: 20px;
            font-size: 13px;
            color: var(--text-muted);
            cursor: pointer;
            transition: all 0.2s;
            text-transform: capitalize;
        }
        .anim-pill:hover {
            color: var(--text-main);
            border-color: rgba(255,255,255,0.2);
        }
        .anim-pill.active {
            background: linear-gradient(135deg, rgba(0, 240, 255, 0.2), rgba(255, 0, 127, 0.2));
            border-color: var(--primary);
            color: #fff;
            font-weight: 600;
        }
        .switch-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }
        .switch-row:last-child { border-bottom: none; }
        .switch-label {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }
        .switch-desc {
            font-size: 12px;
            color: var(--text-muted);
        }
        .toggle {
            position: relative;
            display: inline-block;
            width: 44px;
            height: 24px;
        }
        .toggle input { opacity: 0; width: 0; height: 0; }
        .slider {
            position: absolute; cursor: pointer;
            top: 0; left: 0; right: 0; bottom: 0;
            background-color: #2b3345;
            transition: .3s;
            border-radius: 24px;
        }
        .slider:before {
            position: absolute; content: "";
            height: 18px; width: 18px;
            left: 3px; bottom: 3px;
            background-color: white;
            transition: .3s;
            border-radius: 50%;
        }
        input:checked + .slider { background-color: var(--primary); }
        input:checked + .slider:before { transform: translateX(20px); }
        .range-wrap {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        input[type="range"] {
            flex: 1;
            accent-color: var(--primary);
            cursor: pointer;
        }
        .range-val {
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            min-width: 45px;
            text-align: right;
            color: var(--primary);
        }
        .actions-bar {
            display: flex;
            gap: 10px;
            margin-top: 8px;
        }
        .btn {
            flex: 1;
            background: linear-gradient(135deg, #00f0ff, #0099ff);
            border: none;
            color: #050b14;
            font-weight: 700;
            padding: 14px;
            border-radius: 12px;
            cursor: pointer;
            font-size: 14px;
            transition: transform 0.15s, opacity 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        .btn:hover { opacity: 0.92; transform: translateY(-1px); }
        .btn:active { transform: translateY(1px); }
        .btn-secondary {
            background: rgba(255, 255, 255, 0.08);
            color: var(--text-main);
            border: 1px solid var(--card-border);
        }
        .btn-secondary:hover { background: rgba(255, 255, 255, 0.14); }
        .toast {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(0, 240, 255, 0.95);
            color: #0b0f19;
            padding: 12px 20px;
            border-radius: 10px;
            font-weight: 600;
            font-size: 14px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
            transform: translateY(100px);
            opacity: 0;
            transition: all 0.3s cubic-bezier(0.18, 0.89, 0.32, 1.28);
            z-index: 999;
        }
        .toast.show {
            transform: translateY(0);
            opacity: 1;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="brand">
                <div class="logo-badge">π</div>
                <div>
                    <h1>PiClock Remote</h1>
                    <div class="version">Raspberry Pi 3 Edition</div>
                </div>
            </div>
            <div class="sys-badge" id="cpuTempBadge">--°C</div>
        </header>

        <!-- Quick Animation Selector -->
        <div class="card">
            <div class="card-title">✨ Animation Mode</div>
            <div class="anim-pills" id="animPills"></div>
            <div style="margin-top: 16px;">
                <label>Animation Speed</label>
                <div class="range-wrap" style="margin-top: 6px;">
                    <input type="range" id="animSpeed" min="0.2" max="3.0" step="0.1" value="1.0">
                    <span class="range-val" id="animSpeedVal">1.0x</span>
                </div>
            </div>
        </div>

        <!-- Color Themes -->
        <div class="card">
            <div class="card-title">🎨 Color Palettes</div>
            <div class="themes-grid" id="themesGrid"></div>
        </div>

        <!-- Clock & Display Options -->
        <div class="card">
            <div class="card-title">⏰ Clock & Display Settings</div>
            
            <div class="switch-row">
                <div class="switch-label">
                    <div>24-Hour Time Format</div>
                    <div class="switch-desc">Switch between 12-hour (AM/PM) and military 24-hour time</div>
                </div>
                <label class="toggle">
                    <input type="checkbox" id="chk24h">
                    <span class="slider"></span>
                </label>
            </div>

            <div class="switch-row">
                <div class="switch-label">
                    <div>Display Seconds</div>
                    <div class="switch-desc">Show or hide the seconds digits</div>
                </div>
                <label class="toggle">
                    <input type="checkbox" id="chkSeconds">
                    <span class="slider"></span>
                </label>
            </div>

            <div class="switch-row">
                <div class="switch-label">
                    <div>Blinking Colon</div>
                    <div class="switch-desc">Flash the separator colon every second</div>
                </div>
                <label class="toggle">
                    <input type="checkbox" id="chkBlink">
                    <span class="slider"></span>
                </label>
            </div>

            <div class="switch-row">
                <div class="switch-label">
                    <div>Neon Glow Effect</div>
                    <div class="switch-desc">Ambient text drop-shadow and glow aura</div>
                </div>
                <label class="toggle">
                    <input type="checkbox" id="chkGlow">
                    <span class="slider"></span>
                </label>
            </div>

            <div style="margin-top: 16px;">
                <label>Display Brightness (Night Dimmer)</label>
                <div class="range-wrap" style="margin-top: 6px;">
                    <input type="range" id="dispBrightness" min="10" max="100" step="5" value="100">
                    <span class="range-val" id="dispBrightnessVal">100%</span>
                </div>
            </div>
        </div>

        <!-- Custom Subtitle / Message -->
        <div class="card">
            <div class="card-title">💬 Custom Subtitle / Greeting</div>
            <div class="control-group">
                <label for="customMsg">Message text shown beneath the date:</label>
                <input type="text" id="customMsg" placeholder="e.g. Raspberry Pi 3 • Smart Display">
            </div>
            <div class="switch-row" style="margin-top: 8px;">
                <div class="switch-label">
                    <div>Show Subtitle</div>
                </div>
                <label class="toggle">
                    <input type="checkbox" id="chkShowMsg">
                    <span class="slider"></span>
                </label>
            </div>
        </div>

        <!-- Country Holidays -->
        <div class="card">
            <div class="card-title">🌍 Country & Holidays</div>
            
            <div class="control-group">
                <label for="selCountry">Selected Country / Region:</label>
                <select id="selCountry" onchange="saveConfig()">
                    <option value="IN">🇮🇳 India (IN)</option>
                    <option value="US">🇺🇸 United States (US)</option>
                    <option value="UK">🇬🇧 United Kingdom (UK)</option>
                    <option value="CA">🇨🇦 Canada (CA)</option>
                    <option value="AU">🇦🇺 Australia (AU)</option>
                    <option value="GLOBAL">🌐 Global / International</option>
                    <option value="ALL">🌎 All Countries Combined</option>
                </select>
            </div>

            <div class="switch-row" style="margin-top: 10px;">
                <div class="switch-label">
                    <div>Display Holidays on Clock</div>
                    <div class="switch-desc">Show today's holiday or upcoming countdown banner</div>
                </div>
                <label class="toggle">
                    <input type="checkbox" id="chkHoliday">
                    <span class="slider"></span>
                </label>
            </div>

            <div class="switch-row">
                <div class="switch-label">
                    <div>Show Upcoming Countdown</div>
                    <div class="switch-desc">Displays days remaining until the next holiday</div>
                </div>
                <label class="toggle">
                    <input type="checkbox" id="chkUpcoming">
                    <span class="slider"></span>
                </label>
            </div>

            <div id="holidayPreviewBox" style="margin-top: 12px; padding: 10px 14px; background: rgba(0, 240, 255, 0.08); border: 1px solid rgba(0, 240, 255, 0.25); border-radius: 10px; font-size: 13px; font-family: 'JetBrains Mono', monospace; color: var(--primary);">
                📅 Next: Loading...
            </div>
        </div>

        <!-- Background Image & Wallpaper -->
        <div class="card">
            <div class="card-title">🖼️ Background Image / Wallpaper</div>

            <div class="switch-row">
                <div class="switch-label">
                    <div>Enable Background Image</div>
                    <div class="switch-desc">Display an online wallpaper behind the clock and animations</div>
                </div>
                <label class="toggle">
                    <input type="checkbox" id="chkBgEnabled">
                    <span class="slider"></span>
                </label>
            </div>

            <div class="control-group" style="margin-top: 12px;">
                <label>Curated Wallpaper & Video Presets:</label>
                <div class="anim-pills" style="margin-top: 4px;">
                    <button class="anim-pill" onclick="selectBgPreset('oceans')">🌊 Ocean Waves</button>
                    <button class="anim-pill" onclick="selectBgPreset('flower')">🌸 Blooming Flower</button>
                    <button class="anim-pill" onclick="selectBgPreset('cyber_city')">🌆 Cyber City</button>
                    <button class="anim-pill" onclick="selectBgPreset('cozy_lofi')">☕ Cozy Lofi</button>
                    <button class="anim-pill" onclick="selectBgPreset('deep_space')">🌌 Deep Space</button>
                    <button class="anim-pill" onclick="selectBgPreset('misty_forest')">🌲 Misty Forest</button>
                    <button class="anim-pill" onclick="selectBgPreset('aurora_sky')">🏔️ Aurora Sky</button>
                </div>
            </div>

            <div class="control-group" style="margin-top: 14px;">
                <label for="txtBgUrl">Or Custom Online Image URL / Local Path:</label>
                <input type="text" id="txtBgUrl" placeholder="https://example.com/wallpaper.jpg or local path">
            </div>

            <div style="margin-top: 14px;">
                <label>Wallpaper Dimmer / Darkness (Improves clock legibility)</label>
                <div class="range-wrap" style="margin-top: 6px;">
                    <input type="range" id="bgDimming" min="10" max="90" step="5" value="55">
                    <span class="range-val" id="bgDimmingVal">55%</span>
                </div>
            </div>
        </div>

        <!-- Action Buttons -->
        <div class="actions-bar">
            <button class="btn btn-secondary" onclick="triggerAction('next_theme')">Cycle Theme</button>
            <button class="btn btn-secondary" onclick="triggerAction('cycle_country')">Cycle Country</button>
            <button class="btn btn-secondary" onclick="triggerAction('toggle_background')">Toggle Wallpaper</button>
            <button class="btn btn-secondary" onclick="triggerAction('next_animation')">Cycle Animation</button>
            <button class="btn" onclick="saveConfig()">Save & Apply</button>
        </div>
    </div>

    <div class="toast" id="toast">Saved Successfully!</div>

    <script>
        let currentConfig = {};
        const toast = document.getElementById('toast');

        function showToast(msg) {
            toast.textContent = msg;
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 2400);
        }

        async function fetchStatus() {
            try {
                const res = await fetch('/api/status');
                const data = await res.json();
                currentConfig = data.config;
                renderUI(data);
            } catch (err) {
                console.error('Failed to load status:', err);
            }
        }

        function renderUI(data) {
            const cfg = data.config;
            const themes = data.themes;
            const animations = data.animations;

            // CPU Temp
            if (data.system && data.system.cpu_temp) {
                document.getElementById('cpuTempBadge').textContent = '🌡️ ' + data.system.cpu_temp;
            }

            // Animations
            const animPills = document.getElementById('animPills');
            animPills.innerHTML = '';
            animations.forEach(anim => {
                const btn = document.createElement('button');
                btn.className = 'anim-pill' + (cfg.visual.animation === anim ? ' active' : '');
                btn.textContent = anim;
                btn.onclick = () => {
                    document.querySelectorAll('.anim-pill').forEach(el => el.classList.remove('active'));
                    btn.classList.add('active');
                    cfg.visual.animation = anim;
                    saveConfig();
                };
                animPills.appendChild(btn);
            });

            // Speed slider
            document.getElementById('animSpeed').value = cfg.visual.animation_speed || 1.0;
            document.getElementById('animSpeedVal').textContent = (cfg.visual.animation_speed || 1.0).toFixed(1) + 'x';

            // Themes Grid
            const themesGrid = document.getElementById('themesGrid');
            themesGrid.innerHTML = '';
            Object.keys(themes).forEach(tKey => {
                const t = themes[tKey];
                const btn = document.createElement('div');
                btn.className = 'theme-btn' + (cfg.visual.theme === tKey ? ' active' : '');
                btn.onclick = () => {
                    document.querySelectorAll('.theme-btn').forEach(el => el.classList.remove('active'));
                    btn.classList.add('active');
                    cfg.visual.theme = tKey;
                    saveConfig();
                };

                const swatches = document.createElement('div');
                swatches.className = 'theme-swatches';
                [t.clock_primary, t.clock_secondary, t.accent].forEach(c => {
                    const sw = document.createElement('div');
                    sw.className = 'swatch';
                    sw.style.backgroundColor = `rgb(${c[0]}, ${c[1]}, ${c[2]})`;
                    swatches.appendChild(sw);
                });

                const name = document.createElement('div');
                name.className = 'theme-name';
                name.textContent = t.name;

                btn.appendChild(swatches);
                btn.appendChild(name);
                themesGrid.appendChild(btn);
            });

            // Switches
            document.getElementById('chk24h').checked = cfg.clock.format_24h;
            document.getElementById('chkSeconds').checked = cfg.clock.show_seconds;
            document.getElementById('chkBlink').checked = cfg.clock.blink_colon;
            document.getElementById('chkGlow').checked = cfg.visual.glow_effect;
            document.getElementById('chkShowMsg').checked = cfg.clock.show_message;
            document.getElementById('customMsg').value = cfg.clock.custom_message || '';
            document.getElementById('dispBrightness').value = cfg.display.brightness || 100;
            document.getElementById('dispBrightnessVal').textContent = (cfg.display.brightness || 100) + '%';

            // Holiday controls
            const hol = cfg.holiday || {};
            if (document.getElementById('selCountry')) {
                document.getElementById('selCountry').value = (hol.country || 'IN').toUpperCase();
            }
            if (document.getElementById('chkHoliday')) {
                document.getElementById('chkHoliday').checked = hol.enabled !== false;
            }
            if (document.getElementById('chkUpcoming')) {
                document.getElementById('chkUpcoming').checked = hol.show_upcoming !== false;
            }
            if (data.system && data.system.holiday_status && document.getElementById('holidayPreviewBox')) {
                document.getElementById('holidayPreviewBox').textContent = data.system.holiday_status;
            }

            // Background controls
            const bg = cfg.background || {};
            document.getElementById('chkBgEnabled').checked = Boolean(bg.enabled);
            document.getElementById('txtBgUrl').value = bg.source || 'cyber_city';
            document.getElementById('bgDimming').value = bg.dimming !== undefined ? bg.dimming : 55;
            document.getElementById('bgDimmingVal').textContent = (bg.dimming !== undefined ? bg.dimming : 55) + '%';
        }

        // Slider listeners
        document.getElementById('animSpeed').oninput = (e) => {
            document.getElementById('animSpeedVal').textContent = parseFloat(e.target.value).toFixed(1) + 'x';
        };
        document.getElementById('dispBrightness').oninput = (e) => {
            document.getElementById('dispBrightnessVal').textContent = e.target.value + '%';
        };
        document.getElementById('bgDimming').oninput = (e) => {
            document.getElementById('bgDimmingVal').textContent = e.target.value + '%';
        };

        function selectBgPreset(presetKey) {
            document.getElementById('chkBgEnabled').checked = true;
            document.getElementById('txtBgUrl').value = presetKey;
            saveConfig();
            showToast("Wallpaper preset selected!");
        }

        async function saveConfig() {
            if (!currentConfig.visual) currentConfig.visual = {};
            if (!currentConfig.clock) currentConfig.clock = {};
            if (!currentConfig.display) currentConfig.display = {};
            if (!currentConfig.holiday) currentConfig.holiday = {};
            if (!currentConfig.background) currentConfig.background = {};

            currentConfig.clock.format_24h = document.getElementById('chk24h').checked;
            currentConfig.clock.show_seconds = document.getElementById('chkSeconds').checked;
            currentConfig.clock.blink_colon = document.getElementById('chkBlink').checked;
            currentConfig.visual.glow_effect = document.getElementById('chkGlow').checked;
            currentConfig.clock.show_message = document.getElementById('chkShowMsg').checked;
            currentConfig.clock.custom_message = document.getElementById('customMsg').value;
            currentConfig.visual.animation_speed = parseFloat(document.getElementById('animSpeed').value);
            currentConfig.display.brightness = parseInt(document.getElementById('dispBrightness').value);

            currentConfig.holiday.country = document.getElementById('selCountry').value;
            currentConfig.holiday.enabled = document.getElementById('chkHoliday').checked;
            currentConfig.holiday.show_upcoming = document.getElementById('chkUpcoming').checked;

            currentConfig.background.enabled = document.getElementById('chkBgEnabled').checked;
            currentConfig.background.source = document.getElementById('txtBgUrl').value;
            currentConfig.background.dimming = parseInt(document.getElementById('bgDimming').value);

            try {
                const res = await fetch('/api/config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(currentConfig)
                });
                if (res.ok) {
                    showToast('Settings Applied!');
                }
            } catch (err) {
                console.error('Error saving config:', err);
                showToast('Save Failed');
            }
        }

        async function triggerAction(action) {
            try {
                const res = await fetch('/api/action', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: action })
                });
                if (res.ok) {
                    fetchStatus();
                    showToast('Action executed');
                }
            } catch (err) {
                console.error(err);
            }
        }

        fetchStatus();
        setInterval(fetchStatus, 8000);
    </script>
</body>
</html>
"""

def get_cpu_temp() -> Optional[str]:
    """Read CPU temperature on Raspberry Pi."""
    thermal_path = "/sys/class/thermal/thermal_zone0/temp"
    if os.path.exists(thermal_path):
        try:
            with open(thermal_path, "r") as f:
                temp_raw = f.read().strip()
                temp_c = float(temp_raw) / 1000.0
                return f"{temp_c:.1f}°C"
        except Exception:
            pass
    return "N/A"

class WebRemoteHandler(BaseHTTPRequestHandler):
    config_manager = None
    on_change_callback = None
    action_callback = None

    def log_message(self, format, *args):
        # Silence normal HTTP request logging to avoid terminal clutter
        pass

    def _send_json(self, data: dict, status: int = 200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        clean_path = self.path.split("?")[0].rstrip("/")
        if clean_path in ("", "/index.html"):
            content = HTML_PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        elif clean_path in ("/preview", "/preview.html"):
            preview_file = os.path.join(os.getcwd(), "preview.html")
            if os.path.exists(preview_file):
                with open(preview_file, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_response(404)
                self.end_headers()
        elif clean_path.startswith("/backgrounds/"):
            rel_file = clean_path.lstrip("/")
            file_path = os.path.join(os.getcwd(), rel_file)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                ext = os.path.splitext(file_path)[1].lower()
                mime_types = {
                    ".mp4": "video/mp4",
                    ".webm": "video/webm",
                    ".jpg": "image/jpeg",
                    ".jpeg": "image/jpeg",
                    ".png": "image/png"
                }
                c_type = mime_types.get(ext, "application/octet-stream")
                file_size = os.path.getsize(file_path)
                with open(file_path, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", c_type)
                self.send_header("Content-Length", str(file_size))
                self.send_header("Accept-Ranges", "bytes")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_response(404)
                self.end_headers()
        elif clean_path == "/api/status":
            cfg = self.config_manager.data.copy() if self.config_manager else {}
            hol_cfg = cfg.get("holiday", {})
            try:
                hm = HolidayManager(country=hol_cfg.get("country", "IN"))
                h_status, _ = hm.get_status_string(datetime.date.today())
            except Exception:
                h_status = "Holidays ready"

            status_data = {
                "config": cfg,
                "themes": THEMES,
                "animations": ANIMATION_NAMES,
                "system": {
                    "platform": platform.platform(),
                    "cpu_temp": get_cpu_temp(),
                    "hostname": socket.gethostname(),
                    "holiday_status": h_status
                }
            }
            self._send_json(status_data)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)

        try:
            payload = json.loads(post_data.decode("utf-8")) if post_data else {}
        except Exception:
            self._send_json({"error": "Invalid JSON"}, status=400)
            return

        if self.path == "/api/config":
            if self.config_manager:
                self.config_manager.update_dict(payload)
                if self.on_change_callback:
                    self.on_change_callback()
            self._send_json({"status": "ok", "message": "Configuration updated"})
        elif self.path == "/api/action":
            action = payload.get("action")
            if self.action_callback and action:
                self.action_callback(action)
            self._send_json({"status": "ok", "action": action})
        else:
            self.send_response(404)
            self.end_headers()


def start_web_remote(config_manager, on_change: Callable, on_action: Callable, port: int = 8080, host: str = "0.0.0.0"):
    """Starts the HTTP server on a background daemon thread."""
    WebRemoteHandler.config_manager = config_manager
    WebRemoteHandler.on_change_callback = on_change
    WebRemoteHandler.action_callback = on_action

    def run_server():
        try:
            server = HTTPServer((host, port), WebRemoteHandler)
            print(f"[Web Remote] Dashboard running on http://{host}:{port}")
            server.serve_forever()
        except Exception as e:
            print(f"[Web Remote] Warning: Could not start web remote on {host}:{port}: {e}")

    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    return thread
