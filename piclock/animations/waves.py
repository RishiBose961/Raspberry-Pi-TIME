"""
Neon Sine Waves animation.
Flowing undulating neon harmonic waves across the display.
Lightweight and smooth on Raspberry Pi 3.
"""

import math
import pygame
from .base import BaseAnimation

class WaveAnimation(BaseAnimation):
    def __init__(self, width: int, height: int, theme: dict, speed: float = 1.0):
        super().__init__(width, height, theme, speed)
        self.time = 0.0
        self.step_px = 14  # Sampling step for high performance
        self.wave_surf = pygame.Surface((width, height), pygame.SRCALPHA)

    def resize(self, width: int, height: int):
        super().resize(width, height)
        self.wave_surf = pygame.Surface((width, height), pygame.SRCALPHA)

    def update(self, dt: float):
        self.time += dt * self.speed * 1.2

    def draw(self, surface: pygame.Surface):
        self.wave_surf.fill((0, 0, 0, 0))

        # Base parameters
        mid_y = self.height * 0.58
        colors = self.colors if self.colors else [(0, 240, 255), (255, 0, 128)]

        # Draw 3 harmonic ribbons
        ribbons = [
            {"freq": 0.005, "amp": self.height * 0.12, "phase_mult": 1.0, "color_idx": 0, "width": 3, "alpha": 180},
            {"freq": 0.008, "amp": self.height * 0.09, "phase_mult": -1.4, "color_idx": 1 % len(colors), "width": 2, "alpha": 140},
            {"freq": 0.003, "amp": self.height * 0.16, "phase_mult": 0.7, "color_idx": 2 % len(colors), "width": 4, "alpha": 110},
        ]

        for ribbon in ribbons:
            points = []
            c = colors[ribbon["color_idx"]]
            rgba = (*c[:3], ribbon["alpha"])
            freq = ribbon["freq"]
            amp = ribbon["amp"]
            phase = self.time * ribbon["phase_mult"]

            for x in range(0, self.width + self.step_px, self.step_px):
                # Harmonic wave formula
                y = mid_y + math.sin(x * freq + phase) * amp + math.cos(x * freq * 0.5 + phase * 0.8) * (amp * 0.4)
                points.append((x, int(y)))

            if len(points) > 1:
                pygame.draw.lines(self.wave_surf, rgba, False, points, ribbon["width"])

        surface.blit(self.wave_surf, (0, 0))
