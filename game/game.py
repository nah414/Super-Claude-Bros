import pygame
from game import settings as S
from game import assets
from game.level import Level
from game.camera import Camera
from game.entities.player import Player
from game.entities.mushroom import Mushroom
from game.hud import HUD
from game.sound import SoundFX
from game.scoring import bonus_lives
from game.effects import ScorePopup, RisingToken

JUMP_KEYS = (pygame.K_SPACE, pygame.K_UP, pygame.K_w)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((S.WIDTH, S.HEIGHT))
        pygame.display.set_caption(S.TITLE)
        self.clock = pygame.time.Clock()
        self.hud = HUD()
        self.big_font = pygame.font.SysFont("Poppins,Arial", 56, bold=True)
        self.sfx = SoundFX()
        self.running = True
        self.reset_game()

    def reset_game(self):
        self.score = 0
        self.tokens = 0
        self.lives = S.START_LIVES
        self.load_level()

    def load_level(self):
        self.level = Level(S.resource_path("levels/level1.txt"))
        self.player = Player(*self.level.player_spawn)
        self.camera = Camera(self.level.width_px)
        self.mushrooms = []
        self.effects = []
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
        gained = bonus_lives(old, self.tokens)
        if gained:
            self.lives += gained
            self.popup(x, y - 40, "1-UP")
            self.sfx.play("power")
        self.sfx.play("token")

    def lose_life(self):
        self.lives -= 1
        self.sfx.play("hurt")
        if self.lives <= 0:
            self.state = "GAME_OVER"
        else:
            self.player = Player(*self.level.player_spawn)
            self.camera.update(self.player.rect)

    # --- main loop ---
    def run(self):
        while self.running:
            self.handle_events()
            if self.state == "PLAYING":
                self.update()
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
                elif event.key in JUMP_KEYS and self.state == "PLAYING":
                    before = self.player.air_jumped
                    self.player.press_jump(self.now())
                    self.sfx.play("double" if (self.player.air_jumped and not before) else "jump")
                elif event.key == pygame.K_RETURN and self.state in ("LEVEL_COMPLETE", "GAME_OVER"):
                    self.reset_game()
            elif event.type == pygame.KEYUP:
                if event.key in JUMP_KEYS and self.state == "PLAYING":
                    self.player.release_jump()

    # --- update ---
    def update(self):
        self.player.update(self.level)
        for e in self.level.enemies:
            e.update(self.level)
        for m in self.mushrooms:
            m.update(self.level)
        for fx in self.effects:
            fx.update()
        self.effects = [fx for fx in self.effects if fx.alive]
        self.camera.update(self.player.rect)

        self.handle_coins()
        self.handle_boxes()
        self.handle_mushrooms()
        if self.handle_enemies():
            return
        self.handle_flag()
        if self.player.y > S.PIT_DEATH_Y:
            self.lose_life()

    def handle_coins(self):
        for c in self.level.coins:
            if not c.collected and self.player.rect.colliderect(c.rect):
                c.collected = True
                self.gain_tokens(1, c.rect.centerx, c.rect.top)

    def handle_boxes(self):
        if self.player.vy >= 0:
            return
        head = self.player.rect.move(0, -2)
        for b in self.level.blocks:
            if b.used or not head.colliderect(b.rect):
                continue
            if b.kind == "?":
                b.used = True
                self.effects.append(RisingToken(b.rect.centerx, b.rect.top))
                self.gain_tokens(1, b.rect.centerx, b.rect.top)
            elif b.kind == "M":
                b.used = True
                self.mushrooms.append(Mushroom(b.rect.x, b.rect.y))
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
                    self.sfx.play("hurt")        # shrank, survived
        return False

    def handle_flag(self):
        if self.level.flag and self.player.rect.colliderect(self.level.flag.rect):
            if self.state != "LEVEL_COMPLETE":
                self.sfx.play("win")
            self.state = "LEVEL_COMPLETE"

    # --- draw ---
    def draw(self):
        assets.draw_background(self.screen, self.camera)
        self.level.draw(self.screen, self.camera)
        for m in self.mushrooms:
            m.draw(self.screen, self.camera)
        self.player.draw(self.screen, self.camera)
        for fx in self.effects:
            fx.draw(self.screen, self.camera, self.hud.font)
        self.hud.draw(self.screen, self.score, self.tokens, self.lives)
        if self.state == "LEVEL_COMPLETE":
            self.banner("LEVEL COMPLETE!", "Press ENTER to play again")
        elif self.state == "GAME_OVER":
            self.banner("GAME OVER", "Press ENTER to retry")
        pygame.display.flip()

    def banner(self, title, subtitle):
        overlay = pygame.Surface((S.WIDTH, S.HEIGHT), pygame.SRCALPHA)
        overlay.fill((20, 20, 19, 170))
        self.screen.blit(overlay, (0, 0))
        t = self.big_font.render(title, True, S.ORANGE)
        s = self.hud.font.render(subtitle, True, S.CREAM)
        self.screen.blit(t, t.get_rect(center=(S.WIDTH // 2, S.HEIGHT // 2 - 20)))
        self.screen.blit(s, s.get_rect(center=(S.WIDTH // 2, S.HEIGHT // 2 + 30)))
