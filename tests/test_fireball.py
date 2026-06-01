import pygame
from game import settings as S
from game.entities.fireball import Fireball


def test_fireball_bounces_off_ground():
    T = S.TILE
    lvl = type("L", (), {"solids": [pygame.Rect(0, 5 * T, 20 * T, T)]})()
    fb = Fireball(40, 5 * T - 20, 1)
    bounced = False
    for _ in range(60):
        fb.update(lvl)
        if fb.vy < 0:
            bounced = True
            break
    assert bounced and fb.x > 40


def test_fireball_despawns_on_wall():
    T = S.TILE
    lvl = type("L", (), {"solids": [pygame.Rect(5 * T, 0, T, 20 * T)]})()
    fb = Fireball(5 * T - 10, T, 1)
    for _ in range(30):
        fb.update(lvl)
        if not fb.alive:
            break
    assert fb.alive is False


def test_fireball_despawns_after_life():
    lvl = type("L", (), {"solids": []})()
    fb = Fireball(0, 0, 1)
    for _ in range(S.FIREBALL_LIFE + 2):
        fb.update(lvl)
    assert fb.alive is False
