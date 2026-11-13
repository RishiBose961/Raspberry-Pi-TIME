"""
Color palettes and theme definitions for PiClock.
"""

THEMES = {
    "cyberpunk": {
        "name": "Cyberpunk Neon",
        "background": (11, 8, 20),          # Deep midnight violet
        "clock_primary": (0, 240, 255),      # Electric cyan
        "clock_secondary": (255, 0, 128),    # Neon pink
        "date_color": (255, 230, 0),         # Cyber yellow
        "accent": (255, 0, 128),             # Neon pink
        "message_color": (160, 160, 200),
        "animation_colors": [
            (0, 240, 255),
            (255, 0, 128),
            (255, 230, 0),
            (140, 0, 255),
            (0, 255, 170)
        ]
    },
    "matrix": {
        "name": "Matrix Terminal",
        "background": (2, 10, 4),            # Void black-green
        "clock_primary": (0, 255, 100),      # Bright hacker green
        "clock_secondary": (180, 255, 200),  # Phosphor white-green
        "date_color": (0, 200, 70),          # Medium green
        "accent": (0, 255, 100),
        "message_color": (0, 170, 60),
        "animation_colors": [
            (0, 255, 100),
            (0, 200, 60),
            (0, 140, 40),
            (200, 255, 220),
            (0, 80, 20)
        ]
    },
    "synthwave": {
        "name": "Synthwave Sunset",
        "background": (13, 2, 33),           # Deep retro navy
        "clock_primary": (255, 42, 133),     # Sunset magenta
        "clock_secondary": (5, 217, 232),    # Retro aqua
        "date_color": (255, 140, 0),         # Warm sunset orange
        "accent": (255, 190, 11),            # Sun yellow
        "message_color": (200, 150, 220),
        "animation_colors": [
            (255, 42, 133),
            (5, 217, 232),
            (255, 140, 0),
            (160, 32, 240),
            (255, 190, 11)
        ]
    },
    "midnight": {
        "name": "Midnight Ice",
        "background": (4, 8, 18),            # Deep space black
        "clock_primary": (30, 144, 255),     # Dodger blue
        "clock_secondary": (0, 229, 255),    # Ice blue
        "date_color": (176, 224, 230),       # Powder blue
        "accent": (0, 229, 255),
        "message_color": (120, 160, 200),
        "animation_colors": [
            (30, 144, 255),
            (0, 229, 255),
            (100, 180, 255),
            (200, 240, 255),
            (70, 130, 180)
        ]
    },
    "amber": {
        "name": "Retro Amber CRT",
        "background": (12, 7, 0),            # Deep warm amber-black
        "clock_primary": (255, 176, 0),      # Vintage amber
        "clock_secondary": (255, 210, 80),   # Light amber
        "date_color": (210, 140, 0),         # Muted amber
        "accent": (255, 176, 0),
        "message_color": (180, 120, 20),
        "animation_colors": [
            (255, 176, 0),
            (255, 200, 50),
            (200, 130, 0),
            (255, 230, 120),
            (150, 90, 0)
        ]
    },
    "sakura": {
        "name": "Sakura Bloom",
        "background": (18, 10, 15),          # Dark plum
        "clock_primary": (255, 105, 180),    # Hot pink
        "clock_secondary": (255, 182, 193),  # Light cherry pink
        "date_color": (255, 218, 224),       # Soft floral cream
        "accent": (255, 105, 180),
        "message_color": (210, 160, 180),
        "animation_colors": [
            (255, 105, 180),
            (255, 182, 193),
            (255, 220, 230),
            (230, 130, 170),
            (255, 192, 203)
        ]
    },
    "emerald": {
        "name": "Emerald Forest",
        "background": (4, 18, 10),           # Dark forest shadow
        "clock_primary": (0, 230, 118),      # Vivid emerald
        "clock_secondary": (105, 240, 174),  # Mint
        "date_color": (255, 215, 0),         # Gold accent
        "accent": (0, 230, 118),
        "message_color": (120, 190, 150),
        "animation_colors": [
            (0, 230, 118),
            (105, 240, 174),
            (255, 215, 0),
            (0, 180, 90),
            (200, 255, 220)
        ]
    },
    "oled_dark": {
        "name": "Minimalist OLED",
        "background": (0, 0, 0),             # True OLED Black
        "clock_primary": (250, 250, 250),    # Pure white
        "clock_secondary": (160, 160, 160),  # Slate grey
        "date_color": (200, 200, 200),       # Light silver
        "accent": (255, 255, 255),
        "message_color": (120, 120, 120),
        "animation_colors": [
            (250, 250, 250),
            (180, 180, 180),
            (120, 120, 120),
            (80, 80, 80),
            (220, 220, 220)
        ]
    }
}

THEME_KEYS = list(THEMES.keys())

def get_theme(theme_name: str) -> dict:
    """Retrieve theme dictionary by name with fallback to cyberpunk."""
    return THEMES.get(theme_name, THEMES["cyberpunk"])

def get_next_theme(current_name: str) -> str:
    """Cycle to the next theme."""
    try:
        idx = THEME_KEYS.index(current_name)
        return THEME_KEYS[(idx + 1) % len(THEME_KEYS)]
    except ValueError:
        return THEME_KEYS[0]
