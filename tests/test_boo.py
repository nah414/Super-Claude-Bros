import pygame
from game.entities.boo import Boo


def _player(x, facing):
    return type("P", (), {"facing": facing, "rect": pygame.Rect(x, 200, 30, 44)})()


def test_boo_freezes_when_faced():
    b = Boo(200, 200)
    b.chase(_player(0, 1))            # player to the left, facing right (toward the boo)
    assert b.frozen is True


def test_boo_chases_when_looked_away():
    b = Boo(200, 200)
    x0 = b.x
    b.chase(_player(0, -1))           # player to the left, facing away (left)
    assert b.frozen is False and b.x < x0      # drifted toward the player


def test_boo_is_stomp_proof():
    assert Boo.stomp_proof is True
