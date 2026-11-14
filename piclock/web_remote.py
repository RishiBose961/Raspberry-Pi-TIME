"""
Lightweight Web Remote control panel for PiClock.
Built using Python standard library http.server (no extra pip dependencies!).
Allows customizing colors, animations, clock settings, and messages from any phone or PC.
"""

import json
import os
import re
import time
import base64
import urllib.parse
import datetime
import platform
import socket
import threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from typing import Callable, Optional
from .themes import THEMES, THEME_KEYS
from .animations import ANIMATION_NAMES
from .holidays import HolidayManager

def get_local_ip() -> str:
    """Discover the primary local LAN IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        # Does not actually transmit data; determines default routing interface
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"

HTML_PAGE = r"""<!DOCTYPE html>
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
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #00ff88;
            box-shadow: 0 0 8px #00ff88;
            display: inline-block;
        }
        .status-dot.offline {
            background: #ff3366;
            box-shadow: 0 0 8px #ff3366;
        }
        button, .anim-pill, .theme-btn, .toggle {
            -webkit-tap-highlight-color: transparent;
            touch-action: manipulation;
            user-select: none;
        }
        .btn:active, .anim-pill:active, .theme-btn:active {
            transform: scale(0.96) !important;
        }
        .gallery-card {
            background: rgba(11, 15, 25, 0.7);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            transition: all 0.2s;
            position: relative;
        }
        .gallery-card:hover {
            border-color: rgba(255,255,255,0.3);
        }
        .gallery-card.active {
            border-color: #00f0ff;
            box-shadow: 0 0 14px rgba(0, 240, 255, 0.4);
            background: rgba(0, 240, 255, 0.06);
        }
        .gallery-thumb-wrap {
            position: relative;
            width: 100%;
            height: 90px;
            background: #000;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }
        .gallery-thumb {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        .gallery-type-badge {
            position: absolute;
            top: 6px;
            left: 6px;
            background: rgba(0,0,0,0.75);
            color: #fff;
            font-size: 10px;
            padding: 2px 6px;
            border-radius: 6px;
            font-weight: 600;
            backdrop-filter: blur(4px);
        }
        .gallery-active-badge {
            position: absolute;
            top: 6px;
            right: 6px;
            background: #00f0ff;
            color: #050b14;
            font-size: 10px;
            padding: 2px 6px;
            border-radius: 6px;
            font-weight: 700;
        }
        .gallery-info {
            padding: 8px 10px;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        .gallery-name {
            font-size: 11px;
            font-weight: 600;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            color: var(--text-main);
        }
        .gallery-size {
            font-size: 10px;
            color: var(--text-muted);
            font-family: 'JetBrains Mono', monospace;
        }
        .gallery-actions {
            display: flex;
            gap: 6px;
            margin-top: 4px;
        }
        .btn-gallery-apply {
            flex: 1;
            padding: 6px 8px;
            background: rgba(0, 240, 255, 0.15);
            border: 1px solid rgba(0, 240, 255, 0.35);
            color: var(--primary);
            border-radius: 8px;
            font-size: 11px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s;
        }
        .btn-gallery-apply:hover {
            background: var(--primary);
            color: #050b14;
        }
        .btn-gallery-del {
            padding: 6px 9px;
            background: rgba(255, 0, 80, 0.15);
            border: 1px solid rgba(255, 0, 80, 0.35);
            color: #ff3366;
            border-radius: 8px;
            font-size: 11px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s;
        }
        .btn-gallery-del:hover {
            background: #ff0050;
            color: #fff;
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
            <div style="display: flex; gap: 8px; align-items: center;">
                <div class="sys-badge" id="connStatusBadge" style="display: flex; align-items: center; gap: 6px;">
                    <span class="status-dot"></span>
                    <span id="connStatusText">Connected</span>
                </div>
                <div class="sys-badge" id="cpuTempBadge">--°C</div>
            </div>
        </header>

        <!-- Mobile Phone Access Card -->
        <div class="card" id="phoneAccessCard" style="background: linear-gradient(135deg, rgba(0, 240, 255, 0.08), rgba(255, 0, 127, 0.08)); border: 1px solid rgba(0, 240, 255, 0.35); padding: 18px 20px;">
            <div style="display: flex; align-items: center; justify-content: space-between; gap: 14px; flex-wrap: wrap;">
                <div style="flex: 1; min-width: 220px;">
                    <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: var(--primary); font-weight: 700; display: flex; align-items: center; gap: 6px;">
                        <span>📱 Open On Your Smartphone</span>
                    </div>
                    <div style="font-size: 16px; font-weight: 700; margin-top: 5px; font-family: 'JetBrains Mono', monospace; word-break: break-all;" id="phoneUrlText">
                        http://<span id="displayLanIp">...</span>:8080
                    </div>
                    <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">
                        Connect your phone to the same Wi-Fi, then scan QR or tap link
                    </div>
                    <div style="display: flex; gap: 8px; margin-top: 10px;">
                        <button type="button" class="anim-pill" style="padding: 5px 12px; font-size: 12px; color: #fff; background: rgba(0,240,255,0.15); border-color: rgba(0,240,255,0.4);" onclick="copyPhoneLink()">
                            📋 Copy Link
                        </button>
                        <a id="btnOpenSimulator" href="/preview" target="_blank" class="anim-pill" style="padding: 5px 12px; font-size: 12px; color: #fff; text-decoration: none; display: inline-flex; align-items: center; gap: 4px;">
                            🖥️ Open Clock Simulator
                        </a>
                    </div>
                </div>
                <div style="display: flex; flex-direction: column; align-items: center; gap: 4px;">
                    <div id="qrCodeWrapper" style="background: #ffffff; padding: 6px; border-radius: 10px; display: inline-flex; box-shadow: 0 4px 15px rgba(0,0,0,0.5);">
                        <img id="qrCodeImg" style="width: 72px; height: 72px; display: block;" alt="Scan QR Code with Phone">
                    </div>
                    <span style="font-size: 10px; color: var(--text-muted); text-transform: uppercase;">Scan with Camera</span>
                </div>
            </div>
        </div>

        <!-- Quick Animation Selector -->
        <div class="card">
            <div class="card-title">✨ Animation Mode</div>
            <div class="anim-pills" id="animPills"></div>
            <div style="margin-top: 16px;">
                <label>Animation Speed</label>
                <div class="range-wrap" style="margin-top: 6px;">
                    <input type="range" id="animSpeed" min="0.2" max="3.0" step="0.1" value="1.0" oninput="document.getElementById('animSpeedVal').textContent=parseFloat(this.value).toFixed(1)+'x'" onchange="autoApplySetting()">
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
                    <input type="checkbox" id="chk24h" onchange="autoApplySetting()">
                    <span class="slider"></span>
                </label>
            </div>

            <div class="switch-row">
                <div class="switch-label">
                    <div>Display Seconds</div>
                    <div class="switch-desc">Show or hide the seconds digits</div>
                </div>
                <label class="toggle">
                    <input type="checkbox" id="chkSeconds" onchange="autoApplySetting()">
                    <span class="slider"></span>
                </label>
            </div>

            <div class="switch-row">
                <div class="switch-label">
                    <div>Blinking Colon</div>
                    <div class="switch-desc">Flash the separator colon every second</div>
                </div>
                <label class="toggle">
                    <input type="checkbox" id="chkBlink" onchange="autoApplySetting()">
                    <span class="slider"></span>
                </label>
            </div>

            <div class="switch-row">
                <div class="switch-label">
                    <div>Neon Glow Effect</div>
                    <div class="switch-desc">Ambient text drop-shadow and glow aura</div>
                </div>
                <label class="toggle">
                    <input type="checkbox" id="chkGlow" onchange="autoApplySetting()">
                    <span class="slider"></span>
                </label>
            </div>

            <div style="margin-top: 16px;">
                <label>Display Brightness (Night Dimmer)</label>
                <div class="range-wrap" style="margin-top: 6px;">
                    <input type="range" id="dispBrightness" min="10" max="100" step="5" value="100" oninput="document.getElementById('dispBrightnessVal').textContent=this.value+'%'" onchange="autoApplySetting()">
                    <span class="range-val" id="dispBrightnessVal">100%</span>
                </div>
            </div>
        </div>

        <!-- Custom Subtitle / Message -->
        <div class="card">
            <div class="card-title">💬 Custom Subtitle / Greeting</div>
            <div class="control-group">
                <label for="customMsg">Message text shown beneath the date:</label>
                <input type="text" id="customMsg" placeholder="e.g. Raspberry Pi 3 • Smart Display" oninput="onCustomMsgInput()" onchange="autoApplySetting()">
            </div>
            <div class="switch-row" style="margin-top: 8px;">
                <div class="switch-label">
                    <div>Show Subtitle</div>
                </div>
                <label class="toggle">
                    <input type="checkbox" id="chkShowMsg" onchange="autoApplySetting()">
                    <span class="slider"></span>
                </label>
            </div>
        </div>

        <!-- Country Holidays -->
        <div class="card">
            <div class="card-title">🌍 Country & Holidays</div>
            
            <div class="control-group">
                <label for="selCountry">Selected Country / Region:</label>
                <select id="selCountry" onchange="autoApplySetting()">
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
                    <input type="checkbox" id="chkHoliday" onchange="autoApplySetting()">
                    <span class="slider"></span>
                </label>
            </div>

            <div class="switch-row">
                <div class="switch-label">
                    <div>Show Upcoming Countdown</div>
                    <div class="switch-desc">Displays days remaining until the next holiday</div>
                </div>
                <label class="toggle">
                    <input type="checkbox" id="chkUpcoming" onchange="autoApplySetting()">
                    <span class="slider"></span>
                </label>
            </div>

            <div id="holidayPreviewBox" style="margin-top: 12px; padding: 10px 14px; background: rgba(0, 240, 255, 0.08); border: 1px solid rgba(0, 240, 255, 0.25); border-radius: 10px; font-size: 13px; font-family: 'JetBrains Mono', monospace; color: var(--primary);">
                📅 Next: Loading...
            </div>
        </div>

        <!-- Background Image, Video & Slideshow -->
        <div class="card">
            <div class="card-title">🖼️ Background Image, Video & Slideshow</div>

            <div class="switch-row">
                <div class="switch-label">
                    <div>Enable Background</div>
                    <div class="switch-desc">Display video or photo wallpaper behind clock and animations</div>
                </div>
                <label class="toggle">
                    <input type="checkbox" id="chkBgEnabled" onchange="autoApplySetting()">
                    <span class="slider"></span>
                </label>
            </div>

            <!-- Slideshow Mode -->
            <div class="switch-row" style="background: rgba(0, 240, 255, 0.05); padding: 12px 14px; border-radius: 12px; margin-top: 12px; border: 1px solid rgba(0, 240, 255, 0.2);">
                <div class="switch-label">
                    <div style="font-weight: 700; color: var(--primary);">📸 Photo Slideshow Mode</div>
                    <div class="switch-desc">Auto-cycles through all your uploaded gallery photos & videos</div>
                </div>
                <label class="toggle">
                    <input type="checkbox" id="chkSlideshow" onchange="autoApplySetting()">
                    <span class="slider"></span>
                </label>
            </div>

            <div class="control-group" id="slideshowIntervalGroup" style="margin-top: 10px;">
                <label for="selSlideInterval">Slideshow Interval:</label>
                <select id="selSlideInterval" onchange="autoApplySetting()">
                    <option value="5">Every 5 Seconds</option>
                    <option value="10" selected>Every 10 Seconds</option>
                    <option value="15">Every 15 Seconds</option>
                    <option value="30">Every 30 Seconds</option>
                    <option value="60">Every 1 Minute</option>
                </select>
            </div>

            <!-- Curated Wallpaper Presets -->
            <div class="control-group" style="margin-top: 14px;">
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

            <!-- Direct Photo & Video Upload from Phone / Device -->
            <div class="control-group" style="margin-top: 16px; padding: 14px; background: rgba(0, 240, 255, 0.05); border: 1px dashed rgba(0, 240, 255, 0.35); border-radius: 12px;">
                <label style="font-weight: 600; color: var(--primary); display: flex; align-items: center; justify-content: space-between;">
                    <span>📤 Add New Photo or Video from Device:</span>
                </label>
                <div style="margin-top: 8px; display: flex; flex-direction: column; gap: 8px;">
                    <input type="file" id="mediaUploadInput" accept="image/*,video/mp4,video/webm,video/quicktime,video/*" style="display: none;" onchange="handleRemoteFileUpload(this)">
                    <button type="button" class="btn" style="background: linear-gradient(135deg, #00f0ff, #0088ff); color: #050b14; font-weight: 700; width: 100%; display: flex; align-items: center; justify-content: center; gap: 8px; cursor: pointer; padding: 12px;" onclick="document.getElementById('mediaUploadInput').click()">
                        <span>📷 Choose Photo or Video to Upload</span>
                    </button>
                    <div id="uploadProgressBox" style="display: none; padding: 8px; background: rgba(0,0,0,0.3); border-radius: 8px; text-align: center; font-size: 12px; color: var(--primary);">
                        <span id="uploadProgressText">Uploading...</span>
                    </div>
                </div>
            </div>

            <!-- Media Gallery Manager (Add / Remove directly from phone) -->
            <div class="control-group" style="margin-top: 18px;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <label style="font-weight: 700; color: var(--primary); display: flex; align-items: center; gap: 8px;">
                        <span>🖼️ Your Media Gallery</span>
                        <span id="galleryCountBadge" style="font-size: 11px; background: rgba(0,240,255,0.18); color: var(--primary); padding: 2px 8px; border-radius: 10px; font-family: 'JetBrains Mono', monospace;">0</span>
                    </label>
                    <button type="button" class="anim-pill" style="padding: 4px 10px; font-size: 11px; color: #fff; background: rgba(255,255,255,0.08);" onclick="loadGallery()">🔄 Refresh</button>
                </div>
                <div id="galleryEmptyNotice" style="display: none; padding: 20px; text-align: center; color: var(--text-muted); font-size: 13px; background: rgba(0,0,0,0.2); border-radius: 10px; margin-top: 8px;">
                    No uploaded photos or videos yet. Use the button above to upload from your phone!
                </div>
                <div id="galleryGrid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 10px; margin-top: 10px;">
                    <!-- Dynamically populated by loadGallery() -->
                </div>
            </div>

            <div class="control-group" style="margin-top: 16px;">
                <label for="txtBgUrl">Or Custom Online Image URL / Local Path:</label>
                <input type="text" id="txtBgUrl" placeholder="https://example.com/wallpaper.jpg or local path" onchange="autoApplySetting()">
            </div>

            <div style="margin-top: 14px;">
                <label>Wallpaper Dimmer / Darkness (Improves clock legibility)</label>
                <div class="range-wrap" style="margin-top: 6px;">
                    <input type="range" id="bgDimming" min="10" max="90" step="5" value="55" oninput="document.getElementById('bgDimmingVal').textContent=this.value+'%'" onchange="autoApplySetting()">
                    <span class="range-val" id="bgDimmingVal">55%</span>
                </div>
            </div>
        </div>

        <!-- Quick Instant Actions Bar for Phone Thumb Navigation -->
        <div class="actions-bar" style="display: flex; flex-wrap: wrap; gap: 8px;">
            <button type="button" class="btn btn-secondary" onclick="triggerAction('next_theme')">🎨 Next Theme</button>
            <button type="button" class="btn btn-secondary" onclick="triggerAction('next_animation')">✨ Next Anim</button>
            <button type="button" class="btn btn-secondary" onclick="triggerAction('cycle_country')">🌍 Next Country</button>
            <button type="button" class="btn btn-secondary" onclick="triggerAction('toggle_background')">🖼️ Wallpaper</button>
            <button type="button" class="btn btn-secondary" onclick="triggerAction('toggle_slideshow')">📸 Slideshow</button>
            <button type="button" class="btn btn-secondary" onclick="triggerAction('toggle_24h')">⏰ 12/24h</button>
            <button type="button" class="btn btn-secondary" onclick="triggerAction('toggle_seconds')">⏱️ Seconds</button>
            <button type="button" class="btn btn-secondary" onclick="triggerAction('toggle_fullscreen')">⛶ Fullscreen</button>
            <button type="button" class="btn" style="flex: 1 1 100%; font-size: 15px; padding: 14px;" onclick="saveConfig(false)">💾 Save All Settings</button>
        </div>
    </div>

    <div class="toast" id="toast">Saved Successfully!</div>

    <script>
        let currentConfig = {};
        let activeTheme = 'cyberpunk';
        let activeAnim = 'starfield';
        let uiInitialized = false;
        let msgDebounceTimer = null;
        const toast = document.getElementById('toast');

        function showToast(msg) {
            toast.textContent = msg;
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 2200);
        }

        function setOnlineStatus(online) {
            const dot = document.querySelector('.status-dot');
            const text = document.getElementById('connStatusText');
            if (dot && text) {
                if (online) {
                    dot.className = 'status-dot';
                    text.textContent = 'Connected';
                } else {
                    dot.className = 'status-dot offline';
                    text.textContent = 'Offline';
                }
            }
        }

        async function fetchStatus() {
            try {
                const res = await fetch('/api/status');
                if (!res.ok) throw new Error('HTTP ' + res.status);
                const data = await res.json();
                currentConfig = data.config || {};
                setOnlineStatus(true);
                if (!uiInitialized) {
                    initUI(data);
                    uiInitialized = true;
                }
                updateUIState(data);
            } catch (err) {
                console.warn('Status fetch error:', err);
                setOnlineStatus(false);
            }
        }

        function initUI(data) {
            const themes = data.themes || {};
            const animations = data.animations || [];
            const cfg = data.config || {};

            activeTheme = (cfg.visual && cfg.visual.theme) || 'cyberpunk';
            activeAnim = (cfg.visual && cfg.visual.animation) || 'starfield';

            // Animation pills
            const animPills = document.getElementById('animPills');
            animPills.innerHTML = '';
            animations.forEach(anim => {
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'anim-pill' + (anim === activeAnim ? ' active' : '');
                btn.dataset.anim = anim;
                btn.textContent = anim.replace('_', ' ');
                btn.onclick = () => selectAnimation(anim);
                animPills.appendChild(btn);
            });

            // Themes Grid
            const themesGrid = document.getElementById('themesGrid');
            themesGrid.innerHTML = '';
            Object.keys(themes).forEach(tKey => {
                const t = themes[tKey];
                const btn = document.createElement('div');
                btn.className = 'theme-btn' + (tKey === activeTheme ? ' active' : '');
                btn.dataset.theme = tKey;
                btn.onclick = () => selectTheme(tKey);

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

            // Sync initial form values
            syncFormValues(cfg);
            loadGallery();
        }

        function syncFormValues(cfg) {
            const clock = cfg.clock || {};
            const visual = cfg.visual || {};
            const disp = cfg.display || {};
            const hol = cfg.holiday || {};
            const bg = cfg.background || {};

            document.getElementById('chk24h').checked = Boolean(clock.format_24h);
            document.getElementById('chkSeconds').checked = clock.show_seconds !== false;
            document.getElementById('chkBlink').checked = clock.blink_colon !== false;
            document.getElementById('chkGlow').checked = visual.glow_effect !== false;
            document.getElementById('chkShowMsg').checked = clock.show_message !== false;
            document.getElementById('customMsg').value = clock.custom_message || '';

            document.getElementById('animSpeed').value = visual.animation_speed || 1.0;
            document.getElementById('animSpeedVal').textContent = (visual.animation_speed || 1.0).toFixed(1) + 'x';

            document.getElementById('dispBrightness').value = disp.brightness || 100;
            document.getElementById('dispBrightnessVal').textContent = (disp.brightness || 100) + '%';

            document.getElementById('selCountry').value = (hol.country || 'IN').toUpperCase();
            document.getElementById('chkHoliday').checked = hol.enabled !== false;
            document.getElementById('chkUpcoming').checked = hol.show_upcoming !== false;

            document.getElementById('chkBgEnabled').checked = Boolean(bg.enabled);
            document.getElementById('txtBgUrl').value = bg.source || 'oceans';
            document.getElementById('bgDimming').value = bg.dimming !== undefined ? bg.dimming : 55;
            document.getElementById('bgDimmingVal').textContent = (bg.dimming !== undefined ? bg.dimming : 55) + '%';

            const slide = bg.slideshow || {};
            if (document.getElementById('chkSlideshow')) {
                document.getElementById('chkSlideshow').checked = Boolean(slide.enabled);
            }
            if (document.getElementById('selSlideInterval')) {
                document.getElementById('selSlideInterval').value = slide.interval ? String(parseInt(slide.interval)) : "10";
            }
        }

        function updateUIState(data) {
            const cfg = data.config || {};
            if (cfg.visual && cfg.visual.theme && cfg.visual.theme !== activeTheme) {
                activeTheme = cfg.visual.theme;
                document.querySelectorAll('.theme-btn').forEach(b => {
                    b.classList.toggle('active', b.dataset.theme === activeTheme);
                });
            }
            if (cfg.visual && cfg.visual.animation && cfg.visual.animation !== activeAnim) {
                activeAnim = cfg.visual.animation;
                document.querySelectorAll('.anim-pill').forEach(b => {
                    b.classList.toggle('active', b.dataset.anim === activeAnim);
                });
            }

            if (data.system && data.system.cpu_temp) {
                document.getElementById('cpuTempBadge').textContent = '🌡️ ' + data.system.cpu_temp;
            }

            if (data.system && data.system.holiday_status) {
                const hBox = document.getElementById('holidayPreviewBox');
                if (hBox) hBox.textContent = data.system.holiday_status;
            }

            if (data.system && data.system.local_ip) {
                const port = window.location.port || '8080';
                const phoneUrl = `http://${data.system.local_ip}:${port}`;
                const urlEl = document.getElementById('phoneUrlText');
                if (urlEl) {
                    urlEl.innerHTML = `<a href="${phoneUrl}" target="_blank" style="color:var(--primary); text-decoration:none;">${phoneUrl}</a>`;
                }
                const qrImg = document.getElementById('qrCodeImg');
                if (qrImg) {
                    qrImg.src = `https://api.qrserver.com/v1/create-qr-code/?size=160x160&data=${encodeURIComponent(phoneUrl)}`;
                }
            }
        }

        function selectTheme(tKey) {
            activeTheme = tKey;
            document.querySelectorAll('.theme-btn').forEach(b => {
                b.classList.toggle('active', b.dataset.theme === tKey);
            });
            autoApplySetting(true);
            showToast(`🎨 Theme: ${tKey}`);
        }

        function selectAnimation(anim) {
            activeAnim = anim;
            document.querySelectorAll('.anim-pill').forEach(b => {
                b.classList.toggle('active', b.dataset.anim === anim);
            });
            autoApplySetting(true);
            showToast(`✨ Animation: ${anim}`);
        }

        function selectBgPreset(presetKey) {
            document.getElementById('chkBgEnabled').checked = true;
            document.getElementById('txtBgUrl').value = presetKey;
            autoApplySetting(true);
            showToast(`🖼️ Wallpaper preset: ${presetKey}`);
        }

        function onCustomMsgInput() {
            if (msgDebounceTimer) clearTimeout(msgDebounceTimer);
            msgDebounceTimer = setTimeout(() => {
                autoApplySetting(true);
            }, 500);
        }

        function autoApplySetting(quick = false) {
            saveConfig(quick);
        }

        async function saveConfig(quick = false) {
            const payload = {
                clock: {
                    format_24h: document.getElementById('chk24h').checked,
                    show_seconds: document.getElementById('chkSeconds').checked,
                    blink_colon: document.getElementById('chkBlink').checked,
                    custom_message: document.getElementById('customMsg').value,
                    show_message: document.getElementById('chkShowMsg').checked
                },
                visual: {
                    theme: activeTheme || 'cyberpunk',
                    animation: activeAnim || 'starfield',
                    animation_speed: parseFloat(document.getElementById('animSpeed').value),
                    glow_effect: document.getElementById('chkGlow').checked
                },
                display: {
                    brightness: parseInt(document.getElementById('dispBrightness').value)
                },
                holiday: {
                    country: document.getElementById('selCountry').value,
                    enabled: document.getElementById('chkHoliday').checked,
                    show_upcoming: document.getElementById('chkUpcoming').checked
                },
                background: {
                    enabled: document.getElementById('chkBgEnabled').checked,
                    source: document.getElementById('txtBgUrl').value,
                    dimming: parseInt(document.getElementById('bgDimming').value),
                    slideshow: {
                        enabled: document.getElementById('chkSlideshow') ? document.getElementById('chkSlideshow').checked : false,
                        interval: document.getElementById('selSlideInterval') ? parseFloat(document.getElementById('selSlideInterval').value) : 10.0
                    }
                }
            };

            try {
                const res = await fetch('/api/config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                if (res.ok) {
                    setOnlineStatus(true);
                    if (!quick) showToast('✅ Settings Saved & Applied!');
                } else {
                    showToast('⚠️ Error saving settings');
                }
            } catch (err) {
                console.error('Config save error:', err);
                setOnlineStatus(false);
                showToast('❌ Connection error');
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
                    setOnlineStatus(true);
                    showToast(`⚡ ${action.replace('_', ' ')}`);
                    setTimeout(fetchStatus, 300);
                }
            } catch (err) {
                console.error(err);
                setOnlineStatus(false);
                showToast('❌ Action failed');
            }
        }

        function copyPhoneLink() {
            const urlEl = document.getElementById('phoneUrlText');
            const url = urlEl ? urlEl.innerText.trim() : window.location.href;
            if (navigator.clipboard) {
                navigator.clipboard.writeText(url).then(() => {
                    showToast('📋 Copied: ' + url);
                }).catch(() => {
                    showToast('Phone Link: ' + url);
                });
            } else {
                showToast('Phone Link: ' + url);
            }
        }

        async function handleRemoteFileUpload(input) {
            if (!input.files || !input.files[0]) return;
            const file = input.files[0];

            const progressBox = document.getElementById('uploadProgressBox');
            const progressText = document.getElementById('uploadProgressText');
            const previewBox = document.getElementById('uploadPreviewBox');
            const thumbImg = document.getElementById('uploadThumbImg');
            const thumbVid = document.getElementById('uploadThumbVid');
            const fileNameEl = document.getElementById('uploadFileName');

            if (progressBox) progressBox.style.display = 'block';
            if (progressText) progressText.textContent = `Uploading ${file.name} (${(file.size / (1024*1024)).toFixed(1)} MB)...`;

            try {
                const reader = new FileReader();
                reader.onload = async (e) => {
                    const dataUrl = e.target.result;
                    const res = await fetch('/api/upload_background', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            filename: file.name,
                            content_type: file.type,
                            data: dataUrl
                        })
                    });
                    const result = await res.json();
                    if (progressBox) progressBox.style.display = 'none';

                    if (result.status === 'ok') {
                        showToast(`✅ Uploaded & Active: ${file.name}`);
                        if (fileNameEl) fileNameEl.textContent = file.name;
                        if (previewBox) previewBox.style.display = 'flex';

                        const isVideo = file.type.startsWith('video/') || /\.(mp4|webm|mov|mkv)$/i.test(file.name);
                        if (isVideo) {
                            thumbVid.src = dataUrl;
                            thumbVid.style.display = 'block';
                            thumbImg.style.display = 'none';
                            thumbVid.play().catch(() => {});
                        } else {
                            thumbImg.src = dataUrl;
                            thumbImg.style.display = 'block';
                            thumbVid.style.display = 'none';
                        }

                        document.getElementById('chkBgEnabled').checked = true;
                        document.getElementById('txtBgUrl').value = result.path;
                        autoApplySetting(true);
                        loadGallery();
                    } else {
                        showToast('Upload failed: ' + (result.error || 'Server error'));
                    }
                };
                reader.readAsDataURL(file);
            } catch (err) {
                console.error('File upload error:', err);
                if (progressBox) progressBox.style.display = 'none';
                showToast('Upload failed: ' + err.message);
            }
        }

        async function loadGallery() {
            try {
                const res = await fetch('/api/gallery');
                if (!res.ok) return;
                const data = await res.json();
                const grid = document.getElementById('galleryGrid');
                const badge = document.getElementById('galleryCountBadge');
                const emptyNotice = document.getElementById('galleryEmptyNotice');
                if (!grid) return;

                const items = data.items || [];
                if (badge) badge.textContent = items.length;

                if (items.length === 0) {
                    grid.innerHTML = '';
                    if (emptyNotice) emptyNotice.style.display = 'block';
                    return;
                }

                if (emptyNotice) emptyNotice.style.display = 'none';
                grid.innerHTML = '';

                items.forEach(item => {
                    const card = document.createElement('div');
                    card.className = 'gallery-card' + (item.is_active ? ' active' : '');

                    const thumbWrap = document.createElement('div');
                    thumbWrap.className = 'gallery-thumb-wrap';

                    if (item.type === 'video') {
                        const vid = document.createElement('video');
                        vid.className = 'gallery-thumb';
                        vid.src = '/' + item.path;
                        vid.muted = true;
                        vid.playsInline = true;
                        vid.preload = 'metadata';
                        thumbWrap.appendChild(vid);

                        const typeBadge = document.createElement('div');
                        typeBadge.className = 'gallery-type-badge';
                        typeBadge.textContent = '🎬 VIDEO';
                        thumbWrap.appendChild(typeBadge);
                    } else {
                        const img = document.createElement('img');
                        img.className = 'gallery-thumb';
                        img.src = '/' + item.path;
                        img.loading = 'lazy';
                        thumbWrap.appendChild(img);

                        const typeBadge = document.createElement('div');
                        typeBadge.className = 'gallery-type-badge';
                        typeBadge.textContent = '📷 PHOTO';
                        thumbWrap.appendChild(typeBadge);
                    }

                    if (item.is_active) {
                        const activeBadge = document.createElement('div');
                        activeBadge.className = 'gallery-active-badge';
                        activeBadge.textContent = '★ Active';
                        thumbWrap.appendChild(activeBadge);
                    }

                    const info = document.createElement('div');
                    info.className = 'gallery-info';

                    const name = document.createElement('div');
                    name.className = 'gallery-name';
                    name.title = item.filename;
                    name.textContent = item.filename;

                    const size = document.createElement('div');
                    size.className = 'gallery-size';
                    size.textContent = item.size_str;

                    const actions = document.createElement('div');
                    actions.className = 'gallery-actions';

                    const btnApply = document.createElement('button');
                    btnApply.type = 'button';
                    btnApply.className = 'btn-gallery-apply';
                    btnApply.textContent = item.is_active ? 'Active' : 'Apply';
                    btnApply.onclick = (e) => {
                        e.stopPropagation();
                        selectGalleryMedia(item.path);
                    };

                    const btnDel = document.createElement('button');
                    btnDel.type = 'button';
                    btnDel.className = 'btn-gallery-del';
                    btnDel.title = 'Delete from clock';
                    btnDel.innerHTML = '🗑️';
                    btnDel.onclick = (e) => {
                        e.stopPropagation();
                        deleteGalleryMedia(item.filename);
                    };

                    actions.appendChild(btnApply);
                    actions.appendChild(btnDel);

                    info.appendChild(name);
                    info.appendChild(size);
                    info.appendChild(actions);

                    card.appendChild(thumbWrap);
                    card.appendChild(info);

                    card.onclick = () => selectGalleryMedia(item.path);
                    grid.appendChild(card);
                });
            } catch (err) {
                console.warn('Failed to load gallery:', err);
            }
        }

        async function selectGalleryMedia(path) {
            try {
                const res = await fetch('/api/gallery/select', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({path: path})
                });
                if (res.ok) {
                    document.getElementById('chkBgEnabled').checked = true;
                    document.getElementById('txtBgUrl').value = path;
                    showToast(`✅ Set Active: ${path.split('/').pop()}`);
                    loadGallery();
                }
            } catch (err) {
                showToast('Error applying background');
            }
        }

        async function deleteGalleryMedia(filename) {
            if (!confirm(`Delete "${filename}" from clock storage?`)) return;
            try {
                const res = await fetch('/api/gallery/delete', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({filename: filename})
                });
                const resData = await res.json();
                if (res.ok) {
                    showToast(`🗑️ Removed: ${filename}`);
                    loadGallery();
                } else {
                    showToast('Delete error: ' + (resData.error || 'Server error'));
                }
            } catch (err) {
                showToast('Delete error: ' + err.message);
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
                    "local_ip": get_local_ip(),
                    "holiday_status": h_status
                }
            }
            self._send_json(status_data)
        elif clean_path == "/api/gallery":
            bg_dir = os.path.join(os.getcwd(), "backgrounds")
            current_src = ""
            if self.config_manager and self.config_manager.data:
                current_src = self.config_manager.data.get("background", {}).get("source", "")

            items = []
            if os.path.exists(bg_dir):
                valid_exts = (".jpg", ".jpeg", ".png", ".webp", ".mp4", ".webm", ".mov", ".mkv")
                for f in sorted(os.listdir(bg_dir)):
                    if f.lower().endswith(valid_exts):
                        fp = os.path.join(bg_dir, f)
                        if os.path.isfile(fp):
                            size = os.path.getsize(fp)
                            is_vid = f.lower().endswith((".mp4", ".webm", ".mov", ".mkv"))
                            rel_p = f"backgrounds/{f}"
                            size_str = f"{size / (1024*1024):.1f} MB" if size >= 1024*1024 else f"{size // 1024} KB"
                            items.append({
                                "filename": f,
                                "path": rel_p,
                                "type": "video" if is_vid else "image",
                                "size_str": size_str,
                                "is_active": (rel_p == current_src or f == current_src or current_src.endswith(f))
                            })
            self._send_json({"items": items})
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)

        # 1. Raw Binary Upload endpoint
        if self.path.startswith("/api/upload_raw"):
            parsed = urllib.parse.urlparse(self.path)
            query = urllib.parse.parse_qs(parsed.query)
            raw_name = query.get("filename", ["upload.bin"])[0]
            safe_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', os.path.basename(raw_name))
            if not safe_name:
                safe_name = f"media_{int(time.time())}.bin"

            bg_dir = os.path.join(os.getcwd(), "backgrounds")
            os.makedirs(bg_dir, exist_ok=True)
            target_path = os.path.join(bg_dir, safe_name)

            with open(target_path, "wb") as f:
                f.write(post_data)

            rel_path = f"backgrounds/{safe_name}"
            print(f"[Web Remote] Received raw uploaded media: {safe_name} ({len(post_data)} bytes)")

            if self.config_manager:
                self.config_manager.update_dict({
                    "background": {
                        "enabled": True,
                        "source": rel_path
                    }
                })
                if WebRemoteHandler.on_change_callback:
                    try:
                        WebRemoteHandler.on_change_callback()
                    except Exception as e:
                        print(f"[Web Remote] Error in upload callback: {e}")

            self._send_json({
                "status": "ok",
                "filename": safe_name,
                "path": rel_path,
                "message": f"Successfully uploaded {safe_name}"
            })
            return

        # 2. JSON Endpoints
        try:
            payload = json.loads(post_data.decode("utf-8")) if post_data else {}
        except Exception:
            self._send_json({"error": "Invalid JSON"}, status=400)
            return

        # 3. Base64 Upload endpoint
        if self.path == "/api/upload_background":
            filename = payload.get("filename", "upload.jpg")
            safe_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', os.path.basename(filename))
            if not safe_name:
                safe_name = f"media_{int(time.time())}.jpg"

            data_uri = payload.get("data", "")
            if "," in data_uri:
                b64_data = data_uri.split(",", 1)[1]
            else:
                b64_data = data_uri

            try:
                file_bytes = base64.b64decode(b64_data)
            except Exception as e:
                self._send_json({"error": f"Base64 decode error: {e}"}, status=400)
                return

            bg_dir = os.path.join(os.getcwd(), "backgrounds")
            os.makedirs(bg_dir, exist_ok=True)
            target_path = os.path.join(bg_dir, safe_name)

            with open(target_path, "wb") as f:
                f.write(file_bytes)

            rel_path = f"backgrounds/{safe_name}"
            print(f"[Web Remote] Received & applied uploaded background: {safe_name} ({len(file_bytes)} bytes)")

            if self.config_manager:
                self.config_manager.update_dict({
                    "background": {
                        "enabled": True,
                        "source": rel_path
                    }
                })
                if WebRemoteHandler.on_change_callback:
                    try:
                        WebRemoteHandler.on_change_callback()
                    except Exception as e:
                        print(f"[Web Remote] Error in upload callback: {e}")

            self._send_json({
                "status": "ok",
                "filename": safe_name,
                "path": rel_path,
                "message": f"Successfully uploaded and applied {safe_name}"
            })
            return

        elif self.path == "/api/config":
            if self.config_manager:
                self.config_manager.update_dict(payload)
                if WebRemoteHandler.on_change_callback:
                    try:
                        WebRemoteHandler.on_change_callback()
                    except Exception as e:
                        print(f"[Web Remote] Error in config callback: {e}")
            self._send_json({"status": "ok", "message": "Configuration updated"})
        elif self.path == "/api/gallery/select":
            path = payload.get("path")
            if path and self.config_manager:
                self.config_manager.update_dict({
                    "background": {
                        "enabled": True,
                        "source": path
                    }
                })
                if WebRemoteHandler.on_change_callback:
                    try:
                        WebRemoteHandler.on_change_callback()
                    except Exception as e:
                        print(f"[Web Remote] Error in select callback: {e}")
            self._send_json({"status": "ok", "path": path})

        elif self.path == "/api/gallery/delete":
            filename = payload.get("filename")
            if filename:
                safe_name = os.path.basename(filename)
                target_fp = os.path.join(os.getcwd(), "backgrounds", safe_name)
                if os.path.exists(target_fp) and os.path.isfile(target_fp):
                    try:
                        os.remove(target_fp)
                        print(f"[Web Remote] Deleted file from gallery: {safe_name}")

                        # Check if deleted file was currently active
                        if self.config_manager:
                            bg_cfg = self.config_manager.data.get("background", {})
                            curr_src = bg_cfg.get("source", "")
                            if safe_name in curr_src:
                                self.config_manager.update_dict({
                                    "background": {
                                        "source": "oceans"
                                    }
                                })
                            if WebRemoteHandler.on_change_callback:
                                try:
                                    WebRemoteHandler.on_change_callback()
                                except Exception as e:
                                    print(f"[Web Remote] Error in delete callback: {e}")

                        self._send_json({"status": "ok", "message": f"Deleted {safe_name}"})
                        return
                    except Exception as e:
                        self._send_json({"error": f"Failed to delete {safe_name}: {e}"}, status=500)
                        return
                else:
                    self._send_json({"error": "File not found"}, status=404)
                    return
            self._send_json({"error": "Filename required"}, status=400)

        elif self.path == "/api/action":
            action = payload.get("action")
            if WebRemoteHandler.action_callback and action:
                try:
                    WebRemoteHandler.action_callback(action)
                except Exception as e:
                    print(f"[Web Remote] Error in action callback: {e}")
            self._send_json({"status": "ok", "action": action})
        else:
            self.send_response(404)
            self.end_headers()


class ThreadedHTTPServer(ThreadingHTTPServer):
    """Multi-threaded HTTP Server with socket address reuse to prevent address-in-use errors."""
    allow_reuse_address = True
    daemon_threads = True

def start_web_remote(config_manager, on_change: Optional[Callable] = None, on_action: Optional[Callable] = None, port: int = 8080, host: str = "0.0.0.0", blocking: bool = False):
    """Starts the HTTP server on a background daemon thread or in blocking mode."""
    WebRemoteHandler.config_manager = config_manager
    WebRemoteHandler.on_change_callback = staticmethod(on_change) if on_change else None
    WebRemoteHandler.action_callback = staticmethod(on_action) if on_action else None

    local_ip = get_local_ip()
    print("\n" + "=" * 70)
    print("  📱 PICLOCK REMOTE CONTROL READY!")
    print(f"  💻 On this PC:       http://localhost:{port}")
    print(f"  📱 On your Phone:    http://{local_ip}:{port}")
    print(f"  🌐 Clock Simulator:  http://{local_ip}:{port}/preview")
    print("=" * 70 + "\n")

    def run_server():
        try:
            server = ThreadedHTTPServer((host, port), WebRemoteHandler)
            server.serve_forever()
        except OSError as e:
            if getattr(e, 'winerror', None) == 10048 or "already in use" in str(e).lower():
                print(f"\n[Web Remote ERROR] Port {port} is already in use by another program!")
                print(f"[Web Remote] Please close any other running PiClock instance or check task manager.")
            else:
                print(f"[Web Remote] Warning: Could not start web remote on {host}:{port}: {e}")
        except Exception as e:
            print(f"[Web Remote] Warning: Could not start web remote on {host}:{port}: {e}")

    if blocking:
        run_server()
        return None
    else:
        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()
        return thread
