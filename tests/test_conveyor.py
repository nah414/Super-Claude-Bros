import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
from game import settings as S
from game.game import Game
from game.level import Level


def test_belt_dir_under_feet():
    fake = type("L", (), {"conveyors": [(pygame.Rect(40, 120, 40, 40), 1)]})()
    on = pygame.Rect(45, 76, 30, 44)        # feet at (60, 122) — inside the belt
    off = pygame.Rect(200, 76, 30, 44)
    assert Level.belt_dir(fake, on) == 1
    assert Level.belt_dir(fake, off) == 0


def test_belt_carries_grounded_hero():
    g = Game(); g.new_game(); g.state = "PLAYING"
    for _ in range(3):
        g.update()                       # settle flush on the ground
    g.level.conveyors = [(pygame.Rect(int(g.player.x) - 10, g.player.rect.bottom, 80, 40), 1)]
    x0 = g.player.x
    g.apply_conveyor()
    assert g.player.x == x0 + S.CONVEYOR_SPEED


def test_belt_no_carry_when_airborne():
    g = Game(); g.new_game(); g.state = "PLAYING"
    g.level.conveyors = [(pygame.Rect(int(g.player.x) - 10, g.player.rect.bottom, 80, 40), 1)]
    g.player.on_ground = False
    x0 = g.player.x
    g.apply_conveyor()
    assert g.player.x == x0                  # belts only carry when grounded
