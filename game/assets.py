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


def draw_player(surface, rect, facing=1, power="small"):
    w, h = rect.w, rect.h
    ox = int(2 * facing)
    body = pygame.Rect(rect.x + int(w * 0.10), rect.y + int(h * 0.42),
                       int(w * 0.80), int(h * 0.46))
    # legs
    fy = body.bottom
    pygame.draw.rect(surface, S.ORANGE, (body.centerx - int(w*0.22), fy - 2, int(w*0.16), int(h*0.12)), border_radius=3)
    pygame.draw.rect(surface, S.ORANGE, (body.centerx + int(w*0.06), fy - 2, int(w*0.16), int(h*0.12)), border_radius=3)
    # feet
    pygame.draw.ellipse(surface, S.INK, (body.left - 2, rect.bottom - int(h*0.10), int(w*0.40), int(h*0.10)))
    pygame.draw.ellipse(surface, S.INK, (body.centerx + 1, rect.bottom - int(h*0.10), int(w*0.40), int(h*0.10)))
    # body
    pygame.draw.rect(surface, S.ORANGE, body, border_radius=int(w*0.30))
    pygame.draw.rect(surface, S.INK, body, 2, border_radius=int(w*0.30))
    # face on the body
    ey = body.y + int(body.h * 0.34)
    er = max(3, int(w * 0.13))
    for ex in (body.centerx - int(w*0.18) + ox, body.centerx + int(w*0.18) + ox):
        pygame.draw.circle(surface, S.CREAM, (ex, ey), er)
        pygame.draw.circle(surface, S.INK, (ex + ox, ey + 2), max(1, er // 2))
    sm = int(w * 0.16)
    smy = ey + int(h * 0.12)
    pygame.draw.lines(surface, S.INK, False,
                      [(body.centerx - sm + ox, smy), (body.centerx + ox, smy + 4), (body.centerx + sm + ox, smy)], 2)
    # glowing sunburst head above the body
    hx, hy = rect.centerx, rect.y + int(h * 0.22)
    R = int(w * 0.42) if power == "big" else int(w * 0.38)
    pygame.draw.line(surface, S.ORANGE, (hx, hy + int(w*0.22)), (hx, body.y), 4)   # neck
    for a in range(0, 360, 30):
        rad = math.radians(a)
        pygame.draw.line(surface, S.ORANGE, (hx, hy), (hx + R*math.cos(rad), hy + R*math.sin(rad)), 3)
    pygame.draw.circle(surface, S.ORANGE, (hx, hy), max(5, int(w*0.26)))
    pygame.draw.circle(surface, S.INK, (hx, hy), max(5, int(w*0.26)), 2)
    pygame.draw.circle(surface, S.CREAM, (hx, hy), max(2, int(w*0.11)))


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
