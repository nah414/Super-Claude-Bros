from game import settings as S
from game.entities.bullet import BulletBill
from game.entities.cannon import Cannon


def test_bullet_flies_straight_no_gravity():
    lvl = type("L", (), {"solids": [], "width_px": 2000})()
    b = BulletBill(100, 100, 1)
    y0 = b.y
    for _ in range(5):
        b.update(lvl)
    assert b.x > 100 and b.y == y0          # straight, no gravity


def test_bullet_despawns_off_level():
    lvl = type("L", (), {"solids": [], "width_px": 300})()
    b = BulletBill(280, 100, 1)
    for _ in range(40):
        b.update(lvl)
        if not b.alive:
            break
    assert not b.alive                       # flew off the right edge


def test_bullet_despawns_after_life():
    lvl = type("L", (), {"solids": [], "width_px": 100000})()
    b = BulletBill(0, 100, 1)
    for _ in range(S.BULLET_LIFE + 1):
        b.update(lvl)
    assert not b.alive


def test_cannon_fires_toward_in_range_player_on_cooldown():
    c = Cannon(500, 300)
    cx = c.rect.centerx
    assert c.tick(player_cx=cx) is None                  # still cooling down
    c.timer = 0
    d = c.tick(player_cx=cx + S.BULLET_MIN_DIST + 50)     # in range, to the right
    assert d == 1 and c.timer == S.BULLET_COOLDOWN        # fired right + reset


def test_cannon_holds_fire_when_too_close_or_far():
    c = Cannon(500, 300)
    cx = c.rect.centerx
    c.timer = 0
    assert c.tick(player_cx=cx + 5) is None                       # too close
    c.timer = 0
    assert c.tick(player_cx=cx + S.BULLET_MAX_DIST + 10) is None   # too far
