# World 2: Twilight Sky + Bullet Bills — Design Spec

**Date:** 2026-06-01
**Status:** Design approved by user. Phase 6 (content) — the first full new world.

---

## 1. Vision

A four-level **Twilight Sky** world (indices 4–7 = Worlds 2-1…2-4) with a bright dusk palette (contrast to World 1's night), the new **Bullet Bill + Cannon** enemy, and a castle finale reusing the Iron Koopa. Plus a **title world-select** so any world can be tested directly.

## 2. Theme: sky (`area_type = "sky"`)

- `draw_background` sky branch: a dusk vertical gradient (violet → amber) with a few soft clouds.
- `draw_block` sky branch: warm, lighter "cloud-stone" ground/edge colors.
- Levels stay **ground-based** (reskinned) with more elevation/platforms and cannon towers — *not* pure death-void islands (keeps them completable). Falling off the bottom is still pit death.

## 3. New enemy: Bullet Bills + Cannons

- New **solid tile `N` = cannon** (drawn as a dark Bill Blaster; stack for towers). In `level._load`, every `N` is a solid `Block`; a **firing point** (`level.cannons`, a list of `Cannon(x,y)` with a `timer`) is recorded only for the **top** `N` of a stack (the cell above is not `N`).
- **Firing:** each frame, `cannon.timer` counts down; at 0, if the player's horizontal distance is in `(BULLET_MIN_DIST, BULLET_MAX_DIST)`, spawn a `BulletBill` toward the player and reset the timer.
- **`BulletBill`** (`self.bullets`, spawned dynamically): flies straight at `BULLET_SPEED`, no gravity, despawns off the level or after `BULLET_LIFE`. **Stompable** (from top → defeat + bounce + score) and **fireball-killable**; side contact → `take_damage`.

## 4. The four levels

- **2-1** (`level_5`): reskin to `sky`, add a cannon or two; keep its gentle layout + existing Goombas/Koopas.
- **2-2 / 2-3** (`level_6` / `level_7`, new): more vertical, cannon towers, tighter (≤3) gaps — the ramp.
- **2-4** (`level_8`, new): the **castle** (reuse `castle` theme) with the **Iron Koopa** *plus* cannons in the arena — dodge Bullet Bills while fighting. Boss stays `BOSS_HP=3`; cannons supply the extra challenge.

## 5. Wiring

- `levelset.LEVELS` → 8 entries. `world_label` already yields 2-1…2-4. The 5 music tracks keep cycling (no new audio).
- **World-select:** `new_game(index=0)`; on `TITLE`, digit keys `1..N` start `new_game((digit-1)*4)` when that index exists; title shows "Press 1–{worlds} to pick a World".

## 6. Constants (`settings.py`)

`SKY_TOP/SKY_BOTTOM/SKY_GROUND/SKY_EDGE/CLOUD`, `CANNON`, `BULLET_SPEED`, `BULLET_SIZE`, `BULLET_LIFE`, `BULLET_SCORE`, `BULLET_COOLDOWN`, `BULLET_MIN_DIST`, `BULLET_MAX_DIST`.

## 7. Testing

- **`test_bullet.py`** (TDD): `BulletBill` flies straight and despawns off-level/after life; a `Cannon` fires on cooldown toward an in-range player and not when too close/far.
- **`test_game.py`**: a Bullet Bill is stompable (top → dies, player bounces) and hurtful (side → damage); a fireball pops it; `new_game(4)` starts at World 2-1.
- **Traversal:** sky levels 2-1/2-2/2-3 complete (gaps ≤3); 2-4 via the platforming bot + the boss smoke.

## 8. Success criteria

Press `2` at the title to drop into a bright dusk World 2: cross cannon-guarded sky levels dodging/stomping Bullet Bills, then face the Iron Koopa amid cannon fire to clear the world. All mechanics covered by tests; every sky level bot-completable; build confirmed (`Build complete!`).
