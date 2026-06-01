# Super Claude Bros — "Night Update" — Design Spec

**Date:** 2026-06-01
**Status:** Design approved in brainstorming; pending spec review before planning.
**Builds on:** the completed base game (see `2026-06-01-claude-platformer-design.md`).

---

## 1. Vision

A substantial gameplay + visual update to *Super Claude Bros* that deepens the experience while
preserving the clean architecture: a more detailed **Spark Hero** mascot, a **moonlit dark
theme**, a **double-jump**, real **power-ups** (visible token pops and a grow+shield mushroom
from mystery boxes), a **second enemy type**, **score pop-ups + bonus lives**, and **synthesized
sound effects**. All new visuals stay behind the `assets.py` seam; all new world objects follow
the existing `Entity` pattern.

This is an **educational build**: code is written and explained as we go.

## 2. Goals

- Replace the simple hero with the **Spark Hero** (sunburst-headed character), with a larger
  powered-up variant.
- Switch the whole game to the **Claude dark/night theme** (moon + stars, dark ground).
- Add a **double-jump** triggered by a fast second tap of the jump key.
- Make mystery boxes **visibly** emit their contents: spark **tokens** (`?` boxes) and a
  **mushroom** power-up (`M` boxes) that grants **grow + a one-hit shield**.
- Add a **second enemy** — a hovering "Flyer".
- Add **score pop-ups** and an **extra life every 100 tokens**.
- Add **synthesized sound effects** that degrade gracefully when no audio device is present.

## 3. Non-Goals (deferred)

- Fire-Flower / projectile power-up (we chose grow+shield only).
- Additional levels (still one level, now richer).
- A shelled "Koopa" enemy (we chose the Flyer; could add later).
- Music / soundtrack (only short SFX).

---

## 4. New tunable constants (all added to `settings.py`)

```python
# Double-jump
DOUBLE_TAP_MS        = 300      # max gap between taps to trigger the mid-air jump
DOUBLE_JUMP_VELOCITY = -12.0    # ~85% of JUMP_VELOCITY

# Player sizes (w, h) per power state
PLAYER_SMALL = (30, 44)
PLAYER_BIG   = (38, 62)
POWER_INVULN_MS = 1500          # invulnerability (with flicker) after taking a hit while big

# Mushroom power-up
MUSHROOM_SPEED  = 1.6
MUSHROOM_SCORE  = 1000

# Flyer enemy
FLYER_SPEED      = 1.8          # horizontal drift
FLYER_BOB_AMP    = 12           # vertical bob amplitude (px)
FLYER_BOB_PERIOD = 90           # frames per bob cycle
FLYER_RANGE      = 120          # px traveled before reversing horizontal direction
FLYER_SCORE      = 200

# Scoring
TOKEN_SCORE      = 100
STOMP_SCORE      = 200
BONUS_LIFE_EVERY = 100          # tokens per extra life

# Theme (night)
NIGHT       = (20, 20, 19)      # #141413 sky / background
GROUND_DARK = (40, 46, 36)      # ground / platform fill
GROUND_EDGE = (72, 86, 58)      # lit top edge of ground
BRICK_DARK  = (74, 72, 66)      # brick fill on dark theme
MOON        = (232, 230, 210)

# Audio
SAMPLE_RATE = 44100
```

(Existing `ORANGE`, `CREAM`, `BLUE`, `INK`, `MIDGRAY` are retained.)

## 5. Tile legend additions

| Char | Meaning |
|---|---|
| `M` | mystery box containing a **mushroom** (drawn identically to `?` — contents are a surprise) |
| `Y` | **Flyer** enemy spawn |

`M` is **solid** (`SOLID_KINDS` becomes `("X","=","B","?","M")`). `Y` is a non-solid entity.

---

## 6. Feature designs

### 6.1 Spark Hero mascot (`assets.py`)
Rewrite `draw_player(surface, rect, facing, power)`: a small orange body with a face (cream eyes
+ smile), arms and legs, and the **Anthropic sunburst as a glowing head** above the body, all
fitted to `rect`. Faces left/right via `facing`. The **big** variant is simply the same art
fitted to the larger `PLAYER_BIG` rect, with a brighter/larger sunburst. Drawing fits the rect,
so growth is automatic. **The desktop icon is updated to match**: `tools/make_icon.py` is rewritten to draw the Spark Hero, regenerating `tools/claude.ico`, after which the app is rebuilt so the embedded icon — and therefore the desktop shortcut — shows the new character.

### 6.2 Dark / night theme
- `settings.py` gains the night palette (above).
- New `assets.draw_background(surface, camera)`: fills `NIGHT`, draws a **moon** (fixed
  upper-right) and a **starfield** with gentle parallax (`star_x - camera.offset_x*0.3`, wrapped).
- `assets.draw_block`: ground/platforms use `GROUND_DARK` with a `GROUND_EDGE` top stripe;
  bricks use `BRICK_DARK`; `?`/`M` boxes stay `BLUE`; used boxes go `MIDGRAY`.
- `hud.py`: dark translucent bar (`NIGHT` @ ~180 alpha) with `CREAM` text.
- `game.draw` calls `draw_background` first (replacing the cream fill).

### 6.3 Double-jump (`player.py`)
Time-injectable so it's unit-testable:
- `press_jump(now_ms)`: if `on_ground` → normal jump, set `air_jumped=False`; **elif** not
  `air_jumped` **and** `now_ms - last_jump_ms <= DOUBLE_TAP_MS` → mid-air jump at
  `DOUBLE_JUMP_VELOCITY`, set `air_jumped=True`. Always update `last_jump_ms = now_ms`.
- `release_jump()`: existing variable-height cutoff.
- `update()` resets `air_jumped=False` whenever `on_ground`.
- `game` calls `press_jump(pygame.time.get_ticks())` on jump KEYDOWN, `release_jump()` on KEYUP.

One mid-air jump per airtime; a single mid-air press after walking off a ledge does nothing
(the double-jump is explicitly the fast double-tap trick).

### 6.4 Power-ups & mystery boxes
- **`?` token box** (bumped from below): credit `+1 token, +TOKEN_SCORE`, mark box `used`, and
  spawn a **rising spark** visual + a score pop-up. (Score is credited on the hit, so it can't be
  "missed".)
- **`M` mushroom box** (bumped): mark `used`, spawn a **`Mushroom`** entity that rises out of the
  box over ~0.4s, then becomes active.
- **`Mushroom`** (`entities/mushroom.py`): after emerging, moves horizontally at `MUSHROOM_SPEED`
  with gravity, reversing at walls (via `move_and_collide`). Player overlap → `player.grow()`,
  consume, `+MUSHROOM_SCORE`, pop-up.
- **Player power state** (`player.py`): `power ∈ {"small","big"}`.
  - `grow()`: small→big; set size to `PLAYER_BIG`, raise `y` by the height delta so feet stay put.
  - `take_damage(now_ms)`: if `now_ms < invuln_until` → ignore (return `False`). Else if `big` →
    shrink to small, set `invuln_until = now_ms + POWER_INVULN_MS`, return `False`. Else → return
    `True` (a life is lost). During invulnerability the sprite flickers (draw on alternate frames).
- `game` damage paths (enemy side-hit, pit) route through `player.take_damage`; pit death ignores
  invulnerability (falling always costs a life).

### 6.5 Flyer enemy (`entities/flyer.py`)
Hovering enemy, ignores gravity. Moves horizontally at `FLYER_SPEED`, reversing every
`FLYER_RANGE` px; bobs vertically by `FLYER_BOB_AMP` over `FLYER_BOB_PERIOD` frames (sine on an
internal phase counter). Stompable exactly like a Goomba (falling on top → dies, bounce,
`+FLYER_SCORE`); side contact → damage. Lives in `level.enemies` alongside Goombas. Art: a small
dark-blue creature with little wings and cream eyes.

### 6.6 Score pop-ups + bonus life (`effects.py`, `scoring.py`)
- `effects.ScorePopup(x, y, text)`: rises ~30px and fades over ~0.7s, then is removed. `game`
  holds a `popups` list, updated/drawn each frame; spawned on token/stomp/power-up events.
- `effects.RisingToken(x, y)`: the spark that pops out of a `?` box (rises + fades).
- `scoring.bonus_lives(old_tokens, new_tokens, every=BONUS_LIFE_EVERY)`: pure function returning
  how many life thresholds were crossed. `game` adds that many lives and shows a "1-UP" pop-up.

### 6.7 Sound (`sound.py`)
`SoundFX` synthesizes short tones with `numpy` into `pygame.Sound` objects for: `jump`,
`double`, `token`, `stomp`, `power`, `hurt`, `win`. On construction it tries to (pre)init the
mixer and build the sounds inside `try/except`; any failure (no audio device, missing numpy,
tests) sets `enabled=False` and `play(name)` becomes a silent no-op. `game` calls
`sfx.play(...)` on the matching events. Adds `numpy` to `requirements.txt`.

---

## 7. Architecture & files

**New files**
- `game/entities/mushroom.py` — `Mushroom`
- `game/entities/flyer.py` — `Flyer`
- `game/effects.py` — `ScorePopup`, `RisingToken`
- `game/scoring.py` — `bonus_lives` (pure)
- `game/sound.py` — `SoundFX`

**Modified files**
- `game/settings.py` — new constants + night palette
- `game/assets.py` — Spark Hero `draw_player`, `draw_background`, dark `draw_block`,
  `draw_mushroom`, `draw_flyer`
- `game/player.py` — double-jump, power state, grow/take_damage, invuln flicker, size
- `game/level.py` — parse `M` (block) and `Y` (flyer); add runtime `powerups` list
- `game/game.py` — background draw, box→token/mushroom spawns, power-up & damage logic, flyer,
  pop-ups, bonus life, sound triggers
- `game/hud.py` — dark translucent bar
- `levels/level1.txt` — add `M` boxes and `Y` flyers (keep it completable)
- `requirements.txt` — add `numpy`
- `tools/make_icon.py` — redraw the desktop icon as the Spark Hero, then rebuild the `.exe` so the shortcut updates

## 8. Testing

**Unit (headless, TDD where practical):**
- `test_player_jump.py` — double-tap window: ground jump → mid-air jump only within
  `DOUBLE_TAP_MS`, only once per airtime; late tap does nothing.
- `test_player_power.py` — `grow()` sets big + larger size; `take_damage` big→small (no life
  lost) + invuln; damage during invuln ignored; small+damage → life lost.
- `test_scoring.py` — `bonus_lives(99,100)==1`, `(100,101)==0`, `(95,205)==2`.
- `test_level.py` (extend) — `M` parses to a solid block; `Y` parses to a Flyer enemy.

**Run-and-observe:** mascot art, night theme, sound, power-up feel, flyer, full playthrough.
A headless integrated smoke (dummy SDL video+audio) drives update+draw to catch crashes; the
traversal bot re-confirms the level is completable after level edits.

## 9. Success criteria

The Spark Hero runs through a moonlit level; a fast double-tap gives a mid-air boost; bumping a
`?` box pops a visible token (with a "+100" and progress toward a 1-UP); bumping an `M` box
releases a mushroom that grows him and lets him survive one hit; Flyers bob through the air to
dodge or stomp; score pop-ups and sound punctuate the action — all on a level that remains
completable, with the pure logic covered by tests.
