"""
Clock & text renderer for PiClock.
Handles date/time formatting, dynamic resolution scaling, glowing shadows,
custom messages, and brightness dimming.
"""

import datetime
import math
import pygame

class ClockRenderer:
    def __init__(self, width: int, height: int, theme: dict, font_scale: float = 1.0):
        self.width = width
        self.height = height
        self.theme = theme
        self.font_scale = font_scale
        self.font_time = None
        self.font_seconds = None
        self.font_ampm = None
        self.font_date = None
        self.font_msg = None
        self.font_help = None
        self._init_fonts()

    def _init_fonts(self):
        """Scale fonts smoothly based on current screen dimensions."""
        if not pygame.font.get_init():
            pygame.font.init()
        base_h = self.height
        # Proportional font sizes based on screen height
        time_size = int(base_h * 0.26 * self.font_scale)
        sec_size = int(time_size * 0.52)
        ampm_size = int(time_size * 0.38)
        date_size = int(base_h * 0.065 * self.font_scale)
        msg_size = int(base_h * 0.045 * self.font_scale)
        help_size = int(base_h * 0.038)

        # Monospace or clean Sans fonts
        font_names = ["consolas", "dejavusansmono", "liberationsans", "ubuntu", "courier", "monospace"]
        self.font_time = pygame.font.SysFont(font_names, max(18, time_size), bold=True)
        self.font_seconds = pygame.font.SysFont(font_names, max(12, sec_size), bold=True)
        self.font_ampm = pygame.font.SysFont(font_names, max(10, ampm_size), bold=True)
        self.font_date = pygame.font.SysFont(font_names, max(12, date_size), bold=False)
        self.font_msg = pygame.font.SysFont(font_names, max(10, msg_size), italic=True)
        self.font_help = pygame.font.SysFont(font_names, max(10, help_size))

    def resize(self, width: int, height: int):
        self.width = width
        self.height = height
        self._init_fonts()

    def set_theme(self, theme: dict):
        self.theme = theme

    def set_font_scale(self, scale: float):
        self.font_scale = max(0.6, min(1.8, scale))
        self._init_fonts()

    def _render_glow_text(self, surface: pygame.Surface, text: str, font: pygame.font.Font,
                          color: tuple, pos: tuple, glow: bool = True, anchor: str = "center"):
        """Render text with an ambient drop-shadow / glow."""
        text_surf = font.render(text, True, color)
        rect = text_surf.get_rect()
        if anchor == "center":
            rect.center = pos
        elif anchor == "topleft":
            rect.topleft = pos
        elif anchor == "midleft":
            rect.midleft = pos
        elif anchor == "midright":
            rect.midright = pos
        elif anchor == "bottomcenter":
            rect.midbottom = pos

        if glow:
            glow_color = (max(0, color[0] // 4), max(0, color[1] // 4), max(0, color[2] // 4))
            glow_surf = font.render(text, True, glow_color)
            for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-3, -3), (3, 3)]:
                surface.blit(glow_surf, (rect.x + dx, rect.y + dy))

        surface.blit(text_surf, rect)
        return rect

    def render(self, surface: pygame.Surface, config: dict, show_help: bool = False, help_opacity: float = 0.0):
        """Render the complete clock, date, custom message, and overlays."""
        now = datetime.datetime.now()

        format_24h = config.get("clock", {}).get("format_24h", False)
        show_seconds = config.get("clock", {}).get("show_seconds", True)
        blink_colon = config.get("clock", {}).get("blink_colon", True)
        date_format = config.get("clock", {}).get("date_format", "%A, %B %d, %Y")
        custom_message = config.get("clock", {}).get("custom_message", "Raspberry Pi 3")
        show_message = config.get("clock", {}).get("show_message", True)
        glow_enabled = config.get("visual", {}).get("glow_effect", True)
        brightness = config.get("display", {}).get("brightness", 100)

        # 1. Format Time String
        if format_24h:
            hours_str = now.strftime("%H")
            ampm_str = ""
        else:
            hours_str = now.strftime("%I").lstrip("0")
            if not hours_str:
                hours_str = "12"
            ampm_str = now.strftime("%p")

        mins_str = now.strftime("%M")
        secs_str = now.strftime("%S")

        # Colon blinking logic (500ms on, 500ms off)
        colon = ":"
        if blink_colon and now.microsecond < 500000:
            colon = " "

        primary_color = self.theme.get("clock_primary", (0, 240, 255))
        secondary_color = self.theme.get("clock_secondary", (255, 0, 128))
        date_color = self.theme.get("date_color", (255, 230, 0))
        msg_color = self.theme.get("message_color", (160, 160, 200))
        accent_color = self.theme.get("accent", (255, 0, 128))

        # Center coordinates
        center_x = self.width // 2
        time_y = int(self.height * 0.40)

        # Render Time digits with exact spacing
        time_text = f"{hours_str}{colon}{mins_str}"
        time_surf = self.font_time.render(time_text, True, primary_color)
        t_w, t_h = time_surf.get_size()

        # If seconds or AM/PM shown, calculate full composite width
        extra_w = 0
        if show_seconds or ampm_str:
            extra_w = int(self.font_seconds.size(" 00")[0] * 1.1)

        total_w = t_w + extra_w
        start_x = center_x - (total_w // 2)

        # Draw main time text
        time_pos = (start_x + (t_w // 2), time_y)
        self._render_glow_text(surface, time_text, self.font_time, primary_color, time_pos, glow=glow_enabled, anchor="center")

        # Draw seconds and AM/PM to the right of time
        right_x = start_x + t_w + int(self.width * 0.015)
        if show_seconds and ampm_str:
            sec_pos = (right_x, time_y - int(t_h * 0.18))
            self._render_glow_text(surface, secs_str, self.font_seconds, secondary_color, sec_pos, glow=glow_enabled, anchor="midleft")

            ampm_pos = (right_x, time_y + int(t_h * 0.22))
            self._render_glow_text(surface, ampm_str, self.font_ampm, accent_color, ampm_pos, glow=glow_enabled, anchor="midleft")
        elif show_seconds:
            sec_pos = (right_x, time_y)
            self._render_glow_text(surface, secs_str, self.font_seconds, secondary_color, sec_pos, glow=glow_enabled, anchor="midleft")
        elif ampm_str:
            ampm_pos = (right_x, time_y)
            self._render_glow_text(surface, ampm_str, self.font_ampm, accent_color, ampm_pos, glow=glow_enabled, anchor="midleft")

        # 2. Date Text
        try:
            date_text = now.strftime(date_format)
        except Exception:
            date_text = now.strftime("%A, %B %d, %Y")

        date_y = int(self.height * 0.60)
        self._render_glow_text(surface, date_text, self.font_date, date_color, (center_x, date_y), glow=glow_enabled, anchor="center")

        # 3. Custom message / Status banner
        if show_message and custom_message:
            msg_y = int(self.height * 0.78)
            self._render_glow_text(surface, custom_message, self.font_msg, msg_color, (center_x, msg_y), glow=False, anchor="center")

        # 4. On-screen Help Overlay (when active)
        if show_help or help_opacity > 0.05:
            help_lines = [
                "SHORTCUTS:  [M] Mode  |  [C] Theme  |  [T] 12/24h  |  [S] Seconds  |  [F] Fullscreen  |  [H] Toggle Help  |  [Q/ESC] Quit",
                "Web Remote: http://<raspberry-pi-ip>:8080"
            ]
            overlay_h = int(len(help_lines) * 28 + 14)
            overlay_surf = pygame.Surface((self.width, overlay_h), pygame.SRCALPHA)
            overlay_surf.fill((10, 10, 15, int(210 * min(1.0, help_opacity))))

            for i, line in enumerate(help_lines):
                line_surf = self.font_help.render(line, True, (220, 230, 245))
                overlay_surf.blit(line_surf, ((self.width - line_surf.get_width()) // 2, 8 + i * 26))

            surface.blit(overlay_surf, (0, self.height - overlay_h))

        # 5. Software Brightness Dimmer (0-100%)
        if brightness < 100:
            dim_factor = max(0, min(100, brightness))
            dim_alpha = int(255 * (1.0 - (dim_factor / 100.0)))
            dim_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            dim_surf.fill((0, 0, 0, dim_alpha))
            surface.blit(dim_surf, (0, 0))
