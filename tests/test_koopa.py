import pygame
from game import settings as S
from game.entities.koopa import Koopa


def test_stomp_to_shell_kick_to_slide_restomp_to_shell():
    k = Koopa(100, 100)
    assert k.state == "walk"
    assert k.player_hit(True, 0) == "stomp" and k.state == "shell"
    # kicked by a player to the LEFT of the shell -> slides right (direction 1)
    assert k.player_hit(False, k.rect.centerx - 50) == "kick"
    assert k.state == "slide" and k.direction == 1
    assert k.player_hit(True, 0) == "stomp_stop" and k.state == "shell"


def test_idle_shell_top_touch_bounces_without_kicking():
    k = Koopa(100, 100)
    k.player_hit(True, 0)                       # -> shell
    assert k.player_hit(True, 0) == "bounce" and k.state == "shell"


def test_walk_turns_at_ledge():
    T = S.TILE
    lvl = type("L", (), {"solids": [pygame.Rect(0, 13 * T, 5 * T, T)]})()
    k = Koopa(3 * T, 12 * T)
    k.direction = 1
    for _ in range(200):
        k.update(lvl)
    assert k.rect.bottom <= 13 * T + 8         # stayed on the platform, did not fall


def test_held_koopa_skips_update():
    lvl = type("L", (), {"solids": []})()
    k = Koopa(100, 100)
    k.held = True
    y0 = k.y
    for _ in range(10):
        k.update(lvl)
    assert k.y == y0            # no gravity/motion while held


def test_sliding_shell_reverses_on_wall():
    T = S.TILE
    lvl = type("L", (), {"solids": [pygame.Rect(0, 13 * T, 20 * T, T),
                                    pygame.Rect(8 * T, 0, T, 14 * T)]})()
    k = Koopa(5 * T, 12 * T)
    k.state = "slide"
    k.direction = 1
    k.kick_cooldown = 0
    for _ in range(150):
        k.update(lvl)
        if k.direction == -1:
            break
    assert k.direction == -1
