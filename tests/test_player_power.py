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


def test_become_fire_keeps_big_size():
    p = Player(0, 100); p.grow(); size = (p.w, p.h)
    p.become_fire()
    assert p.power == "fire" and (p.w, p.h) == size


def test_tier_drop_damage():
    p = Player(0, 100); p.become_fire()
    assert p.power == "fire"
    assert p.take_damage(1000) is False and p.power == "big"
    assert p.take_damage(5000) is False and p.power == "small"
    assert p.take_damage(9000) is True


def test_can_shoot_respects_cooldown():
    p = Player(0, 100)
    assert p.can_shoot(1000) is False
    p.become_fire()
    assert p.can_shoot(1000) is True
    p.record_fire(1000)
    assert p.can_shoot(1100) is False
    assert p.can_shoot(1400) is True
