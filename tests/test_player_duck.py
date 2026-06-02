"""Ducking on S/Down: crouch shrinks the hitbox (feet planted), suppresses walking,
and you can only stand back up when there's headroom."""
import pygame
from game import settings as S
from game.entities.player import Player

T = S.TILE


class Keys:
    def __init__(self):
        self.d = {}

    def __getitem__(self, k):
        return self.d.get(k, False)

    def set(self, k, v):
        self.d[k] = v


def _level(solids, area="overworld"):
    return type("L", (), {"solids": solids, "area_type": area, "enemies": []})()


def _floor(n=16):
    return [pygame.Rect(c * T, 10 * T, T, T) for c in range(n)]


def _settle(p, lvl, keys, frames=4):
    pygame.key.get_pressed = lambda: keys
    for _ in range(frames):
        p.update(lvl)


def test_duck_shrinks_and_plants_feet():
    keys = Keys()
    lvl = _level(_floor())
    p = Player(3 * T, 10 * T - S.PLAYER_SMALL[1])
    _settle(p, lvl, keys)
    assert p.on_ground
    bottom_before = p.rect.bottom
    keys.set(pygame.K_s, True)
    p.update(lvl)
    assert p.ducking
    assert p.h == S.PLAYER_SMALL_DUCK[1]            # crouched height
    assert p.rect.bottom == bottom_before          # feet stayed put


def test_no_walking_while_ducking():
    keys = Keys()
    lvl = _level(_floor())
    p = Player(3 * T, 10 * T - S.PLAYER_SMALL[1])
    _settle(p, lvl, keys)
    keys.set(pygame.K_s, True)
    keys.set(pygame.K_RIGHT, True)                 # try to walk while crouched
    for _ in range(20):
        p.update(lvl)
    assert p.ducking
    assert abs(p.vx) < 0.6                          # never built up walking speed


def test_release_duck_stands_up_when_clear():
    keys = Keys()
    lvl = _level(_floor())
    p = Player(3 * T, 10 * T - S.PLAYER_SMALL[1])
    _settle(p, lvl, keys)
    keys.set(pygame.K_DOWN, True)
    p.update(lvl)
    assert p.ducking
    keys.set(pygame.K_DOWN, False)
    p.update(lvl)
    assert not p.ducking
    assert p.h == S.PLAYER_SMALL[1]                 # back to full height


def test_cannot_stand_under_low_ceiling():
    keys = Keys()
    floor = _floor()
    lvl = _level(floor)
    p = Player(4 * T, 10 * T - S.PLAYER_SMALL[1])
    _settle(p, lvl, keys)
    keys.set(pygame.K_DOWN, True)
    p.update(lvl)
    assert p.ducking                               # crouched: top at y=370
    # drop a ceiling whose bottom (364) clears the crouch (370) but blocks standing (356)
    ceiling = pygame.Rect(3 * T, 0, 3 * T, 364)
    lvl.solids = floor + [ceiling]
    keys.set(pygame.K_DOWN, False)
    p.update(lvl)
    assert p.ducking                               # no headroom -> stays crouched
    assert p.h == S.PLAYER_SMALL_DUCK[1]
    # remove the ceiling -> now it can stand
    lvl.solids = floor
    p.update(lvl)
    assert not p.ducking
    assert p.h == S.PLAYER_SMALL[1]


def test_big_player_ducks_to_one_tile():
    keys = Keys()
    lvl = _level(_floor())
    p = Player(3 * T, 10 * T - S.PLAYER_SMALL[1])
    p.grow(lvl.solids)                              # become big
    _settle(p, lvl, keys)
    keys.set(pygame.K_DOWN, True)
    p.update(lvl)
    assert p.ducking
    assert p.h == S.PLAYER_BIG_DUCK[1]              # tucks down to ~1 tile
