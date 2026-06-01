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
    def new_game(self):
        self.score = 0
        self.tokens = 0
        self.lives = S.START_LIVES
        self.index = 0
        self.carry_power = "small"
        self.start_level()

    def start_level(self):
        self.level = Level(S.resource_path("levels/" + levelset.level_file(self.index)))
        self.player = Player(*self.level.player_spawn)
        self.camera = Camera(self.level.width_px)
        self.mushrooms = []
        self.flowers = []
        self.fireballs = []
        self.effects = []
        if self.carry_power == "big":
            self.player.grow()
        elif self.carry_power == "fire":
            self.player.become_fire()
        self.intro_timer = INTRO_FRAMES
        self.music_track = 1
        self.music.play_track(1)
        self.state = "LEVEL_INTRO"

    def respawn(self):
        self.player = Player(*self.level.player_spawn)
        self.camera = Camera(self.level.width_px)
        self.mushrooms = []
        self.flowers = []
        self.fireballs = []
        self.effects = []
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
                elif event.key in JUMP_KEYS and self.state == "PLAYING":
                    before = self.player.air_jumped
                    self.player.press_jump(self.now())
                    self.sfx.play("double" if (self.player.air_jumped and not before) else "jump")
                elif event.key == pygame.K_f and self.state == "PLAYING":
                    if self.player.can_shoot(self.now()) and len(self.fireballs) < S.MAX_FIREBALLS:
                        self.fireballs.append(Fireball(self.player.rect.centerx, self.player.rect.centery, self.player.facing))
                        self.player.record_fire(self.now())
                        self.sfx.play("fire")
            elif event.type == pygame.KEYUP:
                if event.key in JUMP_KEYS and self.state == "PLAYING":
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
        for e in self.level.enemies:
            e.update(self.level)
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
        seg = levelset.segment_track(self.player.x, self.level.width_px)
        if seg > self.music_track:
            self.music_track = seg
            self.music.play_track(seg)

        self.handle_coins()
        self.handle_boxes()
        self.handle_mushrooms()
        self.handle_flowers()
        self.handle_fireballs()
        if self.handle_enemies():
            return
        if self.level.flag and self.player.rect.colliderect(self.level.flag.rect):
            self.sfx.play("win")
            self.state = "LEVEL_COMPLETE"
            return
        if self.player.y > S.PIT_DEATH_Y:
            self.lose_life()

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
        self.fireballs = [f for f in self.fireballs if f.alive]

    def handle_enemies(self):
        for e in self.level.enemies:
            if not e.alive:
                continue
            if self.player.rect.colliderect(e.rect):
                if self.player.vy > 0 and self.player.rect.bottom - e.rect.top < 20:
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

    # --- draw ---
    def draw(self):
        if self.state == "TITLE":
            self.draw_title()
        else:
            area = self.level.area_type
            assets.draw_background(self.screen, self.camera, area)
            self.level.draw(self.screen, self.camera)
            for m in self.mushrooms:
                m.draw(self.screen, self.camera)
            for fl in self.flowers:
                fl.draw(self.screen, self.camera)
            for f in self.fireballs:
                f.draw(self.screen, self.camera)
            self.player.draw(self.screen, self.camera)
            for fx in self.effects:
                fx.draw(self.screen, self.camera, self.hud.font)
            self.hud.draw(self.screen, self.score, self.tokens, self.lives, levelset.world_label(self.index))
            if self.state == "LEVEL_INTRO":
                self.banner(f"WORLD {levelset.world_label(self.index)}", "")
            elif self.state == "LEVEL_COMPLETE":
                self.banner("LEVEL COMPLETE!", "Press ENTER")
            elif self.state == "GAME_OVER":
                self.banner("GAME OVER", "Press ENTER for title")
            elif self.state == "GAME_COMPLETE":
                self.banner("YOU SAVED THE DAY!", "Press ENTER for title")
        pygame.display.flip()

    def draw_title(self):
        self.screen.fill(S.NIGHT)
        assets.draw_player(self.screen, pygame.Rect(S.WIDTH // 2 - 30, 150, 60, 88), 1, "big")
        t = self.big_font.render("SUPER CLAUDE BROS", True, S.ORANGE)
        s = self.small_font.render("Press ENTER to play", True, S.CREAM)
        self.screen.blit(t, t.get_rect(center=(S.WIDTH // 2, 300)))
        self.screen.blit(s, s.get_rect(center=(S.WIDTH // 2, 360)))

    def banner(self, title, subtitle):
        overlay = pygame.Surface((S.WIDTH, S.HEIGHT), pygame.SRCALPHA)
        overlay.fill((20, 20, 19, 150))
        self.screen.blit(overlay, (0, 0))
        t = self.big_font.render(title, True, S.ORANGE)
        self.screen.blit(t, t.get_rect(center=(S.WIDTH // 2, S.HEIGHT // 2 - 16)))
        if subtitle:
            s = self.small_font.render(subtitle, True, S.CREAM)
            self.screen.blit(s, s.get_rect(center=(S.WIDTH // 2, S.HEIGHT // 2 + 34)))
