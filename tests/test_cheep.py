import pygame
from game import settings as S
from game.entities.cheep import CheepCheep


def test_cheep_drifts_and_reverses_at_range():
    lvl = type("L", (), {"solids": []})()
    c = CheepCheep(100, 100)
    d0 = c.direction
    for _ in range(400):
        c.update(lvl)
        if c.direction != d0:
            break
    assert c.direction != d0


def test_cheep_bobs_and_ignores_gravity():
    lvl = type("L", (), {"solids": [pygame.Rect(0, 200, 1000, 40)]})()
    c = CheepCheep(100, 100)
    ys = set()
    for _ in range(60):
        c.update(lvl)
        ys.add(round(c.y))
    assert len(ys) > 1 and c.y < 200          # bobs, never sinks to the floor
