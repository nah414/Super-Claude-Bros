import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
from game.game import Game


def test_question_box_bumps_on_head_contact():
    """Regression: bumping a box must register on the contact frame, even though
    the collision has just zeroed the player's upward velocity (vy == 0)."""
    g = Game()
    g.new_game()
    qb = next(b for b in g.level.blocks if b.kind == "?")
    # the moment of contact: player snapped just under the block, vy arrested to 0
    g.player.x = float(qb.rect.x)
    g.player.y = float(qb.rect.bottom)
    g.player.vy = 0.0
    tokens0 = g.tokens
    g.handle_boxes()
    assert qb.used is True
    assert g.tokens == tokens0 + 1
