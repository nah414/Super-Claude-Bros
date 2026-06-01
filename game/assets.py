"""All drawing lives here. Entities call these; they never blit directly.
This is the swappable art seam: replace these bodies with sprite blits later
and no game logic changes."""
import math
import pygame
from game import settings as S

# fixed star positions (screen space), gently parallaxed by the camera
_STARS = [(57, 60), (140, 38), (210, 90), (320, 50), (440, 110), (560, 44),
          (640, 95), (740, 70), (840, 36), (900, 120), (480, 150), (260, 150)]


def draw_background(surface, camera):
    surface.fill(S.NIGHT)
    pygame.draw.circle(surface, S.MOON, (S.WIDTH - 90, 90), 34)
    pygame.draw.circle(surface, S.NIGHT, (S.WIDTH - 78, 82), 30)   # crescent bite
    shift = int(camera.offset_x * 0.3)
    for sx, sy in _STARS:
        x = (sx - shift) % S.WIDTH
        pygame.draw.circle(surface, S.CREAM, (x, sy), 2)


_qfont = None


def _question_font():
    global _qfont
    if _qfont is None:
        _qfont = pygame.font.SysFont("Arial", 24, bold=True)
    return _qfont


def draw_block(surface, rect, kind, used=False):
    if kind == "X":                       # solid ground
        pygame.draw.rect(surface, S.GROUND_DARK, rect)
        pygame.draw.rect(surface, S.GROUND_EDGE, (rect.x, rect.y, rect.w, 4))
        pygame.draw.rect(surface, S.INK, rect, 1)
    elif kind == "=":                     # floating platform
        pygame.draw.rect(surface, S.GROUND_DARK, rect, border_radius=6)
        pygame.draw.rect(surface, S.GROUND_EDGE, (rect.x + 3, rect.y + 2, rect.w - 6, 4))
        pygame.draw.rect(surface, S.INK, rect, 1, border_radius=6)
    elif kind == "B":                     # brick
        pygame.draw.rect(surface, S.BRICK_DARK, rect)
        pygame.draw.rect(surface, S.INK, rect, 1)
        pygame.draw.line(surface, S.INK, (rect.left, rect.centery),
                         (rect.right, rect.centery), 1)
        pygame.draw.line(surface, S.INK, (rect.centerx, rect.top),
                         (rect.centerx, rect.centery), 1)
    elif kind in ("?", "M"):              # mystery box (M looks identical to ?)
        pygame.draw.rect(surface, S.MIDGRAY if used else S.BLUE, rect, border_radius=4)
        pygame.draw.rect(surface, S.INK, rect, 2, border_radius=4)
        if not used:
            q = _question_font().render("?", True, S.CREAM)
            surface.blit(q, q.get_rect(center=rect.center))


def draw_player(surface, rect, facing=1):
    pygame.draw.rect(surface, S.ORANGE, rect, border_radius=10)
    pygame.draw.rect(surface, S.INK, rect, 2, border_radius=10)
    ox = 4 * facing
    eye_y = rect.y + rect.h // 3
    for ex in (rect.centerx - 7 + ox, rect.centerx + 7 + ox):
        pygame.draw.circle(surface, S.CREAM, (ex, eye_y), 5)
        pygame.draw.circle(surface, S.INK, (ex, eye_y), 2)
    mx, my = rect.centerx + ox, eye_y + 11
    pygame.draw.lines(surface, S.INK, False,
                      [(mx - 7, my), (mx, my + 4), (mx + 7, my)], 2)
    pygame.draw.ellipse(surface, S.INK, (rect.left + 3, rect.bottom - 6, 12, 6))
    pygame.draw.ellipse(surface, S.INK, (rect.right - 15, rect.bottom - 6, 12, 6))


def draw_coin(surface, rect):
    cx, cy = rect.center
    r = rect.w // 2
    for a in range(0, 360, 45):
        rad = math.radians(a)
        pygame.draw.line(surface, S.ORANGE, (cx, cy),
                         (cx + r * math.cos(rad), cy + r * math.sin(rad)), 3)
    pygame.draw.circle(surface, S.ORANGE, (cx, cy), max(2, r // 2))
    pygame.draw.circle(surface, S.CREAM, (cx, cy), max(1, r // 4))


def draw_goomba(surface, rect):
    body = pygame.Rect(rect.left, rect.top, rect.w, rect.h)
    pygame.draw.ellipse(surface, S.INK, body)
    pygame.draw.ellipse(surface, S.MIDGRAY, body, 2)        # light rim for night visibility
    eye_y = rect.y + rect.h // 3
    for ex in (rect.centerx - 6, rect.centerx + 6):
        pygame.draw.circle(surface, S.CREAM, (ex, eye_y), 4)
        pygame.draw.circle(surface, S.INK, (ex, eye_y), 2)
    pygame.draw.ellipse(surface, S.SAGE, (rect.left, rect.bottom - 5, rect.w // 2 - 1, 5))
    pygame.draw.ellipse(surface, S.SAGE, (rect.centerx + 1, rect.bottom - 5, rect.w // 2 - 1, 5))


def draw_flag(surface, rect):
    pole = pygame.Rect(rect.centerx - 3, rect.top, 6, rect.h)
    pygame.draw.rect(surface, S.CREAM, pole)                # cream so it shows on the night sky
    pygame.draw.rect(surface, S.INK, pole, 1)
    pygame.draw.circle(surface, S.BLUE, (rect.centerx, rect.top), 6)
    pts = [(rect.centerx + 3, rect.top + 6),
           (rect.centerx + 30, rect.top + 14),
           (rect.centerx + 3, rect.top + 22)]
    pygame.draw.polygon(surface, S.ORANGE, pts)
