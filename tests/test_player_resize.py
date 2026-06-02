"""Regression tests for the World-8 'grow against a wall -> frozen' bug.

A power-up resize enlarges the hitbox (grow: +8px wide to the right, +18px tall
upward). If a wall/ceiling occupies that newly-claimed space, the hero ends up
embedded in a solid. The velocity-sign collision resolver then snaps the hero to
the solid's FAR side on the next move (teleport-through) and wedges them in an
enclosed pocket -> 'frozen, cannot move in any direction'.

Fix: Player.unstick(solids) ejects the hitbox from any overlapped solid right
after a resize, so every frame starts from a valid (non-overlapping) position.
"""
import pygame
from game import settings as S
from game.entities.player import Player

T = S.TILE


def _solid(col, row, w=1, h=1):
    return pygame.Rect(col * T, row * T, w * T, h * T)


class _Keys:
    def __init__(self):
        self.d = {}

    def __getitem__(self, k):
        return self.d.get(k, False)

    def set(self, k, v):
        self.d[k] = v


def test_grow_against_wall_extracts_not_embeds():
    """grow() with solids must leave the hero clear of every solid (on the near side)."""
    wall = _solid(5, 7, 1, 3)                        # x 200..240, a 3-tall wall
    floor = [_solid(c, 10) for c in range(12)]
    solids = [wall] + floor
    # small hero flush against the wall's left face (right edge == wall.left == 200)
    p = Player(5 * T - S.PLAYER_SMALL[0], 10 * T - S.PLAYER_SMALL[1])
    p.grow(solids)
    assert p.power == "big"
    assert not any(p.rect.colliderect(s) for s in solids), "hero left embedded in a solid after grow"
    assert p.rect.right <= wall.left                 # extracted to the NEAR (left) side, not through


def test_grow_under_ceiling_pushes_down_clear():
    """Growing taller with a low ceiling must lower the hero so the head clears it."""
    ceil = _solid(5, 5, 1, 1)                         # ceiling tile at y 200..240
    floor = [_solid(c, 10) for c in range(12)]
    solids = [ceil] + floor
    # small hero whose head, once grown (+18 up), would poke into that ceiling
    p = Player(5 * T + 5, 6 * T)                      # below the ceiling tile
    p.grow(solids)
    assert not any(p.rect.colliderect(s) for s in solids), "head left embedded in ceiling after grow"


def test_grow_then_press_away_never_teleports_through_wall():
    """The actual freeze: grow flush to a wall, press AWAY -> must stay on the near side."""
    wall = _solid(5, 7, 1, 3)
    floor = [_solid(c, 10) for c in range(12)]
    solids = [wall] + floor
    lvl = type("L", (), {"solids": solids, "area_type": "keep", "enemies": []})()
    keys = _Keys()
    pygame.key.get_pressed = lambda: keys

    p = Player(5 * T - S.PLAYER_SMALL[0], 10 * T - S.PLAYER_SMALL[1])
    for _ in range(3):
        p.update(lvl)
    p.grow(lvl.solids)
    keys.set(pygame.K_LEFT, True)                     # press AWAY from the wall
    xs = []
    for _ in range(20):
        p.update(lvl)
        xs.append(p.x)
    assert max(xs) < wall.right, f"teleported through the wall to far side: xs={xs}"
    assert p.rect.right <= wall.left + 1              # ended on the near side, free to move


def test_grow_with_no_solids_is_backward_compatible():
    """grow()/become_fire() must still work with no argument (existing call sites)."""
    p = Player(0, 100)
    p.grow()
    assert (p.w, p.h) == S.PLAYER_BIG
    q = Player(0, 100)
    q.become_fire()
    assert q.power == "fire"
