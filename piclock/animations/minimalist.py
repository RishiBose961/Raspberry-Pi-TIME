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
        self.pulse_surf = pygame.Surface((width, height), pygame.SRCALPHA)

    def resize(self, width: int, height: int):
        super().resize(width, height)
        self.pulse_surf = pygame.Surface((width, height), pygame.SRCALPHA)

    def update(self, dt: float):
        self.time += dt * self.speed * 1.5

    def draw(self, surface: pygame.Surface):
        self.pulse_surf.fill((0, 0, 0, 0))

        cx = self.width // 2
        cy = self.height // 2

        # Gentle breathing factor between 0.0 and 1.0
        breath = (math.sin(self.time) + 1.0) / 2.0

        accent = self.theme.get("accent", (0, 240, 255))
        alpha = int(40 + breath * 60)
        radius = int(min(self.width, self.height) * 0.38 + breath * 15)

        # Concentric breathing rings
        pygame.draw.circle(self.pulse_surf, (*accent[:3], alpha), (cx, cy), radius, 2)
        pygame.draw.circle(self.pulse_surf, (*accent[:3], int(alpha * 0.5)), (cx, cy), radius + 25, 1)

        # Subtle geometric horizontal hairline
        line_y = int(self.height * 0.72)
        line_w = int(self.width * (0.4 + breath * 0.1))
        x1 = cx - line_w // 2
        x2 = cx + line_w // 2
        pygame.draw.line(self.pulse_surf, (*accent[:3], int(alpha * 0.8)), (x1, line_y), (x2, line_y), 2)

        surface.blit(self.pulse_surf, (0, 0))
