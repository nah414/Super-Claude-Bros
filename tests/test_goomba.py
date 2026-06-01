import pygame
from game import settings as S
from game.entities.goomba import Goomba


def test_goomba_turns_at_ledge_instead_of_falling():
    T = S.TILE
    # ground only under cols 0..4 (x in [0, 5T)); pit beyond
    solids = [pygame.Rect(0, 13 * T, 5 * T, T)]
    lvl = type("L", (), {"solids": solids})()
    g = Goomba(3 * T, 12 * T)
    g.direction = 1                      # head toward the right ledge at x = 5T
    for _ in range(180):
        g.update(lvl)
    assert g.rect.bottom <= 13 * T + 8, f"goomba fell off the ledge: bottom={g.rect.bottom}"
    assert 0 <= g.x <= 5 * T, f"goomba left the platform: x={g.x}"
