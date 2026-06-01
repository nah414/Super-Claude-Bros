# Shell Grab, Carry & Throw Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Press `E` to lift an idle Koopa shell, carry it (running/jumping, as a battering ram), and press `E` again to throw it as a slide. The existing side-kick stays.

**Architecture:** A held shell is the existing `Koopa` with `held=True` (AI suspended), its position slaved to the hero by `game.handle_carry()`. Throwing funnels into the existing slide path. No new entities, no new art.

**Tech Stack:** Python 3.13, Pygame 2.6, pytest.

**Reference spec:** `docs/superpowers/specs/2026-06-01-shell-carry-design.md`

**Conventions:** `PYTHONPATH=<repo> SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m pytest`; commits end with the `Co-Authored-By` trailer.

---

## Task 1: Held-shell suspension + carry slots (TDD)

**Files:** Modify `game/entities/koopa.py`, `game/entities/player.py`; Test `tests/test_koopa.py`

- [ ] **Step 1: Failing test** — append to `tests/test_koopa.py`

```python
def test_held_koopa_skips_update():
    lvl = type("L", (), {"solids": []})()
    k = Koopa(100, 100)
    k.held = True
    y0 = k.y
    for _ in range(10):
        k.update(lvl)
    assert k.y == y0            # no gravity/motion while held
```

- [ ] **Step 2: Run → fail** (`AttributeError: held` or it falls).

- [ ] **Step 3: Implement.** In `game/entities/koopa.py` `__init__`, add after `self.score = S.KOOPA_SCORE`:

```python
        self.held = False
```

and as the first lines of `update`:

```python
    def update(self, level):
        if self.held:
            return                       # carried: position is driven by the game
```

In `game/entities/player.py` `__init__`, add after `self.last_fire_ms = -100000`:

```python
        self.carrying = None             # a held Koopa shell, or None
```

- [ ] **Step 4: Run → pass.** **Step 5: Commit** (`feat: held-shell suspension + player carry slot`).

---

## Task 2: Grab / throw / drop / battering-ram (TDD)

**Files:** Modify `game/game.py`; Test `tests/test_game.py`

- [ ] **Step 1: Failing tests** — append to `tests/test_game.py`

```python
def _shell_game():
    from game.entities.koopa import Koopa
    g = Game(); g.new_game(); g.state = "PLAYING"; g.level.enemies.clear()
    k = Koopa(300, 300); k.state = "shell"
    g.level.enemies.append(k)
    return g, k


def test_grab_then_throw_slides_in_facing_dir():
    g, k = _shell_game()
    g.player.x = float(k.rect.left - g.player.w + 8)
    g.player.y = float(k.rect.centery - g.player.h // 2)
    g.player.facing = 1
    g.grab_or_throw()
    assert g.player.carrying is k and k.held
    g.grab_or_throw()                                  # press E again -> throw
    assert g.player.carrying is None and not k.held
    assert k.state == "slide" and k.direction == 1 and k.kick_cooldown > 0


def test_cannot_grab_walking_koopa():
    g, k = _shell_game()
    k.state = "walk"
    g.player.x = float(k.rect.x); g.player.y = float(k.rect.y)
    g.grab_or_throw()
    assert g.player.carrying is None


def test_carried_shell_battering_rams_enemy():
    from game.entities.goomba import Goomba
    g, k = _shell_game()
    k.held = True; g.player.carrying = k
    g.player.x = 300.0; g.player.y = 300.0; g.player.facing = 1
    g.handle_carry()                                   # position the held shell
    gm = Goomba(k.rect.x, k.rect.y)                     # overlap it
    g.level.enemies.append(gm)
    g.handle_carry()
    assert gm.alive is False


def test_damage_drops_carried_shell():
    g, k = _shell_game()
    k.held = True; g.player.carrying = k
    g.drop_shell()
    assert g.player.carrying is None and not k.held and k.state == "shell"
```

- [ ] **Step 2: Run → fail** (`AttributeError: grab_or_throw`).

- [ ] **Step 3: Implement in `game/game.py`.** Add the `E` branch in `handle_events` after the `K_f` branch:

```python
                elif event.key == pygame.K_e and self.state == "PLAYING":
                    self.grab_or_throw()
```

Add these methods (near `handle_enemies`):

```python
    def grab_or_throw(self):
        if self.player.carrying is not None:
            self.throw_shell()
            return
        reach = self.player.rect.inflate(10, 6)
        for e in self.level.enemies:
            if isinstance(e, Koopa) and e.alive and e.state == "shell" and not e.held \
                    and reach.colliderect(e.rect):
                e.held = True
                e.vx = e.vy = 0.0
                self.player.carrying = e
                self.sfx.play("power")
                break

    def throw_shell(self):
        k = self.player.carrying
        self.player.carrying = None
        k.held = False
        k.state = "slide"
        k.direction = self.player.facing
        k.kick_cooldown = S.SHELL_KICK_COOLDOWN
        self.sfx.play("stomp")

    def drop_shell(self):
        k = self.player.carrying
        if k is not None:
            self.player.carrying = None
            k.held = False
            k.state = "shell"

    def handle_carry(self):
        k = self.player.carrying
        if k is None:
            return
        if not k.alive:
            self.player.carrying = None
            return
        p = self.player
        k.x = float(p.rect.right - 6) if p.facing > 0 else float(p.rect.left - k.w + 6)
        k.y = float(p.rect.centery - k.h // 2)
        for e in self.level.enemies:
            if e is not k and e.alive and k.rect.colliderect(e.rect):
                e.alive = False
                pts = getattr(e, "score", S.STOMP_SCORE)
                self.score += pts
                self.popup(e.rect.centerx, e.rect.top, f"+{pts}")
                self.sfx.play("stomp")
```

In `handle_enemies`, skip the carried shell — change the loop guard to:

```python
            if not e.alive or e is self.player.carrying or not self.player.rect.colliderect(e.rect):
                continue
```

In `update`, call `self.handle_carry()` right before `self.handle_shells()`.

In `lose_life`, drop any held shell first — add as the first line:

```python
        self.drop_shell()
```

- [ ] **Step 4: Run → pass** (new tests + full suite). **Step 5: Commit** (`feat: shell grab/carry/throw + battering-ram`).

---

## Task 3: Draw the held shell on top of the hero

**Files:** Modify `game/game.py`

- [ ] **Step 1:** In `draw`, right after `self.player.draw(self.screen, self.camera)`, add:

```python
            if self.player.carrying is not None:
                self.player.carrying.draw(self.screen, self.camera)   # on top of the hero
```

- [ ] **Step 2: Visual check** — render a carrying frame to `tools/_preview/carry.png`; confirm the shell reads as held at the hands. **Step 3: Commit** (`feat: draw carried shell over the hero`).

---

## Task 4: Verify + rebuild + merge

- [ ] **Step 1:** Full suite green.
- [ ] **Step 2: Smoke (headless)** — stomp a Koopa, press-E grab, move, press-E throw → slides and chain-kills; 300-frame soak with a grab/throw, no crash.
- [ ] **Step 3: Traversal** — `python tools/traverse.py` still completes all 5 levels (the bot ignores `E`, so this just confirms no regression).
- [ ] **Step 4: Rebuild** `dist/SuperClaudeBros.exe`.
- [ ] **Step 5: Merge** `shell-carry` → `main` (`--no-ff`), delete branch.

---

## Self-review
Spec coverage: controls (T2 `E` handler), grab/throw/drop/ram (T2), held suspension (T1), carry slots (T1), draw (T3), tests (T1/T2), verify+rebuild (T4). Types consistent: `Koopa.held`, `Player.carrying`, `game.grab_or_throw/throw_shell/drop_shell/handle_carry`. Reuses `SHELL_SPEED`/`SHELL_KICK_COOLDOWN`/`KOOPA_SCORE` — no new constants strictly required (the spec's `GRAB_REACH`/`CARRY_AHEAD` are inlined as literals 10,6 / 6 for simplicity).
