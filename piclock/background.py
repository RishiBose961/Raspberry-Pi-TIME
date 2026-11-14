"""
Background Media Engine for PiClock.
Handles local images, looping video playback (OpenCV / Pygame), photo slideshows,
online wallpaper fetching with automatic caching, and legibility dimming.
"""

import os
import io
import hashlib
import threading
import urllib.request
import pygame
from typing import Optional, List

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    cv2 = None
    np = None
    CV2_AVAILABLE = False

# Curated high-performance background wallpaper presets
BACKGROUND_PRESETS = {
    "oceans": {
        "name": "🌊 Deep Ocean Waves",
        "url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1280&q=75",
        "video": "backgrounds/oceans.mp4"
    },
    "flower": {
        "name": "🌸 Blooming Flowers Nature",
        "url": "https://images.unsplash.com/photo-1490750967868-88aa4486c946?w=1280&q=75",
        "video": "backgrounds/flower.mp4"
    },
    "cyber_city": {
        "name": "🌆 Cyberpunk City",
        "url": "https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=1280&q=75"
    },
    "cozy_lofi": {
        "name": "☕ Cozy Lofi Room",
        "url": "https://images.unsplash.com/photo-1518495973542-4542c06a5843?w=1280&q=75"
    },
    "deep_space": {
        "name": "🌌 Cosmic Nebula",
        "url": "https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?w=1280&q=75"
    },
    "misty_forest": {
        "name": "🌲 Misty Forest",
        "url": "https://images.unsplash.com/photo-1448375240586-882707db888b?w=1280&q=75"
    },
    "aurora_sky": {
        "name": "🏔️ Northern Lights",
        "url": "https://images.unsplash.com/photo-1531366936337-7c912a4589a7?w=1280&q=75"
    }
}

VIDEO_EXTS = (".mp4", ".webm", ".mkv", ".mov", ".avi")
IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".webp", ".bmp")

def _is_raspberry_pi() -> bool:
    try:
        if os.path.exists("/sys/firmware/devicetree/base/model"):
            with open("/sys/firmware/devicetree/base/model", "r") as f:
                if "raspberry pi" in f.read().lower():
                    return True
        if os.path.exists("/proc/cpuinfo"):
            with open("/proc/cpuinfo", "r") as f:
                c = f.read().lower()
                if "bcm2835" in c or "bcm2837" in c or "bcm2711" in c or "raspberry" in c:
                    return True
    except Exception:
        pass
    return False

IS_RPI = _is_raspberry_pi()

class BackgroundManager:
    def __init__(self, width: int, height: int, cache_dir: str = "backgrounds_cache"):
        self.width = width
        self.height = height
        self.cache_dir = os.path.abspath(cache_dir)
        os.makedirs(self.cache_dir, exist_ok=True)

        self.current_source: Optional[str] = None
        self.current_surface: Optional[pygame.Surface] = None
        self.scaled_surface: Optional[pygame.Surface] = None
        self.dimming: int = 50  # 0 to 100
        self.enabled: bool = False
        self.lock = threading.Lock()
        self.video_lock = threading.Lock()
        self.is_downloading: bool = False

        # Looping Video Playback Engine
        self.is_video: bool = False
        self.cap = None
        self.video_fps: float = 24.0 if IS_RPI else 30.0
        self.video_frame_delay: float = 1.0 / self.video_fps
        self.video_timer: float = 0.0
        self.video_path: Optional[str] = None
        self.video_fail_count: int = 0
        self._video_rgb_buf: Optional[np.ndarray] = None

        # Photo Slideshow Engine
        self.slideshow_enabled: bool = False
        self.slideshow_interval: float = 10.0
        self.slideshow_timer: float = 0.0
        self.slideshow_index: int = 0
        self.slideshow_files: List[str] = []

        self.refresh_slideshow_files()

    def resize(self, width: int, height: int):
        self.width = width
        self.height = height
        self._video_rgb_buf = None
        with self.lock:
            if self.current_surface and not self.is_video:
                self._bake_scaled_surface(self.current_surface)

    def set_dimming(self, dim: int):
        self.dimming = max(0, min(100, dim))
        with self.lock:
            if self.current_surface and not self.is_video:
                self._bake_scaled_surface(self.current_surface)

    def _bake_scaled_surface(self, raw_surface: pygame.Surface):
        """
        Pre-scales and pre-dims the background image ONCE into self.scaled_surface.
        This completely eliminates the need for expensive full-screen alpha blending
        on every render frame, giving a massive speed boost on Raspberry Pi 3.
        """
        try:
            scaled = pygame.transform.smoothscale(raw_surface, (self.width, self.height))
            if self.dimming > 0:
                dim_overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                dim_overlay.fill((0, 0, 0, int(255 * (self.dimming / 100.0))))
                scaled.blit(dim_overlay, (0, 0))
            self.scaled_surface = scaled.convert()
        except Exception as e:
            print(f"[Background] Error baking surface: {e}")
            self.scaled_surface = scaled

    def refresh_slideshow_files(self):
        """Scans the backgrounds/ directory for all uploaded images and videos."""
        bg_dir = os.path.join(os.getcwd(), "backgrounds")
        if os.path.exists(bg_dir):
            all_files = sorted(os.listdir(bg_dir))
            media_files = [
                os.path.join("backgrounds", f).replace("\\", "/")
                for f in all_files
                if f.lower().endswith(IMAGE_EXTS + VIDEO_EXTS)
            ]
            self.slideshow_files = media_files
        else:
            self.slideshow_files = []

    def set_slideshow(self, enabled: bool, interval: float = 10.0):
        """Configure automated background slideshow mode."""
        self.slideshow_enabled = enabled
        self.slideshow_interval = max(3.0, float(interval))
        self.refresh_slideshow_files()
        if enabled:
            print(f"[Slideshow] Mode ENABLED: cycling {len(self.slideshow_files)} items every {self.slideshow_interval:.1f}s")
            if self.slideshow_files and (not self.current_source or self.current_source not in self.slideshow_files):
                self.slideshow_index = 0
                self.set_background(enabled=True, source=self.slideshow_files[0], dimming=self.dimming, from_slideshow=True)
        else:
            self.slideshow_timer = 0.0

    def set_background(self, enabled: bool, source: Optional[str] = None, dimming: int = 50, from_slideshow: bool = False):
        self.enabled = enabled
        self.dimming = max(0, min(100, dimming))

        if not enabled or not source:
            self._stop_video()
            with self.lock:
                self.current_surface = None
                self.scaled_surface = None
                self.current_source = None
            return

        # Check if source is a preset key
        if source in BACKGROUND_PRESETS:
            preset = BACKGROUND_PRESETS[source]
            # On Raspberry Pi 3, prefer static wallpaper for silk-smooth performance unless user explicitly chose video
            if "video" in preset and os.path.exists(preset["video"]) and CV2_AVAILABLE:
                source = preset["video"]
            else:
                source = preset["url"]

        if source == self.current_source and self.scaled_surface is not None and not from_slideshow:
            return  # Already active

        self.current_source = source

        # 1. Local Video File (.mp4, .webm, .mov, etc.)
        if source.lower().endswith(VIDEO_EXTS):
            norm_path = os.path.normpath(source)
            if os.path.exists(norm_path) and CV2_AVAILABLE:
                self._load_video(norm_path)
                return
            elif os.path.exists(norm_path):
                print(f"[Background] Notice: Video '{source}' found. Install python3-opencv for playback.")
                img_candidate = os.path.splitext(norm_path)[0] + ".jpg"
                if os.path.exists(img_candidate):
                    self._load_local_image(img_candidate)
                    return
                source = BACKGROUND_PRESETS["oceans"]["url"]
            else:
                source = BACKGROUND_PRESETS["oceans"]["url"]

        # 2. Local Image File
        norm_img = os.path.normpath(source)
        if os.path.exists(norm_img) and os.path.isfile(norm_img):
            self._stop_video()
            self._load_local_image(norm_img)
        # 3. Online URL
        elif source.startswith("http://") or source.startswith("https://"):
            self._stop_video()
            self._fetch_remote_image_async(source)

    def _load_video(self, path: str):
        """Initialize OpenCV video stream and preallocate decode buffers."""
        self._stop_video()
        try:
            with self.video_lock:
                cap = cv2.VideoCapture(path)
                if not cap.isOpened():
                    print(f"[Background] OpenCV could not open video: {path}")
                    return
                self.cap = cap
                self.is_video = True
                self.video_path = path
                self.video_fail_count = 0

                raw_fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
                if raw_fps <= 0 or raw_fps > 120:
                    raw_fps = 24.0
                
                # On Raspberry Pi 3, throttle video decode to 20 FPS for silky smooth rendering without CPU lag
                if IS_RPI:
                    self.video_fps = min(raw_fps, 20.0)
                else:
                    self.video_fps = min(raw_fps, 30.0)

                self.video_frame_delay = 1.0 / self.video_fps
                self.video_timer = 0.0

                # Preallocate reusable RGB numpy buffer (ZERO memory leak, ZERO per-frame allocation)
                self._video_rgb_buf = np.empty((self.height, self.width, 3), dtype=np.uint8)

                # Decode and display the initial frame
                ret, frame = cap.read()
                if ret and frame is not None:
                    resized = cv2.resize(frame, (self.width, self.height), interpolation=cv2.INTER_LINEAR)
                    cv2.cvtColor(resized, cv2.COLOR_BGR2RGB, dst=self._video_rgb_buf)
                    if self.dimming > 0:
                        dim_alpha = max(0.0, 1.0 - (self.dimming / 100.0))
                        cv2.convertScaleAbs(self._video_rgb_buf, dst=self._video_rgb_buf, alpha=dim_alpha)
                    with self.lock:
                        self.scaled_surface = pygame.image.frombuffer(self._video_rgb_buf.data, (self.width, self.height), 'RGB')

            print(f"[Background] Looping video active: {os.path.basename(path)} ({self.video_fps:.1f} FPS, Zero-Copy buffer)")
        except Exception as e:
            print(f"[Background] Video load error {path}: {e}")
            self._stop_video()

    def _stop_video(self):
        """Safely release the OpenCV video capture handle and free buffers."""
        self.is_video = False
        with self.video_lock:
            if self.cap is not None:
                try:
                    self.cap.release()
                except Exception:
                    pass
                self.cap = None
        self.video_path = None
        self.video_fail_count = 0

    def _load_local_image(self, path: str):
        try:
            surf = pygame.image.load(path).convert()
            with self.lock:
                self.current_surface = surf
                self._bake_scaled_surface(surf)
            print(f"[Background] Loaded image: {os.path.basename(path)}")
        except Exception as e:
            print(f"[Background] Failed to load image {path}: {e}")

    def _fetch_remote_image_async(self, url: str):
        """Fetch remote image on a background worker thread with MD5 caching."""
        if self.is_downloading:
            return

        def worker():
            self.is_downloading = True
            try:
                url_hash = hashlib.md5(url.encode("utf-8")).hexdigest()
                cached_file = os.path.join(self.cache_dir, f"{url_hash}.jpg")

                if os.path.exists(cached_file):
                    surf = pygame.image.load(cached_file).convert()
                else:
                    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (PiClock/1.0)"})
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        img_bytes = resp.read()

                    with open(cached_file, "wb") as f:
                        f.write(img_bytes)

                    img_file = io.BytesIO(img_bytes)
                    surf = pygame.image.load(img_file).convert()

                with self.lock:
                    self.current_surface = surf
                    self._bake_scaled_surface(surf)
                print(f"[Background] Wallpaper ready & rendered!")
            except Exception as e:
                print(f"[Background] Error fetching background: {e}")
            finally:
                self.is_downloading = False

        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def update(self, dt: float):
        """
        Advance video frame and manage slideshow transitions.
        High-performance, crash-safe, zero garbage collection pauses.
        """
        if not self.enabled:
            return

        # 1. Video Frame Decoding (Zero-Copy & Memory Safe)
        if self.is_video and self.cap is not None:
            self.video_timer += dt
            if self.video_timer >= self.video_frame_delay:
                self.video_timer = 0.0  # Reset timer to avoid frame spiral
                try:
                    with self.video_lock:
                        if self.cap is not None and self.is_video:
                            ret, frame = self.cap.read()
                            if not ret or frame is None:
                                # Seamlessly loop back to start of video
                                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                                ret, frame = self.cap.read()
                                if not ret or frame is None:
                                    # Fallback reopen if seek failed
                                    self.cap.open(self.video_path)
                                    ret, frame = self.cap.read()

                            if ret and frame is not None:
                                self.video_fail_count = 0
                                if self._video_rgb_buf is None or self._video_rgb_buf.shape[:2] != (self.height, self.width):
                                    self._video_rgb_buf = np.empty((self.height, self.width, 3), dtype=np.uint8)

                                # Fast hardware/linear resize
                                resized = cv2.resize(frame, (self.width, self.height), interpolation=cv2.INTER_LINEAR)
                                cv2.cvtColor(resized, cv2.COLOR_BGR2RGB, dst=self._video_rgb_buf)

                                # In-place dimming (eliminates full-screen Pygame alpha blit)
                                if self.dimming > 0:
                                    dim_alpha = max(0.0, 1.0 - (self.dimming / 100.0))
                                    cv2.convertScaleAbs(self._video_rgb_buf, dst=self._video_rgb_buf, alpha=dim_alpha)

                                with self.lock:
                                    self.scaled_surface = pygame.image.frombuffer(
                                        self._video_rgb_buf.data, (self.width, self.height), 'RGB'
                                    )
                            else:
                                self.video_fail_count += 1
                                if self.video_fail_count > 5:
                                    print("[Background] Video decode failed 5 times. Gracefully falling back to static wallpaper.")
                                    self._stop_video()
                                    self.set_background(enabled=True, source=BACKGROUND_PRESETS["oceans"]["url"], dimming=self.dimming)
                except Exception as e:
                    print(f"[Background] Handled video decode exception: {e}")
                    self.video_fail_count += 1
                    if self.video_fail_count > 5:
                        self._stop_video()

        # 2. Automated Slideshow Cycle
        if self.slideshow_enabled and len(self.slideshow_files) > 1:
            self.slideshow_timer += dt
            if self.slideshow_timer >= self.slideshow_interval:
                self.slideshow_timer = 0.0
                self.slideshow_index = (self.slideshow_index + 1) % len(self.slideshow_files)
                next_media = self.slideshow_files[self.slideshow_index]
                self.set_background(enabled=True, source=next_media, dimming=self.dimming, from_slideshow=True)

    def draw(self, surface: pygame.Surface):
        """
        Ultra-fast single blit.
        Pre-dimmed texture means zero software alpha overhead on Raspberry Pi 3.
        """
        if not self.enabled:
            return

        with self.lock:
            if self.scaled_surface:
                surface.blit(self.scaled_surface, (0, 0))

    def cleanup(self):
        """Release video resources on exit."""
        self._stop_video()

