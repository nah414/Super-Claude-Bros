# Warp Pipes + Bonus Vault Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tap Down on a pipe to teleport into a hidden coin vault in the same level and a return pipe back out, shown in `level_3`.

**Architecture:** Pipes are solid `T`/`t` tiles. A level parses `# warp:` header lines into `(trigger_rect, dest_tile)`. `game.try_warp()` snaps the hero+camera when Down is pressed over a trigger. The vault is a sealed region of the same grid placed past the flag.

**Tech Stack:** Python 3.13, Pygame 2.6, pytest.

**Reference spec:** `docs/superpowers/specs/2026-06-01-warp-pipes-design.md`

**Conventions:** `PYTHONPATH=<repo> SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m pytest`; commits end with the `Co-Authored-By` trailer.

---

## Task 1: Pipe tiles — solid + colors + art

**Files:** Modify `game/entities/block.py` (DONE: `T`,`t` added to `SOLID_KINDS`), `game/settings.py`, `game/assets.py`

- [ ] **Step 1: Colors** — append to `game/settings.py` (after the Koopa block):

```python
# --- Pipes ---
PIPE    = (84, 138, 74)
PIPE_DK = (54, 92, 50)
```

- [ ] **Step 2: Art** — in `game/assets.py` `draw_block`, add two branches before the final `else`/return:

```python
    elif kind == "t":                     # pipe shaft
        pygame.draw.rect(surface, S.PIPE, rect)
        pygame.draw.rect(surface, S.PIPE_DK, (rect.right - 8, rect.y, 8, rect.h))   # shaded side
        pygame.draw.line(surface, S.CREAM, (rect.x + 4, rect.y), (rect.x + 4, rect.bottom), 2)
    elif kind == "T":                     # pipe mouth (overhanging rim)
        body = pygame.Rect(rect.x, rect.y + 12, rect.w, rect.h - 12)
        pygame.draw.rect(surface, S.PIPE, body)
        pygame.draw.rect(surface, S.PIPE_DK, (body.right - 8, body.y, 8, body.h))
        rim = pygame.Rect(rect.x - 2, rect.y, rect.w + 4, 12)
        pygame.draw.rect(surface, S.PIPE, rim)
        pygame.draw.rect(surface, S.INK, rim, 2)
        pygame.draw.line(surface, S.CREAM, (rim.x + 4, rim.y + 3), (rim.right - 4, rim.y + 3), 2)
```

- [ ] **Step 3: Visual check** — render `tt`/`TT` (a 2-wide, 2-tall pipe) to `tools/_preview/pipe.png`; confirm it reads as a green pipe with a lipped mouth; tune. **Step 4: Commit** (`feat: pipe tiles (solid + art)`).

---

## Task 2: Warp parsing in the level (TDD)

**Files:** Modify `game/level.py`; Test `tests/test_warp.py`

- [ ] **Step 1: Failing test** — create `tests/test_warp.py`

```python
import os, tempfile
import pygame
from game import settings as S
from game.level import Level

LEVEL = """# type: underground
# warp: 3,2 -> 7,5
XX..TT..XX
XXXXXXXXXX
"""

def _write(tmp, text):
    p = os.path.join(tmp, "w.txt")
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    return p

def test_warp_parses_to_trigger_and_dest(tmp_path):
    p = _write(str(tmp_path), LEVEL)
    lvl = Level(p)
    assert len(lvl.warps) == 1
    trig, dest = lvl.warps[0]
    assert trig == pygame.Rect(3 * S.TILE, 2 * S.TILE, S.TILE, S.TILE)
    assert dest == (7, 5)

def test_pipe_tiles_are_solid(tmp_path):
    p = _write(str(tmp_path), LEVEL)
    lvl = Level(p)
    assert any(b.kind == "T" for b in lvl.blocks)
    assert pygame.Rect(4 * S.TILE, 0 * S.TILE, S.TILE, S.TILE) in lvl.solids
```

- [ ] **Step 2: Run → fail** (`AttributeError: warps`).

- [ ] **Step 3: Implement in `game/level.py`.** Add `import pygame` at the top. In `__init__`, add `self.warps = []` before `self._load(path)`, and after `self.solids = ...` add:

```python
        self.play_width = self.flag.rect.right if self.flag else self.width_px
```

In `_load`, collect warp specs in the comment loop:

```python
        warp_specs = []
        for line in raw:
            if line.startswith("#"):
                if "type:" in line:
                    self.area_type = line.split("type:", 1)[1].strip()
                elif "warp:" in line:
                    warp_specs.append(line.split("warp:", 1)[1].strip())
                continue
            if line != "":
                rows.append(line)
```

and at the END of `_load`, convert them (grid dims are known by then):

```python
        for spec in warp_specs:
            entry, dest = spec.split("->")
            ex, ey = (int(v) for v in entry.strip().split(","))
            dx, dy = (int(v) for v in dest.strip().split(","))
            self.warps.append((pygame.Rect(ex * S.TILE, ey * S.TILE, S.TILE, S.TILE), (dx, dy)))
```

- [ ] **Step 4: Run → pass** (new tests + full suite). **Step 5: Commit** (`feat: parse # warp: directives + play_width`).

---

## Task 3: try_warp + Down key + music (TDD)

**Files:** Modify `game/game.py`; Test `tests/test_game.py`

- [ ] **Step 1: Failing test** — append to `tests/test_game.py`

```python
def test_down_on_trigger_teleports_hero():
    g = Game(); g.new_game(); g.state = "PLAYING"
    import pygame
    trig = pygame.Rect(5 * 40, 6 * 40, 40, 40)
    g.level.warps = [(trig, (9, 10))]
    # stand the hero on top of the trigger tile
    g.player.x = float(trig.x); g.player.y = float(trig.top - g.player.h)
    g.player.on_ground = True
    g.try_warp()
    assert g.player.x == 9 * 40 and g.player.rect.bottom == 10 * 40


def test_down_off_trigger_does_nothing():
    g = Game(); g.new_game(); g.state = "PLAYING"
    import pygame
    g.level.warps = [(pygame.Rect(5 * 40, 6 * 40, 40, 40), (9, 10))]
    g.player.x = 800.0; g.player.y = 100.0; g.player.on_ground = True
    before = (g.player.x, g.player.y)
    g.try_warp()
    assert (g.player.x, g.player.y) == before
```

- [ ] **Step 2: Run → fail** (`AttributeError: try_warp`).

- [ ] **Step 3: Implement in `game/game.py`.** Add the Down branch in `handle_events` after the `K_e` branch:

```python
                elif event.key in (pygame.K_DOWN, pygame.K_s) and self.state == "PLAYING":
                    self.try_warp()
```

Add the method (near `grab_or_throw`):

```python
    def try_warp(self):
        p = self.player
        if not p.on_ground:
            return
        foot = (p.rect.centerx, p.rect.bottom + 2)
        for trig, (dx, dy) in self.level.warps:
            if trig.collidepoint(*foot):
                p.x = float(dx * S.TILE)
                p.y = float(dy * S.TILE - p.h)
                p.vx = p.vy = 0.0
                self.camera.update(p.rect)
                self.sfx.play("power")
                self.popup(p.rect.centerx, p.rect.top, "WARP")
                return
```

Change the music line in `update` from `self.level.width_px` to the play width:

```python
        seg = levelset.segment_track(min(self.player.x, self.level.play_width), self.level.play_width)
```

- [ ] **Step 4: Run → pass** (new tests + full suite). **Step 5: Commit** (`feat: try_warp + Down key + main-path music`).

---

## Task 4: level_3 content (pipe + vault) + verify + rebuild + merge

**Files:** Modify `levels/level_3.txt` (via the build script below)

- [ ] **Step 1: Build the pipe + vault** with this deterministic script (avoids hand-counting columns):

```python
# tools/_build_vault.py  (run once; not committed)
W = 116
path = "levels/level_3.txt"
with open(path, encoding="utf-8") as f:
    lines = [l.rstrip("\n") for l in f]
hdr = [l for l in lines if l.startswith("#")]
rows = [l for l in lines if not l.startswith("#") and l != ""]
grid = [list(r.ljust(W, ".")) for r in rows]   # 15 rows, padded to W

def put(r, c, ch): grid[r][c] = ch
def fill(r, c0, c1, ch):
    for c in range(c0, c1 + 1): put(r, c, ch)

# entry pipe at cols 40-41, mouth row 11, body row 12 (floor is rows 13-14)
assert grid[13][40] == "X" and grid[13][41] == "X", "entry pipe must stand on floor"
for c in (40, 41):
    put(11, c, "T"); put(12, c, "t")

# sealed vault cols 95-114
fill(9, 95, 114, "X")            # ceiling
fill(13, 95, 114, "X"); fill(14, 95, 114, "X")   # floor
for r in range(9, 15):
    put(r, 95, "X"); put(r, 114, "X")            # walls
for r in (10, 11, 12):
    fill(r, 98, 109, "C")        # coins
put(11, 111, "T"); put(11, 112, "T")             # return pipe mouth
put(12, 111, "t"); put(12, 112, "t")             # return pipe shaft

warps = ["# warp: 40,11 -> 96,13", "# warp: 41,11 -> 96,13",
         "# warp: 111,11 -> 46,13", "# warp: 112,11 -> 46,13"]
out = ["# type: underground"] + warps + ["".join(r).rstrip() for r in grid]
with open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(out) + "\n")
print("rebuilt", path)
```

Run: `PYTHONPATH=. python tools/_build_vault.py`.

- [ ] **Step 2: Full suite** green (`Level(level_3)` now loads pipes + warps).
- [ ] **Step 3: Smoke (headless)** — place the hero on the entry pipe mouth, `try_warp()` → x is in the vault (>3700); place on the return pipe mouth, `try_warp()` → x back near col 46. No crash.
- [ ] **Step 4: Traversal** — `python tools/traverse.py` completes all 5 levels (the bot jumps the pipe; it never presses Down).
- [ ] **Step 5: Visual check** — render a frame of the vault and the entry pipe to confirm placement reads correctly.
- [ ] **Step 6: Rebuild** `dist/SuperClaudeBros.exe`; **merge** `warp-pipes` → `main` (`--no-ff`), delete branch.

---

## Self-review
Spec coverage: tiles+art (T1), warp parse + play_width (T2), try_warp + Down + music (T3), content+verify (T4), tests (T2/T3). Types consistent: `Level.warps` = list of `(Rect, (dx,dy))`, `Level.play_width`, `game.try_warp`, `S.PIPE/PIPE_DK`, tiles `T`/`t`. Dest convention (`player.bottom = dy*TILE`, `player.x = dx*TILE`) identical in spec, test, and `try_warp`.
