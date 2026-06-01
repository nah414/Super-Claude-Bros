import pygame
from game import settings as S


class HUD:
    def __init__(self):
        self.font = pygame.font.SysFont("Poppins,Arial", 24, bold=True)

    def draw(self, surface, score, sparks, lives):
        bar = pygame.Rect(0, 0, S.WIDTH, 40)
        pygame.draw.rect(surface, S.CREAM, bar)
        pygame.draw.line(surface, S.LIGHTGRAY, (0, 40), (S.WIDTH, 40), 2)
        text = f"SCORE {score:06d}    SPARKS {sparks:02d}    LIVES {lives}    WORLD 1-1"
        surface.blit(self.font.render(text, True, S.INK), (16, 8))
