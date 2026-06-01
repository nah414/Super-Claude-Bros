import pygame
from game import settings as S
from game.entities.player import Player


def test_double_tap_gives_one_air_jump():
    p = Player(0, 0); p.on_ground = True
    p.press_jump(1000)                      # ground jump
    assert p.vy == S.JUMP_VELOCITY and p.air_jumped is False
    p.on_ground = False
    p.press_jump(1200)                      # 200ms later -> double jump
    assert p.vy == S.DOUBLE_JUMP_VELOCITY and p.air_jumped is True
    p.press_jump(1300)                      # already used -> ignored
    assert p.vy == S.DOUBLE_JUMP_VELOCITY


def test_late_tap_does_not_double_jump():
    p = Player(0, 0); p.on_ground = True
    p.press_jump(2000)
    p.on_ground = False
    p.press_jump(2500)                      # 500ms > window -> no double jump
    assert p.vy == S.JUMP_VELOCITY
