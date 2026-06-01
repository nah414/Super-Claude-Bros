from game import settings as S
from game.entities.player import Player


def test_grow_makes_big():
    p = Player(0, 100)
    assert p.power == "small" and p.h == S.PLAYER_SMALL[1]
    p.grow()
    assert p.power == "big" and (p.w, p.h) == S.PLAYER_BIG


def test_big_hit_shrinks_then_invulnerable():
    p = Player(0, 100); p.grow()
    assert p.take_damage(1000) is False         # shrinks, no life lost
    assert p.power == "small" and p.invuln_until == 1000 + S.POWER_INVULN_MS
    assert p.take_damage(1100) is False          # still invulnerable -> ignored


def test_small_hit_costs_life_after_invuln():
    p = Player(0, 100)
    assert p.take_damage(5000) is True           # small + vulnerable -> life lost
