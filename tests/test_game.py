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


def test_m_box_gives_mushroom_small_flower_when_big():
    g = Game(); g.new_game()
    mb = next(b for b in g.level.blocks if b.kind == "M" and not b.used)
    g.player.x = float(mb.rect.x); g.player.y = float(mb.rect.bottom); g.player.vy = 0.0
    g.player.power = "small"
    g.handle_boxes()
    assert len(g.mushrooms) == 1 and len(g.flowers) == 0

    g2 = Game(); g2.new_game()
    mb2 = next(b for b in g2.level.blocks if b.kind == "M" and not b.used)
    g2.player.x = float(mb2.rect.x); g2.player.y = float(mb2.rect.bottom); g2.player.vy = 0.0
    g2.player.power = "big"
    g2.handle_boxes()
    assert len(g2.flowers) == 1 and len(g2.mushrooms) == 0


def test_power_persists_across_levels_and_resets_on_death():
    g = Game(); g.new_game()
    g.player.become_fire()
    g.advance()
    assert g.carry_power == "fire" and g.player.power == "fire"
    g.lose_life()
    assert g.carry_power == "small"
