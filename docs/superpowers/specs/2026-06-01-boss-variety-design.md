# Castle & Boss Variety Pass — Design Spec

**Date:** 2026-06-01
**Status:** Approved (user expanded scope: themed bosses AND themed castle stages + difficulty ramp). Brings all 5 existing castles "up to par" before World 6.

---

## 1. Vision

Each world's 4th-level castle becomes a **distinct, themed, progressively harder finale** instead of five identical lava castles with the same green Iron Koopa.

## 2. Per-world boss tiers (`Boss.set_tier(world)`)

Applied when a castle loads (`game.start_level`/`respawn`):
- **HP**: `BOSS_HP + (world-1)//2` → 3,3,4,4,5,…
- **Speed**: `BOSS_SPEED + (world-1)*0.12`.
- **Fire rate**: `shot_cd = max(45, BOSS_SHOT_COOLDOWN - (world-1)*9)` (faster later).
- **Shell color** + **name** per world from `BOSS_COLORS` / `BOSS_TITLES` (8 entries): Iron, Gale, Tide, Frost, Phantom, Ember, Storm, King Koopa.
- A **gold crown** drawn on the boss so it reads as a lord.
- `boss_defeated` shows the name: *"FROST KOOPA DEFEATED!"*.
- `Boss.__init__` keeps defaults (HP/speed/cooldown/color/title) so untiered bosses (tests) still work.

## 3. Themed castle stages (`CASTLE_SKINS`)

Each castle level uses a per-world castle `area_type`, all rendered via one skin lookup — **visuals only; physics stay "castle"** (dry, lava hazards, normal movement — *not* swim/ice, so boss fights stay fair):
- `castle` (W1 lava), `castle_sky` (W2 dusk), `castle_sea` (W3 teal), `castle_ice` (W4 icy-blue), `castle_haunt` (W5 violet).
- `CASTLE_SKINS[type] = {bg, ground, edge, glow}`; `draw_background` fills `bg` + a `glow` band; `draw_block` uses `ground/edge`. (Lava `L` keeps its hot color — it's the hazard.)
- The castle level files (`level_8/12/16/20`) get the themed header; `level_4` stays `castle`.

## 4. Difficulty ramp in castles

Later castles gain **arena cannons** (Bullet Bills during the fight): W2 already has 1; add 1–2 to W3/W4/W5 castles. Combined with boss tiers = rising challenge.

## 5. Constants (`settings.py`)

`BOSS_COLORS` (8), `BOSS_TITLES` (8), `CASTLE_SKINS` (5 dicts). `Boss` reads `self.speed/shot_cd/color/title`.

## 6. Testing

- **`test_boss.py`**: `set_tier(5)` raises HP above base and sets the World-5 title/color; existing default-boss tests still pass.
- Boss smoke at a high tier (more HP) is still beatable.
- Traverse: castle platforming (boss removed) still clean for the themed castles; full suite green.

## 7. Success criteria

Each world's castle looks like that world and hosts a uniquely-colored, crowned, progressively tougher Koopa lord with a name on defeat. Tiers + skins covered/verified; build confirmed (`Build complete!`). Then: World 6.
