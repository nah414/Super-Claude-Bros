import pygame
from game import settings as S
from game.entities.boss import Boss


def test_set_tier_scales_and_themes():
    b = Boss(0, 0)
    base = b.hp
    b.set_tier(5)
    assert b.hp > base and b.title == "PHANTOM KOOPA" and b.color == S.BOSS_COLORS[4]


def test_boss_takes_three_fireballs():
    b = Boss(100, 100)
    assert b.hp == S.BOSS_HP
    assert b.hit() is False and b.hp == S.BOSS_HP - 1
    b.flash = 0
    assert b.hit() is False
    b.flash = 0
    assert b.hit() is True and not b.alive


def test_flash_blocks_rapid_hits():
    b = Boss(100, 100)
    b.hit()
    assert b.hit() is False and b.hp == S.BOSS_HP - 1   # second hit ignored during flash


def test_boss_shoots_on_cooldown():
    lvl = type("L", (), {"solids": []})()
    b = Boss(100, 100)
    fired = 0
    for _ in range(S.BOSS_SHOT_COOLDOWN * 2 + 4):
        b.update(lvl)
        if b.ready_to_shoot():
            fired += 1
    assert fired >= 2


def test_boss_reverses_at_wall():
    T = S.TILE
    lvl = type("L", (), {"solids": [pygame.Rect(0, 13 * T, 20 * T, T),
                                    pygame.Rect(9 * T, 0, T, 13 * T)]})()
    b = Boss(5 * T, 12 * T)
    b.direction = 1
    for _ in range(300):
        b.update(lvl)
        if b.direction == -1:
            break
    assert b.direction == -1
