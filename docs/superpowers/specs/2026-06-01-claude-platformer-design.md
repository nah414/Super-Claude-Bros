# Claude Platformer — Design Spec

**Date:** 2026-06-01
**Status:** Design approved in brainstorming; pending final spec review before planning.

---

## 1. Vision

A polished, single-level 2D side-scrolling platformer built in **Python + Pygame**, in the
spirit of the original *Super Mario Bros.* — but starring the **Claude mascot** as the hero,
themed in **Anthropic's brand palette**.

The north star is authentic **"game feel"**: momentum-based running, a satisfying
variable-height jump, and responsive controls on one *complete, fun* level. The codebase is
deliberately modular and heavily commented so it doubles as a learning artifact and so that
power-ups, additional levels, and richer art can be added later **without reworking the core**.

This is an **educational build**: all code is written and explained step-by-step. The user
learns by reading along and understanding each system (the user opted not to hand-write code).

The game is an **original work** — no Nintendo characters, art, music, or level data. The hero
is the Claude mascot; all art is original programmer-art in Anthropic's colors.

---

## 2. Goals

- One complete, polished level playable from player spawn to the finish flag.
- Excellent game feel: acceleration, friction, turn-around skid, a run button, variable-height
  jump, and gravity with terminal velocity.
- Clean, modular, well-commented architecture that is easy to learn from and to extend.
- Original and IP-clean: Claude-mascot hero, Anthropic palette, code-drawn programmer art.

## 3. Non-Goals (v1 — deliberately deferred)

These are **designed for** (see §11 Extension Points) but **not built** in the first version:

- Power-ups (Mushroom / Fire Flower) and the grow/shrink/fire states.
- Multiple levels or a world map.
- Enemy variety beyond one Goomba-style walker.
- Sound effects and music.
- Packaging to a standalone `.exe`.

---

## 4. Tech & Platform

- **Language/Engine:** Python 3 + Pygame. (Machine has Python 3.13.9 and 3.12.10; Pygame not
  yet installed.)
- **Run target:** native desktop window.
- **Setup step:** `pip install pygame` (captured in `requirements.txt`).
- **Frame timing:** fixed **60 FPS** timestep — each frame counts as one physics tick, which
  keeps hand-tuned feel constants predictable.
- **Window:** 960 × 600 px. **Tile size:** 40 px → a 24 × 15 tile viewport.

---

## 5. Architecture — Classic OOP

Chosen over ECS (too much abstraction for one level) and a single procedural file (becomes
spaghetti, fails the "easy to extend" goal). This is the canonical pygame-platformer shape, so
the concepts transfer directly to other engines.

```
mario/
  main.py                  # entry point — creates Game, runs the loop
  requirements.txt         # pygame
  README.md                # how to install & run
  game/
    settings.py            # ALL tunable constants (window, gravity, speeds, colors)
    game.py                # main loop: input -> update -> draw; owns game state machine
    physics.py             # pure AABB collision + movement resolution (unit-tested)
    level.py               # parses the ASCII tile map, owns all entities, updates/draws world
    camera.py              # world->screen offset; follows player; clamps to level bounds
    assets.py              # programmer-art draw_* functions (THE swappable art seam)
    hud.py                 # score / coins / lives overlay (drawn in screen space)
    entities/
      __init__.py
      entity.py            # base Entity: float position, velocity, rect, update(), draw()
      player.py            # Claude hero: input-driven movement, power-state field, stomp
      goomba.py            # walker enemy: patrol, reverse at walls/ledges, die on stomp
      coin.py              # sunburst "spark" collectible: +score on overlap
      block.py             # ground / brick / question-block (bump -> emits a coin)
      flag.py              # finish flag: overlap -> LEVEL_COMPLETE
  levels/
    level1.txt             # the level, authored as an editable ASCII grid
  tests/
    test_physics.py        # collision/movement resolution
    test_level.py          # tile-map parsing
```

**Module responsibility, one line each:**
- `settings.py` — single source of truth for every number and color; tuning lives here.
- `game.py` — orchestrates the loop and transitions between states; owns no game *rules*.
- `physics.py` — pure functions: given rects and velocity, return resolved position + contacts.
- `level.py` — turns text into a world; holds entity lists; delegates update/draw.
- `camera.py` — coordinate transform only.
- `assets.py` — the *only* place that knows what things look like.
- `entities/*` — each entity owns its own behavior and nothing else.

---

## 6. Game Loop & State Machine

Each frame: **process input → update world (fixed dt) → draw**.

States for v1:
- `PLAYING` — normal gameplay.
- `LEVEL_COMPLETE` — reached the flag; show a win banner, then allow restart.
- `DEAD` — fell in a pit or took a hit; lose a life, then respawn at the level start.
- `GAME_OVER` — out of lives (start with **3**); show banner, allow restart.

(A `TITLE` state is an easy future add; v1 can boot straight into `PLAYING`.)

---

## 7. Physics & Game Feel — the heart of the project

All four behaviors are simple arithmetic on a velocity vector; the *constants* are what make it
feel like Claude-Mario rather than ice or molasses. They live in `settings.py`.

- **Horizontal momentum:** hold a direction → accelerate toward a top speed; release → friction
  decelerates to a stop; reverse mid-run → a higher "skid" deceleration for that satisfying
  turn-around.
- **Run button:** holding **Shift** raises the top speed (walk vs. run), authentic to the genre.
- **Variable-height jump:** pressing jump applies an upward impulse; if the player *releases*
  the button while still rising, we clamp the upward velocity so the jump ends early. Tap = hop,
  hold = full leap.
- **Gravity:** constant downward acceleration each frame, capped at a terminal velocity.

**Starting constants (to be tuned during playtesting), px & px/frame at 60 FPS:**

| Constant | Start value | Meaning |
|---|---|---|
| `GRAVITY` | `0.8` | downward accel per frame |
| `MAX_FALL` | `16` | terminal fall speed |
| `MOVE_ACCEL` | `0.5` | horizontal accel while holding a direction |
| `MAX_WALK` | `4.0` | top walking speed |
| `MAX_RUN` | `6.5` | top speed with run held |
| `FRICTION` | `0.4` | decel when no direction held |
| `SKID_DECEL` | `0.8` | decel when reversing direction |
| `JUMP_VELOCITY` | `-14.0` | initial jump impulse (up is negative) |
| `JUMP_CUTOFF` | `-4.0` | max upward velocity retained if jump released early |
| `STOMP_BOUNCE` | `-8.0` | upward bounce after stomping an enemy |

---

## 8. Collision — axis-separated AABB

Axis-aligned bounding boxes, resolved **one axis at a time**: move on X and resolve horizontal
overlaps, then move on Y and resolve vertical overlaps. Separating the axes is the standard
trick that eliminates the corner-snag bugs naïve collision produces, and it cleanly yields the
"is the player standing on ground?" (`on_ground`) flag we need for jumping.

**Stomp rule:** if the player is moving downward and contacts an enemy from above → the enemy
dies and the player bounces (`STOMP_BOUNCE`). Any other contact → the player takes a hit
(loses a life, → `DEAD`).

---

## 9. The Level — ASCII tile map

`levels/level1.txt` is a human-editable grid; you can *see* and redraw the level in a text file.

Legend (initial):

| Char | Meaning |
|---|---|
| `X` | solid ground |
| `=` | floating platform |
| `B` | brick block |
| `?` | question block (bump from below → emits a spark/coin) |
| `C` | coin / sunburst spark |
| `G` | Goomba spawn |
| `P` | player start |
| `F` | finish flag |
| `.` / space | empty |

The parser converts static tiles into `Block` objects and the markers (`P`, `G`, `C`, `F`)
into entity spawns.

---

## 10. Visual Design — Claude theme

**Hero — "Round Claude buddy":** a warm rounded character in **Claude orange `#d97757`** —
soft capsule body, simple dot eyes, a gentle smile, little feet, and a small Anthropic sunburst
as a wink to the logo. Chosen because simple rounded shapes read best as small sprites and match
Claude's friendly personality. Facing flips with movement direction.

**Palette (Anthropic brand):**

| Role | Hex |
|---|---|
| Hero / sparks / accents (orange) | `#d97757` |
| Sky / light (cream) | `#faf9f5` |
| Ground / platforms (sage green) | `#788c5d` |
| Secondary accents (blue) | `#6a9bcc` |
| Ink / outlines / text (near-black) | `#141413` |
| Subtle fills (light gray) | `#e8e6dc` |

**World theming:** cream sky background, sage-green ground/platforms, blue accent details;
**coins are orange sunburst "sparks."** HUD/text in ink on a light bar; title text may use a
Poppins-like font if available (clean sans fallback otherwise).

**Art seam:** every visual is produced by an `assets.py` function (`draw_player`, `draw_goomba`,
`draw_coin`, `draw_block`, …). Entities call these functions; they never blit pixels directly.
Upgrading to pixel art later means editing *only* these functions.

---

## 11. Controls (default)

- **Move:** Arrow keys **or** WASD.
- **Jump:** Space or Up (hold for higher).
- **Run:** Shift (hold).
- **Restart:** Enter on a win/game-over banner. **Quit:** Esc / window close.

---

## 12. Testing Strategy

- **Unit tests (headless, no window):** collision/movement resolution in `physics.py`; tile-map
  parsing in `level.py`. Pure logic, fast, deterministic — written test-first where practical.
- **Manual playtesting:** game *feel* (jump arc, momentum, difficulty) is tuned by playing and
  adjusting `settings.py`.

---

## 13. Extension Points (designed-in, not built in v1)

- **Power-ups:** `Player` already carries a power-state field and renders via the art seam —
  Mushroom/Fire add a state value + new `assets.py` art + a fireball entity.
- **More levels:** add `levels/level2.txt` and a level sequence/loader; the tile parser is reused.
- **More enemies:** follow `Goomba`'s behavior pattern (e.g., a Koopa with a sliding shell).
- **Sound:** a small audio module triggered on jump/stomp/coin/level-complete events.
- **Packaging:** bundle to a double-clickable `.exe` (e.g., PyInstaller) once content is settled.

---

## 14. Success Criteria

A player can launch the game, control the Claude hero with momentum-rich movement, jump on a
Goomba, collect sparks, bump a question block, and reach the finish flag to win — on a single
hand-authored level that *feels good to move around in* — with code clean enough to extend.
