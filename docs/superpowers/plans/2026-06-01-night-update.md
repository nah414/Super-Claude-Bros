# Super Claude Bros — Night Update — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the Spark Hero mascot, a moonlit dark theme, a double-jump, mushroom/token power-up boxes, a Flyer enemy, score pop-ups + bonus lives, and synthesized sound — then update the icon and rebuild the app.

**Architecture:** Extend the existing OOP engine. New world objects (`Mushroom`, `Flyer`) follow the `Entity` pattern; all visuals go through `assets.py`; pure logic (double-jump timing, power transitions, scoring) lives in testable methods/modules; sound and effects are isolated modules that degrade gracefully.

**Tech Stack:** Python 3.13, Pygame 2.6, numpy (sound), pytest.

**Reference spec:** `docs/superpowers/specs/2026-06-01-night-update-design.md`

**Conventions:** run tests with `PYTHONPATH=<repo> SDL_VIDEODRIVER=dummy python -m pytest`. Headless smokes set `SDL_VIDEODRIVER=dummy` and `SDL_AUDIODRIVER=dummy`. Commit messages end with the `Co-Authored-By` trailer.

---

## Task 1: Night theme — palette, constants, background, dark blocks, HUD

**Files:**
- Modify: `game/settings.py` (all new constants + night palette)
- Modify: `game/assets.py` (`draw_background`, dark `draw_block`)
- Modify: `game/hud.py` (dark bar)
- Modify: `game/game.py` (`draw` calls `draw_background`)

- [ ] **Step 1: Append constants to `game/settings.py`** (after the existing `PIT_DEATH_Y` line, before `resource_path`)

```python
# --- Night theme ---
NIGHT       = (20, 20, 19)      # sky / background (#141413)
GROUND_DARK = (40, 46, 36)      # ground / platform fill
GROUND_EDGE = (72, 86, 58)      # lit top edge
BRICK_DARK  = (74, 72, 66)
MOON        = (232, 230, 210)

# --- Double-jump ---
DOUBLE_TAP_MS        = 300
DOUBLE_JUMP_VELOCITY = -12.0

# --- Player power sizes ---
PLAYER_SMALL    = (30, 44)
PLAYER_BIG      = (38, 62)
POWER_INVULN_MS = 1500

# --- Mushroom ---
MUSHROOM_SPEED = 1.6
MUSHROOM_SCORE = 1000

# --- Flyer ---
FLYER_SPEED      = 1.8
FLYER_BOB_AMP    = 12
FLYER_BOB_PERIOD = 90
FLYER_RANGE      = 120
FLYER_SCORE      = 200

# --- Scoring ---
TOKEN_SCORE      = 100
STOMP_SCORE      = 200
BONUS_LIFE_EVERY = 100

# --- Audio ---
SAMPLE_RATE = 44100
```

- [ ] **Step 2: Add `draw_background` and dark-theme blocks to `game/assets.py`**

Add a module-level starfield and the function (append near the top after imports):

```python
# fixed star positions (screen space), gently parallaxed by the camera
_STARS = [(57, 60), (140, 38), (210, 90), (320, 50), (440, 110), (560, 44),
          (640, 95), (740, 70), (840, 36), (900, 120), (480, 150), (260, 150)]


def draw_background(surface, camera):
    surface.fill(S.NIGHT)
    pygame.draw.circle(surface, S.MOON, (S.WIDTH - 90, 90), 34)
    pygame.draw.circle(surface, S.NIGHT, (S.WIDTH - 78, 82), 30)  # crescent bite
    shift = int(camera.offset_x * 0.3)
    for sx, sy in _STARS:
        x = (sx - shift) % S.WIDTH
        pygame.draw.circle(surface, S.CREAM, (x, sy), 2)
```

Replace the `draw_block` body's `kind == "X"`, `"="`, `"B"`, and `"?"` branches so it reads:

```python
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
        pygame.draw.line(surface, S.INK, (rect.left, rect.centery), (rect.right, rect.centery), 1)
        pygame.draw.line(surface, S.INK, (rect.centerx, rect.top), (rect.centerx, rect.centery), 1)
    elif kind in ("?", "M"):              # mystery box (M looks identical to ?)
        pygame.draw.rect(surface, S.MIDGRAY if used else S.BLUE, rect, border_radius=4)
        pygame.draw.rect(surface, S.INK, rect, 2, border_radius=4)
        if not used:
            q = _question_font().render("?", True, S.CREAM)
            surface.blit(q, q.get_rect(center=rect.center))
```

- [ ] **Step 3: Dark HUD bar — replace the body of `HUD.draw` in `game/hud.py`**

```python
    def draw(self, surface, score, sparks, lives):
        bar = pygame.Surface((S.WIDTH, 40), pygame.SRCALPHA)
        bar.fill((20, 20, 19, 190))
        surface.blit(bar, (0, 0))
        pygame.draw.line(surface, S.GROUND_EDGE, (0, 40), (S.WIDTH, 40), 2)
        text = f"SCORE {score:06d}    SPARKS {sparks:02d}    LIVES {lives}    WORLD 1-1"
        surface.blit(self.font.render(text, True, S.CREAM), (16, 8))
```

- [ ] **Step 4: In `game/game.py`, replace `self.screen.fill(S.CREAM)` in `draw()`** with:

```python
        from game import assets
        assets.draw_background(self.screen, self.camera)
```

(Place it as the first line of `draw()`.)

- [ ] **Step 5: Headless smoke**

Run:
```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy PYGAME_HIDE_SUPPORT_PROMPT=1 PYTHONPATH=. python -c "import pygame; from game.game import Game; g=Game(); [ (g.update(), g.draw()) for _ in range(30)]; print('THEME OK')"
```
Expected: prints `THEME OK` with no error.

- [ ] **Step 6: Commit**

```bash
git add game/settings.py game/assets.py game/hud.py game/game.py
git commit -m "feat: moonlit dark theme + all night-update constants"
```

---

## Task 2: Spark Hero mascot art

**Files:**
- Modify: `game/assets.py` (`draw_player` → Spark Hero, rect-relative)
- Modify: `game/entities/player.py` (use `PLAYER_SMALL` size; pass `power` to draw)

- [ ] **Step 1: Replace `draw_player` in `game/assets.py`**

```python
def draw_player(surface, rect, facing=1, power="small"):
    w, h = rect.w, rect.h
    ox = int(2 * facing)
    # body (lower ~55%)
    body = pygame.Rect(rect.x + int(w * 0.10), rect.y + int(h * 0.42),
                       int(w * 0.80), int(h * 0.46))
    # legs + feet
    fy = body.bottom
    pygame.draw.rect(surface, S.ORANGE, (body.centerx - int(w*0.22), fy - 2, int(w*0.16), int(h*0.12)), border_radius=3)
    pygame.draw.rect(surface, S.ORANGE, (body.centerx + int(w*0.06), fy - 2, int(w*0.16), int(h*0.12)), border_radius=3)
    pygame.draw.ellipse(surface, S.INK, (body.left - 2, rect.bottom - int(h*0.10), int(w*0.40), int(h*0.10)))
    pygame.draw.ellipse(surface, S.INK, (body.centerx + 1, rect.bottom - int(h*0.10), int(w*0.40), int(h*0.10)))
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
    # sunburst head above the body
    hx, hy = rect.centerx, rect.y + int(h * 0.22)
    R = int(w * 0.42) if power == "big" else int(w * 0.38)
    for a in range(0, 360, 30):
        rad = math.radians(a)
        pygame.draw.line(surface, S.ORANGE, (hx, hy), (hx + R*math.cos(rad), hy + R*math.sin(rad)), 3)
    pygame.draw.circle(surface, S.ORANGE, (hx, hy), max(5, int(w*0.26)))
    pygame.draw.circle(surface, S.INK, (hx, hy), max(5, int(w*0.26)), 2)
    pygame.draw.circle(surface, S.CREAM, (hx, hy), max(2, int(w*0.11)))
    # neck
    pygame.draw.line(surface, S.ORANGE, (hx, hy + int(w*0.26)), (hx, body.y), 4)
```

- [ ] **Step 2: In `game/entities/player.py`, use the size constant.** Replace the `super().__init__(...)` line in `Player.__init__` with:

```python
        super().__init__(x, y, S.PLAYER_SMALL[0], S.PLAYER_SMALL[1])
```

And replace the `draw` method with (passes `power`):

```python
    def draw(self, surface, camera):
        assets.draw_player(surface, camera.apply(self.rect), self.facing, self.power)
```

- [ ] **Step 3: Visual check (render the sprite to a PNG and inspect)**

Run:
```bash
SDL_VIDEODRIVER=dummy PYGAME_HIDE_SUPPORT_PROMPT=1 PYTHONPATH=. python -c "import pygame; pygame.init(); from game import assets, settings as S; s=pygame.Surface((120,160)); s.fill(S.NIGHT); import pygame as p; assets.draw_player(s, p.Rect(45,55,S.PLAYER_SMALL[0],S.PLAYER_SMALL[1]), 1, 'small'); pygame.image.save(s, 'tools/_preview/hero_small.png'); print('saved')"
```
Then open `tools/_preview/hero_small.png`. Tune the proportions in `draw_player` if needed. Expected: a recognizable Spark Hero (sunburst head, body, face, legs).

- [ ] **Step 4: Commit**

```bash
git add game/assets.py game/entities/player.py
git commit -m "feat: Spark Hero mascot art"
```

---

## Task 3: Double-jump (TDD)

**Files:**
- Create: `tests/test_player_jump.py`
- Modify: `game/entities/player.py` (jump methods + state + reset)
- Modify: `game/game.py` (wire `press_jump`/`release_jump`)

- [ ] **Step 1: Write the failing test** — `tests/test_player_jump.py`

```python
import pygame
from game import settings as S
from game.entities.player import Player


def test_double_tap_gives_one_air_jump():
    p = Player(0, 0); p.on_ground = True
    p.press_jump(1000)                      # ground jump
    assert p.vy == S.JUMP_VELOCITY and p.air_jumped is False
    p.on_ground = False
    p.press_jump(1200)                      # 200ms later -> double jump
    assert p.vy == S.DOUBLE_JUMP_VELOCITY and p.air_jumped is True
    p.press_jump(1300)                      # already used -> ignored
    assert p.vy == S.DOUBLE_JUMP_VELOCITY


def test_late_tap_does_not_double_jump():
    p = Player(0, 0); p.on_ground = True
    p.press_jump(2000)
    p.on_ground = False
    p.press_jump(2500)                      # 500ms > window -> no double jump
    assert p.vy == S.JUMP_VELOCITY
```

- [ ] **Step 2: Run to verify it fails**

Run: `SDL_VIDEODRIVER=dummy PYTHONPATH=. python -m pytest tests/test_player_jump.py -v`
Expected: FAIL (`AttributeError: 'Player' object has no attribute 'press_jump'`).

- [ ] **Step 3: Implement in `game/entities/player.py`.** In `__init__` add (after `self.power = "small"`):

```python
        self.air_jumped = False
        self.last_jump_ms = -100000
        self.invuln_until = 0
```

Replace `start_jump`/`end_jump` with:

```python
    def press_jump(self, now_ms):
        gap = now_ms - self.last_jump_ms
        self.last_jump_ms = now_ms
        if self.on_ground:
            self.vy = S.JUMP_VELOCITY
            self.on_ground = False
            self.air_jumped = False
        elif not self.air_jumped and gap <= S.DOUBLE_TAP_MS:
            self.vy = S.DOUBLE_JUMP_VELOCITY
            self.air_jumped = True

    def release_jump(self):
        if self.vy < S.JUMP_CUTOFF:
            self.vy = S.JUMP_CUTOFF
```

In `update`, after computing `self.on_ground = contacts["bottom"]`, add:

```python
        if self.on_ground:
            self.air_jumped = False
```

- [ ] **Step 4: Run to verify it passes**

Run: `SDL_VIDEODRIVER=dummy PYTHONPATH=. python -m pytest tests/test_player_jump.py -v`
Expected: 2 passed.

- [ ] **Step 5: Wire into `game/game.py` events.** In `handle_events`, replace the jump KEYDOWN/KEYUP calls:

```python
                elif event.key in JUMP_KEYS and self.state == "PLAYING":
                    self.player.press_jump(pygame.time.get_ticks())
```
```python
            elif event.type == pygame.KEYUP:
                if event.key in JUMP_KEYS and self.state == "PLAYING":
                    self.player.release_jump()
```

- [ ] **Step 6: Commit**

```bash
git add tests/test_player_jump.py game/entities/player.py game/game.py
git commit -m "feat: double-jump on fast double-tap (tested)"
```

---

## Task 4: Power state — grow / take_damage (TDD)

**Files:**
- Create: `tests/test_player_power.py`
- Modify: `game/entities/player.py` (`grow`, `take_damage`, invuln flicker draw)

- [ ] **Step 1: Write the failing test** — `tests/test_player_power.py`

```python
from game import settings as S
from game.entities.player import Player


def test_grow_makes_big():
    p = Player(0, 100)
    assert p.power == "small" and p.h == S.PLAYER_SMALL[1]
    p.grow()
    assert p.power == "big" and (p.w, p.h) == S.PLAYER_BIG


def test_big_hit_shrinks_then_invulnerable():
    p = Player(0, 100); p.grow()
    assert p.take_damage(1000) is False        # shrinks, no life lost
    assert p.power == "small" and p.invuln_until == 1000 + S.POWER_INVULN_MS
    assert p.take_damage(1100) is False         # still invulnerable -> ignored


def test_small_hit_costs_life_after_invuln():
    p = Player(0, 100)
    assert p.take_damage(5000) is True          # small + vulnerable -> life lost
```

- [ ] **Step 2: Run to verify it fails**

Run: `SDL_VIDEODRIVER=dummy PYTHONPATH=. python -m pytest tests/test_player_power.py -v`
Expected: FAIL (`AttributeError: ... 'grow'`).

- [ ] **Step 3: Implement in `game/entities/player.py`** (add methods):

```python
    def grow(self):
        if self.power == "small":
            old_h = self.h
            self.w, self.h = S.PLAYER_BIG
            self.y -= (self.h - old_h)          # keep feet planted
            self.power = "big"

    def take_damage(self, now_ms):
        if now_ms < self.invuln_until:
            return False                         # invulnerable: ignore
        if self.power == "big":
            old_h = self.h
            self.w, self.h = S.PLAYER_SMALL
            self.y += (old_h - self.h)
            self.power = "small"
            self.invuln_until = now_ms + S.POWER_INVULN_MS
            return False                         # shrank, no life lost
        return True                              # life lost
```

Replace `draw` to flicker while invulnerable:

```python
    def draw(self, surface, camera):
        if pygame.time.get_ticks() < self.invuln_until and (pygame.time.get_ticks() // 100) % 2 == 0:
            return                               # flicker: skip this frame
        assets.draw_player(surface, camera.apply(self.rect), self.facing, self.power)
```

- [ ] **Step 4: Run to verify it passes**

Run: `SDL_VIDEODRIVER=dummy PYTHONPATH=. python -m pytest tests/test_player_power.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add tests/test_player_power.py game/entities/player.py
git commit -m "feat: player grow + one-hit shield with invulnerability (tested)"
```

---

## Task 5: Scoring — bonus lives (TDD)

**Files:**
- Create: `game/scoring.py`, `tests/test_scoring.py`

- [ ] **Step 1: Write the failing test** — `tests/test_scoring.py`

```python
from game.scoring import bonus_lives


def test_bonus_lives():
    assert bonus_lives(99, 100) == 1
    assert bonus_lives(100, 101) == 0
    assert bonus_lives(95, 205) == 2
    assert bonus_lives(0, 0) == 0
```

- [ ] **Step 2: Run to verify it fails**

Run: `PYTHONPATH=. python -m pytest tests/test_scoring.py -v`
Expected: FAIL (no module `game.scoring`).

- [ ] **Step 3: Implement `game/scoring.py`**

```python
"""Pure scoring helpers."""
from game import settings as S


def bonus_lives(old_tokens, new_tokens, every=S.BONUS_LIFE_EVERY):
    """How many life thresholds were crossed going from old_tokens to new_tokens."""
    return new_tokens // every - old_tokens // every
```

- [ ] **Step 4: Run to verify it passes**

Run: `PYTHONPATH=. python -m pytest tests/test_scoring.py -v`
Expected: 1 passed.

- [ ] **Step 5: Commit**

```bash
git add game/scoring.py tests/test_scoring.py
git commit -m "feat: bonus-life scoring helper (tested)"
```

---

## Task 6: Mushroom + Flyer entities, level parsing (TDD), and their art

**Files:**
- Create: `game/entities/mushroom.py`, `game/entities/flyer.py`
- Modify: `game/entities/block.py` (`SOLID_KINDS` adds `"M"`)
- Modify: `game/assets.py` (`draw_mushroom`, `draw_flyer`)
- Modify: `game/level.py` (parse `M`, `Y`; add `powerups` list isn't needed here — handled in game)
- Modify: `tests/test_level.py` (assert `M`/`Y`)

- [ ] **Step 1: `SOLID_KINDS` in `game/entities/block.py`** — replace its definition with:

```python
SOLID_KINDS = ("X", "=", "B", "?", "M")
```

- [ ] **Step 2: Create `game/entities/mushroom.py`**

```python
import math
from game import settings as S
from game import assets
from game.physics import move_and_collide
from game.entities.entity import Entity


class Mushroom(Entity):
    """Rises out of an 'M' box, then walks, reversing at walls. Grows the player."""

    def __init__(self, box_x, box_y):
        size = S.TILE - 8
        super().__init__(box_x + 4, box_y, size, size)
        self.target_y = box_y - size          # rise one mushroom-height out of the box
        self.emerging = True
        self.direction = 1
        self.score = S.MUSHROOM_SCORE

    def update(self, level):
        if self.emerging:
            self.y -= 2.0
            if self.y <= self.target_y:
                self.y = self.target_y
                self.emerging = False
            return
        self.vx = S.MUSHROOM_SPEED * self.direction
        self.vy = min(self.vy + S.GRAVITY, S.MAX_FALL)
        c = move_and_collide(self, level.solids)
        if c["left"] or c["right"]:
            self.direction *= -1

    def draw(self, surface, camera):
        assets.draw_mushroom(surface, camera.apply(self.rect))
```

- [ ] **Step 3: Create `game/entities/flyer.py`**

```python
import math
from game import settings as S
from game import assets
from game.entities.entity import Entity


class Flyer(Entity):
    """Hovering enemy: drifts horizontally, bobs vertically, ignores gravity. Stompable."""

    def __init__(self, x, y):
        super().__init__(x + 4, y + 4, S.TILE - 8, S.TILE - 12)
        self.origin_x = float(x + 4)
        self.base_y = float(y + 4)
        self.direction = -1
        self.phase = 0
        self.score = S.FLYER_SCORE

    def update(self, level):
        self.phase += 1
        self.x += S.FLYER_SPEED * self.direction
        if abs(self.x - self.origin_x) >= S.FLYER_RANGE:
            self.direction *= -1
        self.y = self.base_y + S.FLYER_BOB_AMP * math.sin(self.phase * 2 * math.pi / S.FLYER_BOB_PERIOD)

    def draw(self, surface, camera):
        assets.draw_flyer(surface, camera.apply(self.rect))
```

- [ ] **Step 4: Add art to `game/assets.py`**

```python
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
    # wings
    pygame.draw.polygon(surface, S.MIDGRAY, [(rect.left, rect.centery), (body.left, rect.top), (body.left, rect.bottom)])
    pygame.draw.polygon(surface, S.MIDGRAY, [(rect.right, rect.centery), (body.right, rect.top), (body.right, rect.bottom)])
    pygame.draw.ellipse(surface, S.BLUE, body)
    pygame.draw.ellipse(surface, S.INK, body, 2)
    for ex in (body.centerx - 5, body.centerx + 5):
        pygame.draw.circle(surface, S.CREAM, (ex, rect.centery - 2), 3)
        pygame.draw.circle(surface, S.INK, (ex, rect.centery - 2), 1)
```

- [ ] **Step 5: Parse `M`/`Y` in `game/level.py`.** Add imports at top:

```python
from game.entities.flyer import Flyer
```

In `_load`, the `if ch in SOLID_KINDS:` branch already creates `Block(x, y, ch)` (so `M` becomes a solid block). Add a `Y` case alongside the others:

```python
                elif ch == "Y":
                    self.enemies.append(Flyer(x, y))
```

- [ ] **Step 6: Extend `tests/test_level.py`** — add:

```python
def test_parses_mushroom_box_and_flyer(tmp_path):
    p = tmp_path / "lvl.txt"
    p.write_text("..M..\n..Y..\nP...F\nXXXXX\n")
    level = Level(str(p))
    kinds = [b.kind for b in level.blocks]
    assert "M" in kinds                          # mushroom box is a solid block
    from game.entities.flyer import Flyer
    assert any(isinstance(e, Flyer) for e in level.enemies)
```

- [ ] **Step 7: Run tests**

Run: `SDL_VIDEODRIVER=dummy PYTHONPATH=. python -m pytest tests/test_level.py -v`
Expected: both level tests pass.

- [ ] **Step 8: Commit**

```bash
git add game/entities/mushroom.py game/entities/flyer.py game/entities/block.py game/assets.py game/level.py tests/test_level.py
git commit -m "feat: Mushroom + Flyer entities, M/Y tiles, their art (tested)"
```

---

## Task 7: Effects — score pop-ups + rising token

**Files:**
- Create: `game/effects.py`

- [ ] **Step 1: Create `game/effects.py`**

```python
import pygame
from game import settings as S
from game import assets


class ScorePopup:
    """Floating text that rises and fades at a world position."""
    LIFE = 42

    def __init__(self, x, y, text):
        self.x = float(x); self.y = float(y); self.text = text
        self.age = 0; self.alive = True

    def update(self):
        self.y -= 0.8; self.age += 1
        if self.age >= self.LIFE:
            self.alive = False

    def draw(self, surface, camera, font):
        img = font.render(self.text, True, S.CREAM)
        img.set_alpha(max(0, 255 - int(255 * self.age / self.LIFE)))
        surface.blit(img, img.get_rect(center=(round(self.x) - camera.offset_x, round(self.y))))


class RisingToken:
    """A spark that pops out of a '?' box, rises, and fades."""
    LIFE = 22

    def __init__(self, x, y):
        self.x = float(x); self.y = float(y); self.age = 0; self.alive = True

    def update(self):
        self.y -= 2.4; self.age += 1
        if self.age >= self.LIFE:
            self.alive = False

    def draw(self, surface, camera, font=None):
        r = pygame.Rect(round(self.x) - camera.offset_x - 8, round(self.y) - 8, 16, 16)
        assets.draw_coin(surface, r)
```

- [ ] **Step 2: Smoke**

Run:
```bash
SDL_VIDEODRIVER=dummy PYGAME_HIDE_SUPPORT_PROMPT=1 PYTHONPATH=. python -c "import pygame; pygame.init(); from game.effects import ScorePopup, RisingToken; from game.camera import Camera; from game import settings as S; f=pygame.font.SysFont('Arial',20); s=pygame.Surface((200,200)); cam=Camera(2000); pp=ScorePopup(50,50,'+200'); rt=RisingToken(60,60); [ (pp.update(), rt.update(), pp.draw(s,cam,f), rt.draw(s,cam)) for _ in range(5)]; print('EFFECTS OK')"
```
Expected: prints `EFFECTS OK`.

- [ ] **Step 3: Commit**

```bash
git add game/effects.py
git commit -m "feat: score pop-ups and rising-token effects"
```

---

## Task 8: Sound — synthesized SFX with graceful fallback

**Files:**
- Create: `game/sound.py`
- Modify: `requirements.txt` (add `numpy`)

- [ ] **Step 1: Add `numpy` to `requirements.txt`** (append a line):

```
numpy>=1.26
```

- [ ] **Step 2: Create `game/sound.py`**

```python
"""Synthesized sound effects. Degrades to silent no-ops if audio/numpy is unavailable."""
import pygame
from game import settings as S

try:
    import numpy as np
except Exception:
    np = None


class SoundFX:
    def __init__(self):
        self.enabled = False
        self.sounds = {}
        if np is None:
            return
        try:
            pygame.mixer.pre_init(S.SAMPLE_RATE, -16, 1)
            pygame.mixer.init()
            self._build()
            self.enabled = True
        except Exception:
            self.enabled = False

    def _tone(self, freqs, dur=0.12, vol=0.35):
        n = int(S.SAMPLE_RATE * dur)
        t = np.linspace(0, dur, n, False)
        wave = sum(np.sin(2 * np.pi * f * t) for f in freqs) / len(freqs)
        wave *= np.linspace(1, 0, n) ** 1.5            # decay envelope
        return pygame.sndarray.make_sound((wave * vol * 32767).astype(np.int16))

    def _build(self):
        self.sounds = {
            "jump":   self._tone([440, 660], 0.12),
            "double": self._tone([660, 990], 0.12),
            "token":  self._tone([880, 1320], 0.09),
            "stomp":  self._tone([320, 180], 0.12),
            "power":  self._tone([523, 659, 784], 0.22),
            "hurt":   self._tone([392, 233], 0.22),
            "win":    self._tone([523, 659, 784, 1047], 0.40),
        }

    def play(self, name):
        if not self.enabled:
            return
        s = self.sounds.get(name)
        if s:
            s.play()
```

- [ ] **Step 3: Smoke (must be safe even with no audio device)**

Run:
```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy PYGAME_HIDE_SUPPORT_PROMPT=1 PYTHONPATH=. python -c "import pygame; pygame.init(); from game.sound import SoundFX; s=SoundFX(); s.play('jump'); s.play('win'); print('SOUND OK enabled=', s.enabled)"
```
Expected: prints `SOUND OK enabled= ...` (True or False) with no crash.

- [ ] **Step 4: Commit**

```bash
git add game/sound.py requirements.txt
git commit -m "feat: synthesized sound effects with graceful fallback"
```

---

## Task 9: Integration — boxes, power-ups, damage, flyers, pop-ups, bonus life, sound

**Files:**
- Modify: `game/game.py` (the orchestration)

- [ ] **Step 1: Replace `game/game.py` entirely** with the integrated version:

```python
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
```

- [ ] **Step 2: Full integrated smoke** (drives boxes, mushroom, flyer, popups, sound headless)

Run:
```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy PYGAME_HIDE_SUPPORT_PROMPT=1 PYTHONPATH=. python -c "import pygame; from game.game import Game; g=Game(); [ (g.update(), g.draw()) for _ in range(120)]; print('INTEGRATION OK lives', g.lives, 'state', g.state)"
```
Expected: prints `INTEGRATION OK ...` with no crash.

- [ ] **Step 3: Run the whole test suite**

Run: `SDL_VIDEODRIVER=dummy PYTHONPATH=. python -m pytest -q`
Expected: all tests pass.

- [ ] **Step 4: Commit**

```bash
git add game/game.py
git commit -m "feat: integrate boxes, mushrooms, damage, flyers, pop-ups, bonus life, sound"
```

---

## Task 10: Level content — add mushroom boxes and flyers; verify traversable

**Files:**
- Modify: `levels/level1.txt`

- [ ] **Step 1: Regenerate the level** with one `M` box and two `Y` flyers added (terrain/gaps unchanged so it stays completable). Run:

```bash
PYTHONPATH=. python - <<'PY'
import os
W,H=88,15
g=[["."]*W for _ in range(H)]
gaps=[(17,3),(37,3),(62,3)]
gapcols={c for s,w in gaps for c in range(s,s+w)}
for r in (13,14):
    for c in range(W):
        if c not in gapcols: g[r][c]="X"
g[12][2]="P"
for c in (8,9,10,11,12): g[12][c]="C"
g[9][22]="B"; g[9][23]="?"; g[9][24]="M"; g[9][25]="B"   # middle box now a Mushroom
for c in range(31,36): g[10][c]="="; g[9][c]="C"
for c in range(54,59): g[10][c]="="; g[9][c]="C"
g[12][28]="G"; g[12][50]="G"; g[12][78]="G"
g[6][40]="Y"; g[7][66]="Y"                                # two Flyers in the air
g[8][82]="F"
open("levels/level1.txt","w",encoding="utf-8").write("\n".join("".join(r) for r in g)+"\n")
print("level updated")
PY
```

- [ ] **Step 2: Verify traversable** (terrain bot, enemies removed — gaps unchanged so it must still complete)

Run:
```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy PYGAME_HIDE_SUPPORT_PROMPT=1 PYTHONPATH=. python - <<'PY'
import pygame
from game.game import Game
g=Game(); g.level.enemies.clear(); solids=g.level.solids
class K:
    def __init__(s,p): s.p=set(p)
    def __getitem__(s,k): return k in s.p
pygame.key.get_pressed=lambda:K({pygame.K_RIGHT,pygame.K_LSHIFT})
sa=lambda x,y: any(r.collidepoint(x,y) for r in solids)
won=False
for _ in range(2400):
    if g.player.on_ground and not sa(g.player.rect.right+22,g.player.rect.bottom+4):
        g.player.press_jump(pygame.time.get_ticks())
    if g.state=="PLAYING": g.update()
    if g.state=="LEVEL_COMPLETE": won=True; break
print("traversable:", won)
assert won
PY
```
Expected: `traversable: True`.

- [ ] **Step 3: Commit**

```bash
git add levels/level1.txt
git commit -m "feat: add a mushroom box and two flyers to level 1"
```

---

## Task 11: Update the desktop icon to the Spark Hero + rebuild

**Files:**
- Modify: `tools/make_icon.py` (draw the Spark Hero)

- [ ] **Step 1: Replace the `draw_icon()` body in `tools/make_icon.py`** with the Spark Hero on a cream tile:

```python
def draw_icon():
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    import math
    d.rounded_rectangle([6, 6, SIZE - 6, SIZE - 6], radius=46, fill=CREAM, outline=INK, width=4)
    cx = SIZE // 2
    # body
    body = [cx - 60, 150, cx + 60, 226]
    d.rounded_rectangle([cx - 14, 214, cx - 2, 244], radius=4, fill=ORANGE, outline=INK, width=2)
    d.rounded_rectangle([cx + 2, 214, cx + 14, 244], radius=4, fill=ORANGE, outline=INK, width=2)
    d.rounded_rectangle(body, radius=26, fill=ORANGE, outline=INK, width=4)
    for ex in (cx - 22, cx + 22):
        d.ellipse([ex - 13, 168, ex + 13, 194], fill=CREAM, outline=INK, width=2)
        d.ellipse([ex - 5, 178, ex + 5, 190], fill=INK)
    d.arc([cx - 22, 188, cx + 22, 214], start=20, end=160, fill=INK, width=4)
    # sunburst head
    hx, hy = cx, 96
    for a in range(0, 360, 30):
        rad = math.radians(a)
        d.line([hx, hy, hx + 52 * math.cos(rad), hy + 52 * math.sin(rad)], fill=ORANGE, width=7)
    d.ellipse([hx - 30, hy - 30, hx + 30, hy + 30], fill=ORANGE, outline=INK, width=3)
    d.ellipse([hx - 12, hy - 12, hx + 12, hy + 12], fill=CREAM)
    d.line([hx, hy + 30, hx, 150], fill=ORANGE, width=8)
    return img
```

- [ ] **Step 2: Regenerate the icon and inspect**

Run: `PYTHONPATH=. python tools/make_icon.py`
Then open `tools/claude_preview.png`. Expected: the Spark Hero icon. Tune if needed.

- [ ] **Step 3: Rebuild the app** (embeds the new icon; the shortcut points at `exe,0` so it updates automatically)

Run:
```bash
rm -rf dist build SuperClaudeBros.spec
python -m PyInstaller --noconfirm --onefile --windowed --name SuperClaudeBros --icon tools/claude.ico --add-data "levels/level1.txt;levels" --paths . main.py
```
Expected: `dist/SuperClaudeBros.exe` rebuilt.

- [ ] **Step 4: Commit** (icon source only; build artifacts are git-ignored)

```bash
git add tools/make_icon.py
git commit -m "feat: update desktop icon to the Spark Hero"
```

---

## Task 12: Full verification + playtest tuning

**Files:**
- Possibly modify: `game/settings.py` (tune by feel)

- [ ] **Step 1: Whole test suite**

Run: `SDL_VIDEODRIVER=dummy PYTHONPATH=. python -m pytest -q`
Expected: all tests pass (physics, level, jump, power, scoring).

- [ ] **Step 2: Launch-test the rebuilt exe** (PowerShell)

```powershell
$p = Start-Process "C:\Users\Atomn\mario\dist\SuperClaudeBros.exe" -PassThru
Start-Sleep 7
$procs = Get-Process SuperClaudeBros -ErrorAction SilentlyContinue
if ($procs) { Write-Output ("RUNNING title='" + ($procs | ? {$_.MainWindowTitle} | Select -First 1 -Expand MainWindowTitle) + "'"); $procs | Stop-Process -Force } else { Write-Output "FAILED" }
```
Expected: `RUNNING title='Super Claude Bros'`.

- [ ] **Step 3: Playtest** `python main.py` and tune `settings.py` only if needed: double-jump height (`DOUBLE_JUMP_VELOCITY`), mushroom speed, flyer bob/speed, invuln duration. Confirm: night theme reads well, Spark Hero looks good small + big, double-tap double-jumps, `?` pops a token, `M` releases a mushroom that grows you, a hit while big shrinks you, flyers are dodgeable/stompable, pop-ups + 1-UP show, sound plays.

- [ ] **Step 4: Commit any tuning**

```bash
git add game/settings.py
git commit -m "tune: night-update playtest pass"
```

---

## Done — definition of success

Per spec §9: the Spark Hero runs through a moonlit level; fast double-tap gives a mid-air boost; `?` boxes pop visible tokens (with "+100" and progress to a 1-UP); `M` boxes release a mushroom that grows him and grants a one-hit shield; Flyers bob through the air; score pop-ups and sound punctuate the action; the level stays completable; pure logic is covered by tests; and the desktop app + icon reflect the new character.
