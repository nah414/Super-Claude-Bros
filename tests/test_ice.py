import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))
from game import settings as S
from game.entities.player import Player


class _NoKeys:
    def __getitem__(self, k):
        return False                  # nothing held


def test_ice_keeps_momentum(monkeypatch):
    monkeypatch.setattr(pygame.key, "get_pressed", lambda: _NoKeys())
    land = type("L", (), {"solids": [], "area_type": "overworld"})()
    ice = type("L", (), {"solids": [], "area_type": "ice"})()
    a = Player(0, 100); a.vx = 5.0
    b = Player(0, 100); b.vx = 5.0
    for _ in range(8):
        a.update(land)
        b.update(ice)
    assert b.vx > a.vx + 2            # ice glides on; land brakes to near-stop
