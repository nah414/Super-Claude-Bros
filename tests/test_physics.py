import types
import pygame
from game.physics import move_and_collide


def make_entity(x, y, w, h, vx=0.0, vy=0.0):
    return types.SimpleNamespace(x=float(x), y=float(y), w=w, h=h,
                                 vx=float(vx), vy=float(vy))


def test_lands_on_floor():
    e = make_entity(0, 0, 10, 10, vy=40)
    floor = pygame.Rect(0, 30, 40, 40)          # spans y 30..70
    contacts = move_and_collide(e, [floor])
    assert e.y == 20            # bottom snapped to floor top (30) - height (10)
    assert e.vy == 0
    assert contacts["bottom"] is True


def test_stops_at_wall_moving_right():
    e = make_entity(0, 0, 10, 10, vx=10)
    wall = pygame.Rect(15, 0, 10, 40)           # spans x 15..25
    contacts = move_and_collide(e, [wall])
    assert e.x == 5             # right snapped to wall left (15) - width (10)
    assert e.vx == 0
    assert contacts["right"] is True


def test_free_fall_keeps_subpixel_velocity():
    e = make_entity(0, 0, 10, 10, vx=2.5, vy=3.5)
    contacts = move_and_collide(e, [])          # nothing to hit
    assert e.x == 2.5 and e.y == 3.5
    assert not any(contacts.values())
