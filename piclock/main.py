"""
PiClock - Main application loop for Raspberry Pi 3.
Combines animations, clock rendering, keyboard/touch inputs, and Web Remote.
"""

import os
import sys
import time
import signal
import pygame

from .config import ConfigManager
from .themes import get_theme, get_next_theme
from .animations import create_animation, get_next_animation
from .clock import ClockRenderer
from .web_remote import start_web_remote

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

        # UI state
        self.show_help = False
        self.help_fade_timer = 4.0  # Show help banner for 4 seconds on startup
        self.running = True

        # Web Remote
        web_cfg = self.config.get("web_remote", {})
        if web_cfg.get("enabled", True):
            port = web_cfg.get("port", 8080)
            bind = web_cfg.get("bind_address", "0.0.0.0")
            start_web_remote(
                self.config_manager,
                on_change=self.on_external_config_change,
                on_action=self.on_remote_action,
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

    def on_external_config_change(self):
        """Invoked when Web Remote updates configuration."""
        self.config = self.config_manager.data

        # Update theme if changed
        new_theme = self.config.get("visual", {}).get("theme", "cyberpunk")
        if new_theme != self.current_theme_name:
            self.set_theme(new_theme, persist=False)

        # Update animation if changed
        new_anim = self.config.get("visual", {}).get("animation", "starfield")
        if new_anim != self.current_anim_name:
            self.set_animation(new_anim, persist=False)

        # Update speed
        speed = float(self.config.get("visual", {}).get("animation_speed", 1.0))
        self.animation.set_speed(speed)

    def on_remote_action(self, action: str):
        """Invoked when Web Remote triggers an action button."""
        if action == "next_theme":
            self.cycle_theme()
        elif action == "next_animation":
            self.cycle_animation()
        elif action == "toggle_24h":
            val = not self.config.get("clock", {}).get("format_24h", False)
            self.config_manager.set(val, "clock", "format_24h")
        elif action == "toggle_seconds":
            val = not self.config.get("clock", {}).get("show_seconds", True)
            self.config_manager.set(val, "clock", "show_seconds")
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

            # Update help timer
            if self.help_fade_timer > 0:
                self.help_fade_timer -= dt

            # Handle user events
            self.handle_events()

            # Clear screen with background color
            bg_color = self.current_theme.get("background", (10, 8, 20))
            self.screen.fill(bg_color)

            # Update and draw animation
            self.animation.update(dt)
            self.animation.draw(self.screen)

            # Render clock, date, custom messages
            self.clock_renderer.render(
                self.screen,
                self.config,
                show_help=self.show_help,
                help_opacity=max(0.0, self.help_fade_timer)
            )

            # Flip buffer
            pygame.display.flip()

        pygame.quit()
        sys.exit(0)

def main():
    config_file = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    app = PiClockApp(config_file=config_file)
    app.run()

if __name__ == "__main__":
    main()
