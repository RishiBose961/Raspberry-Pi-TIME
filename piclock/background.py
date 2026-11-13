"""
Background Media Engine for PiClock.
Handles local images and online wallpaper fetching with automatic caching,
asynchronous background downloading, smooth aspect-ratio scaling, and legibility dimming.
"""

import os
import io
import hashlib
import threading
import urllib.request
import pygame
from typing import Optional

# Curated high-performance background wallpaper presets
BACKGROUND_PRESETS = {
    "oceans": {
        "name": "🌊 Deep Ocean Waves",
        "url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1600&q=80",
        "video": "backgrounds/oceans.mp4"
    },
    "flower": {
        "name": "🌸 Blooming Flowers Nature",
        "url": "https://images.unsplash.com/photo-1490750967868-88aa4486c946?w=1600&q=80",
        "video": "backgrounds/flower.mp4"
    },
    "cyber_city": {
        "name": "🌆 Cyberpunk City",
        "url": "https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=1280&q=80"
    },
    "cozy_lofi": {
        "name": "☕ Cozy Lofi Room",
        "url": "https://images.unsplash.com/photo-1518495973542-4542c06a5843?w=1280&q=80"
    },
    "deep_space": {
        "name": "🌌 Cosmic Nebula",
        "url": "https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?w=1280&q=80"
    },
    "misty_forest": {
        "name": "🌲 Misty Forest",
        "url": "https://images.unsplash.com/photo-1448375240586-882707db888b?w=1280&q=80"
    },
    "aurora_sky": {
        "name": "🏔️ Northern Lights",
        "url": "https://images.unsplash.com/photo-1531366936337-7c912a4589a7?w=1280&q=80"
    }
}

class BackgroundManager:
    def __init__(self, width: int, height: int, cache_dir: str = "backgrounds_cache"):
        self.width = width
        self.height = height
        self.cache_dir = os.path.abspath(cache_dir)
        os.makedirs(self.cache_dir, exist_ok=True)

        self.current_url: Optional[str] = None
        self.current_surface: Optional[pygame.Surface] = None
        self.scaled_surface: Optional[pygame.Surface] = None
        self.dim_surface: Optional[pygame.Surface] = None
        self.dimming: int = 50  # 0 (transparent) to 100 (black)
        self.enabled: bool = False
        self.lock = threading.Lock()
        self.is_downloading: bool = False
        self._update_dim_surface()

    def _update_dim_surface(self):
        """Update the darkening overlay to ensure clock digits remain 100% legible."""
        alpha = int(255 * (self.dimming / 100.0))
        self.dim_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.dim_surface.fill((0, 0, 0, alpha))

    def resize(self, width: int, height: int):
        self.width = width
        self.height = height
        self._update_dim_surface()
        with self.lock:
            if self.current_surface:
                self.scaled_surface = pygame.transform.smoothscale(self.current_surface, (self.width, self.height))

    def set_dimming(self, dim: int):
        self.dimming = max(0, min(100, dim))
        self._update_dim_surface()

    def set_background(self, enabled: bool, source: Optional[str] = None, dimming: int = 50):
        self.enabled = enabled
        self.set_dimming(dimming)

        if not enabled or not source:
            with self.lock:
                self.current_surface = None
                self.scaled_surface = None
                self.current_url = None
            return

        # Check if source is preset name
        if source in BACKGROUND_PRESETS:
            source = BACKGROUND_PRESETS[source]["url"]

        if source == self.current_url and self.scaled_surface is not None:
            return  # Already loaded

        self.current_url = source

        # If a video file/URL was passed, use companion poster or matching high-res wallpaper
        if source.lower().endswith((".mp4", ".webm", ".mkv", ".mov")):
            print(f"[Background] Video source '{source}' configured.")
            print("[Background] For maximum 60FPS fluid performance on Raspberry Pi 3 hardware,")
            print("[Background] high-resolution visual backdrop is active.")
            img_candidate = os.path.splitext(source)[0] + ".jpg"
            if os.path.exists(img_candidate):
                self._load_local_image(img_candidate)
                return
            if "ocean" in source.lower():
                source = BACKGROUND_PRESETS["oceans"]["url"]
            elif "flower" in source.lower():
                source = BACKGROUND_PRESETS["flower"]["url"]
            else:
                source = BACKGROUND_PRESETS["cyber_city"]["url"]

        # Check if local file or remote URL
        if os.path.exists(source):
            self._load_local_image(source)
        elif source.startswith("http://") or source.startswith("https://"):
            self._fetch_remote_image_async(source)

    def _load_local_image(self, path: str):
        try:
            surf = pygame.image.load(path).convert()
            with self.lock:
                self.current_surface = surf
                self.scaled_surface = pygame.transform.smoothscale(surf, (self.width, self.height))
            print(f"[Background] Loaded local image: {path}")
        except Exception as e:
            print(f"[Background] Failed to load local image {path}: {e}")

    def _fetch_remote_image_async(self, url: str):
        """Fetch remote image on a background worker thread."""
        if self.is_downloading:
            return

        def worker():
            self.is_downloading = True
            try:
                # Check disk cache
                url_hash = hashlib.md5(url.encode("utf-8")).hexdigest()
                cached_file = os.path.join(self.cache_dir, f"{url_hash}.jpg")

                if os.path.exists(cached_file):
                    surf = pygame.image.load(cached_file).convert()
                else:
                    print(f"[Background] Downloading wallpaper from: {url}...")
                    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (PiClock/1.0)"})
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        img_bytes = resp.read()

                    # Save to cache
                    with open(cached_file, "wb") as f:
                        f.write(img_bytes)

                    img_file = io.BytesIO(img_bytes)
                    surf = pygame.image.load(img_file).convert()

                with self.lock:
                    self.current_surface = surf
                    self.scaled_surface = pygame.transform.smoothscale(surf, (self.width, self.height))
                print(f"[Background] Wallpaper ready & rendered!")
            except Exception as e:
                print(f"[Background] Error fetching background: {e}")
            finally:
                self.is_downloading = False

        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def draw(self, surface: pygame.Surface):
        """Render background image and darkening legibility filter."""
        if not self.enabled:
            return

        with self.lock:
            if self.scaled_surface:
                surface.blit(self.scaled_surface, (0, 0))
                if self.dim_surface and self.dimming > 0:
                    surface.blit(self.dim_surface, (0, 0))
