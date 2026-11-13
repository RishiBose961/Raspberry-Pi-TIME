"""
Retro Synthwave 3D Perspective Grid animation.
Outrun-style infinite neon ground grid scrolling towards the viewer.
"""

import math
import pygame
from .base import BaseAnimation

class RetroGridAnimation(BaseAnimation):
    def __init__(self, width: int, height: int, theme: dict, speed: float = 1.0):
        super().__init__(width, height, theme, speed)
        self.offset = 0.0

    def update(self, dt: float):
        self.offset = (self.offset + dt * self.speed * 1.5) % 1.0

    def draw(self, surface: pygame.Surface):
        horizon_y = int(self.height * 0.52)
        ground_h = self.height - horizon_y
        cx = self.width // 2

        color = self.colors[0] if self.colors else (0, 240, 255)
        accent = self.theme.get("accent", (255, 0, 128))

        # 1. Horizon glow line
        pygame.draw.line(surface, accent, (0, horizon_y), (self.width, horizon_y), 2)

        # 2. Perspective vertical radiating lines
        num_v_lines = 16
        for i in range(-num_v_lines, num_v_lines + 1):
            bottom_x = cx + i * (self.width / (num_v_lines * 0.9))
            alpha_factor = max(0.2, 1.0 - abs(i) / (num_v_lines + 2))
            c = (int(color[0] * alpha_factor), int(color[1] * alpha_factor), int(color[2] * alpha_factor))
            pygame.draw.line(surface, c, (cx, horizon_y), (int(bottom_x), self.height), 1)

        # 3. Horizontal scrolling perspective lines
        # Using exponential distribution for 3D depth perception
        num_h_lines = 14
        for i in range(num_h_lines):
            # Normalised progress [0, 1] with scrolling offset
            progress = ((i + self.offset) / num_h_lines)
            # Power curve gives 3D perspective spacing
            depth_factor = math.pow(progress, 2.8)
            line_y = int(horizon_y + depth_factor * ground_h)

            if line_y > horizon_y and line_y <= self.height:
                alpha = max(0.1, min(1.0, depth_factor * 1.2))
                c = (int(color[0] * alpha), int(color[1] * alpha), int(color[2] * alpha))
                thickness = 2 if depth_factor > 0.6 else 1
                pygame.draw.line(surface, c, (0, line_y), (self.width, line_y), thickness)
