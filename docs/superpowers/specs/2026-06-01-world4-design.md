# World 4: Frostpeak + Ice Physics — Design Spec

**Date:** 2026-06-01
**Status:** Approved. Phase 6 content — fourth world; second movement modifier (slippery ice).

---

## 1. Vision

A four-level snowy world (indices 12–15 = Worlds 4-1…4-4) with **slippery ice physics**, a bright white-blue palette, the **stomp-proof Frostbite** ice walker, and the castle finale. Press `4` at the title to test.

## 2. Theme: ice (`area_type = "ice"`)

- `draw_background` ice: a pale-blue sky with drifting snowflakes (reuse the star field as cream dots).
- `draw_block` ice: glossy white-blue ground/edge.

## 3. Ice physics (the new feel)

Only when `level.area_type == "ice"`: the no-input deceleration uses `ICE_FRICTION` (≈0.05) instead of `FRICTION` (0.4), so releasing a direction lets the hero **keep gliding** — building speed and stopping/turning take real distance. Set via a `self._ice` flag in `Player.update` before `_horizontal`; everywhere else unchanged. Accel/skid stay normal (the slide-on-release is the core feel; one tunable).

## 4. New enemy: Frostbite (`game/entities/frostbite.py`, tile `I`)

A spiky ice walker that paces with ledge detection (Koopa-style), **stomp-proof** (`stomp_proof = True`), defeated by **fireball or kicked shell**. Touch from any side (incl. top) → `take_damage`. Implemented generically: `handle_enemies` honors a `getattr(e, "stomp_proof", False)` flag (reusable for future spiky foes). Lives in `level.enemies`, so fireball/shell kills flow through existing code. `FROST_SCORE`.

## 5. The four levels

- **4-1 / 4-2 / 4-3** (`level_13/14/15`, ice): slippery ground platforming (gaps ≤3), Frostbites + familiar foes, **`M` power boxes so you can arm fire** to fight the stomp-proof Frostbites; ramping length/tightness.
- **4-4** (`level_16`, castle): the Iron Koopa finale (reuse).
- `levelset.LEVELS` → 16 entries; music keeps cycling.

## 6. Constants (`settings.py`)

`ICE_SKY/ICE_GROUND/ICE_EDGE/SNOW`; `ICE_FRICTION ≈ 0.05`; `FROST_SPEED ≈ 1.2`, `FROST_SCORE`.

## 7. Testing

- **`test_ice.py`** (TDD): on ice, releasing input keeps `vx` far longer than on land (after N frames, `vx` is still high vs ~0 on land).
- **`test_frostbite.py`**: paces + ledge-reverses; `stomp_proof` is True.
- **`test_game.py`**: a stomp-proof enemy hurts on a top hit (no stomp); a fireball still kills it.
- **Traversal:** ice levels 4-1/4-2/4-3 complete (the bot's momentum carries it; Frostbites placed with room to jump clear); 4-4 via platforming + boss smoke.

## 8. Success criteria

Press `4` → glide across Frostpeak: slide with momentum, fireball the Frostbites you can't stomp, reach each flag, then clear the castle. Ice physics + Frostbite covered by tests; ice levels bot-completable; build confirmed (`Build complete!`).
