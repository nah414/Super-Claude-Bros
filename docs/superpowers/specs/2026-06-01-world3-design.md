# World 3: Underwater Depths + Swimming — Design Spec

**Date:** 2026-06-01
**Status:** Approved. Phase 5 (water) + Phase 6 content. The first new *movement mechanic*.

---

## 1. Vision

A four-level underwater world (indices 8–11 = Worlds 3-1…3-4) with a new **swim** movement mode, a teal depth palette, the drifting **Cheep-Cheep** fish, and a dry castle finale (Iron Koopa). Press `3` at the title to dive in.

## 2. Theme: water (`area_type = "water"`)

- `draw_background` water: a teal→deep-blue vertical gradient + rising bubbles (camera-parallaxed).
- `draw_block` water: coral/seabed colors.
- Levels are enclosed (solid ceiling + seabed) so strokes don't fling you off-screen and you can't sink to death.

## 3. Swimming (the new mechanic)

Only when `level.area_type == "water"`:
- **Slow sink** replaces gravity: `vy = min(vy + SWIM_GRAVITY, SWIM_MAX_SINK)` (small values).
- **Tap jump = `player.swim_stroke()`** → a fixed upward velocity (`SWIM_STROKE`). Repeatable every frame; **no double-jump, no jump-cutoff** in water.
- Horizontal movement is unchanged (the float comes from the vertical); the hero can still rest on the seabed.
- `game.handle_events`: in water, a JUMP key calls `swim_stroke()` (not `press_jump`); KEYUP `release_jump` is skipped in water.
- Everywhere else is byte-for-byte unchanged.

## 4. New enemy: Cheep-Cheep (`game/entities/cheep.py`, tile `H`)

A fish that drifts horizontally and bobs vertically (the proven Flyer pattern, re-themed), ignores gravity, **hurts on contact**, and is **fireball- or swim-stomp-killable** (it flows through the existing `handle_enemies`/`handle_fireballs` since it lives in `level.enemies`). `CHEEP_SCORE`.

## 5. The four levels

- **3-1 / 3-2 / 3-3** (`level_9/10/11`, water): open swimmable corridors — a clear mid-depth channel, coral pillars rising from the seabed to swim over, Cheep-Cheeps drifting, flag at the end; ramping density.
- **3-4** (`level_12`, castle): reuse the lava castle + Iron Koopa (dry, classic). Beating it is the finale.
- `levelset.LEVELS` → 12 entries; music keeps cycling.

## 6. Constants (`settings.py`)

`WATER_TOP/WATER_BOTTOM/SEABED/SEABED_EDGE/BUBBLE`; `SWIM_GRAVITY ≈ 0.28`, `SWIM_MAX_SINK ≈ 3.0`, `SWIM_STROKE ≈ -5.0`; `CHEEP_SPEED/CHEEP_BOB_AMP/CHEEP_BOB_PERIOD/CHEEP_RANGE/CHEEP_SCORE`.

## 7. Testing

- **`test_swim.py`** (TDD): `swim_stroke()` sets an upward `vy`; in a water level `update()` applies `SWIM_GRAVITY` (not `GRAVITY`) and caps at `SWIM_MAX_SINK`; a non-water level still uses normal gravity.
- **`test_cheep.py`**: Cheep-Cheep drifts + reverses at its range; no gravity.
- **`tools/traverse.py`** gains a **water mode** (hold right + stroke to hold a target depth + rise over obstacles); verifies 3-1/3-2/3-3 swimmable end-to-end. 3-4 via the platforming bot + boss smoke.

## 8. Success criteria

Press `3` → dive into a teal depth: stroke to swim, drift past coral and Cheep-Cheeps to each flag, then surface for the castle and the Iron Koopa. Swim physics + Cheep-Cheep covered by tests; water levels bot-swimmable; build confirmed (`Build complete!`).
