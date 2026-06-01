import pygame
from game import settings as S


class HUD:
    def __init__(self):
        self.font = pygame.font.SysFont("Poppins,Arial", 24, bold=True)

    def draw(self, surface, score, sparks, lives, world="1-1"):
        bar = pygame.Surface((S.WIDTH, 40), pygame.SRCALPHA)
        bar.fill((20, 20, 19, 190))
        surface.blit(bar, (0, 0))
        pygame.draw.line(surface, S.GROUND_EDGE, (0, 40), (S.WIDTH, 40), 2)
        text = f"SCORE {score:06d}    SPARKS {sparks:02d}    LIVES {lives}    WORLD {world}"
        surface.blit(self.font.render(text, True, S.CREAM), (16, 8))
