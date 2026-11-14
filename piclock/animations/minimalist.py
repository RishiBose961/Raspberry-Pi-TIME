"""
Minimalist Geometric Pulse animation.
Ultra-low CPU usage (<1% on Raspberry Pi 3).
Features smooth ambient breathing aura and clean geometric accents.
"""

import math
import pygame
from .base import BaseAnimation

class MinimalistAnimation(BaseAnimation):
    def __init__(self, width: int, height: int, theme: dict, speed: float = 1.0):
        super().__init__(width, height, theme, speed)
        self.time = 0.0

    def resize(self, width: int, height: int):
        super().resize(width, height)

    def update(self, dt: float):
        self.time += dt * self.speed * 1.5

    def draw(self, surface: pygame.Surface):
        cx = self.width // 2
        cy = self.height // 2

        # Gentle breathing factor between 0.0 and 1.0
        breath = (math.sin(self.time) + 1.0) / 2.0

        accent = self.theme.get("accent", (0, 240, 255))
        # Subtle alpha shading via pre-multiplied RGB color
        factor = 0.4 + breath * 0.4
        c_ring = (int(accent[0] * factor), int(accent[1] * factor), int(accent[2] * factor))
        c_ring2 = (int(accent[0] * factor * 0.5), int(accent[1] * factor * 0.5), int(accent[2] * factor * 0.5))
        radius = int(min(self.width, self.height) * 0.38 + breath * 15)

        # Concentric breathing rings drawn directly (zero-copy, zero alpha surface)
        pygame.draw.circle(surface, c_ring, (cx, cy), radius, 2)
        pygame.draw.circle(surface, c_ring2, (cx, cy), radius + 25, 1)

        # Subtle geometric horizontal hairline
        line_y = int(self.height * 0.72)
        line_w = int(self.width * (0.4 + breath * 0.1))
        x1 = cx - line_w // 2
        x2 = cx + line_w // 2
        pygame.draw.line(surface, c_ring, (x1, line_y), (x2, line_y), 2)
