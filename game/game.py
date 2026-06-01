import pygame
from game import settings as S
from game.level import Level
from game.camera import Camera
from game.entities.player import Player
from game.hud import HUD

JUMP_KEYS = (pygame.K_SPACE, pygame.K_UP, pygame.K_w)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((S.WIDTH, S.HEIGHT))
        pygame.display.set_caption(S.TITLE)
        self.clock = pygame.time.Clock()
        self.hud = HUD()
        self.big_font = pygame.font.SysFont("Poppins,Arial", 56, bold=True)
        self.running = True
        self.reset_game()

    def reset_game(self):
        self.score = 0
        self.sparks = 0
        self.lives = S.START_LIVES
        self.load_level()

    def load_level(self):
        self.level = Level("levels/level1.txt")
        self.player = Player(*self.level.player_spawn)
        self.camera = Camera(self.level.width_px)
        self.state = "PLAYING"

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
                    self.player.start_jump()
                elif event.key == pygame.K_RETURN and self.state in ("LEVEL_COMPLETE", "GAME_OVER"):
                    self.reset_game()
            elif event.type == pygame.KEYUP:
                if event.key in JUMP_KEYS and self.state == "PLAYING":
                    self.player.end_jump()

    # --- update ---
    def update(self):
        self.player.update(self.level)
        for e in self.level.enemies:
            e.update(self.level)
        self.camera.update(self.player.rect)
        self.handle_coins()
        self.handle_question_blocks()
        if self.handle_enemies():
            return                       # player got hit; stop this frame
        self.handle_flag()
        if self.player.y > S.PIT_DEATH_Y:
            self.player_hit()

    def handle_coins(self):
        for c in self.level.coins:
            if not c.collected and self.player.rect.colliderect(c.rect):
                c.collected = True
                self.sparks += 1
                self.score += 100

    def handle_question_blocks(self):
        if self.player.vy >= 0:
            return                       # only when moving upward
        head = self.player.rect.move(0, -2)
        for b in self.level.blocks:
            if b.kind == "?" and not b.used and head.colliderect(b.rect):
                b.used = True
                self.sparks += 1
                self.score += 100

    def handle_enemies(self):
        for e in self.level.enemies:
            if not e.alive:
                continue
            if self.player.rect.colliderect(e.rect):
                falling = self.player.vy > 0
                on_top = self.player.rect.bottom - e.rect.top < 20
                if falling and on_top:
                    e.alive = False
                    self.player.vy = S.STOMP_BOUNCE
                    self.score += 200
                else:
                    self.player_hit()
                    return True
        return False

    def handle_flag(self):
        if self.level.flag and self.player.rect.colliderect(self.level.flag.rect):
            self.state = "LEVEL_COMPLETE"

    def player_hit(self):
        self.lives -= 1
        if self.lives <= 0:
            self.state = "GAME_OVER"
        else:
            self.player = Player(*self.level.player_spawn)
            self.camera.update(self.player.rect)

    # --- draw ---
    def draw(self):
        self.screen.fill(S.CREAM)
        self.level.draw(self.screen, self.camera)
        self.player.draw(self.screen, self.camera)
        self.hud.draw(self.screen, self.score, self.sparks, self.lives)
        if self.state == "LEVEL_COMPLETE":
            self.banner("LEVEL COMPLETE!", "Press ENTER to play again")
        elif self.state == "GAME_OVER":
            self.banner("GAME OVER", "Press ENTER to retry")
        pygame.display.flip()

    def banner(self, title, subtitle):
        overlay = pygame.Surface((S.WIDTH, S.HEIGHT), pygame.SRCALPHA)
        overlay.fill((20, 20, 19, 150))
        self.screen.blit(overlay, (0, 0))
        t = self.big_font.render(title, True, S.ORANGE)
        s = self.hud.font.render(subtitle, True, S.CREAM)
        self.screen.blit(t, t.get_rect(center=(S.WIDTH // 2, S.HEIGHT // 2 - 20)))
        self.screen.blit(s, s.get_rect(center=(S.WIDTH // 2, S.HEIGHT // 2 + 30)))
