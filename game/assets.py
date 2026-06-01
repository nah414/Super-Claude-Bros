"""All drawing lives here. Entities call these; they never blit directly.
This is the swappable art seam: replace these bodies with sprite blits later
and no game logic changes."""
import math
import pygame
from game import settings as S

_qfont = None


def _question_font():
    global _qfont
    if _qfont is None:
        _qfont = pygame.font.SysFont("Arial", 24, bold=True)
    return _qfont


def draw_block(surface, rect, kind, used=False):
    if kind == "X":                       # solid ground
        pygame.draw.rect(surface, S.SAGE, rect)
        pygame.draw.rect(surface, S.INK, rect, 1)
    elif kind == "=":                     # floating platform
        pygame.draw.rect(surface, S.SAGE, rect, border_radius=6)
        pygame.draw.rect(surface, S.INK, rect, 1, border_radius=6)
    elif kind == "B":                     # brick
        pygame.draw.rect(surface, S.LIGHTGRAY, rect)
        pygame.draw.rect(surface, S.INK, rect, 1)
        pygame.draw.line(surface, S.INK, (rect.left, rect.centery),
                         (rect.right, rect.centery), 1)
        pygame.draw.line(surface, S.INK, (rect.centerx, rect.top),
                         (rect.centerx, rect.centery), 1)
    elif kind == "?":                     # question block
        pygame.draw.rect(surface, S.MIDGRAY if used else S.BLUE, rect, border_radius=4)
        pygame.draw.rect(surface, S.INK, rect, 2, border_radius=4)
        if not used:
            q = _question_font().render("?", True, S.CREAM)
            surface.blit(q, q.get_rect(center=rect.center))
