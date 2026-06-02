import pygame
from game import settings as S
from game.entities.frostbite import Frostbite


def test_frostbite_is_stomp_proof():
    assert Frostbite.stomp_proof is True


def test_frostbite_turns_at_ledge():
    T = S.TILE
    lvl = type("L", (), {"solids": [pygame.Rect(0, 13 * T, 5 * T, T)]})()
    f = Frostbite(3 * T, 12 * T)
    f.direction = 1
    for _ in range(200):
        f.update(lvl)
    assert f.rect.bottom <= 13 * T + 8          # stayed on the platform


def test_frostbite_reverses_at_wall():
    T = S.TILE
    lvl = type("L", (), {"solids": [pygame.Rect(0, 13 * T, 20 * T, T),
                                    pygame.Rect(8 * T, 0, T, 13 * T)]})()
    f = Frostbite(5 * T, 12 * T)
    f.direction = 1
    for _ in range(300):
        f.update(lvl)
        if f.direction == -1:
            break
    assert f.direction == -1
