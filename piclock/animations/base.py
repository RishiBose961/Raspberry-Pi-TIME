"""
Base animation class for PiClock visual effects.
"""

from abc import ABC, abstractmethod
import pygame

class BaseAnimation(ABC):
    def __init__(self, width: int, height: int, theme: dict, speed: float = 1.0):
        self.width = width
        self.height = height
        self.theme = theme
        self.speed = speed
        self.colors = theme.get("animation_colors", [(255, 255, 255)])

    @abstractmethod
    def update(self, dt: float):
        """Update animation state given delta time in seconds."""
        pass

    @abstractmethod
    def draw(self, surface: pygame.Surface):
        """Render animation to target surface."""
        pass

    def resize(self, width: int, height: int):
        """Handle screen resize."""
        self.width = width
        self.height = height

    def set_theme(self, theme: dict):
        """Update theme colors."""
        self.theme = theme
        self.colors = theme.get("animation_colors", [(255, 255, 255)])

    def set_speed(self, speed: float):
        """Adjust animation speed factor."""
        self.speed = max(0.1, min(5.0, speed))
