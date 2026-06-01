# World 1-4: Castle + the Iron Koopa — Design Spec

**Date:** 2026-06-01
**Status:** Design approved by user. Phase 4. Scope: "Fireball boss" (focused).

---

## 1. Vision

`level_4` (which is World 1-4) becomes a lava-lit **castle** ending in a boss arena. The **Iron Koopa** is armored and **stomp-proof** — you defeat it with **fireballs** (the Fire Flower payoff). Beating it clears World 1 → World 2.

## 2. Castle level

- New `area_type = "castle"` — stone blocks, dark red ambiance.
- New tile **`L` = lava**: non-solid, **instant death on contact** (like a pit). Lava pools sit in floor gaps (≤2-3 wide, jumpable).
- New tile **`Z` = boss** spawn.
- Two **`M` boxes** on the approach guarantee fire (small→big→fire across two boxes), placed before the arena.
- The arena: solid floor bounded by a right wall and (on the left) a lava pool — the boss paces between them. No flag; **defeating the boss completes the level**.

## 3. The Iron Koopa (`game/entities/boss.py`)

A separate `level.boss` (NOT in `level.enemies`, so the normal stomp/shell/fireball-instakill loops don't touch it).

- **Paces** at `BOSS_SPEED`, reversing at walls and ledges (lava edge) — same logic as Koopa.
- **Stomp-proof:** any contact with the player calls `player.take_damage` (no stomp branch).
- **Shoots:** a `shot_timer` counts down; `ready_to_shoot()` fires every `BOSS_SHOT_COOLDOWN` frames → the game spawns a `BossShot` toward the player.
- **HP:** `hit()` decrements `hp`, sets a brief `flash` invuln (so one fireball = one hit), returns `True` when `hp` hits 0 (defeated).
- `BOSS_HP=3`.

## 4. Boss shot (`game/entities/boss_shot.py`)

`BossShot(x, y, direction)`: flies straight horizontally at `BOSS_SHOT_SPEED`, despawns after `BOSS_SHOT_LIFE`. Touching the player → `take_damage`. Dodged by jumping over it.

## 5. Game integration (`game/game.py`)

- `update`: update `level.boss` + spawn shots on `ready_to_shoot`; update/cull `boss_shots`.
- `handle_fireballs`: a fireball hitting the boss calls `boss.hit()`; if defeated → `boss_defeated()` (score, "win" sfx, `cleared_boss=True`, `state="LEVEL_COMPLETE"`).
- `handle_boss()`: boss body contact and any boss-shot contact → `take_damage` (→ `lose_life` if it kills).
- Lava: in `update`, `player.rect` overlapping any `level.lava` rect → `lose_life`.
- **Respawn reloads the level** (fresh boxes/enemies/boss) — classic Mario death behavior, and what guarantees you can re-arm with fire (no softlock).
- Banner: on a boss clear, "WORLD 1 CLEARED!" instead of "LEVEL COMPLETE!".
- `start_level`/`respawn` init `self.boss_shots = []`; `start_level` sets `self.cleared_boss = False`.

## 6. Art & constants

- `assets`: `draw_background` castle branch, `draw_block` castle stone colors, `draw_lava`, `draw_boss`, `draw_boss_shot`.
- `settings`: `CASTLE_BG/GROUND/EDGE`, `LAVA`, `LAVA_GLOW`, `BOSS_SIZE`, `BOSS_HP=3`, `BOSS_SPEED`, `BOSS_FLASH`, `BOSS_SHOT_SIZE/SPEED/LIFE/COOLDOWN`, `BOSS_SCORE`.

## 7. Testing

- **`test_boss.py`** (TDD): `hit()` 3× defeats it; `flash` blocks rapid hits; it shoots on cooldown; it paces/reverses.
- **`test_game.py`**: fireball defeats boss → `LEVEL_COMPLETE`; boss is stomp-proof (top contact still damages); lava costs a life; death reloads the level (a used box returns).
- **Boss smoke (headless):** enter the arena with fire, throw fireballs → boss dies → level completes; a boss shot hurts; lava kills.
- **Traversal:** levels 1/2/3/5 still complete; the castle is verified by (a) the bot physically *reaching* the arena and (b) the boss smoke (the bot can't aim fireballs).

## 8. Success criteria

In World 1-4 you cross a lava castle, grab fire, and face the Iron Koopa: it paces and lobs fire, shrugs off stomps, and falls to 3 fireballs — clearing World 1 into World 2. Dying restarts the level cleanly. All logic covered by tests; the build is confirmed (`Build complete!`).
