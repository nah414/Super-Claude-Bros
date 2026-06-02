# World 5: Haunted Hollow + Boo Ghosts — Design Spec

**Date:** 2026-06-01
**Status:** Approved. Phase 6 content — fifth world; novel "look-away" enemy behavior.

---

## 1. Vision

A four-level haunted manor (indices 16–19 = Worlds 5-1…5-4) with a foggy purple palette and the **Boo Ghost** — a stomp-proof ghost that freezes when you face it and hunts you when you look away. Press `5` at the title to test.

## 2. Theme: haunted (`area_type = "haunted"`)

- `draw_background` haunted: deep-violet fill + drifting pale fog wisps (parallaxed) + a wan moon.
- `draw_block` haunted: dark wood/stone ground/edge.

## 3. New enemy: Boo Ghost (`game/entities/boo.py`, tile `O`)

A pale floating ghost that **ignores gravity and terrain** (floats freely) and is **stomp-proof** (`stomp_proof = True`).

- The game drives it each frame via `boo.chase(player)` (a Boo pass in `update`, since the chase needs the player):
  - `to_boo = +1/-1` (side the Boo is on relative to the player).
  - **If `player.facing == to_boo`** (you're looking toward it) → `frozen = True` (it stops, covers its face).
  - **Else** (you looked away) → drift toward the player: normalize `(dx, dy)` to the player's center and move `BOO_SPEED`.
- `Boo.update(level)` is a no-op (inherits Entity); movement is all in `chase`.
- **Fireball-killable** (it's in `level.enemies`, so `handle_fireballs` kills it); touch → `take_damage` via the existing `stomp_proof` gate. `BOO_SCORE`.

## 4. The four levels

- **5-1 / 5-2 / 5-3** (`level_17/18/19`, haunted): manor platforming (≤3 gaps), Boos + a familiar foe, `M` fire boxes; ramping.
- **5-4** (`level_20`, castle): the Iron Koopa finale.
- `levelset.LEVELS` → 20 entries; music keeps cycling.

## 5. Constants (`settings.py`)

`HAUNT_BG/HAUNT_GROUND/HAUNT_EDGE/FOG/MOON_PALE`; `BOO_SPEED ≈ 1.3`, `BOO_SCORE`.

## 6. Testing

- **`test_boo.py`** (TDD): faces it → `frozen`; looks away → drifts toward the player (x moves toward player); `stomp_proof is True`.
- **`test_game.py`**: a fireball kills a Boo.
- Verify haunted **platforming** with Boos removed (the bot can't out-think stomp-proof ghosts — same approach as Frostbites/bosses); 5-4 via boss smoke.

## 7. Success criteria

Press `5` → creep through a foggy manor: freeze Boos by staring them down, dart past when they're shy, fireball the ones you can corner, then clear the castle. Boo behavior + stomp-proof + fireball-kill covered by tests; haunted platforming bot-clear; build confirmed (`Build complete!`).
