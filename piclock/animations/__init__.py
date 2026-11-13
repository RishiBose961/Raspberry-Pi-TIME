"""
Animations registry and factory for PiClock.
"""

from typing import Dict, Type
from .base import BaseAnimation
from .starfield import StarfieldAnimation
from .matrix import MatrixAnimation
from .particles import ParticleAnimation
from .waves import WaveAnimation
from .minimalist import MinimalistAnimation

ANIMATION_MAP: Dict[str, Type[BaseAnimation]] = {
    "starfield": StarfieldAnimation,
    "matrix": MatrixAnimation,
    "particles": ParticleAnimation,
    "waves": WaveAnimation,
    "minimalist": MinimalistAnimation,
}

ANIMATION_NAMES = list(ANIMATION_MAP.keys())

def create_animation(name: str, width: int, height: int, theme: dict, speed: float = 1.0) -> BaseAnimation:
    """Create an animation instance by name with fallback to starfield."""
    anim_cls = ANIMATION_MAP.get(name, StarfieldAnimation)
    return anim_cls(width, height, theme, speed)

def get_next_animation(current_name: str) -> str:
    """Cycle to the next animation name."""
    try:
        idx = ANIMATION_NAMES.index(current_name)
        return ANIMATION_NAMES[(idx + 1) % len(ANIMATION_NAMES)]
    except ValueError:
        return ANIMATION_NAMES[0]
