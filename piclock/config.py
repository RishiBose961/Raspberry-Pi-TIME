"""
Configuration management for PiClock.
Handles reading, writing, and validating config.json safely with thread locking.
"""

import json
import os
import threading
from typing import Any, Dict

DEFAULT_CONFIG: Dict[str, Any] = {
    "display": {
        "fullscreen": False,
        "width": 1024,
        "height": 600,
        "fps": 60,
        "brightness": 100,  # 10 to 100%
        "show_cursor": False
    },
    "clock": {
        "format_24h": False,
        "show_seconds": True,
        "blink_colon": True,
        "date_format": "%A, %B %d, %Y",
        "custom_message": "Raspberry Pi 3",
        "show_message": True
    },
    "visual": {
        "theme": "cyberpunk",
        "animation": "starfield",     # starfield, matrix, particles, waves, minimalist
        "animation_speed": 1.0,
        "particle_count": 80,
        "glow_effect": True,
        "font_scale": 1.0
    },
    "web_remote": {
        "enabled": True,
        "port": 8080,
        "bind_address": "0.0.0.0"
    },
    "holiday": {
        "enabled": True,
        "country": "IN",              # IN, US, UK, CA, AU, GLOBAL, ALL
        "show_upcoming": True,
        "custom_holidays": []
    },
    "background": {
        "enabled": False,
        "source": "cyber_city",       # preset name, URL, or local image path
        "dimming": 55                 # 0 to 100% dark overlay for readability
    }
}

class ConfigManager:
    """Thread-safe configuration manager."""
    def __init__(self, config_path: str = "config.json"):
        self.config_path = os.path.abspath(config_path)
        self.lock = threading.Lock()
        self.data: Dict[str, Any] = {}
        self.load()

    def _deep_merge(self, base: dict, override: dict) -> dict:
        """Deep merge two dictionaries."""
        merged = base.copy()
        for key, value in override.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._deep_merge(merged[key], value)
            else:
                merged[key] = value
        return merged

    def load(self) -> Dict[str, Any]:
        """Load configuration from disk, falling back to defaults for missing keys."""
        with self.lock:
            if os.path.exists(self.config_path):
                try:
                    with open(self.config_path, "r", encoding="utf-8") as f:
                        user_config = json.load(f)
                    self.data = self._deep_merge(DEFAULT_CONFIG, user_config)
                except Exception as e:
                    print(f"[Config] Error reading {self.config_path}: {e}. Using defaults.")
                    self.data = DEFAULT_CONFIG.copy()
            else:
                print(f"[Config] {self.config_path} not found. Creating with default settings.")
                self.data = DEFAULT_CONFIG.copy()
                self._save_unlocked()
            return self.data.copy()

    def _save_unlocked(self):
        """Internal save without acquiring lock."""
        try:
            tmp_path = f"{self.config_path}.tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
            if os.path.exists(self.config_path):
                os.replace(tmp_path, self.config_path)
            else:
                os.rename(tmp_path, self.config_path)
        except Exception as e:
            print(f"[Config] Failed to save config: {e}")

    def save(self):
        """Save current configuration to disk safely."""
        with self.lock:
            self._save_unlocked()

    def get(self, *keys, default=None):
        """Retrieve nested configuration value."""
        with self.lock:
            curr = self.data
            for key in keys:
                if isinstance(curr, dict) and key in curr:
                    curr = curr[key]
                else:
                    return default
            return curr

    def set(self, value, *keys):
        """Set nested configuration value and persist."""
        with self.lock:
            curr = self.data
            for key in keys[:-1]:
                if key not in curr or not isinstance(curr[key], dict):
                    curr[key] = {}
                curr = curr[key]
            curr[keys[-1]] = value
            self._save_unlocked()

    def update_dict(self, new_data: dict):
        """Merge a dictionary into config and persist."""
        with self.lock:
            self.data = self._deep_merge(self.data, new_data)
            self._save_unlocked()
