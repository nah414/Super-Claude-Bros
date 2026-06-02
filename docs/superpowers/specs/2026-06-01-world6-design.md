# World 6: Clockwork Factory + Conveyors — Design Spec

**Date:** 2026-06-01
**Status:** Approved. Phase 6 content — sixth world; conveyor-belt movement modifier.

---

## 1. Vision

A four-level steel factory (indices 20–23 = Worlds 6-1…6-4) with **conveyor‑belt floors** that carry you, a marching **Cog‑bot**, and the Ember Koopa in a metal castle. Press `6` at the title to test.

## 2. Theme: factory (`area_type = "factory"`)

- `draw_background` factory: gunmetal fill + faint background gears.
- `draw_block` factory: riveted metal ground/edge.
- New `castle_factory` skin added to `CASTLE_SKINS` (metal) for 6‑4.

## 3. Conveyor belts (the new mechanic)

- New **solid floor tiles `>`/`<`** (push right/left). In `_load` (within the `SOLID_KINDS` branch, like cannons): append a `Block`, and record `self.conveyors.append((rect, +1/-1))`.
- `Level.belt_dir(rect)` → the conveyor direction under the hero's feet (`centerx, bottom+2`), else 0.
- `game.apply_conveyor()` (called each frame after `player.update`): if grounded on a belt, `player.x += CONVEYOR_SPEED * dir`, then clamp against any solid it overlaps (can't be shoved through a wall). Ride for speed; walk against it to crawl.

## 4. New enemy: Cog‑bot (`game/entities/cog.py`, tile `R`)

A marching robot that paces with ledge detection (Koopa-style) and is **stompable** (a normal enemy — keeps factory levels fully bot‑verifiable). `COG_SCORE`.

## 5. The four levels

- **6‑1 / 6‑2 / 6‑3** (`level_21/22/23`, factory): belt‑driven platforming (≤3 gaps; belts to ride/fight), Cog‑bots + a familiar foe, `M` fire boxes; ramping.
- **6‑4** (`level_24`, `castle_factory`): metal castle + **Ember Koopa** (world‑6 tier from the variety system: 6 HP, faster, orange, crowned; arena cannons).
- `levelset.LEVELS` → 24 entries; music keeps cycling.

## 6. Constants (`settings.py`)

`FACTORY_BG/FACTORY_GROUND/FACTORY_EDGE/BELT/BELT_LIGHT`; `CONVEYOR_SPEED ≈ 2.0`; `COG_SPEED ≈ 1.4`, `COG_SCORE`; `CASTLE_SKINS["castle_factory"]`.

## 7. Testing

- **`test_conveyor.py`** (TDD): `Level.belt_dir` returns the direction under the feet (else 0); `game.apply_conveyor` carries a grounded hero by `CONVEYOR_SPEED` and clamps at a wall.
- **`test_cog.py`**: paces + ledge‑reverses; stompable (no `stomp_proof`).
- **Traversal:** factory 6‑1/6‑2/6‑3 complete (belts carry, Cog‑bots stompable — fully bot‑checkable); 6‑4 via boss smoke.

## 8. Success criteria

Press `6` → ride and fight steel conveyors past stompable Cog‑bots to each flag, then face the crowned Ember Koopa in a metal castle. Belt + Cog covered/verified; factory levels bot‑complete; build confirmed (`Build complete!`).
