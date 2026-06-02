import pygame
from game import settings as S
from game import assets
from game import levelset
from game.level import Level
from game.camera import Camera
from game.entities.player import Player
from game.entities.mushroom import Mushroom
from game.entities.fireflower import FireFlower
from game.entities.fireball import Fireball
from game.entities.koopa import Koopa
from game.entities.boo import Boo
from game.entities.boss_shot import BossShot
from game.entities.bullet import BulletBill
from game.entities.lava_bubble import LavaBubble
from game.hud import HUD
from game.sound import SoundFX
from game.music import MusicManager
from game.scoring import bonus_lives
from game.effects import ScorePopup, RisingToken

JUMP_KEYS = (pygame.K_SPACE, pygame.K_UP, pygame.K_w)
INTRO_FRAMES = 72        # ~1.2s at 60fps


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((S.WIDTH, S.HEIGHT))
        pygame.display.set_caption(S.TITLE)
        self.clock = pygame.time.Clock()
        self.hud = HUD()
        self.big_font = pygame.font.SysFont("Poppins,Arial", 56, bold=True)
        self.small_font = pygame.font.SysFont("Poppins,Arial", 26, bold=True)
        self.sfx = SoundFX()
        self.music = MusicManager()
        self.running = True
        self.state = "TITLE"

    # --- lifecycle ---
    def new_game(self, index=0):
        self.score = 0
        self.tokens = 0
        self.lives = S.START_LIVES
        self.index = index
        self.carry_power = "small"
        self.start_level()

    def start_level(self):
        self.level = Level(S.resource_path("levels/" + levelset.level_file(self.index)))
        if self.level.boss:
            self.level.boss.set_tier(self.index // 4 + 1)
        self.lava_rising = self.level.area_type == "caldera"
        self.lava_rise_y = float(S.HEIGHT + 30)
        self.bubble_timer = S.BUBBLE_INTERVAL
        self.player = Player(*self.level.player_spawn)
        self.camera = Camera(self.level.width_px)
        self.mushrooms = []
        self.flowers = []
        self.fireballs = []
        self.boss_shots = []
        self.bullets = []
        self.lava_bubbles = []
        self.effects = []
        self.cleared_boss = False
        self.boss_title = ""
        if self.carry_power == "big":
            self.player.grow()
        elif self.carry_power == "fire":
            self.player.become_fire()
        self.intro_timer = INTRO_FRAMES
        self.music_track = 1
        self.music.play_track(1)
        self.state = "LEVEL_INTRO"

    def respawn(self):
        # death restarts the level fresh (boxes/enemies/boss reset) — classic Mario, no softlock
        self.level = Level(S.resource_path("levels/" + levelset.level_file(self.index)))
        if self.level.boss:
            self.level.boss.set_tier(self.index // 4 + 1)
        self.lava_rising = self.level.area_type == "caldera"
        self.lava_rise_y = float(S.HEIGHT + 30)
        self.bubble_timer = S.BUBBLE_INTERVAL
        self.player = Player(*self.level.player_spawn)
        self.camera = Camera(self.level.width_px)
        self.mushrooms = []
        self.flowers = []
        self.fireballs = []
        self.boss_shots = []
        self.bullets = []
        self.lava_bubbles = []
        self.effects = []
        if self.carry_power == "big":
            self.player.grow()
        elif self.carry_power == "fire":
            self.player.become_fire()
        self.music_track = 1
        self.music.play_track(1)
        self.state = "PLAYING"

    # --- helpers ---
    def now(self):
        return pygame.time.get_ticks()

    def popup(self, x, y, text):
        self.effects.append(ScorePopup(x, y, text))

    def gain_tokens(self, n, x, y):
        old = self.tokens
        self.tokens += n
        self.score += n * S.TOKEN_SCORE
        self.popup(x, y - 16, f"+{n * S.TOKEN_SCORE}")
        g = bonus_lives(old, self.tokens)
        if g:
            self.lives += g
            self.popup(x, y - 40, "1-UP")
            self.sfx.play("power")
        self.sfx.play("token")

    def lose_life(self):
        self.drop_shell()
        self.carry_power = "small"
        self.lives -= 1
        self.sfx.play("hurt")
        if self.lives <= 0:
            self.music.stop()
            self.state = "GAME_OVER"
        else:
            self.respawn()

    # --- main loop ---
    def run(self):
        while self.running:
            self.handle_events()
            if self.state == "PLAYING":
                self.update()
            elif self.state == "LEVEL_INTRO":
                self.intro_timer -= 1
                if self.intro_timer <= 0:
                    self.state = "PLAYING"
            self.draw()
            self.clock.tick(S.FPS)
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_RETURN:
                    if self.state == "TITLE":
                        self.new_game()
                    elif self.state in ("GAME_OVER", "GAME_COMPLETE"):
                        self.music.stop()
                        self.state = "TITLE"
                    elif self.state == "LEVEL_COMPLETE":
                        self.advance()
                elif self.state == "TITLE" and pygame.K_1 <= event.key <= pygame.K_9:
                    idx = (event.key - pygame.K_1) * 4        # digit -> that World's first level
                    if idx < levelset.level_count():
                        self.new_game(idx)
                elif event.key in JUMP_KEYS and self.state == "PLAYING":
                    if self.level.area_type == "water":
                        self.player.swim_stroke()
                        self.sfx.play("jump")
                    else:
                        before = self.player.air_jumped
                        self.player.press_jump(self.now())
                        self.sfx.play("double" if (self.player.air_jumped and not before) else "jump")
                elif event.key == pygame.K_f and self.state == "PLAYING":
                    if self.player.can_shoot(self.now()) and len(self.fireballs) < S.MAX_FIREBALLS:
                        self.fireballs.append(Fireball(self.player.rect.centerx, self.player.rect.centery, self.player.facing))
                        self.player.record_fire(self.now())
                        self.sfx.play("fire")
                elif event.key == pygame.K_e and self.state == "PLAYING":
                    self.grab_or_throw()
                elif event.key in (pygame.K_DOWN, pygame.K_s) and self.state == "PLAYING":
                    self.try_warp()
            elif event.type == pygame.KEYUP:
                if event.key in JUMP_KEYS and self.state == "PLAYING" and self.level.area_type != "water":
                    self.player.release_jump()

    def advance(self):
        self.carry_power = self.player.power
        nxt = levelset.next_index(self.index)
        if nxt is None:
            self.music.stop()
            self.state = "GAME_COMPLETE"
        else:
            self.index = nxt
            self.start_level()

    # --- update ---
    def update(self):
        self.player.update(self.level)
        self.apply_conveyor()
        for e in self.level.enemies:
            e.update(self.level)
        for e in self.level.enemies:
            if isinstance(e, Boo) and e.alive:
                e.chase(self.player)             # ghosts hunt when you look away
        if self.level.boss and self.level.boss.alive:
            self.level.boss.update(self.level)
            if self.level.boss.ready_to_shoot():
                d = 1 if self.player.rect.centerx >= self.level.boss.rect.centerx else -1
                self.boss_shots.append(BossShot(self.level.boss.rect.centerx, self.level.boss.rect.centery, d))
                self.sfx.play("fire")
        for s in self.boss_shots:
            s.update(self.level)
        self.boss_shots = [s for s in self.boss_shots if s.alive]
        for c in self.level.cannons:
            d = c.tick(self.player.rect.centerx)
            if d and len(self.bullets) < 6:
                self.bullets.append(BulletBill(c.rect.centerx, c.rect.centery, d))
                self.sfx.play("fire")
        for bl in self.bullets:
            bl.update(self.level)
        self.bullets = [bl for bl in self.bullets if bl.alive]
        if self.lava_rising:
            self.lava_rise_y -= S.LAVA_RISE_SPEED
            self.bubble_timer -= 1
            if self.bubble_timer <= 0:
                self.bubble_timer = S.BUBBLE_INTERVAL
                bx = self.player.rect.centerx + (60 if self.player.facing > 0 else -60)
                self.lava_bubbles.append(LavaBubble(bx, self.lava_rise_y))
        for lb in self.lava_bubbles:
            lb.update(self.level)
        self.lava_bubbles = [lb for lb in self.lava_bubbles if lb.alive]
        for m in self.mushrooms:
            m.update(self.level)
        for fl in self.flowers:
            fl.update(self.level)
        for f in self.fireballs:
            f.update(self.level)
        for fx in self.effects:
            fx.update()
        self.effects = [fx for fx in self.effects if fx.alive]
        self.camera.update(self.player.rect)
        seg = levelset.segment_track(min(self.player.x, self.level.play_width), self.level.play_width)
        if seg > self.music_track:
            self.music_track = seg
            self.music.play_track(seg)

        self.handle_coins()
        self.handle_boxes()
        self.handle_mushrooms()
        self.handle_flowers()
        self.handle_fireballs()
        self.handle_carry()
        self.handle_shells()
        if self.handle_enemies():
            return
        if self.handle_boss():
            return
        if self.handle_bullets():
            return
        if self.lava_rising and self.player.rect.bottom >= self.lava_rise_y:
            self.lose_life()
            return
        for lb in self.lava_bubbles:
            if lb.alive and self.player.rect.colliderect(lb.rect):
                lb.alive = False
                if self.player.take_damage(self.now()):
                    self.lose_life()
                    return
                self.sfx.play("hurt")
        if self.level.flag and self.player.rect.colliderect(self.level.flag.rect):
            self.sfx.play("win")
            self.state = "LEVEL_COMPLETE"
            return
        if self.player.y > S.PIT_DEATH_Y:
            self.lose_life()
            return
        if any(self.player.rect.colliderect(l) for l in self.level.lava):
            self.lose_life()

    def apply_conveyor(self):
        """Belt floors carry a grounded hero; a wall stops the carry."""
        if not self.player.on_ground:
            return
        d = self.level.belt_dir(self.player.rect)
        if not d:
            return
        self.player.x += S.CONVEYOR_SPEED * d
        for s in self.level.solids:
            if self.player.rect.colliderect(s):
                self.player.x = float(s.left - self.player.w) if d > 0 else float(s.right)

    def handle_coins(self):
        for c in self.level.coins:
            if not c.collected and self.player.rect.colliderect(c.rect):
                c.collected = True
                self.gain_tokens(1, c.rect.centerx, c.rect.top)

    def handle_boxes(self):
        if self.player.vy > 0:
            return                       # only when rising or just bonked the head (vy <= 0)
        head = self.player.rect.move(0, -3)
        for b in self.level.blocks:
            if b.used or not head.colliderect(b.rect):
                continue
            if b.kind == "?":
                b.used = True
                self.effects.append(RisingToken(b.rect.centerx, b.rect.top))
                self.gain_tokens(1, b.rect.centerx, b.rect.top)
            elif b.kind == "M":
                b.used = True
                if self.player.power == "small":
                    self.mushrooms.append(Mushroom(b.rect.x, b.rect.y))
                else:
                    self.flowers.append(FireFlower(b.rect.x, b.rect.y))
                self.sfx.play("power")

    def handle_mushrooms(self):
        for m in self.mushrooms:
            if m.alive and not m.emerging and self.player.rect.colliderect(m.rect):
                m.alive = False
                self.player.grow()
                self.score += m.score
                self.popup(m.rect.centerx, m.rect.top, f"+{m.score}")
                self.sfx.play("power")
        self.mushrooms = [m for m in self.mushrooms if m.alive]

    def handle_flowers(self):
        for fl in self.flowers:
            if fl.alive and not fl.emerging and self.player.rect.colliderect(fl.rect):
                fl.alive = False
                self.player.become_fire()
                self.score += fl.score
                self.popup(fl.rect.centerx, fl.rect.top, f"+{fl.score}")
                self.sfx.play("power")
        self.flowers = [fl for fl in self.flowers if fl.alive]

    def handle_fireballs(self):
        for f in self.fireballs:
            if not f.alive:
                continue
            for e in self.level.enemies:
                if e.alive and f.alive and f.rect.colliderect(e.rect):
                    e.alive = False
                    f.alive = False
                    self.score += f.score
                    self.popup(e.rect.centerx, e.rect.top, f"+{f.score}")
                    self.sfx.play("stomp")
            b = self.level.boss
            if f.alive and b and b.alive and f.rect.colliderect(b.rect):
                f.alive = False
                if b.hit():
                    self.boss_defeated()
                else:
                    self.sfx.play("stomp")
            for bl in self.bullets:
                if bl.alive and f.alive and f.rect.colliderect(bl.rect):
                    bl.alive = False
                    f.alive = False
                    self.score += f.score
                    self.popup(bl.rect.centerx, bl.rect.top, f"+{f.score}")
                    self.sfx.play("stomp")
        self.fireballs = [f for f in self.fireballs if f.alive]

    def try_warp(self):
        p = self.player
        if not p.on_ground:
            return
        foot = (p.rect.centerx, p.rect.bottom + 2)
        for trig, (dx, dy) in self.level.warps:
            if trig.collidepoint(*foot):
                p.x = float(dx * S.TILE)
                p.y = float(dy * S.TILE - p.h)
                p.vx = p.vy = 0.0
                self.camera.update(p.rect)
                self.sfx.play("power")
                self.popup(p.rect.centerx, p.rect.top, "WARP")
                return

    def grab_or_throw(self):
        if self.player.carrying is not None:
            self.throw_shell()
            return
        reach = self.player.rect.inflate(10, 6)
        for e in self.level.enemies:
            if isinstance(e, Koopa) and e.alive and e.state == "shell" and not e.held \
                    and reach.colliderect(e.rect):
                e.held = True
                e.vx = e.vy = 0.0
                self.player.carrying = e
                self.sfx.play("power")
                break

    def throw_shell(self):
        k = self.player.carrying
        self.player.carrying = None
        k.held = False
        k.state = "slide"
        k.direction = self.player.facing
        k.kick_cooldown = S.SHELL_KICK_COOLDOWN
        self.sfx.play("stomp")

    def drop_shell(self):
        k = self.player.carrying
        if k is not None:
            self.player.carrying = None
            k.held = False
            k.state = "shell"

    def handle_carry(self):
        k = self.player.carrying
        if k is None:
            return
        if not k.alive:
            self.player.carrying = None
            return
        p = self.player
        k.x = float(p.rect.right - 6) if p.facing > 0 else float(p.rect.left - k.w + 6)
        k.y = float(p.rect.centery - k.h // 2)
        for e in self.level.enemies:
            if e is not k and e.alive and k.rect.colliderect(e.rect):
                e.alive = False
                pts = getattr(e, "score", S.STOMP_SCORE)
                self.score += pts
                self.popup(e.rect.centerx, e.rect.top, f"+{pts}")
                self.sfx.play("stomp")

    def handle_enemies(self):
        for e in self.level.enemies:
            if not e.alive or e is self.player.carrying or not self.player.rect.colliderect(e.rect):
                continue
            from_top = self.player.vy > 0 and self.player.rect.bottom - e.rect.top < 20
            if isinstance(e, Koopa):
                if e.state == "slide" and e.kick_cooldown > 0:
                    continue                 # you don't hurt yourself the instant you kick
                outcome = e.player_hit(from_top, self.player.rect.centerx)
                if outcome in ("stomp", "bounce", "stomp_stop"):
                    self.player.vy = S.STOMP_BOUNCE
                    if outcome == "stomp":
                        self.score += e.score
                        self.popup(e.rect.centerx, e.rect.top, f"+{e.score}")
                    self.sfx.play("stomp")
                elif outcome == "kick":
                    self.sfx.play("stomp")
                elif outcome == "hurt":
                    if self.player.take_damage(self.now()):
                        self.lose_life()
                        return True
                    self.sfx.play("hurt")
            else:
                if from_top and not getattr(e, "stomp_proof", False):
                    e.alive = False
                    self.player.vy = S.STOMP_BOUNCE
                    pts = getattr(e, "score", S.STOMP_SCORE)
                    self.score += pts
                    self.popup(e.rect.centerx, e.rect.top, f"+{pts}")
                    self.sfx.play("stomp")
                elif self.player.take_damage(self.now()):
                    self.lose_life()
                    return True
                else:
                    self.sfx.play("hurt")
        return False

    def handle_shells(self):
        """A sliding shell bowls over any other live enemy it overlaps."""
        for k in self.level.enemies:
            if not (isinstance(k, Koopa) and k.alive and k.state == "slide"):
                continue
            for e in self.level.enemies:
                if e is not k and e.alive and k.rect.colliderect(e.rect):
                    e.alive = False
                    pts = getattr(e, "score", S.STOMP_SCORE)
                    self.score += pts
                    self.popup(e.rect.centerx, e.rect.top, f"+{pts}")
                    self.sfx.play("stomp")

    def boss_defeated(self):
        b = self.level.boss
        self.score += b.score
        self.popup(b.rect.centerx, b.rect.top, f"+{b.score}")
        self.sfx.play("win")
        self.cleared_boss = True
        self.boss_title = b.title
        self.state = "LEVEL_COMPLETE"

    def handle_boss(self):
        """Boss body and its shots hurt the player (the boss is stomp-proof)."""
        b = self.level.boss
        if b and b.alive and self.player.rect.colliderect(b.rect):
            if self.player.take_damage(self.now()):
                self.lose_life()
                return True
            self.sfx.play("hurt")
        for s in self.boss_shots:
            if s.alive and self.player.rect.colliderect(s.rect):
                s.alive = False
                if self.player.take_damage(self.now()):
                    self.lose_life()
                    return True
                self.sfx.play("hurt")
        return False

    def handle_bullets(self):
        """Bullet Bills: stompable from the top, hurt from the side."""
        for bl in self.bullets:
            if not bl.alive or not self.player.rect.colliderect(bl.rect):
                continue
            if self.player.vy > 0 and self.player.rect.bottom - bl.rect.top < 20:
                bl.alive = False
                self.player.vy = S.STOMP_BOUNCE
                self.score += bl.score
                self.popup(bl.rect.centerx, bl.rect.top, f"+{bl.score}")
                self.sfx.play("stomp")
            elif self.player.take_damage(self.now()):
                self.lose_life()
                return True
            else:
                self.sfx.play("hurt")
        return False

    # --- draw ---
    def draw(self):
        if self.state == "TITLE":
            self.draw_title()
        else:
            area = self.level.area_type
            assets.draw_background(self.screen, self.camera, area)
            self.level.draw(self.screen, self.camera)
            if self.lava_rising:
                assets.draw_lava_sea(self.screen, self.lava_rise_y)
            for lb in self.lava_bubbles:
                lb.draw(self.screen, self.camera)
            for m in self.mushrooms:
                m.draw(self.screen, self.camera)
            for fl in self.flowers:
                fl.draw(self.screen, self.camera)
            for f in self.fireballs:
                f.draw(self.screen, self.camera)
            for s in self.boss_shots:
                s.draw(self.screen, self.camera)
            for bl in self.bullets:
                bl.draw(self.screen, self.camera)
            self.player.draw(self.screen, self.camera)
            if self.player.carrying is not None:
                self.player.carrying.draw(self.screen, self.camera)   # held shell on top
            for fx in self.effects:
                fx.draw(self.screen, self.camera, self.hud.font)
            self.hud.draw(self.screen, self.score, self.tokens, self.lives, levelset.world_label(self.index))
            if self.state == "LEVEL_INTRO":
                self.banner(f"WORLD {levelset.world_label(self.index)}", "")
            elif self.state == "LEVEL_COMPLETE":
                if self.cleared_boss:
                    self.banner(f"{self.boss_title} DEFEATED!",
                                f"World {levelset.world_label(self.index)[0]} clear — Press ENTER")
                else:
                    self.banner("LEVEL COMPLETE!", "Press ENTER")
            elif self.state == "GAME_OVER":
                self.banner("GAME OVER", "Press ENTER for title")
            elif self.state == "GAME_COMPLETE":
                self.banner("YOU SAVED THE DAY!", "Press ENTER for title")
        pygame.display.flip()

    def draw_title(self):
        self.screen.fill(S.NIGHT)
        assets.draw_player(self.screen, pygame.Rect(S.WIDTH // 2 - 30, 150, 60, 88), 1, "big")
        worlds = (levelset.level_count() + 3) // 4
        t = self.big_font.render("SUPER CLAUDE BROS", True, S.ORANGE)
        s = self.small_font.render("Press ENTER to play", True, S.CREAM)
        s2 = self.small_font.render(f"or 1-{worlds} to pick a World", True, S.MIDGRAY)
        self.screen.blit(t, t.get_rect(center=(S.WIDTH // 2, 300)))
        self.screen.blit(s, s.get_rect(center=(S.WIDTH // 2, 354)))
        self.screen.blit(s2, s2.get_rect(center=(S.WIDTH // 2, 392)))

    def banner(self, title, subtitle):
        overlay = pygame.Surface((S.WIDTH, S.HEIGHT), pygame.SRCALPHA)
        overlay.fill((20, 20, 19, 150))
        self.screen.blit(overlay, (0, 0))
        t = self.big_font.render(title, True, S.ORANGE)
        self.screen.blit(t, t.get_rect(center=(S.WIDTH // 2, S.HEIGHT // 2 - 16)))
        if subtitle:
            s = self.small_font.render(subtitle, True, S.CREAM)
            self.screen.blit(s, s.get_rect(center=(S.WIDTH // 2, S.HEIGHT // 2 + 34)))
