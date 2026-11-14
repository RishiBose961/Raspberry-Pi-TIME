"""
PiClock - Main application loop for Raspberry Pi 3.
Combines animations, clock rendering, keyboard/touch inputs, and Web Remote.
"""

import os
import sys
import time
import queue
import datetime
import signal
import pygame

from .config import ConfigManager
from .themes import get_theme, get_next_theme
from .animations import create_animation, get_next_animation
from .clock import ClockRenderer
from .web_remote import start_web_remote
from .holidays import HolidayManager
from .background import BackgroundManager, BACKGROUND_PRESETS

COUNTRY_LIST = ["IN", "US", "UK", "CA", "AU", "GLOBAL", "ALL"]

class PiClockApp:
    def __init__(self, config_file: str = "config.json"):
        self.config_manager = ConfigManager(config_file)
        self.config = self.config_manager.data

        # Configure SDL environment for Raspberry Pi before pygame.init()
        self._setup_display_environment()

        pygame.init()
        pygame.font.init()

        # Display parameters
        disp_cfg = self.config.get("display", {})
        self.is_fullscreen = disp_cfg.get("fullscreen", True)
        self.width = disp_cfg.get("width", 1024)
        self.height = disp_cfg.get("height", 600)
        self.target_fps = disp_cfg.get("fps", 60)
        self.show_cursor = disp_cfg.get("show_cursor", False)

        # Create window or fullscreen display
        self.screen = None
        self._setup_screen()

        # Theme & Animation initialization
        theme_name = self.config.get("visual", {}).get("theme", "cyberpunk")
        self.current_theme_name = theme_name
        self.current_theme = get_theme(theme_name)

        anim_name = self.config.get("visual", {}).get("animation", "starfield")
        self.current_anim_name = anim_name
        anim_speed = float(self.config.get("visual", {}).get("animation_speed", 1.0))
        self.animation = create_animation(anim_name, self.width, self.height, self.current_theme, anim_speed)

        # Clock renderer
        font_scale = float(self.config.get("visual", {}).get("font_scale", 1.0))
        self.clock_renderer = ClockRenderer(self.width, self.height, self.current_theme, font_scale)

        # Holiday manager (100% offline, multi-country)
        hol_cfg = self.config.get("holiday", {})
        self.holiday_manager = HolidayManager(
            country=hol_cfg.get("country", "IN"),
            custom_holidays=hol_cfg.get("custom_holidays", [])
        )

        # Background media manager (online images, local wallpapers, presets, video loops, slideshow)
        self.bg_manager = BackgroundManager(self.width, self.height)
        bg_cfg = self.config.get("background", {})
        slide_cfg = bg_cfg.get("slideshow", {})
        self.bg_manager.set_slideshow(
            enabled=slide_cfg.get("enabled", False),
            interval=float(slide_cfg.get("interval", 10.0))
        )
        self.bg_manager.set_background(
            enabled=bg_cfg.get("enabled", True),
            source=bg_cfg.get("source", "oceans"),
            dimming=bg_cfg.get("dimming", 55)
        )

        # UI state
        self.show_help = False
        self.help_fade_timer = 4.0  # Show help banner for 4 seconds on startup
        self.running = True

        # Thread-safe command queue for Web Remote events
        self.cmd_queue = queue.Queue()

        # Web Remote
        web_cfg = self.config.get("web_remote", {})
        if web_cfg.get("enabled", True):
            port = web_cfg.get("port", 8080)
            bind = web_cfg.get("bind_address", "0.0.0.0")
            start_web_remote(
                self.config_manager,
                on_change=lambda *args, **kwargs: self.cmd_queue.put(("config_change", None)),
                on_action=lambda action, *args, **kwargs: self.cmd_queue.put(("action", action)),
                port=port,
                host=bind
            )

        # Handle system shutdown signals gracefully
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _setup_display_environment(self):
        """Configure Linux / Raspberry Pi environment drivers."""
        # Hide mouse cursor on framebuffer/touchscreens if requested
        if not self.config.get("display", {}).get("show_cursor", False):
            os.environ["SDL_NOMOUSE"] = "0"

    def _setup_screen(self):
        """Create Pygame display surface."""
        flags = pygame.DOUBLEBUF
        if self.is_fullscreen:
            flags |= pygame.FULLSCREEN
            # If fullscreen on Pi, query native resolution
            try:
                info = pygame.display.Info()
                if info.current_w > 0 and info.current_h > 0:
                    self.width = info.current_w
                    self.height = info.current_h
            except Exception:
                pass
            self.screen = pygame.display.set_mode((self.width, self.height), flags)
        else:
            flags |= pygame.RESIZABLE
            self.screen = pygame.display.set_mode((self.width, self.height), flags)

        pygame.display.set_caption("PiClock - Raspberry Pi 3")
        pygame.mouse.set_visible(self.show_cursor)

    def _signal_handler(self, sig, frame):
        print("\n[PiClock] Received exit signal. Shutting down cleanly...")
        self.running = False

    def on_external_config_change(self, *args, **kwargs):
        """Thread-safe enqueue when Web Remote updates configuration."""
        self.cmd_queue.put(("config_change", None))

    def on_remote_action(self, action: str, *args, **kwargs):
        """Thread-safe enqueue when Web Remote triggers an action button."""
        self.cmd_queue.put(("action", action))

    def process_remote_commands(self):
        """Processes pending remote commands safely on the main Pygame thread."""
        while not self.cmd_queue.empty():
            try:
                cmd_type, data = self.cmd_queue.get_nowait()
            except queue.Empty:
                break
            except Exception:
                break

            try:
                if cmd_type == "config_change":
                    self._apply_external_config_change()
                elif cmd_type == "action":
                    self._handle_remote_action(data)
            except Exception as e:
                print(f"[PiClock] Error processing remote command '{cmd_type}': {e}")

    def _apply_external_config_change(self):
        """Safely applies updated configuration on the main thread."""
        self.config = self.config_manager.data.copy()

        # Update theme if changed
        new_theme = self.config.get("visual", {}).get("theme", "cyberpunk")
        if new_theme != self.current_theme_name:
            self.set_theme(new_theme, persist=False)

        # Update animation if changed
        new_anim = self.config.get("visual", {}).get("animation", "starfield")
        if new_anim != self.current_anim_name:
            self.set_animation(new_anim, persist=False)

        # Update animation speed
        speed = float(self.config.get("visual", {}).get("animation_speed", 1.0))
        self.animation.set_speed(speed)

        # Update font scale if changed
        font_scale = float(self.config.get("visual", {}).get("font_scale", 1.0))
        if abs(self.clock_renderer.font_scale - font_scale) > 0.01:
            self.clock_renderer.set_font_scale(font_scale)

        # Update holiday configuration
        hol_cfg = self.config.get("holiday", {})
        self.holiday_manager.set_country(hol_cfg.get("country", "IN"))
        self.holiday_manager.set_custom_holidays(hol_cfg.get("custom_holidays", []))

        # Update background & slideshow configuration
        bg_cfg = self.config.get("background", {})
        slide_cfg = bg_cfg.get("slideshow", {})
        self.bg_manager.set_slideshow(
            enabled=slide_cfg.get("enabled", False),
            interval=float(slide_cfg.get("interval", 10.0))
        )
        self.bg_manager.set_background(
            enabled=bg_cfg.get("enabled", True),
            source=bg_cfg.get("source", "oceans"),
            dimming=bg_cfg.get("dimming", 55)
        )
        self.help_fade_timer = 2.0

    def _handle_remote_action(self, action: str):
        """Safely executes action buttons on the main thread."""
        if action == "next_theme":
            self.cycle_theme()
        elif action == "next_animation":
            self.cycle_animation()
        elif action == "cycle_country":
            self.cycle_country()
        elif action == "toggle_background":
            curr_bg = self.config.get("background", {}).get("enabled", False)
            self.config_manager.set(not curr_bg, "background", "enabled")
            self.bg_manager.enabled = not curr_bg
            self.help_fade_timer = 2.0
        elif action == "toggle_slideshow":
            slide_cfg = self.config.setdefault("background", {}).setdefault("slideshow", {})
            val = not slide_cfg.get("enabled", False)
            slide_cfg["enabled"] = val
            self.config_manager.set(val, "background", "slideshow", "enabled")
            self.bg_manager.set_slideshow(val, float(slide_cfg.get("interval", 10.0)))
            self.help_fade_timer = 2.0
        elif action == "toggle_24h":
            val = not self.config.get("clock", {}).get("format_24h", False)
            self.config_manager.set(val, "clock", "format_24h")
            self.config.setdefault("clock", {})["format_24h"] = val
            self.help_fade_timer = 2.0
        elif action == "toggle_seconds":
            val = not self.config.get("clock", {}).get("show_seconds", True)
            self.config_manager.set(val, "clock", "show_seconds")
            self.config.setdefault("clock", {})["show_seconds"] = val
            self.help_fade_timer = 2.0
        elif action == "toggle_fullscreen":
            self.toggle_fullscreen()
        elif action == "quit":
            self.running = False

    def set_theme(self, theme_name: str, persist: bool = True):
        self.current_theme_name = theme_name
        self.current_theme = get_theme(theme_name)
        self.animation.set_theme(self.current_theme)
        self.clock_renderer.set_theme(self.current_theme)
        if persist:
            self.config_manager.set(theme_name, "visual", "theme")

    def cycle_theme(self):
        next_t = get_next_theme(self.current_theme_name)
        self.set_theme(next_t)
        self.help_fade_timer = 2.0  # briefly show help

    def set_animation(self, anim_name: str, persist: bool = True):
        self.current_anim_name = anim_name
        speed = float(self.config.get("visual", {}).get("animation_speed", 1.0))
        self.animation = create_animation(anim_name, self.width, self.height, self.current_theme, speed)
        if persist:
            self.config_manager.set(anim_name, "visual", "animation")

    def cycle_animation(self):
        next_a = get_next_animation(self.current_anim_name)
        self.set_animation(next_a)
        self.help_fade_timer = 2.0

    def cycle_country(self):
        """Cycle holiday country (IN -> US -> UK -> CA -> AU -> GLOBAL -> ALL)."""
        curr = self.config.get("holiday", {}).get("country", "IN").upper()
        try:
            idx = COUNTRY_LIST.index(curr)
            next_c = COUNTRY_LIST[(idx + 1) % len(COUNTRY_LIST)]
        except ValueError:
            next_c = COUNTRY_LIST[0]
        self.config_manager.set(next_c, "holiday", "country")
        self.holiday_manager.set_country(next_c)
        self.help_fade_timer = 2.5
        print(f"[PiClock] Holiday country set to: {next_c}")

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        self.config_manager.set(self.is_fullscreen, "display", "fullscreen")
        self._setup_screen()
        self.handle_resize(self.width, self.height)

    def cycle_brightness(self):
        curr_b = self.config.get("display", {}).get("brightness", 100)
        steps = [100, 75, 50, 25]
        try:
            idx = steps.index(curr_b)
            next_b = steps[(idx + 1) % len(steps)]
        except ValueError:
            next_b = 100
        self.config_manager.set(next_b, "display", "brightness")

    def handle_resize(self, w: int, h: int):
        self.width = w
        self.height = h
        self.animation.resize(w, h)
        self.clock_renderer.resize(w, h)
        self.bg_manager.resize(w, h)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.handle_resize(event.w, event.h)
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    self.running = False
                elif event.key == pygame.K_m:
                    self.cycle_animation()
                elif event.key == pygame.K_c:
                    self.cycle_theme()
                elif event.key == pygame.K_l:
                    self.cycle_country()
                elif event.key == pygame.K_g:
                    # Toggle background wallpaper
                    curr_bg = self.config.get("background", {}).get("enabled", False)
                    self.config_manager.set(not curr_bg, "background", "enabled")
                    self.bg_manager.enabled = not curr_bg
                    self.help_fade_timer = 2.0
                elif event.key == pygame.K_o:
                    # Toggle Photo Slideshow mode
                    slide_cfg = self.config.setdefault("background", {}).setdefault("slideshow", {})
                    val = not slide_cfg.get("enabled", False)
                    slide_cfg["enabled"] = val
                    self.config_manager.set(val, "background", "slideshow", "enabled")
                    self.bg_manager.set_slideshow(val, float(slide_cfg.get("interval", 10.0)))
                    self.help_fade_timer = 2.0
                elif event.key == pygame.K_t:
                    curr_24h = self.config.get("clock", {}).get("format_24h", False)
                    self.config_manager.set(not curr_24h, "clock", "format_24h")
                elif event.key == pygame.K_s:
                    curr_sec = self.config.get("clock", {}).get("show_seconds", True)
                    self.config_manager.set(not curr_sec, "clock", "show_seconds")
                elif event.key == pygame.K_f:
                    self.toggle_fullscreen()
                elif event.key == pygame.K_b:
                    self.cycle_brightness()
                elif event.key == pygame.K_h:
                    self.show_help = not self.show_help
                elif event.key == pygame.K_UP:
                    curr_spd = float(self.config.get("visual", {}).get("animation_speed", 1.0))
                    new_spd = min(3.0, curr_spd + 0.2)
                    self.config_manager.set(new_spd, "visual", "animation_speed")
                    self.animation.set_speed(new_spd)
                elif event.key == pygame.K_DOWN:
                    curr_spd = float(self.config.get("visual", {}).get("animation_speed", 1.0))
                    new_spd = max(0.2, curr_spd - 0.2)
                    self.config_manager.set(new_spd, "visual", "animation_speed")
                    self.animation.set_speed(new_spd)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Screen tapped (e.g. on 7" touchscreen)
                # Tap top half = cycle animation, tap bottom half = cycle theme
                if event.pos[1] < self.height * 0.5:
                    self.cycle_animation()
                else:
                    self.cycle_theme()

    def run(self):
        """Main rendering loop."""
        clock = pygame.time.Clock()
        print("[PiClock] Running! Press [H] for hotkey shortcuts, or visit the Web Remote.")

        while self.running:
            dt = clock.tick(self.target_fps) / 1000.0  # Delta time in seconds

            # Process any pending commands from Web Remote / Mobile phone (thread-safe)
            self.process_remote_commands()

            # Update help timer
            if self.help_fade_timer > 0:
                self.help_fade_timer -= dt

            # Handle user events
            self.handle_events()

            # Clear screen with background color
            bg_color = self.current_theme.get("background", (10, 8, 20))
            self.screen.fill(bg_color)

            # Advance video playback frames / slideshow timer and draw background
            self.bg_manager.update(dt)
            self.bg_manager.draw(self.screen)

            # Update and draw animation (floating over background!)
            self.animation.update(dt)
            self.animation.draw(self.screen)

            # Holiday calculation
            hol_cfg = self.config.get("holiday", {})
            if hol_cfg.get("enabled", True):
                holiday_text, is_today = self.holiday_manager.get_status_string(datetime.date.today())
            else:
                holiday_text, is_today = "", False

            # Render clock, date, holiday banner, custom messages
            self.clock_renderer.render(
                self.screen,
                self.config,
                holiday_text=holiday_text,
                is_today_holiday=is_today,
                show_help=self.show_help,
                help_opacity=max(0.0, self.help_fade_timer)
            )

            # Flip buffer
            pygame.display.flip()

        self.bg_manager.cleanup()
        pygame.quit()
        sys.exit(0)

def main():
    config_file = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    app = PiClockApp(config_file=config_file)
    app.run()

if __name__ == "__main__":
    main()
