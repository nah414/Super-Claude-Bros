# Koopa Troopa & Sliding Shell (Phase 2) — Design Spec

**Date:** 2026-06-01
**Status:** Design approved. Phase 2 of the roadmap (enemy roster), scoped to the signature Koopa for now.

---

## 1. Vision

Add the signature SMB enemy: a themed turtle (`K` tile) with a **`walk → shell → slide`** state machine. Stomp it into a shell, kick the shell to send it sliding through other enemies — the richest combat toy in the game so far. Reuses ledge logic and the stomp/fireball/damage systems.

## 2. Koopa state machine (`entities/koopa.py`)

Single hitbox (~28×28) across states; only the art and motion differ. `state ∈ {"walk","shell","slide"}`, plus `direction`, `kick_cooldown`.

- **walk** — paces at `KOOPA_SPEED`, reverses at **walls and ledges** (same ledge check as Goomba). Gravity.
- **shell** — stationary (vx=0); gravity holds it on the ground.
- **slide** — moves at `SHELL_SPEED`, **reverses on a wall**, **no ledge-detect** (falls into pits). `kick_cooldown` counts down each frame.
- All states: despawn if it falls below `PIT_DEATH_Y`.

## 3. Player interactions

`koopa.player_hit(from_top, player_cx)` mutates state and returns an outcome the game acts on:

| State | from_top (stomp) | side touch |
|---|---|---|
| walk | → `shell`; returns `"stomp"` (bounce + score) | `"hurt"` |
| shell | returns `"bounce"` (bounce, shell stays idle) | kick → `slide` away from player (`direction = 1 if player_cx <= centerx else -1`), `kick_cooldown` set; returns `"kick"` |
| slide | → `shell`; returns `"stomp_stop"` (bounce) | `"hurt"` (a live shell is dangerous) |

`game.handle_enemies` special-cases `Koopa` (via `isinstance`): maps `"stomp"/"bounce"/"stomp_stop"` → `player.vy = STOMP_BOUNCE` (+score for `"stomp"`), `"kick"` → stomp sound, `"hurt"` → `player.take_damage` (tier-drop). While `state=="slide"` and `kick_cooldown>0`, player collision is skipped (you don't hurt yourself the instant you kick).

## 4. Shell-vs-world

- `game.handle_shells`: any `slide` Koopa overlapping another live enemy kills it (+its score) and keeps going — chain kills.
- Fireball hits a Koopa in any state → defeated (existing `handle_fireballs`).

## 5. Art & content (`assets.draw_koopa`)

A friendly turtle in our palette: green domed **shell** (`KOOPA_SHELL`) with a cream band + ink outline; a cream/orange **head** poking out front (facing `direction`) and two feet while **walking**; just the shell when **idle/sliding** (a small swirl hint while sliding). New tile **`K`** (parsed in `level.py`). Add a few `K` to the 5 levels near ledges/platforms so the shell mechanic shines.

## 6. Architecture & files

- **New:** `game/entities/koopa.py`.
- **Modified:** `game/level.py` (parse `K`), `game/game.py` (Koopa-aware `handle_enemies` + `handle_shells` + import), `game/assets.py` (`draw_koopa`), `game/settings.py` (constants below), `levels/*` (place `K`).
- **Reuses:** Goomba ledge logic, stomp/fireball combat, `take_damage` tier-drop.

## 7. Constants (`settings.py`)

```python
KOOPA_SPEED        = 1.3
SHELL_SPEED        = 6.0
SHELL_KICK_COOLDOWN = 12       # frames the kicker is safe after a kick
KOOPA_SCORE        = 200
KOOPA_SHELL        = (96, 156, 76)
```

## 8. Testing (TDD the state machine)

`test_koopa.py`: walk + stomp → `shell`; idle shell + side-kick → `slide` with correct away-from-player direction; slide + stomp → `shell`; a sliding shell **reverses on a wall**; a walking Koopa **turns at a ledge** (doesn't fall). Plus a `game` smoke: stomp a Koopa, kick the shell, the shell kills a Goomba.

## 9. Success criteria

Stomp a Koopa → it shells up; kick it → the shell rockets off, bounces off walls, bowls over other enemies, and is dangerous if it comes back at you; re-stomp stops it; a fireball ends it in any state — all on levels placed to make the mechanic sing, with the state machine covered by tests.
