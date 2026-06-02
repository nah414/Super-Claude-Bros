import pygame
from game import settings as S
from game.entities.cog import Cog


def test_cog_is_not_stomp_proof():
    assert getattr(Cog, "stomp_proof", False) is False     # stompable


def test_cog_turns_at_ledge():
    T = S.TILE
    lvl = type("L", (), {"solids": [pygame.Rect(0, 13 * T, 5 * T, T)]})()
    c = Cog(3 * T, 12 * T)
    c.direction = 1
    for _ in range(200):
        c.update(lvl)
    assert c.rect.bottom <= 13 * T + 8


def test_cog_reverses_at_wall():
    T = S.TILE
    lvl = type("L", (), {"solids": [pygame.Rect(0, 13 * T, 20 * T, T),
                                    pygame.Rect(8 * T, 0, T, 13 * T)]})()
    c = Cog(5 * T, 12 * T)
    c.direction = 1
    for _ in range(300):
        c.update(lvl)
        if c.direction == -1:
            break
    assert c.direction == -1
