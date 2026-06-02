import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
from game import settings as S
from game.game import Game
from game.entities.lava_bubble import LavaBubble


def test_lava_rises_then_catches_hero():
    g = Game(); g.new_game(); g.state = "PLAYING"
    g.lava_rising = True
    g.lava_rise_y = float(S.HEIGHT)
    g.lava_bubbles = []
    g.bubble_timer = 999
    y0 = g.lava_rise_y
    g.update()
    assert g.lava_rise_y < y0                     # the sea climbed
    lives = g.lives
    g.lava_rising = True                          # (respawn may have cleared it on level_1)
    g.lava_rise_y = float(g.player.rect.bottom - 1)
    g.update()
    assert g.lives == lives - 1                    # feet below the surface -> caught


def test_lava_bubble_arcs_and_despawns():
    lvl = type("L", (), {"solids": []})()
    b = LavaBubble(100, 300)
    rose = False
    for _ in range(90):
        b.update(lvl)
        if b.y < 280:
            rose = True
        if not b.alive:
            break
    assert rose and not b.alive
