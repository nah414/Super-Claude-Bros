# World 7: Molten Caldera + Rising Lava — Design Spec

**Date:** 2026-06-01
**Status:** Approved. Phase 6 content — seventh world; rising-lava escape mechanic.

---

## 1. Vision

A four-level volcano (indices 24–27 = Worlds 7-1…7-4): platform-hop right across islands over a **sea of lava that rises from below**, dodging **Lava Bubbles**, then the Storm Koopa in a molten castle. Press `7`.

## 2. Theme: caldera (`area_type = "caldera"`)

- `draw_background` caldera: charred dark-red rock + an orange under-glow.
- `draw_block` caldera: dark volcanic rock ground/edge.
- New `castle_caldera` skin for 7-4.

## 3. Rising lava (the new mechanic)

- `game.lava_rise_y` (screen-space y; the camera only scrolls x, so world-y == screen-y). In `start_level`/`respawn`, caldera levels set `lava_rising=True`, `lava_rise_y = HEIGHT + 30` (below view); else False.
- `update`: if rising, `lava_rise_y -= LAVA_RISE_SPEED`; if `player.rect.bottom >= lava_rise_y` → `lose_life` (caught). Death resets it.
- `draw`: a lava sea filled from `lava_rise_y` to the bottom (LAVA + LAVA_GLOW wavy top).
- Levels are **platform islands over the sea** (no full floor); keep moving right/up — linger and the rising lava engulfs your island.

## 4. New enemy: Lava Bubble (`game/entities/lava_bubble.py`)

Spawned by the game near the player every `BUBBLE_INTERVAL` frames at the lava surface, launched up (`BUBBLE_VY`), arcs under gravity, despawns when it falls back below the surface. Hurts on contact. Kept in `self.lava_bubbles`.

## 5. The four levels

- **7-1 / 7-2 / 7-3** (`level_25/26/27`, caldera): right-trending platform islands (≤3 gaps) over the rising lava, a Koopa or two, `M` fire boxes; ramping rise speed.
- **7-4** (`level_28`, `castle_caldera`): molten castle + crowned **Storm Koopa** (world-7 tier).
- `levelset` → **28 levels** (World 7 = 24–27).

## 6. Constants (`settings.py`)

`CALDERA_BG/CALDERA_GROUND/CALDERA_EDGE`; `LAVA_RISE_SPEED` (tune ~0.25); `BUBBLE_INTERVAL`, `BUBBLE_VY`, `BUBBLE_SIZE`; `CASTLE_SKINS["castle_caldera"]`.

## 7. Testing

- TDD: `lava_rise_y` climbs each frame in a caldera level; feet below → a life lost. Lava Bubble arcs (rises then falls) and despawns; hurts on contact.
- Traverse: caldera 7-1/7-2/7-3 finishable ahead of the lava (tune `LAVA_RISE_SPEED` vs the bot); 7-4 via boss smoke.

## 8. Success criteria

Press `7` → race up-and-right across molten islands ahead of the rising lava, dodging bubbles, to each flag, then beat the Storm Koopa. Rise + bubble covered/verified; caldera levels bot-completable; build confirmed.
