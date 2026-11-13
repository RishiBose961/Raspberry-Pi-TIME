"""
Digital Matrix Rain animation.
Renders cascading digital rain with bright leading glyphs and fading phosphor trails.
Optimized with surface caching for Raspberry Pi 3.
"""

import random
import pygame
from .base import BaseAnimation

CHAR_SET = "0123456789ABCDEF$#@*+<>~-=%&"

class MatrixAnimation(BaseAnimation):
    def __init__(self, width: int, height: int, theme: dict, speed: float = 1.0):
        super().__init__(width, height, theme, speed)
        if not pygame.font.get_init():
            pygame.font.init()
        self.font_size = 20
        self.font = pygame.font.SysFont("monospace", self.font_size, bold=True)
        self.glyph_cache = {}
        self.columns = []
        self._init_columns()

    def _get_glyph(self, char: str, color: tuple) -> pygame.Surface:
        key = (char, color)
        if key not in self.glyph_cache:
            self.glyph_cache[key] = self.font.render(char, True, color)
        return self.glyph_cache[key]

    def _init_columns(self):
        self.glyph_cache.clear()
        col_width = self.font_size + 4
        num_cols = max(10, self.width // col_width)
        self.columns = []

        for i in range(num_cols):
            x = i * col_width
            y = random.uniform(-self.height, 0)
            col_speed = random.uniform(80, 220)
            trail_len = random.randint(6, 16)
            chars = [random.choice(CHAR_SET) for _ in range(trail_len)]
            self.columns.append({
                "x": x,
                "y": y,
                "speed": col_speed,
                "trail_len": trail_len,
                "chars": chars,
                "mutate_timer": random.uniform(0.05, 0.2)
            })

    def resize(self, width: int, height: int):
        super().resize(width, height)
        self._init_columns()

    def set_theme(self, theme: dict):
        super().set_theme(theme)
        self.glyph_cache.clear()

    def update(self, dt: float):
        row_height = self.font_size + 2
        for col in self.columns:
            col["y"] += col["speed"] * self.speed * dt

            # Random character flicker / mutation
            col["mutate_timer"] -= dt
            if col["mutate_timer"] <= 0:
                col["mutate_timer"] = random.uniform(0.08, 0.25)
                idx = random.randint(0, len(col["chars"]) - 1)
                col["chars"][idx] = random.choice(CHAR_SET)

            # Reset column when trail falls off bottom
            if col["y"] - (col["trail_len"] * row_height) > self.height:
                col["y"] = random.uniform(-100, 0)
                col["speed"] = random.uniform(80, 220)
                col["trail_len"] = random.randint(6, 16)
                col["chars"] = [random.choice(CHAR_SET) for _ in range(col["trail_len"])]

    def draw(self, surface: pygame.Surface):
        row_height = self.font_size + 2
        lead_color = (255, 255, 255)
        base_color = self.colors[0] if self.colors else (0, 255, 100)

        for col in self.columns:
            x = col["x"]
            y = col["y"]
            trail_len = col["trail_len"]

            for i, char in enumerate(col["chars"]):
                glyph_y = y - (i * row_height)
                if glyph_y < -row_height or glyph_y > self.height:
                    continue

                if i == 0:
                    # Bright leading glyph
                    color = lead_color
                else:
                    # Fading trail
                    alpha_factor = max(0.1, 1.0 - (i / trail_len))
                    color = (
                        int(base_color[0] * alpha_factor),
                        int(base_color[1] * alpha_factor),
                        int(base_color[2] * alpha_factor)
                    )

                glyph_surf = self._get_glyph(char, color)
                surface.blit(glyph_surf, (x, int(glyph_y)))
