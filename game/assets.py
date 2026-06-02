"""All drawing lives here. Entities call these; they never blit directly.
This is the swappable art seam: replace these bodies with sprite blits later
and no game logic changes."""
import math
import pygame
from game import settings as S

# fixed star positions (screen space), gently parallaxed by the camera
_STARS = [(57, 60), (140, 38), (210, 90), (320, 50), (440, 110), (560, 44),
          (640, 95), (740, 70), (840, 36), (900, 120), (480, 150), (260, 150)]


def draw_background(surface, camera, area_type="overworld"):
    if area_type == "haunted":
        surface.fill(S.HAUNT_BG)
        pygame.draw.circle(surface, S.MOON_PALE, (S.WIDTH - 110, 78), 28)
        shift = int(camera.offset_x * 0.2)
        for fx, fy, fw in [(120, 210, 90), (380, 150, 120), (640, 270, 100), (860, 190, 80), (300, 360, 110)]:
            wisp = pygame.Surface((fw, 28), pygame.SRCALPHA)
            wisp.fill((*S.FOG, 38))
            surface.blit(wisp, ((fx - shift) % (S.WIDTH + 200) - 100, fy))
        return
    if area_type == "ice":
        surface.fill(S.ICE_SKY)
        shift = int(camera.offset_x * 0.3)
        for sx, sy in _STARS:                            # drifting snowflakes
            pygame.draw.circle(surface, S.CREAM, ((sx - shift) % S.WIDTH, sy), 2)
        return
    if area_type == "water":
        for i in range(0, S.HEIGHT, 8):                  # teal -> deep-blue depth gradient
            t = i / S.HEIGHT
            surface.fill((int(S.WATER_TOP[0] * (1 - t) + S.WATER_BOTTOM[0] * t),
                          int(S.WATER_TOP[1] * (1 - t) + S.WATER_BOTTOM[1] * t),
                          int(S.WATER_TOP[2] * (1 - t) + S.WATER_BOTTOM[2] * t)),
                         (0, i, S.WIDTH, 8))
        shift = int(camera.offset_x * 0.3)
        for bx, by, r in [(80, 200, 4), (220, 360, 3), (400, 140, 5), (560, 420, 3),
                          (720, 260, 4), (880, 330, 4), (300, 500, 3), (640, 90, 3)]:
            pygame.draw.circle(surface, S.BUBBLE, ((bx - shift) % S.WIDTH, by), r)
        return
    if area_type == "sky":
        for i in range(0, S.HEIGHT, 8):                  # dusk vertical gradient
            t = i / S.HEIGHT
            surface.fill((int(S.SKY_TOP[0] * (1 - t) + S.SKY_BOTTOM[0] * t),
                          int(S.SKY_TOP[1] * (1 - t) + S.SKY_BOTTOM[1] * t),
                          int(S.SKY_TOP[2] * (1 - t) + S.SKY_BOTTOM[2] * t)),
                         (0, i, S.WIDTH, 8))
        shift = int(camera.offset_x * 0.3)
        for cx, cy, r in [(120, 90, 24), (360, 58, 18), (640, 120, 28), (820, 76, 20), (500, 150, 16)]:
            x = (cx - shift) % (S.WIDTH + 160) - 80
            pygame.draw.ellipse(surface, S.CLOUD, (x, cy, r * 3, r))
            pygame.draw.ellipse(surface, S.CLOUD, (x + r, cy - r // 2, r * 2, r))
        return
    if area_type == "castle":
        surface.fill(S.CASTLE_BG)
        glow = pygame.Surface((S.WIDTH, 70), pygame.SRCALPHA)
        glow.fill((200, 70, 30, 45))                 # lava glow rising from below
        surface.blit(glow, (0, S.HEIGHT - 70))
        return
    if area_type == "underground":
        surface.fill(S.CAVE_BG)
        pygame.draw.rect(surface, S.CAVE_CEIL, (0, 0, S.WIDTH, 30))   # dim cave ceiling band
        return
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


def draw_block(surface, rect, kind, used=False, area_type="overworld"):
    if area_type == "castle":
        ground, edge = S.CASTLE_GROUND, S.CASTLE_EDGE
    elif area_type == "sky":
        ground, edge = S.SKY_GROUND, S.SKY_EDGE
    elif area_type == "water":
        ground, edge = S.SEABED, S.SEABED_EDGE
    elif area_type == "ice":
        ground, edge = S.ICE_GROUND, S.ICE_EDGE
    elif area_type == "haunted":
        ground, edge = S.HAUNT_GROUND, S.HAUNT_EDGE
    elif area_type == "underground":
        ground, edge = S.CAVE_GROUND, S.CAVE_EDGE
    else:
        ground, edge = S.GROUND_DARK, S.GROUND_EDGE
    if kind == "X":                       # solid ground
        pygame.draw.rect(surface, ground, rect)
        pygame.draw.rect(surface, edge, (rect.x, rect.y, rect.w, 4))
        pygame.draw.rect(surface, S.INK, rect, 1)
    elif kind == "=":                     # floating platform
        pygame.draw.rect(surface, ground, rect, border_radius=6)
        pygame.draw.rect(surface, edge, (rect.x + 3, rect.y + 2, rect.w - 6, 4))
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
    elif kind == "T":                     # pipe mouth
        draw_pipe(surface, rect, mouth=True)
    elif kind == "t":                     # pipe shaft
        draw_pipe(surface, rect, mouth=False)
    elif kind == "N":                     # cannon (Bill Blaster)
        draw_cannon(surface, rect)


def _burst(surface, cx, cy, R, color, width, step=30):
    for a in range(0, 360, step):
        rad = math.radians(a)
        pygame.draw.line(surface, color, (cx, cy), (cx + R * math.cos(rad), cy + R * math.sin(rad)), width)


def draw_player(surface, rect, facing=1, power="small"):
    """The Claude Spark Hero: a bold sunburst-spark head (the Anthropic mark) over a
    friendly orange body. Drawn relative to `rect`, so the big variant scales up."""
    w, h = rect.w, rect.h
    ox = int(2 * facing)
    body = pygame.Rect(rect.x + int(w * 0.12), rect.y + int(h * 0.44), int(w * 0.76), int(h * 0.44))
    # arms
    pygame.draw.rect(surface, S.ORANGE, (body.left - int(w*0.12), body.y + int(body.h*0.30), int(w*0.14), int(body.h*0.42)), border_radius=4)
    pygame.draw.rect(surface, S.ORANGE, (body.right - int(w*0.02), body.y + int(body.h*0.30), int(w*0.14), int(body.h*0.42)), border_radius=4)
    # legs
    pygame.draw.rect(surface, S.ORANGE, (body.centerx - int(w*0.20), body.bottom - 2, int(w*0.16), int(h*0.12)), border_radius=3)
    pygame.draw.rect(surface, S.ORANGE, (body.centerx + int(w*0.05), body.bottom - 2, int(w*0.16), int(h*0.12)), border_radius=3)
    # feet
    pygame.draw.ellipse(surface, S.INK, (body.left, rect.bottom - int(h*0.09), int(w*0.40), int(h*0.09)))
    pygame.draw.ellipse(surface, S.INK, (body.centerx, rect.bottom - int(h*0.09), int(w*0.40), int(h*0.09)))
    # body
    pygame.draw.rect(surface, S.ORANGE, body, border_radius=int(w*0.34))
    pygame.draw.rect(surface, S.INK, body, 2, border_radius=int(w*0.34))
    # face
    ey = body.y + int(body.h * 0.36)
    er = max(3, int(w * 0.14))
    for ex in (body.centerx - int(w*0.17) + ox, body.centerx + int(w*0.17) + ox):
        pygame.draw.circle(surface, S.CREAM, (ex, ey), er)
        pygame.draw.circle(surface, S.INK, (ex + ox, ey + 1), max(1, er // 2))
    sm = int(w * 0.17)
    smy = ey + int(h * 0.11)
    pygame.draw.lines(surface, S.INK, False,
                      [(body.centerx - sm + ox, smy), (body.centerx + ox, smy + 4), (body.centerx + sm + ox, smy)], 2)
    # bold sunburst spark head (the Claude identity)
    hx, hy = rect.centerx, rect.y + int(h * 0.17)
    R = int(w * 0.60) if power in ("big", "fire") else int(w * 0.56)
    spark = S.FIRE if power == "fire" else S.ORANGE
    pygame.draw.line(surface, spark, (hx, hy + int(w*0.24)), (hx, body.y), 3)   # neck
    _burst(surface, hx, hy, R, spark, 4)
    pygame.draw.circle(surface, spark, (hx, hy), max(7, int(w*0.30)))
    pygame.draw.circle(surface, S.INK, (hx, hy), max(7, int(w*0.30)), 2)
    pygame.draw.circle(surface, S.CREAM, (hx, hy), max(3, int(w*0.14)))


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


def draw_pipe(surface, rect, mouth):
    if mouth:
        body = pygame.Rect(rect.x, rect.y + 12, rect.w, rect.h - 12)
        pygame.draw.rect(surface, S.PIPE, body)
        pygame.draw.rect(surface, S.PIPE_DK, (body.right - 8, body.y, 8, body.h))
        rim = pygame.Rect(rect.x - 2, rect.y, rect.w + 4, 12)
        pygame.draw.rect(surface, S.PIPE, rim)
        pygame.draw.rect(surface, S.INK, rim, 2)
        pygame.draw.line(surface, S.CREAM, (rim.x + 4, rim.y + 3), (rim.right - 4, rim.y + 3), 2)
    else:
        pygame.draw.rect(surface, S.PIPE, rect)
        pygame.draw.rect(surface, S.PIPE_DK, (rect.right - 8, rect.y, 8, rect.h))
        pygame.draw.line(surface, S.CREAM, (rect.x + 4, rect.y), (rect.x + 4, rect.bottom), 2)


def draw_boo(surface, rect, frozen=False, facing=1):
    pygame.draw.ellipse(surface, S.CREAM, rect)
    pygame.draw.ellipse(surface, S.MIDGRAY, rect, 2)
    pygame.draw.circle(surface, S.CREAM, (rect.left + 7, rect.bottom - 3), 5)     # wavy tail
    pygame.draw.circle(surface, S.CREAM, (rect.centerx, rect.bottom - 2), 5)
    pygame.draw.circle(surface, S.CREAM, (rect.right - 7, rect.bottom - 3), 5)
    if frozen:
        for ex in (rect.centerx - 7, rect.centerx + 7):                            # hands over face (shy)
            pygame.draw.circle(surface, S.LIGHTGRAY, (ex, rect.centery), 5)
            pygame.draw.circle(surface, S.INK, (ex, rect.centery), 5, 1)
    else:
        ox = 2 * facing
        for ex in (rect.centerx - 6 + ox, rect.centerx + 6 + ox):                  # eyes
            pygame.draw.circle(surface, S.INK, (ex, rect.centery - 2), 3)
        pygame.draw.arc(surface, S.INK, pygame.Rect(rect.centerx - 8, rect.centery + 2, 16, 10), 3.4, 6.0, 2)


def draw_frostbite(surface, rect, direction=1):
    pygame.draw.ellipse(surface, S.SNOW, rect)
    pygame.draw.ellipse(surface, S.INK, rect, 2)
    for i in range(3):                                   # ice spikes on top (don't stomp!)
        sx = rect.left + 7 + i * (rect.w - 14) // 2
        spike = [(sx - 4, rect.top + 5), (sx + 4, rect.top + 5), (sx, rect.top - 6)]
        pygame.draw.polygon(surface, S.ICE_EDGE, spike)
        pygame.draw.polygon(surface, S.BLUE, spike, 1)
    for ex in (rect.centerx - 6, rect.centerx + 6):
        pygame.draw.circle(surface, S.INK, (ex, rect.centery + 2), 2)
    pygame.draw.ellipse(surface, S.BLUE, (rect.left + 2, rect.bottom - 5, rect.w // 2 - 3, 5))
    pygame.draw.ellipse(surface, S.BLUE, (rect.centerx + 1, rect.bottom - 5, rect.w // 2 - 3, 5))


def draw_cheep(surface, rect, direction=1):
    pygame.draw.ellipse(surface, S.CHEEP_COLOR, rect)
    pygame.draw.ellipse(surface, S.INK, rect, 2)
    if direction > 0:                                  # tail trails behind
        tail = [(rect.left + 2, rect.centery), (rect.left - 8, rect.top + 2), (rect.left - 8, rect.bottom - 2)]
    else:
        tail = [(rect.right - 2, rect.centery), (rect.right + 8, rect.top + 2), (rect.right + 8, rect.bottom - 2)]
    pygame.draw.polygon(surface, S.CHEEP_COLOR, tail)
    pygame.draw.polygon(surface, S.INK, tail, 1)
    ex = rect.right - 8 if direction > 0 else rect.left + 8
    pygame.draw.circle(surface, S.CREAM, (ex, rect.centery - 2), 3)
    pygame.draw.circle(surface, S.INK, (ex, rect.centery - 2), 1)


def draw_cannon(surface, rect):
    pygame.draw.rect(surface, S.CANNON, rect, border_radius=3)
    pygame.draw.rect(surface, S.INK, rect, 2, border_radius=3)
    pygame.draw.circle(surface, S.MIDGRAY, (rect.centerx, rect.y + 9), 6)   # bore
    pygame.draw.circle(surface, S.INK, (rect.centerx, rect.y + 9), 6, 2)


def draw_bullet(surface, rect, direction=1):
    pygame.draw.ellipse(surface, S.INK, rect)
    pygame.draw.ellipse(surface, S.MIDGRAY, rect, 2)
    nose = rect.right - 4 if direction > 0 else rect.left + 4
    pygame.draw.circle(surface, S.MIDGRAY, (nose, rect.centery), 3)         # nose glint
    ex = rect.centerx - 4 * direction
    pygame.draw.circle(surface, S.CREAM, (ex, rect.centery), 3)             # eye
    pygame.draw.circle(surface, S.INK, (ex, rect.centery), 1)
    # little fins at the tail
    tail = rect.left + 2 if direction > 0 else rect.right - 2
    pygame.draw.line(surface, S.MIDGRAY, (tail, rect.top + 4), (tail, rect.bottom - 4), 2)


def draw_koopa(surface, rect, state="walk", direction=1):
    # shell occupies the lower band when walking (head/feet show above-front)
    shell = pygame.Rect(rect.x, rect.y + (5 if state == "walk" else 0),
                        rect.w, rect.h - (5 if state == "walk" else 0))
    if state == "walk":
        hx = rect.right - 3 if direction > 0 else rect.left + 3
        pygame.draw.circle(surface, S.CREAM, (hx, rect.y + 7), 6)
        pygame.draw.circle(surface, S.INK, (hx, rect.y + 7), 6, 1)
        pygame.draw.circle(surface, S.INK, (hx + direction * 2, rect.y + 6), 1)   # eye
        pygame.draw.ellipse(surface, S.SAGE, (rect.left, rect.bottom - 5, rect.w // 2 - 1, 5))
        pygame.draw.ellipse(surface, S.SAGE, (rect.centerx + 1, rect.bottom - 5, rect.w // 2 - 1, 5))
    pygame.draw.ellipse(surface, S.KOOPA_SHELL, shell)
    pygame.draw.ellipse(surface, S.MIDGRAY, shell, 1)        # light rim for night visibility
    pygame.draw.ellipse(surface, S.INK, shell, 2)
    pygame.draw.ellipse(surface, S.CREAM, shell.inflate(-shell.w // 2, -shell.h // 2))   # shell hub
    if state == "slide":
        pygame.draw.line(surface, S.INK, (shell.left + 3, shell.centery),
                         (shell.right - 3, shell.centery), 1)    # spin streak


def draw_lava(surface, rect):
    pygame.draw.rect(surface, S.LAVA, rect)
    pygame.draw.rect(surface, S.LAVA_GLOW, (rect.x, rect.y, rect.w, 5))    # bright molten surface
    pygame.draw.circle(surface, S.LAVA_GLOW, (rect.x + 12, rect.y + 16), 3)
    pygame.draw.circle(surface, S.LAVA_GLOW, (rect.right - 13, rect.y + 24), 2)


def draw_boss_shot(surface, rect):
    c = rect.center
    pygame.draw.circle(surface, S.INK, c, rect.w // 2)
    pygame.draw.circle(surface, S.FIRE, c, rect.w // 2 - 2)
    pygame.draw.circle(surface, S.LAVA_GLOW, c, max(2, rect.w // 2 - 6))


def draw_boss(surface, rect, direction=1, flashing=False):
    shell = pygame.Rect(rect.x, rect.y + 12, rect.w, rect.h - 12)
    dome = S.CREAM if flashing else S.KOOPA_SHELL
    # angry head poking forward
    hx = rect.right - 12 if direction > 0 else rect.left + 12
    pygame.draw.circle(surface, S.SAGE, (hx, rect.y + 18), 12)
    pygame.draw.circle(surface, S.INK, (hx, rect.y + 18), 12, 2)
    ex = hx + 4 * direction
    pygame.draw.circle(surface, S.CREAM, (ex, rect.y + 15), 4)
    pygame.draw.circle(surface, S.INK, (ex, rect.y + 15), 2)
    pygame.draw.line(surface, S.INK, (hx - 7, rect.y + 8), (hx + 7, rect.y + 12), 3)   # brow
    # armored shell dome
    pygame.draw.ellipse(surface, dome, shell)
    pygame.draw.ellipse(surface, S.INK, shell, 3)
    # spikes
    for i in range(4):
        sx = shell.left + 10 + i * (shell.w - 20) // 3
        spike = [(sx - 6, shell.top + 7), (sx + 6, shell.top + 7), (sx, shell.top - 8)]
        pygame.draw.polygon(surface, S.MIDGRAY, spike)
        pygame.draw.polygon(surface, S.INK, spike, 1)
    # feet
    pygame.draw.ellipse(surface, S.SAGE, (rect.left + 5, rect.bottom - 8, rect.w // 2 - 7, 8))
    pygame.draw.ellipse(surface, S.SAGE, (rect.centerx + 4, rect.bottom - 8, rect.w // 2 - 7, 8))


def draw_flag(surface, rect):
    pole = pygame.Rect(rect.centerx - 3, rect.top, 6, rect.h)
    pygame.draw.rect(surface, S.CREAM, pole)                # cream so it shows on the night sky
    pygame.draw.rect(surface, S.INK, pole, 1)
    pygame.draw.circle(surface, S.BLUE, (rect.centerx, rect.top), 6)
    pts = [(rect.centerx + 3, rect.top + 6),
           (rect.centerx + 30, rect.top + 14),
           (rect.centerx + 3, rect.top + 22)]
    pygame.draw.polygon(surface, S.ORANGE, pts)


def draw_mushroom(surface, rect):
    cap = pygame.Rect(rect.x, rect.y, rect.w, int(rect.h * 0.6))
    stem = pygame.Rect(rect.x + rect.w // 4, rect.centery, rect.w // 2, rect.h // 2)
    pygame.draw.rect(surface, S.CREAM, stem, border_radius=3)
    pygame.draw.rect(surface, S.INK, stem, 2, border_radius=3)
    pygame.draw.ellipse(surface, S.ORANGE, cap)
    pygame.draw.ellipse(surface, S.INK, cap, 2)
    pygame.draw.circle(surface, S.CREAM, (cap.centerx, cap.centery), 4)
    pygame.draw.circle(surface, S.CREAM, (cap.left + 7, cap.centery + 3), 3)
    pygame.draw.circle(surface, S.CREAM, (cap.right - 7, cap.centery + 3), 3)


def draw_flyer(surface, rect):
    body = rect.inflate(-rect.w // 4, 0)
    pygame.draw.polygon(surface, S.MIDGRAY, [(rect.left, rect.centery), (body.left, rect.top), (body.left, rect.bottom)])
    pygame.draw.polygon(surface, S.MIDGRAY, [(rect.right, rect.centery), (body.right, rect.top), (body.right, rect.bottom)])
    pygame.draw.ellipse(surface, S.BLUE, body)
    pygame.draw.ellipse(surface, S.INK, body, 2)
    for ex in (body.centerx - 5, body.centerx + 5):
        pygame.draw.circle(surface, S.CREAM, (ex, rect.centery - 2), 3)
        pygame.draw.circle(surface, S.INK, (ex, rect.centery - 2), 1)


def draw_fireflower(surface, rect):
    stem = pygame.Rect(rect.centerx - 2, rect.centery, 4, rect.h // 2)
    pygame.draw.rect(surface, S.SAGE, stem)
    cx, cy, r = rect.centerx, rect.y + rect.h // 3, max(4, rect.w // 3)
    for a in range(0, 360, 60):
        rad = math.radians(a)
        pygame.draw.circle(surface, S.FIRE, (int(cx + r * math.cos(rad)), int(cy + r * math.sin(rad))), r)
    pygame.draw.circle(surface, S.CREAM, (cx, cy), max(2, r // 2))
    pygame.draw.circle(surface, S.INK, (cx, cy), max(2, r // 2), 1)


def draw_fireball(surface, rect):
    cx, cy = rect.center
    r = rect.w // 2
    pygame.draw.circle(surface, S.FIRE, (cx, cy), r)
    pygame.draw.circle(surface, S.ORANGE, (cx, cy), max(2, r * 2 // 3))
    pygame.draw.circle(surface, S.CREAM, (cx, cy), max(1, r // 3))
