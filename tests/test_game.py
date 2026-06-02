import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
from game import settings as S
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


def test_sliding_shell_kills_another_enemy():
    from game.entities.koopa import Koopa
    from game.entities.goomba import Goomba
    g = Game(); g.new_game()
    g.level.enemies.clear()
    k = Koopa(200, 100); k.state = "slide"; k.kick_cooldown = 0
    goomba = Goomba(200, 100)            # overlapping the shell
    g.level.enemies.extend([k, goomba])
    g.handle_shells()
    assert goomba.alive is False


def test_power_persists_across_levels_and_resets_on_death():
    g = Game(); g.new_game()
    g.player.become_fire()
    g.advance()
    assert g.carry_power == "fire" and g.player.power == "fire"
    g.lose_life()
    assert g.carry_power == "small"


def _shell_game():
    from game.entities.koopa import Koopa
    g = Game(); g.new_game(); g.state = "PLAYING"; g.level.enemies.clear()
    k = Koopa(300, 300); k.state = "shell"
    g.level.enemies.append(k)
    return g, k


def test_grab_then_throw_slides_in_facing_dir():
    g, k = _shell_game()
    g.player.x = float(k.rect.left - g.player.w + 8)
    g.player.y = float(k.rect.centery - g.player.h // 2)
    g.player.facing = 1
    g.grab_or_throw()
    assert g.player.carrying is k and k.held
    g.grab_or_throw()                                  # press E again -> throw
    assert g.player.carrying is None and not k.held
    assert k.state == "slide" and k.direction == 1 and k.kick_cooldown > 0


def test_cannot_grab_walking_koopa():
    g, k = _shell_game()
    k.state = "walk"
    g.player.x = float(k.rect.x); g.player.y = float(k.rect.y)
    g.grab_or_throw()
    assert g.player.carrying is None


def test_carried_shell_battering_rams_enemy():
    from game.entities.goomba import Goomba
    g, k = _shell_game()
    k.held = True; g.player.carrying = k
    g.player.x = 300.0; g.player.y = 300.0; g.player.facing = 1
    g.handle_carry()                                   # position the held shell
    gm = Goomba(k.rect.x, k.rect.y)                     # overlap it
    g.level.enemies.append(gm)
    g.handle_carry()
    assert gm.alive is False


def test_damage_drops_carried_shell():
    g, k = _shell_game()
    k.held = True; g.player.carrying = k
    g.drop_shell()
    assert g.player.carrying is None and not k.held and k.state == "shell"


def test_new_game_starts_at_chosen_world():
    from game import levelset
    g = Game(); g.new_game(4)
    assert g.index == 4 and levelset.world_label(4) == "2-1"


def test_bullet_stomped_from_top():
    from game.entities.bullet import BulletBill
    g = Game(); g.new_game(); g.state = "PLAYING"
    bl = BulletBill(int(g.player.x) + 200, int(g.player.y), -1)
    g.bullets = [bl]
    g.player.x = float(bl.rect.x)
    g.player.y = float(bl.rect.top - g.player.h + 5); g.player.vy = 4.0
    g.handle_bullets()
    assert not bl.alive and g.player.vy == S.STOMP_BOUNCE


def test_bullet_hurts_from_side():
    from game.entities.bullet import BulletBill
    g = Game(); g.new_game(); g.state = "PLAYING"; g.player.grow()    # big -> survives one hit
    bl = BulletBill(g.player.rect.centerx, g.player.rect.centery, 1)
    g.bullets = [bl]; g.player.vy = 0.0
    g.handle_bullets()
    assert g.player.power == "small"


def test_fireball_pops_bullet():
    from game.entities.bullet import BulletBill
    from game.entities.fireball import Fireball
    g = Game(); g.new_game(); g.state = "PLAYING"
    bl = BulletBill(300, 300, 1); g.bullets = [bl]
    g.fireballs.append(Fireball(bl.rect.centerx, bl.rect.centery, 1))
    g.handle_fireballs()
    assert not bl.alive


def test_cannon_in_range_spawns_a_bullet():
    from game.entities.cannon import Cannon
    g = Game(); g.new_game(); g.state = "PLAYING"
    c = Cannon(int(g.player.x) + 200, 300); c.timer = 0
    g.level.cannons = [c]
    g.player.x = float(c.rect.centerx - (S.BULLET_MIN_DIST + 40))
    g.update()
    assert len(g.bullets) >= 1


def test_fireball_defeats_boss_completes_level():
    from game.entities.boss import Boss
    from game.entities.fireball import Fireball
    g = Game(); g.new_game(); g.state = "PLAYING"
    b = Boss(int(g.player.x) + 60, int(g.player.y)); b.hp = 1
    g.level.boss = b
    g.fireballs.append(Fireball(b.rect.centerx, b.rect.centery, 1))
    g.handle_fireballs()
    assert not b.alive and g.state == "LEVEL_COMPLETE" and g.cleared_boss


def test_boss_is_stomp_proof():
    from game.entities.boss import Boss
    g = Game(); g.new_game(); g.state = "PLAYING"; g.player.grow()      # big
    b = Boss(int(g.player.x), int(g.player.y)); g.level.boss = b
    g.player.x = float(b.rect.x)
    g.player.y = float(b.rect.top - g.player.h + 6); g.player.vy = 4.0   # "stomping" from above
    g.handle_boss()
    assert g.player.power == "small"        # damaged (no stomp), big -> small


def test_lava_costs_a_life():
    g = Game(); g.new_game(); g.state = "PLAYING"
    g.level.lava = [g.player.rect.inflate(40, 40)]
    lives = g.lives
    g.update()
    assert g.lives == lives - 1


def test_death_reloads_level():
    g = Game(); g.new_game(); g.state = "PLAYING"
    box = next(b for b in g.level.blocks if b.kind in ("?", "M"))
    box.used = True
    g.lose_life()
    assert all(not b.used for b in g.level.blocks)   # fresh reload restores boxes


def test_down_on_trigger_teleports_hero():
    g = Game(); g.new_game(); g.state = "PLAYING"
    trig = pygame.Rect(5 * 40, 6 * 40, 40, 40)
    g.level.warps = [(trig, (9, 10))]
    g.player.x = float(trig.x); g.player.y = float(trig.top - g.player.h)
    g.player.on_ground = True
    g.try_warp()
    assert g.player.x == 9 * 40 and g.player.rect.bottom == 10 * 40


def test_down_off_trigger_does_nothing():
    g = Game(); g.new_game(); g.state = "PLAYING"
    g.level.warps = [(pygame.Rect(5 * 40, 6 * 40, 40, 40), (9, 10))]
    g.player.x = 800.0; g.player.y = 100.0; g.player.on_ground = True
    before = (g.player.x, g.player.y)
    g.try_warp()
    assert (g.player.x, g.player.y) == before
