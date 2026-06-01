import pygame
from game import settings as S
from game.level import Level
from game.camera import Camera
from game.entities.player import Player

JUMP_KEYS = (pygame.K_SPACE, pygame.K_UP, pygame.K_w)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((S.WIDTH, S.HEIGHT))
        pygame.display.set_caption(S.TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.load_level()

    def load_level(self):
        self.level = Level("levels/level1.txt")
        self.player = Player(*self.level.player_spawn)
        self.camera = Camera(self.level.width_px)

    def run(self):
        while self.running:
            self.handle_events()
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
                elif event.key in JUMP_KEYS:
                    self.player.start_jump()
            elif event.type == pygame.KEYUP:
                if event.key in JUMP_KEYS:
                    self.player.end_jump()

    def update(self):
        self.player.update(self.level)
        for e in self.level.enemies:
            e.update(self.level)
        self.camera.update(self.player.rect)

    def draw(self):
        self.screen.fill(S.CREAM)
        self.level.draw(self.screen, self.camera)
        self.player.draw(self.screen, self.camera)
        pygame.display.flip()
