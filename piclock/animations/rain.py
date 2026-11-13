"""
Cozy Rain & Snow animation for PiClock.
Lightweight diagonal weather streaks with gentle wind oscillation and splash ripples.
"""

import math
import random
import pygame
from .base import BaseAnimation

class RainAnimation(BaseAnimation):
    def __init__(self, width: int, height: int, theme: dict, speed: float = 1.0, count: int = 110):
        super().__init__(width, height, theme, speed)
        self.count = count
        self.drops = []
        self.ripples = []
        self.wind_time = 0.0
        self._init_drops()

    def _init_drops(self):
        self.drops = []
        self.ripples = []
        for _ in range(self.count):
            self.drops.append(self._create_drop(random_y=True))

    def _create_drop(self, random_y: bool = False):
        x = random.uniform(-100, self.width + 100)
        y = random.uniform(-50, self.height) if random_y else random.uniform(-60, -10)
        length = random.uniform(12, 28)
        speed_y = random.uniform(340, 680)
        thickness = random.choice([1, 1, 2])
        color = random.choice(self.colors)
        return {
            "x": x, "y": y, "len": length,
            "speed": speed_y, "thick": thickness,
            "color": color
        }

    def resize(self, width: int, height: int):
        super().resize(width, height)
        self._init_drops()

    def update(self, dt: float):
        self.wind_time += dt * 0.8
        wind = math.sin(self.wind_time) * 45.0  # gentle swaying wind

        for drop in self.drops:
            drop["y"] += drop["speed"] * self.speed * dt
            drop["x"] += wind * dt * self.speed

            # Hit the ground -> spawn subtle ripple
            if drop["y"] > self.height:
                if len(self.ripples) < 30 and random.random() < 0.25:
                    self.ripples.append({
                        "x": drop["x"],
                        "y": self.height - random.uniform(2, 25),
                        "radius": 2.0,
                        "max_radius": random.uniform(10, 24),
                        "alpha": 160,
                        "color": drop["color"]
                    })
                drop.update(self._create_drop(random_y=False))

        # Update ripples
        for rip in self.ripples[:]:
            rip["radius"] += 45.0 * dt * self.speed
            rip["alpha"] -= 280.0 * dt * self.speed
            if rip["alpha"] <= 0 or rip["radius"] >= rip["max_radius"]:
                self.ripples.remove(rip)

    def draw(self, surface: pygame.Surface):
        wind_angle = math.sin(self.wind_time) * 0.15
        dx = math.sin(wind_angle)

        for drop in self.drops:
            x1 = drop["x"]
            y1 = drop["y"]
            x2 = x1 + dx * drop["len"]
            y2 = y1 + drop["len"]

            color = drop["color"]
            alpha_color = (
                max(0, min(255, int(color[0] * 0.8))),
                max(0, min(255, int(color[1] * 0.8))),
                max(0, min(255, int(color[2] * 0.8)))
            )
            pygame.draw.line(surface, alpha_color, (int(x1), int(y1)), (int(x2), int(y2)), drop["thick"])

        # Draw ripples on screen bottom
        for rip in self.ripples:
            if rip["alpha"] > 5:
                rad_x = int(rip["radius"])
                rad_y = max(1, int(rip["radius"] * 0.35))  # Perspective oval
                c = rip["color"]
                rip_color = (
                    max(0, min(255, int(c[0] * (rip["alpha"] / 255.0)))),
                    max(0, min(255, int(c[1] * (rip["alpha"] / 255.0)))),
                    max(0, min(255, int(c[2] * (rip["alpha"] / 255.0))))
                )
                rect = pygame.Rect(int(rip["x"] - rad_x), int(rip["y"] - rad_y), rad_x * 2, rad_y * 2)
                pygame.draw.ellipse(surface, rip_color, rect, 1)
