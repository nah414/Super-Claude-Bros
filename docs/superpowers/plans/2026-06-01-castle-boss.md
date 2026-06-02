# Castle + Iron Koopa Boss Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans. Steps use `- [ ]` tracking.

**Goal:** Turn `level_4` into a lava castle ending in a stomp-proof Iron Koopa beaten by 3 fireballs; clearing it advances to World 2.

**Architecture:** `level.boss` (separate from `level.enemies`) + `game.boss_shots`. Boss paces/shoots/takes fireball hits; lava is a non-solid death tile; respawn reloads the level. Art via the seam.

**Tech Stack:** Python 3.13, Pygame 2.6, pytest. **Reference spec:** `docs/superpowers/specs/2026-06-01-castle-boss-design.md`

**Build rule:** after rebuilding the exe, CONFIRM PyInstaller prints `Build complete!` (a truncated build once shipped a dead-input exe).

---

## Task 1: Constants + castle theming

- [ ] **settings.py** — append:
```python
# --- Castle / Boss ---
CASTLE_BG     = (26, 16, 18)
CASTLE_GROUND = (54, 42, 46)
CASTLE_EDGE   = (122, 74, 64)
LAVA          = (226, 94, 38)
LAVA_GLOW     = (250, 176, 80)
BOSS_SIZE          = (58, 58)
BOSS_HP            = 3
BOSS_SPEED         = 1.1
BOSS_FLASH         = 30
BOSS_SHOT_SIZE     = 18
BOSS_SHOT_SPEED    = 4.5
BOSS_SHOT_LIFE     = 150
BOSS_SHOT_COOLDOWN = 90
BOSS_SCORE         = 5000
```
- [ ] **assets.py** — `draw_background` castle branch; `draw_block` castle stone colors; add `draw_lava`, `draw_boss`, `draw_boss_shot` (see spec §6; tune at visual check).
- [ ] Visual check pipe/lava/boss preview; commit.

## Task 2: Boss + BossShot entities (TDD)

- [ ] **tests/test_boss.py**:
```python
import pygame
from game import settings as S
from game.entities.boss import Boss

def test_boss_takes_three_fireballs():
    b = Boss(100, 100)
    assert b.hp == S.BOSS_HP
    assert b.hit() is False and b.hp == S.BOSS_HP - 1
    b.flash = 0
    assert b.hit() is False
    b.flash = 0
    assert b.hit() is True and not b.alive

def test_flash_blocks_rapid_hits():
    b = Boss(100, 100)
    b.hit()
    assert b.hit() is False and b.hp == S.BOSS_HP - 1   # ignored during flash

def test_boss_shoots_on_cooldown():
    lvl = type("L", (), {"solids": []})()
    b = Boss(100, 100)
    fired = sum(1 for _ in range(S.BOSS_SHOT_COOLDOWN * 2 + 4) if (b.update(lvl) or b.ready_to_shoot()))
    assert fired >= 1
```
- [ ] **game/entities/boss.py** (spec §3): `Boss(Entity)` — `hp`, `flash`, `shot_timer`, `direction`, `score=BOSS_SCORE`; `hit()`; `update(level)` (gravity + pace + ledge/wall reverse + decrement flash/shot_timer); `ready_to_shoot()`; `draw` → `assets.draw_boss(surface, cam.apply(rect), direction, flash>0)`.
- [ ] **game/entities/boss_shot.py** (spec §4): `BossShot(x,y,direction)` straight horizontal, `life`, `draw` → `assets.draw_boss_shot`.
- [ ] Run → pass; commit.

## Task 3: level.py parse + draw

- [ ] **level.py**: `import pygame`, `from game import assets`, `from game.entities.boss import Boss`. In `__init__` init `self.lava = []`, `self.boss = None`. Parse `L` → `self.lava.append(pygame.Rect(x, y, S.TILE, S.TILE))`; `Z` → `self.boss = Boss(x, y)`. In `draw`: after blocks, `for r in self.lava: assets.draw_lava(surface, camera.apply(r))`; after enemies, `if self.boss and self.boss.alive: self.boss.draw(surface, camera)`.
- [ ] (`L`/`Z` are NOT added to `SOLID_KINDS`.) Run suite; commit.

## Task 4: Game integration (TDD)

- [ ] **tests/test_game.py** add: fireball defeats boss → `LEVEL_COMPLETE`; boss stomp-proof (top contact damages a big player to small); lava costs a life; death reloads level (used box returns). (See spec §7.)
- [ ] **game.py**:
  - import `from game.entities.boss import Boss` and `from game.entities.boss_shot import BossShot`.
  - `start_level`: add `self.boss_shots = []` and `self.cleared_boss = False`.
  - `respawn`: **reload the level** (mirror `start_level`'s level/player/list setup incl. `self.boss_shots = []` and carry-power re-apply), end in `state="PLAYING"`.
  - `update`: after enemy updates, drive the boss:
```python
        if self.level.boss and self.level.boss.alive:
            self.level.boss.update(self.level)
            if self.level.boss.ready_to_shoot():
                d = 1 if self.player.rect.centerx >= self.level.boss.rect.centerx else -1
                self.boss_shots.append(BossShot(self.level.boss.rect.centerx, self.level.boss.rect.centery, d))
                self.sfx.play("fire")
        for s in self.boss_shots:
            s.update(self.level)
        self.boss_shots = [s for s in self.boss_shots if s.alive]
```
  - `handle_fireballs`: after the enemy loop, also test the boss:
```python
            b = self.level.boss
            if f.alive and b and b.alive and f.rect.colliderect(b.rect):
                f.alive = False
                if b.hit():
                    self.boss_defeated()
                else:
                    self.sfx.play("stomp")
```
  - add `boss_defeated()` (score, popup, "win" sfx, `cleared_boss=True`, `state="LEVEL_COMPLETE"`) and `handle_boss()` (boss body + each boss shot → `take_damage`; `lose_life` returns True).
  - `update` collision section: `if self.handle_boss(): return` (after `handle_enemies`); and after the pit check, `if any(self.player.rect.colliderect(l) for l in self.level.lava): self.lose_life()`.
  - `draw`: after `level.draw`, `for s in self.boss_shots: s.draw(self.screen, self.camera)`; LEVEL_COMPLETE banner shows `f"WORLD {levelset.world_label(self.index)[0]} CLEARED!"` when `self.cleared_boss` else "LEVEL COMPLETE!".
- [ ] Run suite; commit.

## Task 5: level_4 castle content + verify + rebuild + merge

- [ ] Generate `levels/level_4.txt` as the castle (script `tools/_build_castle.py`, not committed): ceiling row 1; floor rows 13-14 with 2-wide lava pools in gaps; two `M` boxes (row 10) before the arena; arena with a right wall; boss `Z` on the arena floor; `P` spawn left; no flag. All non-lava gaps ≤3.
- [ ] Boss smoke (headless): give player fire in the arena, throw fireballs → boss dies → `LEVEL_COMPLETE`; a boss shot hurts; lava kills.
- [ ] Traversal: levels 1/2/3/5 complete; castle — bot reaches the arena x.
- [ ] Visual check the castle + boss in-level.
- [ ] Rebuild exe; **confirm `Build complete!`**; merge `castle-boss` → `main` (`--no-ff`), delete branch.

---

## Self-review
Spec coverage: theming (T1), boss/shot (T2), parse/draw (T3), integration+lava+respawn-reload+banner (T4), content+verify (T5), tests (T2/T4). Types: `Boss.hit/hp/flash/ready_to_shoot/score`, `BossShot`, `level.boss`, `level.lava`, `game.boss_shots/cleared_boss/boss_defeated/handle_boss`, `S.BOSS_*`/`LAVA*`/`CASTLE_*`. `L`/`Z` non-solid (NOT in SOLID_KINDS).
