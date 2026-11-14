"""
Aurora Borealis (Northern Lights) animation.
Majestic undulating translucent celestial curtains flowing across the sky.
"""

import math
import pygame
from .base import BaseAnimation

class AuroraAnimation(BaseAnimation):
    def __init__(self, width: int, height: int, theme: dict, speed: float = 1.0):
        super().__init__(width, height, theme, speed)
        self.time = 0.0
        self.aurora_surf = pygame.Surface((width, height), pygame.SRCALPHA)

    def resize(self, width: int, height: int):
        super().resize(width, height)
        self.aurora_surf = pygame.Surface((width, height), pygame.SRCALPHA)

    def update(self, dt: float):
        self.time += dt * self.speed * 0.9

    def draw(self, surface: pygame.Surface):
        self.aurora_surf.fill((0, 0, 0, 0))

        # 3 Layers of aurora curtains
        step_x = 24
        colors = self.colors if len(self.colors) >= 3 else [
            (0, 255, 170), (0, 200, 255), (160, 32, 240)
        ]

        layers = [
            {"base_y": self.height * 0.35, "amp": self.height * 0.15, "freq": 0.004, "speed_m": 0.7, "color": colors[0], "height_curtain": int(self.height * 0.35), "alpha": 65},
            {"base_y": self.height * 0.42, "amp": self.height * 0.18, "freq": 0.006, "speed_m": -0.9, "color": colors[1 % len(colors)], "height_curtain": int(self.height * 0.30), "alpha": 50},
            {"base_y": self.height * 0.28, "amp": self.height * 0.12, "freq": 0.003, "speed_m": 1.2, "color": colors[2 % len(colors)], "height_curtain": int(self.height * 0.40), "alpha": 40},
        ]

        for lyr in layers:
            col = lyr["color"]
            alpha = lyr["alpha"]
            curtain_h = lyr["height_curtain"]

            for x in range(0, self.width + step_x, step_x):
                # Double harmonic undulation
                y = lyr["base_y"] + math.sin(x * lyr["freq"] + self.time * lyr["speed_m"]) * lyr["amp"] + \
                    math.cos(x * lyr["freq"] * 0.6 + self.time * 0.5) * (lyr["amp"] * 0.4)

                # Vertical ray gradient
                ray_rect = pygame.Rect(x, int(y - curtain_h), step_x + 2, curtain_h)
                # Soft vertical curtain segment
                curtain_rgba = (*col[:3], alpha)
                pygame.draw.rect(self.aurora_surf, curtain_rgba, ray_rect)

                # Bright glowing ribbon edge
                edge_rgba = (min(255, col[0] + 50), min(255, col[1] + 50), min(255, col[2] + 50), min(255, alpha * 2))
                pygame.draw.line(self.aurora_surf, edge_rgba, (x, int(y)), (x + step_x, int(y)), 2)

        surface.blit(self.aurora_surf, (0, 0))
