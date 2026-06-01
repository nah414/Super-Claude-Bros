# Claude Platformer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a polished, single-level side-scrolling platformer in Python + Pygame starring the Claude mascot, themed in Anthropic's brand palette, with momentum-based game feel.

**Architecture:** Classic OOP — a `Game` object runs a fixed-60-FPS loop (input → update → draw) over a `Level` parsed from an ASCII tile map. Pure collision math lives in `physics.py` (unit-tested headlessly). All rendering goes through `assets.py` draw functions (the swappable art seam), so game logic never knows what anything looks like.

**Tech Stack:** Python 3.13, Pygame 2.6+, pytest.

**Reference spec:** `docs/superpowers/specs/2026-06-01-claude-platformer-design.md`

---

## File Structure

| File | Responsibility |
|---|---|
| `main.py` | Entry point — construct `Game`, call `.run()` |
| `game/settings.py` | All tunable constants: window, colors, physics, gameplay |
| `game/physics.py` | Pure `move_and_collide(entity, solids)` — axis-separated AABB |
| `game/camera.py` | World→screen offset; follows player; clamps to level bounds |
| `game/level.py` | Parse tile map; own blocks/coins/enemies/flag; draw world |
| `game/assets.py` | `draw_*()` programmer-art functions (the art seam) |
| `game/hud.py` | Score/sparks/lives overlay (screen space) |
| `game/game.py` | Main loop, state machine, interactions (coins/stomp/flag/death) |
| `game/entities/entity.py` | Base `Entity`: float pos, velocity, `rect`, `update`, `draw` |
| `game/entities/player.py` | Claude hero: input movement, variable jump, power-state field |
| `game/entities/goomba.py` | Walker enemy: patrol, reverse at walls, die on stomp |
| `game/entities/coin.py` | Sunburst "spark" collectible |
| `game/entities/block.py` | Ground / platform / brick / question block |
| `game/entities/flag.py` | Finish pole — overlap triggers level complete |
| `levels/level1.txt` | The level as an editable ASCII grid |
| `tests/test_physics.py` | Collision resolution unit tests |
| `tests/test_level.py` | Tile-map parsing unit tests |

---

## Task 0: Project setup

**Files:**
- Create: `requirements.txt`, `.gitignore`, `README.md`
- Create: `game/__init__.py`, `game/entities/__init__.py` (empty package markers)

- [ ] **Step 1: Create `requirements.txt`**

```
pygame>=2.6
pytest>=8.0
```

- [ ] **Step 2: Create `.gitignore`**

```
__pycache__/
*.pyc
.venv/
venv/
.pytest_cache/
```

- [ ] **Step 3: Create empty package markers**

Create `game/__init__.py` and `game/entities/__init__.py`, both empty files.

- [ ] **Step 4: Create `README.md`**

```markdown
# Claude's Platformer

A side-scrolling platformer starring the Claude mascot, built with Python + Pygame.

## Run
    python -m pip install -r requirements.txt
    python main.py

## Controls
- Move: Arrow keys or A/D
- Jump: Space / Up / W (hold for higher)
- Run: hold Shift
- Restart (on win/game-over): Enter   ·   Quit: Esc
```

- [ ] **Step 5: Install dependencies**

Run: `python -m pip install -r requirements.txt`
Expected: pygame and pytest install successfully.

- [ ] **Step 6: Commit**

```bash
git add requirements.txt .gitignore README.md game/__init__.py game/entities/__init__.py
git commit -m "chore: project scaffold and dependencies"
```

---

## Task 1: Settings + blank window (walking skeleton)

**Files:**
- Create: `game/settings.py`, `game/game.py`, `main.py`

- [ ] **Step 1: Create `game/settings.py`**

```python
"""Single source of truth for every tunable constant."""

# --- Window ---
WIDTH, HEIGHT = 960, 600
TILE = 40
FPS = 60
TITLE = "Claude's Platformer"

# --- Colors (Anthropic brand) ---
ORANGE    = (217, 119, 87)   # #d97757  hero, sparks, accents
CREAM     = (250, 249, 245)  # #faf9f5  sky / light
SAGE      = (120, 140, 93)   # #788c5d  ground / platforms
BLUE      = (106, 155, 204)  # #6a9bcc  secondary accents
INK       = (20, 20, 19)     # #141413  outlines / text
LIGHTGRAY = (232, 230, 220)  # #e8e6dc  subtle fills
MIDGRAY   = (176, 174, 165)  # #b0aea5  used question block

# --- Physics (pixels, pixels/frame @ 60 FPS) ---
GRAVITY       = 0.8
MAX_FALL      = 16.0
MOVE_ACCEL    = 0.5
MAX_WALK      = 4.0
MAX_RUN       = 6.5
FRICTION      = 0.4
SKID_DECEL    = 0.8
JUMP_VELOCITY = -14.0
JUMP_CUTOFF   = -4.0
STOMP_BOUNCE  = -8.0

# --- Gameplay ---
START_LIVES = 3
PIT_DEATH_Y = HEIGHT + 80   # falling below this = death
```

- [ ] **Step 2: Create a minimal `game/game.py`**

```python
import pygame
from game import settings as S


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((S.WIDTH, S.HEIGHT))
        pygame.display.set_caption(S.TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
            self.screen.fill(S.CREAM)
            pygame.display.flip()
            self.clock.tick(S.FPS)
        pygame.quit()
```

- [ ] **Step 3: Create `main.py`**

```python
from game.game import Game

if __name__ == "__main__":
    Game().run()
```

- [ ] **Step 4: Run and observe**

Run: `python main.py`
Expected: a 960×600 cream-colored window titled "Claude's Platformer" opens; Esc or the close button quits cleanly with no errors.

- [ ] **Step 5: Commit**

```bash
git add game/settings.py game/game.py main.py
git commit -m "feat: settings and blank game window"
```

---

## Task 2: Physics — axis-separated AABB collision (TDD)

**Files:**
- Create: `game/physics.py`
- Test: `tests/test_physics.py`

- [ ] **Step 1: Write the failing tests**

`tests/test_physics.py`:

```python
import types
import pygame
from game.physics import move_and_collide


def make_entity(x, y, w, h, vx=0.0, vy=0.0):
    return types.SimpleNamespace(x=float(x), y=float(y), w=w, h=h,
                                 vx=float(vx), vy=float(vy))


def test_lands_on_floor():
    e = make_entity(0, 0, 10, 10, vy=40)
    floor = pygame.Rect(0, 30, 40, 40)          # spans y 30..70
    contacts = move_and_collide(e, [floor])
    assert e.y == 20            # bottom snapped to floor top (30) - height (10)
    assert e.vy == 0
    assert contacts["bottom"] is True


def test_stops_at_wall_moving_right():
    e = make_entity(0, 0, 10, 10, vx=10)
    wall = pygame.Rect(15, 0, 10, 40)           # spans x 15..25
    contacts = move_and_collide(e, [wall])
    assert e.x == 5             # right snapped to wall left (15) - width (10)
    assert e.vx == 0
    assert contacts["right"] is True


def test_free_fall_keeps_subpixel_velocity():
    e = make_entity(0, 0, 10, 10, vx=2.5, vy=3.5)
    contacts = move_and_collide(e, [])          # nothing to hit
    assert e.x == 2.5 and e.y == 3.5
    assert not any(contacts.values())
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_physics.py -v`
Expected: FAIL — `ModuleNotFoundError` / `cannot import name 'move_and_collide'`.

- [ ] **Step 3: Implement `game/physics.py`**

```python
"""Pure movement + collision resolution. No display required."""
import pygame


def move_and_collide(entity, solids):
    """Apply entity.vx/vy to entity.x/y, resolving collisions one axis at a time.

    `entity` must expose floats x, y, vx, vy and ints w, h (top-left box).
    `solids` is an iterable of pygame.Rect. Mutates `entity` in place.
    Returns contacts dict: {'left','right','top','bottom'} -> bool.
    'bottom' True means the entity is standing on something.
    """
    contacts = {"left": False, "right": False, "top": False, "bottom": False}

    # --- X axis ---
    entity.x += entity.vx
    rect = pygame.Rect(round(entity.x), round(entity.y), entity.w, entity.h)
    for s in solids:
        if rect.colliderect(s):
            if entity.vx > 0:
                rect.right = s.left
                contacts["right"] = True
            elif entity.vx < 0:
                rect.left = s.right
                contacts["left"] = True
            entity.x = float(rect.x)
    if contacts["left"] or contacts["right"]:
        entity.vx = 0.0

    # --- Y axis ---
    entity.y += entity.vy
    rect = pygame.Rect(round(entity.x), round(entity.y), entity.w, entity.h)
    for s in solids:
        if rect.colliderect(s):
            if entity.vy > 0:
                rect.bottom = s.top
                contacts["bottom"] = True
            elif entity.vy < 0:
                rect.top = s.bottom
                contacts["top"] = True
            entity.y = float(rect.y)
    if contacts["top"] or contacts["bottom"]:
        entity.vy = 0.0

    return contacts
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_physics.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add game/physics.py tests/test_physics.py
git commit -m "feat: axis-separated AABB collision (tested)"
```

---

## Task 3: Entity base + assets seam + Block

**Files:**
- Create: `game/entities/entity.py`, `game/assets.py`, `game/entities/block.py`

- [ ] **Step 1: Create `game/entities/entity.py`**

```python
import pygame


class Entity:
    """Base for everything that lives in the world."""

    def __init__(self, x, y, w, h):
        self.x = float(x)
        self.y = float(y)
        self.w = w
        self.h = h
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True

    @property
    def rect(self):
        return pygame.Rect(round(self.x), round(self.y), self.w, self.h)

    def update(self, level):
        pass

    def draw(self, surface, camera):
        pass
```

- [ ] **Step 2: Create `game/assets.py` (block art for now; others added later)**

```python
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
```

- [ ] **Step 3: Create `game/entities/block.py`**

```python
from game import settings as S
from game import assets
from game.entities.entity import Entity

SOLID_KINDS = ("X", "=", "B", "?")


class Block(Entity):
    def __init__(self, x, y, kind):
        super().__init__(x, y, S.TILE, S.TILE)
        self.kind = kind
        self.used = False     # for '?' blocks once bumped

    def draw(self, surface, camera):
        assets.draw_block(surface, camera.apply(self.rect), self.kind, self.used)
```

- [ ] **Step 4: Sanity import check**

Run: `python -c "import game.entities.block, game.assets, game.entities.entity; print('ok')"`
Expected: prints `ok` (no import errors).

- [ ] **Step 5: Commit**

```bash
git add game/entities/entity.py game/assets.py game/entities/block.py
git commit -m "feat: entity base, asset seam, block"
```

---

## Task 4: Level parsing (TDD) + remaining entity stubs

**Files:**
- Create: `game/entities/coin.py`, `game/entities/goomba.py`, `game/entities/flag.py`
- Create: `game/level.py`
- Test: `tests/test_level.py`

- [ ] **Step 1: Create the three remaining entities**

`game/entities/coin.py`:

```python
from game import settings as S
from game import assets
from game.entities.entity import Entity


class Coin(Entity):
    """A sunburst 'spark' collectible, centered in its tile."""

    def __init__(self, x, y):
        size = S.TILE // 2
        super().__init__(x + size // 2, y + size // 2, size, size)
        self.collected = False

    def draw(self, surface, camera):
        assets.draw_coin(surface, camera.apply(self.rect))
```

`game/entities/goomba.py`:

```python
from game import settings as S
from game import assets
from game.physics import move_and_collide
from game.entities.entity import Entity


class Goomba(Entity):
    """Walker enemy: paces left/right, reverses at walls, dies on stomp."""
    SPEED = 1.5

    def __init__(self, x, y):
        super().__init__(x + 4, y + S.TILE // 2, S.TILE - 8, S.TILE // 2)
        self.direction = -1

    def update(self, level):
        self.vx = self.SPEED * self.direction
        self.vy = min(self.vy + S.GRAVITY, S.MAX_FALL)
        contacts = move_and_collide(self, level.solids)
        if contacts["left"] or contacts["right"]:
            self.direction *= -1

    def draw(self, surface, camera):
        assets.draw_goomba(surface, camera.apply(self.rect))
```

`game/entities/flag.py`:

```python
from game import settings as S
from game import assets
from game.entities.entity import Entity


class Flag(Entity):
    """Finish pole. The 'F' marker is its top; the pole hangs down 5 tiles."""

    def __init__(self, x, y):
        super().__init__(x + S.TILE // 2 - 4, y, 8, S.TILE * 5)

    def draw(self, surface, camera):
        assets.draw_flag(surface, camera.apply(self.rect))
```

- [ ] **Step 2: Write the failing level test**

`tests/test_level.py`:

```python
from game import settings as S
from game.level import Level

MAP = "......\n..C...\nP.G..F\nXXXXXX\n"


def test_parses_map(tmp_path):
    p = tmp_path / "lvl.txt"
    p.write_text(MAP)
    level = Level(str(p))

    assert len(level.blocks) == 6          # six 'X' ground tiles
    assert len(level.coins) == 1
    assert len(level.enemies) == 1
    assert level.flag is not None
    assert level.player_spawn == (0, 2 * S.TILE)   # 'P' at col 0, row 2
    assert len(level.solids) == 6          # solids derived from blocks
```

- [ ] **Step 3: Run to verify it fails**

Run: `python -m pytest tests/test_level.py -v`
Expected: FAIL — cannot import `Level`.

- [ ] **Step 4: Implement `game/level.py`**

```python
from game import settings as S
from game.entities.block import Block, SOLID_KINDS
from game.entities.coin import Coin
from game.entities.goomba import Goomba
from game.entities.flag import Flag


class Level:
    def __init__(self, path):
        self.blocks = []
        self.coins = []
        self.enemies = []
        self.flag = None
        self.player_spawn = (0, 0)
        self._load(path)
        self.width_px = self.cols * S.TILE
        self.solids = [b.rect for b in self.blocks]

    def _load(self, path):
        with open(path, encoding="utf-8") as f:
            rows = [line.rstrip("\n") for line in f]
        rows = [r for r in rows if r != ""]
        self.rows = len(rows)
        self.cols = max((len(r) for r in rows), default=0)
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                x, y = i * S.TILE, j * S.TILE
                if ch in SOLID_KINDS:
                    self.blocks.append(Block(x, y, ch))
                elif ch == "C":
                    self.coins.append(Coin(x, y))
                elif ch == "G":
                    self.enemies.append(Goomba(x, y))
                elif ch == "F":
                    self.flag = Flag(x, y)
                elif ch == "P":
                    self.player_spawn = (x, y)

    def draw(self, surface, camera):
        for b in self.blocks:
            b.draw(surface, camera)
        for c in self.coins:
            if not c.collected:
                c.draw(surface, camera)
        if self.flag:
            self.flag.draw(surface, camera)
        for e in self.enemies:
            if e.alive:
                e.draw(surface, camera)
```

- [ ] **Step 5: Run to verify it passes**

Run: `python -m pytest tests/test_level.py -v`
Expected: 1 passed.

- [ ] **Step 6: Commit**

```bash
git add game/entities/coin.py game/entities/goomba.py game/entities/flag.py game/level.py tests/test_level.py
git commit -m "feat: level parsing with coin/goomba/flag entities (tested)"
```

---

## Task 5: Camera + Player + render the world (the "it's a game" moment)

**Files:**
- Create: `game/camera.py`, `game/entities/player.py`, `levels/level1.txt`
- Modify: `game/assets.py` (add player + remaining art), `game/game.py` (wire it up)

- [ ] **Step 1: Create `game/camera.py`**

```python
from game import settings as S


class Camera:
    def __init__(self, level_width_px):
        self.offset_x = 0
        self.level_width = level_width_px

    def update(self, target_rect):
        self.offset_x = target_rect.centerx - S.WIDTH // 3
        self.offset_x = max(0, min(self.offset_x, self.level_width - S.WIDTH))

    def apply(self, rect):
        return rect.move(-self.offset_x, 0)
```

- [ ] **Step 2: Add the remaining art to `game/assets.py`**

Append these functions to `game/assets.py`:

```python
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
    eye_y = rect.y + rect.h // 3
    for ex in (rect.centerx - 6, rect.centerx + 6):
        pygame.draw.circle(surface, S.CREAM, (ex, eye_y), 4)
        pygame.draw.circle(surface, S.INK, (ex, eye_y), 2)
    pygame.draw.ellipse(surface, S.SAGE, (rect.left, rect.bottom - 5, rect.w // 2 - 1, 5))
    pygame.draw.ellipse(surface, S.SAGE, (rect.centerx + 1, rect.bottom - 5, rect.w // 2 - 1, 5))


def draw_flag(surface, rect):
    pole = pygame.Rect(rect.centerx - 3, rect.top, 6, rect.h)
    pygame.draw.rect(surface, S.INK, pole)
    pygame.draw.circle(surface, S.BLUE, (rect.centerx, rect.top), 6)
    pts = [(rect.centerx + 3, rect.top + 6),
           (rect.centerx + 30, rect.top + 14),
           (rect.centerx + 3, rect.top + 22)]
    pygame.draw.polygon(surface, S.ORANGE, pts)
```

- [ ] **Step 3: Create `game/entities/player.py`**

```python
import pygame
from game import settings as S
from game import assets
from game.physics import move_and_collide
from game.entities.entity import Entity


class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 30, 36)
        self.on_ground = False
        self.facing = 1
        self.power = "small"      # extension point for power-ups

    def start_jump(self):
        if self.on_ground:
            self.vy = S.JUMP_VELOCITY
            self.on_ground = False

    def end_jump(self):
        if self.vy < S.JUMP_CUTOFF:      # released while still rising fast
            self.vy = S.JUMP_CUTOFF

    def update(self, level):
        self._horizontal(pygame.key.get_pressed())
        self.vy = min(self.vy + S.GRAVITY, S.MAX_FALL)
        contacts = move_and_collide(self, level.solids)
        self.on_ground = contacts["bottom"]

    def _horizontal(self, keys):
        left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        run = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        top = S.MAX_RUN if run else S.MAX_WALK
        if right and not left:
            self.facing = 1
            self.vx += S.SKID_DECEL if self.vx < 0 else S.MOVE_ACCEL
            self.vx = min(self.vx, top)
        elif left and not right:
            self.facing = -1
            self.vx -= S.SKID_DECEL if self.vx > 0 else S.MOVE_ACCEL
            self.vx = max(self.vx, -top)
        else:
            if self.vx > 0:
                self.vx = max(0.0, self.vx - S.FRICTION)
            else:
                self.vx = min(0.0, self.vx + S.FRICTION)

    def draw(self, surface, camera):
        assets.draw_player(surface, camera.apply(self.rect), self.facing)
```

- [ ] **Step 4: Author `levels/level1.txt`** (15 rows tall; ground rows at bottom; edit freely later)

```
................................................................................
................................................................................
................................................................................
................................................................................
.................C.C............................C.C.............................
................BBBB.........?...B?B.........=====...............................
................................................................................
...........C.C..........C..C.....................................C.C.............
..........=====........====.....=====...................========................
...............................................................................F
.................G..............G.........G...............G.....................F
............................................................................XXXXX
P...........................XXXX.................XXXXXXXX........................XXXXX
XXXXXXXXXXXXXXXX....XXXXXXXXXXXXX.....XXXXXXXXXXXXXXXXXXXXXXXX...XXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXX....XXXXXXXXXXXXX.....XXXXXXXXXXXXXXXXXXXXXXXX...XXXXXXXXXXXXXXXXXXXXXX
```

- [ ] **Step 5: Replace `game/game.py` to wire level + camera + player**

```python
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
```

- [ ] **Step 6: Run and observe**

Run: `python main.py`
Expected: The Claude buddy stands on sage-green ground in a cream world. Arrow keys/A-D move with momentum and a turn-around skid; Shift runs faster; Space/Up/W jumps (higher when held). The camera scrolls right as you advance and stops at the level edges. Goombas pace back and forth. (They don't hurt you yet; that's Task 6.)

- [ ] **Step 7: Commit**

```bash
git add game/camera.py game/entities/player.py game/assets.py game/game.py levels/level1.txt
git commit -m "feat: playable Claude hero, camera, and rendered level"
```

---

## Task 6: Interactions — coins, stomp, death, flag, HUD, states

**Files:**
- Create: `game/hud.py`
- Modify: `game/game.py`

- [ ] **Step 1: Create `game/hud.py`**

```python
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
```

- [ ] **Step 2: Replace `game/game.py` with the full version (states + interactions)**

```python
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
```

- [ ] **Step 3: Run and observe**

Run: `python main.py`
Expected: Touching a spark collects it (SPARKS count rises, score +100). Landing on a Goomba's head squashes it and bounces you (score +200); touching one from the side costs a life and respawns you at the start. Falling into a pit costs a life. Reaching the flag shows "LEVEL COMPLETE!"; losing all 3 lives shows "GAME OVER"; Enter restarts. HUD shows score/sparks/lives.

- [ ] **Step 4: Commit**

```bash
git add game/hud.py game/game.py
git commit -m "feat: coins, stomp, death/respawn, flag, HUD, win/lose states"
```

---

## Task 7: Question blocks emit a spark when bumped

**Files:**
- Modify: `game/game.py` (detect upward head-bump into a '?' block)

- [ ] **Step 1: Add bump detection to `Game.update`**

In `game/game.py`, add a call to `self.handle_question_blocks()` inside `update()`, right after `self.handle_coins()`. Then add this method:

```python
    def handle_question_blocks(self):
        if self.player.vy >= 0:
            return                       # only when moving upward
        head = self.player.rect.move(0, -2)
        for b in self.level.blocks:
            if b.kind == "?" and not b.used and head.colliderect(b.rect):
                b.used = True
                self.sparks += 1
                self.score += 100
```

- [ ] **Step 2: Run and observe**

Run: `python main.py`
Expected: Jumping so your head hits a blue "?" block turns it gray (used) and awards a spark (+100). Already-used blocks do nothing.

- [ ] **Step 3: Commit**

```bash
git add game/game.py
git commit -m "feat: question blocks award a spark when bumped"
```

---

## Task 8: Full-suite check + playtest tuning pass

**Files:**
- Modify: `game/settings.py` (tune constants by feel, if needed)

- [ ] **Step 1: Run the whole test suite**

Run: `python -m pytest -v`
Expected: all physics + level tests pass.

- [ ] **Step 2: Playtest and tune**

Run: `python main.py` and play the whole level start to flag. Adjust constants in `game/settings.py` *only if needed* for feel:
- Jump too floaty/short → tune `JUMP_VELOCITY` / `GRAVITY`.
- Run feels too slow/fast → tune `MAX_RUN` / `MOVE_ACCEL`.
- Turn-around too slippery → tune `SKID_DECEL` / `FRICTION`.
Confirm the level is completable: every gap is jumpable, every Goomba avoidable or stompable, and the flag is reachable.

- [ ] **Step 3: Commit any tuning**

```bash
git add game/settings.py
git commit -m "tune: playtest pass on movement and level balance"
```

---

## Done — definition of success

A player launches `python main.py`, controls the Claude hero with momentum-rich movement, collects sparks, bumps question blocks, stomps Goombas, survives pits, and reaches the flag to win — on one hand-authored level that feels good to move around in. Code is modular, tested where it counts, and ready to extend (power-ups, more levels, enemies, sound — see spec §13).
