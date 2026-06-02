import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))
from game import settings as S
from game.entities.player import Player


def _water():
    return type("L", (), {"solids": [], "area_type": "water"})()


def _dry():
    return type("L", (), {"solids": [], "area_type": "overworld"})()


def test_swim_stroke_pushes_up():
    p = Player(0, 100)
    p.swim_stroke()
    assert p.vy == S.SWIM_STROKE          # upward impulse


def test_water_uses_slow_gravity_capped():
    p = Player(0, 100)
    p.update(_water())
    assert p.vy == min(S.SWIM_GRAVITY, S.SWIM_MAX_SINK)    # gentle sink, not full gravity
    for _ in range(120):
        p.update(_water())
    assert p.vy <= S.SWIM_MAX_SINK         # terminal sink stays slow


def test_dry_level_uses_normal_gravity():
    p = Player(0, 100)
    p.update(_dry())
    assert p.vy == min(S.GRAVITY, S.MAX_FALL)
