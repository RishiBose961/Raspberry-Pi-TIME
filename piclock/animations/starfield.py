"""
3D Starfield warp animation with depth perspective and subtle speed trails.
Ultra-lightweight on Raspberry Pi 3.
"""

import random
import pygame
from .base import BaseAnimation

class StarfieldAnimation(BaseAnimation):
    def __init__(self, width: int, height: int, theme: dict, speed: float = 1.0, count: int = 90):
        super().__init__(width, height, theme, speed)
        self.count = count
        self.max_depth = 1000.0
        self.stars = []
        self._init_stars()

    def _init_stars(self):
        self.stars = []
        cx = self.width / 2
        cy = self.height / 2
        for _ in range(self.count):
            x = random.uniform(-self.width, self.width)
            y = random.uniform(-self.height, self.height)
            z = random.uniform(10, self.max_depth)
            color = random.choice(self.colors)
            self.stars.append([x, y, z, z, color])  # [x, y, z, prev_z, color]

    def resize(self, width: int, height: int):
        super().resize(width, height)
        self._init_stars()

    def update(self, dt: float):
        cx = self.width / 2
        cy = self.height / 2
        travel_speed = 350.0 * self.speed * dt

        for star in self.stars:
            star[3] = star[2]  # Save prev_z
            star[2] -= travel_speed  # Move closer

            # Reset star if it passes the camera or goes off bounds
            if star[2] <= 1:
                star[0] = random.uniform(-self.width, self.width)
                star[1] = random.uniform(-self.height, self.height)
                star[2] = self.max_depth
                star[3] = self.max_depth
                star[4] = random.choice(self.colors)
            else:
                # Check if projected coordinates leave screen bounds
                fov = self.width * 0.7
                sx = int(star[0] / star[2] * fov + cx)
                sy = int(star[1] / star[2] * fov + cy)
                if sx < -50 or sx > self.width + 50 or sy < -50 or sy > self.height + 50:
                    star[0] = random.uniform(-self.width, self.width)
                    star[1] = random.uniform(-self.height, self.height)
                    star[2] = self.max_depth
                    star[3] = self.max_depth
                    star[4] = random.choice(self.colors)

    def draw(self, surface: pygame.Surface):
        cx = self.width / 2
        cy = self.height / 2
        fov = self.width * 0.7

        for x, y, z, pz, color in self.stars:
            if z <= 1:
                continue

            # Project current position
            sx = star_x = x / z * fov + cx
            sy = star_y = y / z * fov + cy

            # Project previous position for trail
            px = x / pz * fov + cx
            py = y / pz * fov + cy

            # Brightness scales with proximity
            factor = max(0.0, min(1.0, 1.0 - (z / self.max_depth)))
            star_color = (
                max(0, min(255, int(color[0] * factor))),
                max(0, min(255, int(color[1] * factor))),
                max(0, min(255, int(color[2] * factor)))
            )

            # Draw trail or star dot
            radius = max(1, int(3.5 * factor))
            if factor > 0.4:
                pygame.draw.line(surface, star_color, (int(px), int(py)), (int(sx), int(sy)), max(1, radius - 1))
            pygame.draw.circle(surface, star_color, (int(sx), int(sy)), radius)
