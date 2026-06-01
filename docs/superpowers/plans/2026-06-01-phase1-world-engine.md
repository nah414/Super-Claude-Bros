# Phase 1: World Engine + Music — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the single-level game into a sequenced, themed, multi-level game with looping music, title/intro/victory screens, and persistent stats.

**Architecture:** A pure `levelset.py` owns the level order + World X-Y labels + music-track mapping. `Level` gains a `# type:` header → `area_type`, which threads through `assets.draw_background`/`draw_block` for overworld vs. underground theming. `game.py` gains a state machine (title → intro → play → complete → next/victory; game-over) and a `MusicManager` that loops a pre-rendered track per level. Music tracks are pre-rendered by `tools/make_music.py` (pure-stdlib synth) to `music/*.wav`.

**Tech Stack:** Python 3.13, Pygame 2.6, pytest (no new deps — music is stdlib synth).

**Reference spec:** `docs/superpowers/specs/2026-06-01-phase1-world-engine-design.md`

**Parallelization:** Tasks 1 (levelset), 2 (music), 3 (level content) touch only NEW disjoint files and are independent. The music render (Task 2) is the slow compute step — run it in the background while building Tasks 4-7 (the interlocking edits to existing files). Task 7 (game.py integration) depends on all prior.

**Conventions:** `PYTHONPATH=<repo> SDL_VIDEODRIVER=dummy python -m pytest`; headless smokes add `SDL_AUDIODRIVER=dummy`; commits end with the `Co-Authored-By` trailer.

---

## File Structure

| File | Responsibility |
|---|---|
| `game/levelset.py` (new) | Pure: level order, `world_label`, `track_number`, `next_index` |
| `game/music.py` (new) | `MusicManager` — loop one pre-rendered track per level |
| `tools/make_music.py` (new) | Pre-render 5 looping synthwave tracks → `music/track_*.wav` |
| `music/track_1..5.wav` (new data) | The looping tracks (committed + bundled) |
| `levels/level_1..5.txt` (new) | 5 sequenced levels (with `# type:` headers) |
| `game/level.py` (mod) | Parse `# type:` header → `area_type`; thread to block draws |
| `game/entities/block.py` (mod) | `Block.draw` accepts `area_type` |
| `game/assets.py` (mod) | `draw_background`/`draw_block` branch on `area_type`; underground theme |
| `game/settings.py` (mod) | Underground palette + music volume |
| `game/hud.py` (mod) | Show dynamic World X-Y |
| `game/game.py` (mod) | State machine, screens, level advance, music, persistent stats |
| `tests/test_levelset.py` (new) | Sequence logic |
| `tests/test_level.py` (mod) | `# type:` header parse |

---

## Task 1: `levelset.py` — pure sequence logic (TDD) — *independent*

**Files:** Create `game/levelset.py`, `tests/test_levelset.py`

- [ ] **Step 1: Failing test** — `tests/test_levelset.py`

```python
from game import levelset as L

def test_world_label():
    assert L.world_label(0) == "1-1"
    assert L.world_label(3) == "1-4"
    assert L.world_label(4) == "2-1"

def test_track_number_cycles_every_5():
    assert L.track_number(0) == 1
    assert L.track_number(4) == 5
    assert L.track_number(5) == 1

def test_next_index_ends_at_none():
    assert L.next_index(0) == 1
    assert L.next_index(L.level_count() - 1) is None
```

- [ ] **Step 2: Run → fail** (`python -m pytest tests/test_levelset.py` → no module).

- [ ] **Step 3: Implement** `game/levelset.py`

```python
"""Pure level-sequence logic: order, World X-Y labels, music track per level."""
LEVELS = ["level_1.txt", "level_2.txt", "level_3.txt", "level_4.txt", "level_5.txt"]
TRACKS = 5

def level_count():
    return len(LEVELS)

def level_file(index):
    return LEVELS[index]

def world_label(index):
    return f"{index // 4 + 1}-{index % 4 + 1}"

def track_number(index):
    return index % TRACKS + 1

def next_index(index):
    nxt = index + 1
    return nxt if nxt < len(LEVELS) else None
```

- [ ] **Step 4: Run → pass.** **Step 5: Commit** (`feat: level-sequence logic (tested)`).

---

## Task 2: Music — synth tool + render + `MusicManager` — *independent (run render in background)*

**Files:** Create `tools/make_music.py`, `game/music.py`, `music/track_1..5.wav`

- [ ] **Step 1: Create `tools/make_music.py`**

```python
"""Pre-render 5 seamlessly-looping soft-synthwave tracks to music/track_N.wav.
Pure stdlib. Run from repo root: python tools/make_music.py"""
import array, math, os, wave

SR = 44100
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "music")

def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12.0)

# (bpm, root_midi, [4 triads as semitone offsets]) — five gentle minor-ish moods
TRACKS = [
    (92,  57, [[0, 3, 7], [-2, 3, 7], [-4, 0, 3], [-5, 2, 7]]),
    (100, 60, [[0, 3, 7], [5, 8, 12], [3, 7, 10], [-2, 2, 5]]),
    (88,  53, [[0, 4, 7], [-3, 0, 4], [2, 5, 9], [-5, -1, 2]]),
    (104, 55, [[0, 3, 7], [-5, -2, 2], [-4, 0, 3], [-2, 1, 5]]),
    (96,  58, [[0, 3, 8], [-1, 4, 7], [-4, 0, 5], [-6, -2, 1]]),
]

def render(bpm, root, chords):
    beat = 60.0 / bpm
    bar = beat * 4
    total = bar * len(chords)              # loop = 4 bars
    n = int(total * SR)
    buf = [0.0] * n
    for i in range(n):
        t = i / SR
        chord = chords[int(t / bar) % len(chords)]
        s = 0.0
        for off in chord:                  # warm pad triad
            s += 0.16 * math.sin(2 * math.pi * midi(root + off) * t)
        s += 0.22 * math.sin(2 * math.pi * midi(root + chord[0] - 12) * t)   # bass
        an = chord[int(t / (beat / 2)) % len(chord)]                          # 8th-note arp
        ph = (t % (beat / 2)) / (beat / 2)
        s += 0.15 * max(0.0, 1.0 - ph) ** 2 * math.sin(2 * math.pi * midi(root + an + 12) * t)
        kph = (t % beat) / beat                                               # soft kick
        kenv = max(0.0, 1.0 - kph * 6)
        if kenv > 0:
            s += 0.5 * kenv * math.sin(2 * math.pi * (90 - 45 * min(1.0, kph * 6)) * t)
        buf[i] = s
    # seamless wrap: crossfade tail into head (~15ms)
    fade = min(660, n // 8)
    for k in range(fade):
        a = k / fade
        buf[n - fade + k] = buf[n - fade + k] * (1 - a) + buf[k] * a
    peak = max(1e-6, max(abs(x) for x in buf))
    g = 0.82 / peak
    return array.array("h", (int(max(-1.0, min(1.0, x * g)) * 32767) for x in buf))

def main():
    os.makedirs(OUT, exist_ok=True)
    for i, (bpm, root, chords) in enumerate(TRACKS, 1):
        samples = render(bpm, root, chords)
        with wave.open(os.path.join(OUT, f"track_{i}.wav"), "w") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes(samples.tobytes())
        print(f"track_{i}.wav  {len(samples)} samples")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Render** (slow — run in background): `python tools/make_music.py`. Expected: 5 wavs in `music/`.

- [ ] **Step 3: Create `game/music.py`**

```python
"""Loops one pre-rendered track per level. Silent no-op if no audio device."""
import pygame
from game import settings as S
from game import levelset


class MusicManager:
    def __init__(self):
        self.enabled = pygame.mixer.get_init() is not None
        self.current = None
        if self.enabled:
            try:
                pygame.mixer.music.set_volume(S.MUSIC_VOLUME)
            except Exception:
                self.enabled = False

    def play_for_level(self, index):
        if not self.enabled:
            return
        track = levelset.track_number(index)
        if track == self.current:
            return
        self.current = track
        try:
            pygame.mixer.music.load(S.resource_path(f"music/track_{track}.wav"))
            pygame.mixer.music.play(loops=-1)
        except Exception:
            self.enabled = False

    def stop(self):
        if self.enabled:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
        self.current = None
```

- [ ] **Step 4: Smoke** (after wavs exist): construct `MusicManager`, `play_for_level(0)`, `stop()` headless — no crash. **Step 5: Commit** (`feat: procedural looping music (synth tool + manager + tracks)`).

---

## Task 3: 5 level files (with area headers) — *independent*

**Files:** Create `levels/level_1..5.txt`

- [ ] **Step 1: Generate the 5 levels** (run; produces aligned, completable maps — overworld + underground mix):

```python
PYTHONPATH=. python - <<'PY'
import os
REPO = "."
def grid(W=88, H=15):
    return [["."] * W for _ in range(H)]
def ground(g, gaps, rows=(13, 14)):
    cols = {c for s, w in gaps for c in range(s, s + w)}
    for r in rows:
        for c in range(len(g[0])):
            if c not in cols:
                g[r][c] = "X"
def save(name, header, g):
    with open(os.path.join(REPO, "levels", name), "w", encoding="utf-8") as f:
        f.write(header + "\n" + "\n".join("".join(r) for r in g) + "\n")

# L1 overworld (gentle intro)
g = grid(); ground(g, [(20, 3), (45, 3)]); g[12][2] = "P"
for c in (8,9,10,11): g[12][c] = "C"
g[9][26]="B"; g[9][27]="?"; g[9][28]="M"; g[9][29]="B"
g[12][34]="G"; g[12][60]="G"; g[6][50]="Y"
g[8][82]="F"; save("level_1.txt", "# type: overworld", g)

# L2 overworld (more gaps + platforms)
g = grid(); ground(g, [(16,3),(33,3),(55,3)]); g[12][2]="P"
for c in range(30,34): g[10][c]="="; g[9][c]="C"
g[9][20]="?"; g[12][24]="G"; g[12][48]="G"; g[7][40]="Y"; g[7][66]="Y"
g[8][82]="F"; save("level_2.txt", "# type: overworld", g)

# L3 underground (cave)
g = grid(); ground(g, [(24,3),(50,3)]); 
for c in range(88): g[1][c]="X"           # ceiling
g[12][2]="P"
for c in (9,10,11): g[12][c]="C"
g[9][18]="B"; g[9][19]="?"; g[9][20]="B"; g[12][30]="G"; g[12][56]="G"; g[10][44]="="; g[10][45]="="; g[10][46]="="
g[8][82]="F"; save("level_3.txt", "# type: underground", g)

# L4 underground (tighter)
g = grid(); ground(g, [(19,3),(38,3),(62,3)])
for c in range(88): g[1][c]="X"
g[12][2]="P"
g[9][26]="?"; g[9][27]="M"; g[12][34]="G"; g[12][52]="G"; g[6][46]="Y"
for c in range(70,74): g[10][c]="="; g[9][c]="C"
g[8][82]="F"; save("level_4.txt", "# type: underground", g)

# L5 overworld (finale)
g = grid(); ground(g, [(17,3),(37,3),(58,3),(72,3)]); g[12][2]="P"
for c in (8,9,10,11,12): g[12][c]="C"
g[9][22]="B"; g[9][23]="?"; g[9][24]="M"; g[9][25]="B"
g[12][30]="G"; g[12][48]="G"; g[12][66]="G"; g[6][40]="Y"; g[7][64]="Y"
for c in range(31,36): g[10][c]="="; g[9][c]="C"
g[8][84]="F"; save("level_5.txt", "# type: overworld", g)
print("wrote 5 levels")
PY
```

- [ ] **Step 2: Commit** (`feat: 5 sequenced starter levels (overworld + underground)`). *(Completability verified in Task 8.)*

---

## Task 4: `Level` area-type header (TDD) + block draw threading

**Files:** Modify `game/level.py`, `game/entities/block.py`, `tests/test_level.py`

- [ ] **Step 1: Failing test** — add to `tests/test_level.py`

```python
def test_area_type_header(tmp_path):
    p = tmp_path / "l.txt"; p.write_text("# type: underground\nP..F\nXXXX\n")
    assert Level(str(p)).area_type == "underground"
    p2 = tmp_path / "l2.txt"; p2.write_text("P..F\nXXXX\n")
    assert Level(str(p2)).area_type == "overworld"
```

- [ ] **Step 2: Run → fail.**

- [ ] **Step 3: Implement.** In `game/level.py` `_load`, replace the file-read + row-filter prologue with header handling:

```python
    def _load(self, path):
        self.area_type = "overworld"
        with open(path, encoding="utf-8") as f:
            raw = [line.rstrip("\n") for line in f]
        rows = []
        for line in raw:
            if line.startswith("#"):
                if "type:" in line:
                    self.area_type = line.split("type:", 1)[1].strip()
                continue
            if line != "":
                rows.append(line)
        self.rows = len(rows)
        self.cols = max((len(r) for r in rows), default=0)
        for j, row in enumerate(rows):
            # ... existing per-char parsing unchanged ...
```

In `Level.draw`, pass area type to blocks: `b.draw(surface, camera, self.area_type)`.

In `game/entities/block.py`, update draw:

```python
    def draw(self, surface, camera, area_type="overworld"):
        assets.draw_block(surface, camera.apply(self.rect), self.kind, self.used, area_type)
```

- [ ] **Step 4: Run → pass** (test_level + test_levelset). **Step 5: Commit** (`feat: level area-type header + themed block draw`).

---

## Task 5: Settings + `assets` area theming

**Files:** Modify `game/settings.py`, `game/assets.py`

- [ ] **Step 1: Append to `game/settings.py`**

```python
# --- Underground theme ---
CAVE_BG     = (12, 12, 14)
CAVE_GROUND = (46, 44, 52)
CAVE_EDGE   = (96, 92, 110)
CAVE_CEIL   = (28, 26, 34)

# --- Music ---
MUSIC_VOLUME = 0.5
```

- [ ] **Step 2: Update `assets.draw_background`** to branch on area type:

```python
def draw_background(surface, camera, area_type="overworld"):
    if area_type == "underground":
        surface.fill(S.CAVE_BG)
        pygame.draw.rect(surface, S.CAVE_CEIL, (0, 0, S.WIDTH, 30))
        return
    surface.fill(S.NIGHT)
    pygame.draw.circle(surface, S.MOON, (S.WIDTH - 90, 90), 34)
    pygame.draw.circle(surface, S.NIGHT, (S.WIDTH - 78, 82), 30)
    shift = int(camera.offset_x * 0.3)
    for sx, sy in _STARS:
        x = (sx - shift) % S.WIDTH
        pygame.draw.circle(surface, S.CREAM, (x, sy), 2)
```

- [ ] **Step 3: Update `assets.draw_block`** signature + ground colors by area:

```python
def draw_block(surface, rect, kind, used=False, area_type="overworld"):
    ground = S.CAVE_GROUND if area_type == "underground" else S.GROUND_DARK
    edge = S.CAVE_EDGE if area_type == "underground" else S.GROUND_EDGE
    if kind == "X":
        pygame.draw.rect(surface, ground, rect)
        pygame.draw.rect(surface, edge, (rect.x, rect.y, rect.w, 4))
        pygame.draw.rect(surface, S.INK, rect, 1)
    elif kind == "=":
        pygame.draw.rect(surface, ground, rect, border_radius=6)
        pygame.draw.rect(surface, edge, (rect.x + 3, rect.y + 2, rect.w - 6, 4))
        pygame.draw.rect(surface, S.INK, rect, 1, border_radius=6)
    elif kind == "B":
        pygame.draw.rect(surface, S.BRICK_DARK, rect)
        pygame.draw.rect(surface, S.INK, rect, 1)
        pygame.draw.line(surface, S.INK, (rect.left, rect.centery), (rect.right, rect.centery), 1)
        pygame.draw.line(surface, S.INK, (rect.centerx, rect.top), (rect.centerx, rect.centery), 1)
    elif kind in ("?", "M"):
        pygame.draw.rect(surface, S.MIDGRAY if used else S.BLUE, rect, border_radius=4)
        pygame.draw.rect(surface, S.INK, rect, 2, border_radius=4)
        if not used:
            q = _question_font().render("?", True, S.CREAM)
            surface.blit(q, q.get_rect(center=rect.center))
```

- [ ] **Step 4: Smoke** (render overworld + underground frames headless, no crash). **Step 5: Commit** (`feat: underground theme + area-typed backgrounds/blocks`).

---

## Task 6: HUD dynamic World X-Y

**Files:** Modify `game/hud.py`

- [ ] **Step 1: Update `HUD.draw`** to take a `world` label:

```python
    def draw(self, surface, score, sparks, lives, world="1-1"):
        bar = pygame.Surface((S.WIDTH, 40), pygame.SRCALPHA)
        bar.fill((20, 20, 19, 190))
        surface.blit(bar, (0, 0))
        pygame.draw.line(surface, S.GROUND_EDGE, (0, 40), (S.WIDTH, 40), 2)
        text = f"SCORE {score:06d}    SPARKS {sparks:02d}    LIVES {lives}    WORLD {world}"
        surface.blit(self.font.render(text, True, S.CREAM), (16, 8))
```

- [ ] **Step 2: Commit** (folded into Task 7's commit, since the caller changes there).

---

## Task 7: `game.py` — state machine, screens, level flow, music, persistence

**Files:** Modify `game/game.py`

- [ ] **Step 1: Replace `game/game.py`** with the integrated version:

```python
import pygame
from game import settings as S
from game import assets
from game import levelset
from game.level import Level
from game.camera import Camera
from game.entities.player import Player
from game.entities.mushroom import Mushroom
from game.hud import HUD
from game.sound import SoundFX
from game.music import MusicManager
from game.scoring import bonus_lives
from game.effects import ScorePopup, RisingToken

JUMP_KEYS = (pygame.K_SPACE, pygame.K_UP, pygame.K_w)
INTRO_FRAMES = 72        # ~1.2s at 60fps


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((S.WIDTH, S.HEIGHT))
        pygame.display.set_caption(S.TITLE)
        self.clock = pygame.time.Clock()
        self.hud = HUD()
        self.big_font = pygame.font.SysFont("Poppins,Arial", 56, bold=True)
        self.small_font = pygame.font.SysFont("Poppins,Arial", 26, bold=True)
        self.sfx = SoundFX()
        self.music = MusicManager()
        self.running = True
        self.state = "TITLE"

    # --- lifecycle ---
    def new_game(self):
        self.score = 0
        self.tokens = 0
        self.lives = S.START_LIVES
        self.index = 0
        self.start_level()

    def start_level(self):
        self.level = Level(S.resource_path("levels/" + levelset.level_file(self.index)))
        self.player = Player(*self.level.player_spawn)
        self.camera = Camera(self.level.width_px)
        self.mushrooms = []
        self.effects = []
        self.intro_timer = INTRO_FRAMES
        self.music.play_for_level(self.index)
        self.state = "LEVEL_INTRO"

    def respawn(self):
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
        g = bonus_lives(old, self.tokens)
        if g:
            self.lives += g
            self.popup(x, y - 40, "1-UP")
            self.sfx.play("power")
        self.sfx.play("token")

    def lose_life(self):
        self.lives -= 1
        self.sfx.play("hurt")
        if self.lives <= 0:
            self.music.stop()
            self.state = "GAME_OVER"
        else:
            self.respawn()

    # --- main loop ---
    def run(self):
        while self.running:
            self.handle_events()
            if self.state == "PLAYING":
                self.update()
            elif self.state == "LEVEL_INTRO":
                self.intro_timer -= 1
                if self.intro_timer <= 0:
                    self.state = "PLAYING"
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
                elif event.key == pygame.K_RETURN:
                    if self.state == "TITLE":
                        self.new_game()
                    elif self.state in ("GAME_OVER", "GAME_COMPLETE"):
                        self.music.stop()
                        self.state = "TITLE"
                    elif self.state == "LEVEL_COMPLETE":
                        self.advance()
                elif event.key in JUMP_KEYS and self.state == "PLAYING":
                    before = self.player.air_jumped
                    self.player.press_jump(self.now())
                    self.sfx.play("double" if (self.player.air_jumped and not before) else "jump")
            elif event.type == pygame.KEYUP:
                if event.key in JUMP_KEYS and self.state == "PLAYING":
                    self.player.release_jump()

    def advance(self):
        nxt = levelset.next_index(self.index)
        if nxt is None:
            self.music.stop()
            self.state = "GAME_COMPLETE"
        else:
            self.index = nxt
            self.start_level()

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
        if self.level.flag and self.player.rect.colliderect(self.level.flag.rect):
            self.sfx.play("win")
            self.state = "LEVEL_COMPLETE"
            return
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
                    self.sfx.play("hurt")
        return False

    # --- draw ---
    def draw(self):
        if self.state == "TITLE":
            self.draw_title()
        else:
            area = self.level.area_type
            assets.draw_background(self.screen, self.camera, area)
            self.level.draw(self.screen, self.camera)
            for m in self.mushrooms:
                m.draw(self.screen, self.camera)
            self.player.draw(self.screen, self.camera)
            for fx in self.effects:
                fx.draw(self.screen, self.camera, self.hud.font)
            self.hud.draw(self.screen, self.score, self.tokens, self.lives, levelset.world_label(self.index))
            if self.state == "LEVEL_INTRO":
                self.banner(f"WORLD {levelset.world_label(self.index)}", "")
            elif self.state == "LEVEL_COMPLETE":
                self.banner("LEVEL COMPLETE!", "Press ENTER")
            elif self.state == "GAME_OVER":
                self.banner("GAME OVER", "Press ENTER for title")
            elif self.state == "GAME_COMPLETE":
                self.banner("YOU SAVED THE DAY!", "Press ENTER for title")
        pygame.display.flip()

    def draw_title(self):
        self.screen.fill(S.NIGHT)
        assets.draw_player(self.screen, pygame.Rect(S.WIDTH // 2 - 30, 150, 60, 88), 1, "big")
        t = self.big_font.render("SUPER CLAUDE BROS", True, S.ORANGE)
        s = self.small_font.render("Press ENTER to play", True, S.CREAM)
        self.screen.blit(t, t.get_rect(center=(S.WIDTH // 2, 300)))
        self.screen.blit(s, s.get_rect(center=(S.WIDTH // 2, 360)))

    def banner(self, title, subtitle):
        overlay = pygame.Surface((S.WIDTH, S.HEIGHT), pygame.SRCALPHA)
        overlay.fill((20, 20, 19, 150))
        self.screen.blit(overlay, (0, 0))
        t = self.big_font.render(title, True, S.ORANGE)
        self.screen.blit(t, t.get_rect(center=(S.WIDTH // 2, S.HEIGHT // 2 - 16)))
        if subtitle:
            s = self.small_font.render(subtitle, True, S.CREAM)
            self.screen.blit(s, s.get_rect(center=(S.WIDTH // 2, S.HEIGHT // 2 + 34)))
```

- [ ] **Step 2: Integrated smoke** — title→play→advance through levels headless (simulate Enter + frames); assert reaches later levels without crash.
- [ ] **Step 3: Full suite** (`python -m pytest`).
- [ ] **Step 4: Commit** (`feat: world engine — states, screens, level flow, music, persistent stats`) — include `game/hud.py`.

---

## Task 8: Verify, level content, rebuild

- [ ] **Step 1: Full suite** green.
- [ ] **Step 2: Traversal bot per level** — load each of the 5 levels, clear enemies, run the auto-player; assert each reaches the flag (LEVEL_COMPLETE). Fix any uncompletable level's gaps.
- [ ] **Step 3: Integrated play smoke** — from TITLE, Enter, play several hundred frames moving/jumping across level transitions; no crash.
- [ ] **Step 4: Update `.gitignore`** to keep `music/*.wav` (ensure not ignored) and `README.md` (controls/run note: Enter starts). Rebuild the exe with `--add-data "music;music"` added.
- [ ] **Step 5: Commit** tuning + docs.

---

## Self-review checklist
Spec coverage: sequencing (T1), area header+theming (T4/T5), screens+flow+persistence (T7), music (T2), 5 levels (T3), HUD (T6), tests (T1/T4/T8). Types: `levelset.world_label/track_number/next_index`, `Level.area_type`, `Block.draw(...,area_type)`, `draw_background/draw_block(...,area_type)`, `MusicManager.play_for_level/stop`, `HUD.draw(...,world)` — all consistent across tasks.
