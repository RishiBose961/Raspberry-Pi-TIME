"""
Enchanted Fireflies & Glowing Bokeh animation.
Organic floating fireflies with smooth luminous pulsing and soft ambient glow.
"""

import math
import random
import pygame
from .base import BaseAnimation

class FirefliesAnimation(BaseAnimation):
    def __init__(self, width: int, height: int, theme: dict, speed: float = 1.0, count: int = 30):
        super().__init__(width, height, theme, speed)
        self.count = count
        self.fireflies = []
        self._glow_cache = {}
        self._init_fireflies()

    def _init_fireflies(self):
        self.fireflies = []
        self._glow_cache.clear()
        colors = self.colors if self.colors else [(0, 240, 255)]
        for _ in range(self.count):
            self.fireflies.append({
                "x": random.uniform(20, self.width - 20),
                "y": random.uniform(20, self.height - 20),
                "vx": random.uniform(-18, 18),
                "vy": random.uniform(-18, 18),
                "radius": random.choice([3, 4, 5]),
                "color": random.choice(colors),
                "pulse_speed": random.uniform(1.2, 3.2),
                "phase": random.uniform(0, math.pi * 2),
                "wander_timer": random.uniform(1.0, 3.0)
            })

    def _get_glow_surf(self, radius: int, color: tuple, pulse: float) -> pygame.Surface:
        radius = max(3, min(5, int(radius)))
        alpha_step = max(0, min(6, int(pulse * 6)))  # 7 discrete pulse states
        key = (radius, color, alpha_step)
        if key not in self._glow_cache:
            p_val = alpha_step / 6.0
            size = radius * 6
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            cx, cy = size // 2, size // 2

            # Outer aura
            alpha1 = max(0, min(255, int(50 * p_val)))
            pygame.draw.circle(surf, (*color[:3], alpha1), (cx, cy), radius * 3)

            # Mid halo
            alpha2 = max(0, min(255, int(130 * p_val)))
            pygame.draw.circle(surf, (*color[:3], alpha2), (cx, cy), int(radius * 1.6))

            # Inner bright spark
            alpha3 = max(0, min(255, int(240 * p_val)))
            core_c = (min(255, color[0] + 80), min(255, color[1] + 80), min(255, color[2] + 80))
            pygame.draw.circle(surf, (*core_c, alpha3), (cx, cy), max(1, radius - 1))

            if len(self._glow_cache) > 80:
                self._glow_cache.clear()
            self._glow_cache[key] = surf
        return self._glow_cache[key]

    def resize(self, width: int, height: int):
        super().resize(width, height)
        self._init_fireflies()

    def set_theme(self, theme: dict):
        super().set_theme(theme)
        self._glow_cache.clear()

    def update(self, dt: float):
        for f in self.fireflies:
            f["phase"] += f["pulse_speed"] * self.speed * dt

            # Organic wandering steering
            f["wander_timer"] -= dt * self.speed
            if f["wander_timer"] <= 0:
                f["wander_timer"] = random.uniform(1.5, 4.0)
                angle = random.uniform(0, math.pi * 2)
                f["vx"] = math.cos(angle) * random.uniform(12, 28)
                f["vy"] = math.sin(angle) * random.uniform(12, 28)

            f["x"] += f["vx"] * dt * self.speed
            f["y"] += f["vy"] * dt * self.speed

            # Screen boundary wrap with soft margin
            if f["x"] < -30: f["x"] = self.width + 20
            elif f["x"] > self.width + 30: f["x"] = -20
            if f["y"] < -30: f["y"] = self.height + 20
            elif f["y"] > self.height + 30: f["y"] = -20

    def draw(self, surface: pygame.Surface):
        for f in self.fireflies:
            # Pulsing luminous factor between 0.15 and 1.0
            pulse = (math.sin(f["phase"]) + 1.0) / 2.0
            pulse = max(0.12, pulse * pulse)  # Quadratic ease for organic glow

            glow_surf = self._get_glow_surf(int(f["radius"]), f["color"], pulse)
            offset = glow_surf.get_width() // 2
            surface.blit(glow_surf, (int(f["x"]) - offset, int(f["y"]) - offset))
