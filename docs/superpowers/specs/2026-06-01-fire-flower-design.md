# Fire Flower & Power Persistence (Phase 3a) — Design Spec

**Date:** 2026-06-01
**Status:** Design approved (tier-drop damage chosen). Part of roadmap Phase 3, pulled forward for the boss phase.

---

## 1. Vision

Add the classic SMB power progression: **small → big → fire**, with power that **persists across levels**, mystery boxes that give a **Fire Flower** when you're already big, and **fireballs** that defeat enemies (the tool for boss levels). Reuses the existing damage/invulnerability, Mushroom, effects, and sound systems.

## 2. Power state machine (`player.py`)

`power ∈ {"small", "big", "fire"}`. **Big and Fire share the same hitbox** (`PLAYER_BIG`); fire differs only in ability + visual.

- `grow()`: small → big (resize up; keep feet planted).
- `become_fire()`: → fire; if currently small, also resize to big.
- `take_damage(now_ms)` — **tier-drop**:
  - `now_ms < invuln_until` → ignore (return `False`).
  - power `"fire"` → `"big"` (no resize), set invuln, return `False`.
  - power `"big"` → `"small"` (resize down), set invuln, return `False`.
  - power `"small"` → return `True` (a life is lost).
- `can_shoot(now_ms)`: `power == "fire"` and `now_ms - last_fire_ms >= FIRE_COOLDOWN_MS`.
- `record_fire(now_ms)`: `last_fire_ms = now_ms`.

## 3. Power persists across levels (`game.py`)

A `carry_power` field threads power between stages:
- `new_game()`: `carry_power = "small"`.
- `advance()` (after a level is cleared): `carry_power = self.player.power`, then load next level.
- `start_level()`: create the Player, then apply `carry_power` (`"big"` → `grow()`; `"fire"` → `become_fire()`).
- `lose_life()`: `carry_power = "small"` (death drops power); respawn is small.

## 4. State-aware mystery boxes & items

`handle_boxes` for an `M` box checks power **at bump time**:
- power `"small"` → spawn a **Mushroom** (slides, as today).
- power `"big"`/`"fire"` → spawn a **Fire Flower**.

- **`Mushroom`** (existing): collected → `player.grow()`.
- **`FireFlower`** (`entities/fireflower.py`): emerges from the box (rises ~0.4s) then **stays stationary** on top of it; collected → `player.become_fire()`, `+FLOWER_SCORE`, pop-up, sound.

## 5. Fireballs (`entities/fireball.py`)

When Fire-Claude, pressing **F** throws a fireball in the facing direction (if `can_shoot` and `< MAX_FIREBALLS` active).
- Spawns at the player's center; `vx = FIREBALL_SPEED * facing`, slight downward `vy`.
- `update(level)`: gravity (capped), `move_and_collide`; **bottom contact → bounce** (`vy = FIREBALL_BOUNCE`); **left/right contact → despawn**; a `life` counter despawns it after `FIREBALL_LIFE` frames.
- Combat (in `game.update`): a fireball overlapping a live enemy kills it (`+FIREBALL_SCORE`, pop-up, stomp sound) and despawns.
- Throwing plays a short `"fire"` sound (added to `SoundFX`).

## 6. Art (`assets.py`, via the seam)

- **Fire-Claude:** the big Spark Hero drawn with a **hot red-white sunburst** (rays in `FIRE` red-orange, white-hot core) so the state is obvious. `draw_player(..., power)` branches on `"fire"`.
- **Fire Flower:** `draw_fireflower` — a red-orange "rose" (layered petals) with a glowing cream center on a small green stem.
- **Fireball:** `draw_fireball` — a small glowing orange/red orb (concentric circles).

## 7. Architecture & files

- **New:** `game/entities/fireflower.py`, `game/entities/fireball.py`.
- **Modified:** `game/entities/player.py` (3-tier power, `become_fire`, tier-drop `take_damage`, fire cooldown), `game/game.py` (state-aware boxes, flower collection, fireball input/update/combat, `carry_power` persistence, draw), `game/assets.py` (fire tint, `draw_fireflower`, `draw_fireball`), `game/settings.py` (fire/fireball constants + `FIRE` color), `game/sound.py` (a `"fire"` blip).
- **Reused:** Mushroom, effects (pop-ups), invulnerability/flicker, scoring, the existing `M` boxes already placed in levels (now yield flowers when big).

## 8. Constants (`settings.py`)

```python
FIRE            = (235, 96, 56)   # hot accent for Fire-Claude / fireballs
FIREBALL_SPEED  = 7.0
FIREBALL_BOUNCE = -7.0
FIREBALL_LIFE   = 150             # frames (~2.5s) before despawn
FIRE_COOLDOWN_MS = 300
MAX_FIREBALLS   = 2
FIREBALL_SCORE  = 200
FLOWER_SCORE    = 1000
```

## 9. Testing (TDD the pure logic)

- `test_player_power.py` (extend): `become_fire()` (small→fire resizes; big→fire keeps size); tier-drop `take_damage` (fire→big→small→life-lost); `can_shoot` honors cooldown.
- `test_fireball.py`: a fireball bounces off the ground (`vy` flips up on bottom contact); despawns on a wall; despawns after its life.
- `test_game.py` (extend): an `M` box bumped while **small** spawns a Mushroom; while **big** spawns a Fire Flower; power **persists** across `advance()` and **resets** on `lose_life()`.

## 10. Success criteria

Small Claude eats a mushroom → big; big Claude bumps a box → a fire rose → Fire-Claude (hot sprite); **F** throws bouncing fireballs that defeat enemies; a hit drops one tier (fire→big→small) rather than all the way; and clearing a stage **keeps** the power into the next — with the pure logic covered by tests.
