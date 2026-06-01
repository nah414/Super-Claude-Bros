# Fire Flower + Power Persistence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the small→big→fire power progression with persistence across levels, state-aware mystery boxes (Fire Flower when big), and bouncing fireballs that defeat enemies.

**Architecture:** Extend `Player` to a 3-tier power state with tier-drop damage and a fire cooldown. New `FireFlower` (stationary item) and `Fireball` (bouncing projectile) follow the `Entity` pattern. `game.py` makes `M` boxes state-aware, collects flowers, handles fireball input/combat, and threads `carry_power` between levels. Art via the `assets.py` seam.

**Tech Stack:** Python 3.13, Pygame 2.6, pytest.

**Reference spec:** `docs/superpowers/specs/2026-06-01-fire-flower-design.md`

**Conventions:** `PYTHONPATH=<repo> SDL_VIDEODRIVER=dummy python -m pytest`; commits end with the `Co-Authored-By` trailer.

---

## Task 1: Settings constants + `"fire"` sound

**Files:** Modify `game/settings.py`, `game/sound.py`

- [ ] **Step 1: Append to `game/settings.py`**

```python
# --- Fire power ---
FIRE             = (235, 96, 56)
FIREBALL_SPEED   = 7.0
FIREBALL_BOUNCE  = -7.0
FIREBALL_LIFE    = 150
FIRE_COOLDOWN_MS = 300
MAX_FIREBALLS    = 2
FIREBALL_SCORE   = 200
FLOWER_SCORE     = 1000
```

- [ ] **Step 2: Add a `"fire"` blip to `SoundFX._build`** in `game/sound.py` (add one entry to the dict):

```python
            "fire":   self._tone([700, 500], 0.10),
```

- [ ] **Step 3: Commit** (`feat: fire constants + fireball sound`).

---

## Task 2: Player 3-tier power (TDD)

**Files:** Modify `game/entities/player.py`; Test `tests/test_player_power.py`

- [ ] **Step 1: Add failing tests** to `tests/test_player_power.py`

```python
def test_become_fire_keeps_big_size():
    p = Player(0, 100); p.grow(); size = (p.w, p.h)
    p.become_fire()
    assert p.power == "fire" and (p.w, p.h) == size


def test_tier_drop_damage():
    p = Player(0, 100); p.become_fire()
    assert p.power == "fire"
    assert p.take_damage(1000) is False and p.power == "big"
    assert p.take_damage(5000) is False and p.power == "small"
    assert p.take_damage(9000) is True


def test_can_shoot_respects_cooldown():
    p = Player(0, 100)
    assert p.can_shoot(1000) is False
    p.become_fire()
    assert p.can_shoot(1000) is True
    p.record_fire(1000)
    assert p.can_shoot(1100) is False
    assert p.can_shoot(1400) is True
```

- [ ] **Step 2: Run → fail** (`AttributeError: become_fire`).

- [ ] **Step 3: Implement in `game/entities/player.py`.** In `__init__` add (after `self.invuln_until = 0`):

```python
        self.last_fire_ms = -100000
```

Add methods and replace `take_damage` with the tier-drop version:

```python
    def become_fire(self):
        if self.power == "small":
            old_h = self.h
            self.w, self.h = S.PLAYER_BIG
            self.y -= (self.h - old_h)
        self.power = "fire"

    def can_shoot(self, now_ms):
        return self.power == "fire" and now_ms - self.last_fire_ms >= S.FIRE_COOLDOWN_MS

    def record_fire(self, now_ms):
        self.last_fire_ms = now_ms

    def take_damage(self, now_ms):
        if now_ms < self.invuln_until:
            return False
        if self.power == "fire":
            self.power = "big"
            self.invuln_until = now_ms + S.POWER_INVULN_MS
            return False
        if self.power == "big":
            old_h = self.h
            self.w, self.h = S.PLAYER_SMALL
            self.y += (old_h - self.h)
            self.power = "small"
            self.invuln_until = now_ms + S.POWER_INVULN_MS
            return False
        return True
```

- [ ] **Step 4: Run → pass** (test_player_power). **Step 5: Commit** (`feat: 3-tier power (fire) with tier-drop damage + fire cooldown (tested)`).

---

## Task 3: Fireball entity (TDD)

**Files:** Create `game/entities/fireball.py`, `tests/test_fireball.py`

- [ ] **Step 1: Failing tests** — `tests/test_fireball.py`

```python
import pygame
from game import settings as S
from game.entities.fireball import Fireball


def test_fireball_bounces_off_ground():
    T = S.TILE
    lvl = type("L", (), {"solids": [pygame.Rect(0, 5 * T, 20 * T, T)]})()
    fb = Fireball(40, 5 * T - 20, 1)
    bounced = False
    for _ in range(60):
        fb.update(lvl)
        if fb.vy < 0:
            bounced = True
            break
    assert bounced and fb.x > 40


def test_fireball_despawns_on_wall():
    T = S.TILE
    lvl = type("L", (), {"solids": [pygame.Rect(5 * T, 0, T, 20 * T)]})()
    fb = Fireball(5 * T - 10, T, 1)
    for _ in range(30):
        fb.update(lvl)
        if not fb.alive:
            break
    assert fb.alive is False


def test_fireball_despawns_after_life():
    lvl = type("L", (), {"solids": []})()
    fb = Fireball(0, 0, 1)
    for _ in range(S.FIREBALL_LIFE + 2):
        fb.update(lvl)
    assert fb.alive is False
```

- [ ] **Step 2: Run → fail.**

- [ ] **Step 3: Implement `game/entities/fireball.py`**

```python
from game import settings as S
from game import assets
from game.physics import move_and_collide
from game.entities.entity import Entity


class Fireball(Entity):
    """A bouncing projectile thrown by Fire-Claude. Defeats enemies on contact."""
    SIZE = 16

    def __init__(self, x, y, direction):
        super().__init__(x - self.SIZE // 2, y, self.SIZE, self.SIZE)
        self.vx = S.FIREBALL_SPEED * direction
        self.vy = 2.0
        self.life = S.FIREBALL_LIFE
        self.score = S.FIREBALL_SCORE

    def update(self, level):
        self.life -= 1
        if self.life <= 0:
            self.alive = False
            return
        self.vy = min(self.vy + S.GRAVITY, S.MAX_FALL)
        c = move_and_collide(self, level.solids)
        if c["bottom"]:
            self.vy = S.FIREBALL_BOUNCE          # bounce up off the ground
        if c["left"] or c["right"]:
            self.alive = False                   # die on a wall

    def draw(self, surface, camera):
        assets.draw_fireball(surface, camera.apply(self.rect))
```

- [ ] **Step 4: Run → pass.** **Step 5: Commit** (`feat: bouncing Fireball entity (tested)`).

---

## Task 4: FireFlower entity + art (flower, fireball, fire-Claude tint)

**Files:** Create `game/entities/fireflower.py`; Modify `game/assets.py`

- [ ] **Step 1: Create `game/entities/fireflower.py`**

```python
from game import settings as S
from game import assets
from game.entities.entity import Entity


class FireFlower(Entity):
    """Emerges from an 'M' box and stays put; collected -> fire power."""

    def __init__(self, box_x, box_y):
        size = S.TILE - 8
        super().__init__(box_x + 4, box_y, size, size)
        self.target_y = box_y - size
        self.emerging = True
        self.score = S.FLOWER_SCORE

    def update(self, level):
        if self.emerging:
            self.y -= 2.0
            if self.y <= self.target_y:
                self.y = self.target_y
                self.emerging = False

    def draw(self, surface, camera):
        assets.draw_fireflower(surface, camera.apply(self.rect))
```

- [ ] **Step 2: Add art to `game/assets.py`** (append):

```python
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
```

- [ ] **Step 3: Tint the Fire-Claude sprite.** In `draw_player`, replace the sunburst head block so the spark uses a hot colour when `power == "fire"`. Change the `R = ...` line and the three sunburst draws:

```python
    hx, hy = rect.centerx, rect.y + int(h * 0.17)
    R = int(w * 0.60) if power in ("big", "fire") else int(w * 0.56)
    spark = S.FIRE if power == "fire" else S.ORANGE
    pygame.draw.line(surface, spark, (hx, hy + int(w*0.24)), (hx, body.y), 3)   # neck
    _burst(surface, hx, hy, R, spark, 4)
    pygame.draw.circle(surface, spark, (hx, hy), max(7, int(w*0.30)))
    pygame.draw.circle(surface, S.INK, (hx, hy), max(7, int(w*0.30)), 2)
    pygame.draw.circle(surface, S.CREAM, (hx, hy), max(3, int(w*0.14)))
```

- [ ] **Step 4: Visual check** — render fire-Claude + flower + fireball to `tools/_preview/fire.png` and inspect; tune if needed. **Step 5: Commit** (`feat: FireFlower entity + fire-Claude/flower/fireball art`).

---

## Task 5: Game integration (state-aware boxes, flowers, fireballs, persistence)

**Files:** Modify `game/game.py`; Test `tests/test_game.py`

- [ ] **Step 1: Add failing tests** to `tests/test_game.py`

```python
def test_m_box_gives_mushroom_small_flower_when_big():
    g = Game(); g.new_game()
    mb = next(b for b in g.level.blocks if b.kind == "M" and not b.used)
    g.player.x = float(mb.rect.x); g.player.y = float(mb.rect.bottom); g.player.vy = 0.0
    g.player.power = "small"
    g.handle_boxes()
    assert len(g.mushrooms) == 1 and len(g.flowers) == 0

    g2 = Game(); g2.new_game()
    mb2 = next(b for b in g2.level.blocks if b.kind == "M" and not b.used)
    g2.player.x = float(mb2.rect.x); g2.player.y = float(mb2.rect.bottom); g2.player.vy = 0.0
    g2.player.power = "big"
    g2.handle_boxes()
    assert len(g2.flowers) == 1 and len(g2.mushrooms) == 0


def test_power_persists_across_levels_and_resets_on_death():
    g = Game(); g.new_game()
    g.player.become_fire()
    g.advance()
    assert g.carry_power == "fire" and g.player.power == "fire"
    g.lose_life()
    assert g.carry_power == "small"
```

- [ ] **Step 2: Run → fail** (`AttributeError: flowers`/`carry_power`).

- [ ] **Step 3: Implement in `game/game.py`.**

Add imports near the other entity imports:

```python
from game.entities.fireflower import FireFlower
from game.entities.fireball import Fireball
```

In `new_game`, add: `self.carry_power = "small"`.

In `start_level`, after `self.camera = Camera(self.level.width_px)` add the lists and apply carried power:

```python
        self.mushrooms = []
        self.flowers = []
        self.fireballs = []
        self.effects = []
        if self.carry_power == "big":
            self.player.grow()
        elif self.carry_power == "fire":
            self.player.become_fire()
```
(Remove the old duplicate `self.mushrooms = []` / `self.effects = []` lines in `start_level` so they aren't set twice.)

In `respawn`, set `self.flowers = []` and `self.fireballs = []` alongside the existing resets.

In `lose_life`, set `self.carry_power = "small"` (first line of the method).

In `advance`, set `self.carry_power = self.player.power` as the first line.

In `handle_events`, add an `F` case (after the jump KEYDOWN handling, inside the KEYDOWN branch):

```python
                elif event.key == pygame.K_f and self.state == "PLAYING":
                    if self.player.can_shoot(self.now()) and len(self.fireballs) < S.MAX_FIREBALLS:
                        self.fireballs.append(Fireball(self.player.rect.centerx, self.player.rect.centery, self.player.facing))
                        self.player.record_fire(self.now())
                        self.sfx.play("fire")
```

In `handle_boxes`, replace the `M` branch:

```python
            elif b.kind == "M":
                b.used = True
                if self.player.power == "small":
                    self.mushrooms.append(Mushroom(b.rect.x, b.rect.y))
                else:
                    self.flowers.append(FireFlower(b.rect.x, b.rect.y))
                self.sfx.play("power")
```

In `update`, add updates + handlers. After the `for m in self.mushrooms: m.update(self.level)` loop add:

```python
        for fl in self.flowers:
            fl.update(self.level)
        for f in self.fireballs:
            f.update(self.level)
```

And after `self.handle_mushrooms()` add:

```python
        self.handle_flowers()
        self.handle_fireballs()
```

Add the two handlers (next to `handle_mushrooms`):

```python
    def handle_flowers(self):
        for fl in self.flowers:
            if fl.alive and not fl.emerging and self.player.rect.colliderect(fl.rect):
                fl.alive = False
                self.player.become_fire()
                self.score += fl.score
                self.popup(fl.rect.centerx, fl.rect.top, f"+{fl.score}")
                self.sfx.play("power")
        self.flowers = [fl for fl in self.flowers if fl.alive]

    def handle_fireballs(self):
        for f in self.fireballs:
            if not f.alive:
                continue
            for e in self.level.enemies:
                if e.alive and f.alive and f.rect.colliderect(e.rect):
                    e.alive = False
                    f.alive = False
                    self.score += f.score
                    self.popup(e.rect.centerx, e.rect.top, f"+{f.score}")
                    self.sfx.play("stomp")
        self.fireballs = [f for f in self.fireballs if f.alive]
```

In `draw`, after the mushrooms-draw loop add:

```python
            for fl in self.flowers:
                fl.draw(self.screen, self.camera)
            for f in self.fireballs:
                f.draw(self.screen, self.camera)
```

- [ ] **Step 4: Run → pass** (test_game) + full suite.

- [ ] **Step 5: Commit** (`feat: integrate fire flowers, fireballs, and power persistence`).

---

## Task 6: Verify + rebuild

- [ ] **Step 1: Full suite** green.
- [ ] **Step 2: Gameplay smoke** — small→mushroom→big; big→box→flower→fire; throw a fireball (F) and kill an enemy; tier-drop damage (fire→big→small); power persists across `advance()`. All headless, no crash.
- [ ] **Step 3: Traversal** of all 5 levels still completes.
- [ ] **Step 4: Rebuild** `dist/SuperClaudeBros.exe`; launch-test.
- [ ] **Step 5: Update README controls** (add "Throw fireball (when Fire): F"); commit.

---

## Self-review
Spec coverage: 3-tier power + persistence (T2/T5), state-aware boxes + FireFlower (T4/T5), fireballs (T3/T5), art (T4), constants+sound (T1), tests (T2/T3/T5). Types: `Player.become_fire/can_shoot/record_fire/take_damage`, `Fireball(x,y,direction)`, `FireFlower(box_x,box_y)`, `game.carry_power/flowers/fireballs`, `assets.draw_fireflower/draw_fireball`, `S.FIRE/FIREBALL_*/FLOWER_SCORE` — consistent across tasks.
