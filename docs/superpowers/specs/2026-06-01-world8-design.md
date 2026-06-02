# World 8: Koopa Keep — Final Fortress — Design Spec

**Date:** 2026-06-01
**Status:** Approved. Phase 6 content — the **finale**. Completes the full 8-world / 32-level game.

---

## 1. Vision

The villain's dark stronghold (indices 28–31 = Worlds 8-1…8-4): the hardest gauntlet — a culmination of returning hazards (cannons + lava + tight jumps) — ending in the ultimate **King Koopa** and a proper **victory/credits ending**. Press `8`.

## 2. Theme: keep (`area_type = "keep"`)

- `draw_background` keep: deep near-black with an ominous dark-red haze.
- `draw_block` keep: dark fortress stone ground/edge.
- New `castle_keep` skin (dark + gold throne accents) for 8-4.

## 3. Gauntlet levels (no new gimmick — the climax)

- **8-1 / 8-2 / 8-3** (`level_29/30/31`, keep): the toughest platforming yet — **static lava pools** (`L`), **cannons** (`N`, Bullet Bills), **Koopas** (`K`, stompable), tight ≤3 gaps, `M` fire boxes; ramping. Built from the player's full toolkit; kept bot-verifiable (stompable foes + dodgeable cannons + jumpable lava).

## 4. King Koopa — the ultimate boss

- **8-4** (`level_32`, `castle_keep`): the gold, crowned **KING KOOPA**. `Boss.set_tier(8)` gives him a **bonus +2 HP** (8 total) on top of the world-8 tier (fastest pace + fire rate), via a special case in `set_tier` (`if world >= 8: hp += 2`). Existing default/low-tier boss tests unaffected.

## 5. Victory ending

- Beating 8-4 = the last level → `GAME_COMPLETE`. Replace the overlay banner with a dedicated **ending screen** (`draw_ending`, like `draw_title`): the Fire-Claude hero, **"YOU SAVED THE DAY!"**, a thank-you/credits line, "Press ENTER for title".

## 6. Constants (`settings.py`)

`KEEP_BG/KEEP_GROUND/KEEP_EDGE`; `CASTLE_SKINS["castle_keep"]`.

## 7. Testing

- TDD: `set_tier(8)` HP is +2 above the world-8 tier and title is "KING KOOPA".
- Boss smoke: King Koopa (8 HP) is beatable; reaching it → `GAME_COMPLETE`.
- Traverse: keep 8-1/8-2/8-3 complete (tune hazards vs the bot); 8-4 via boss smoke.

## 8. Success criteria

Press `8` → fight through the dark keep's gauntlet to the throne, topple the 8-HP gold King Koopa, and see a triumphant ending — **the full 32-level, 8-world game, complete.** All covered/verified; build confirmed.
