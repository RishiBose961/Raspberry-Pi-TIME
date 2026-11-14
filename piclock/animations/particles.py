"""
Ambient floating particles & glowing embers.
Features gentle sinusoidal drift and glowing halos.
"""

import math
import random
import pygame
from .base import BaseAnimation

class ParticleAnimation(BaseAnimation):
    def __init__(self, width: int, height: int, theme: dict, speed: float = 1.0, count: int = 38):
        super().__init__(width, height, theme, speed)
        self.count = count
        self.particles = []
        self._glow_surfaces = {}
        self._prebake_glow_surfaces()
        self._init_particles()

    def _prebake_glow_surfaces(self):
        """Pre-bake particle glow textures to eliminate allocation during runtime."""
        self._glow_surfaces.clear()
        colors = self.colors if self.colors else [(0, 240, 255), (255, 0, 128)]
        for rad in [2, 3, 4, 5, 6]:
            for color in colors:
                surf_size = rad * 4
                surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
                # Outer soft glow
                outer_color = (*color[:3], 45)
                pygame.draw.circle(surf, outer_color, (surf_size // 2, surf_size // 2), rad * 2)
                # Mid glow
                mid_color = (*color[:3], 110)
                pygame.draw.circle(surf, mid_color, (surf_size // 2, surf_size // 2), int(rad * 1.3))
                # Inner bright core
                core_color = (min(255, color[0] + 60), min(255, color[1] + 60), min(255, color[2] + 60), 220)
                pygame.draw.circle(surf, core_color, (surf_size // 2, surf_size // 2), max(1, rad - 1))
                self._glow_surfaces[(rad, color)] = surf

    def _init_particles(self):
        self.particles = []
        for _ in range(self.count):
            self.particles.append(self._create_particle(random_y=True))

    def _create_particle(self, random_y: bool = False):
        x = random.uniform(0, self.width)
        y = random.uniform(0, self.height) if random_y else self.height + random.uniform(5, 50)
        radius = random.choice([2, 3, 4, 5, 6])
        vx = random.uniform(-20, 20)
        vy = random.uniform(-45, -15)
        color = random.choice(self.colors if self.colors else [(0, 240, 255)])
        phase = random.uniform(0, math.pi * 2)
        life = random.uniform(0.3, 1.0) if random_y else 0.0
        max_life = random.uniform(8.0, 16.0)
        return {
            "x": x, "y": y, "vx": vx, "vy": vy,
            "radius": radius, "color": color, "phase": phase,
            "life": life, "max_life": max_life
        }

    def _get_glow_surf(self, radius: int, color: tuple) -> pygame.Surface:
        rad = max(2, min(6, int(radius)))
        key = (rad, color)
        if key not in self._glow_surfaces:
            surf_size = rad * 4
            surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*color[:3], 120), (surf_size // 2, surf_size // 2), rad)
            self._glow_surfaces[key] = surf
        return self._glow_surfaces[key]

    def resize(self, width: int, height: int):
        super().resize(width, height)
        self._init_particles()

    def set_theme(self, theme: dict):
        super().set_theme(theme)
        self._prebake_glow_surfaces()

    def update(self, dt: float):
        for p in self.particles:
            p["life"] += dt * self.speed
            p["phase"] += 1.5 * self.speed * dt
            # Sinusoidal horizontal drift
            drift = math.sin(p["phase"]) * 25.0
            p["x"] += (p["vx"] + drift) * dt * self.speed
            p["y"] += p["vy"] * dt * self.speed

            # Reset when dead or off-screen
            if p["y"] < -20 or p["x"] < -30 or p["x"] > self.width + 30 or p["life"] >= p["max_life"]:
                p.update(self._create_particle(random_y=False))

    def draw(self, surface: pygame.Surface):
        for p in self.particles:
            rad = int(p["radius"])
            glow_surf = self._get_glow_surf(rad, p["color"])
            offset = glow_surf.get_width() // 2
            surface.blit(glow_surf, (int(p["x"]) - offset, int(p["y"]) - offset))
