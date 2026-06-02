"""Regression guards for the bonus-pipe warps and boss-arena fire recovery.

- A warp must never drop the hero into the void (its destination must be solid ground).
- Each bonus pipe must lead to a coin room.
- Each castle/boss level must have enough power-up boxes to reach AND regain fire,
  otherwise the stomp-proof boss (3 fireballs) is unbeatable after a single hit.
"""
import pygame
from game import settings as S
from game.level import Level
from game.levelset import LEVELS

T = S.TILE

PIPE_LEVELS = ("level_1.txt", "level_5.txt", "level_9.txt", "level_13.txt",
               "level_17.txt", "level_21.txt", "level_25.txt", "level_29.txt")
BOSS_LEVELS = (4, 8, 12, 16, 20, 24, 28, 32)


def _solid_at(level, col, row):
    cx, cy = col * T + T // 2, row * T + T // 2
    return any(r.collidepoint(cx, cy) for r in level.solids)


def test_every_warp_destination_is_solid_ground():
    """try_warp puts the hero's feet at dy*TILE, so row dy (or just below) must be solid."""
    for name in LEVELS:
        lv = Level(S.resource_path("levels/" + name))
        for trig, (dx, dy) in lv.warps:
            landed = _solid_at(lv, dx, dy) or _solid_at(lv, dx, dy + 1)
            assert landed, f"{name}: warp -> ({dx},{dy}) is not on solid ground (void warp)"


def test_every_warp_destination_is_in_bounds():
    for name in LEVELS:
        lv = Level(S.resource_path("levels/" + name))
        cols = lv.width_px // T
        for trig, (dx, dy) in lv.warps:
            assert 0 <= dx < cols, f"{name}: warp dest col {dx} out of bounds"


def test_pipe_levels_have_a_bonus_coin_room():
    for name in PIPE_LEVELS:
        lv = Level(S.resource_path("levels/" + name))
        # the bonus room sits past the goal flag (play_width)
        room_coins = [c for c in lv.coins if c.rect.x >= lv.play_width]
        assert len(room_coins) >= 20, f"{name}: bonus room has only {len(room_coins)} coins"


def test_boss_levels_allow_fire_and_recovery():
    for n in BOSS_LEVELS:
        lv = Level(S.resource_path(f"levels/level_{n}.txt"))
        mboxes = [b for b in lv.blocks if b.kind == "M"]
        # 2 to reach fire (small->big->fire) + spares to recover after a hit
        assert len(mboxes) >= 4, f"level_{n}: only {len(mboxes)} M boxes (boss unbeatable after one hit)"
