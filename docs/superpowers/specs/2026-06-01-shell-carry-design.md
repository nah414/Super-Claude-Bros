# Shell Grab, Carry & Throw — Design Spec

**Date:** 2026-06-01
**Status:** Design approved by user. Extends Phase 2 (Koopa) with an SMB3/World-style carry mechanic. The quick side-kick stays; carry is additive.

---

## 1. Vision

Press **`E`** next to a stomped (idle) shell to **lift** it; carry it while running and jumping; press **`E`** again to **throw** it forward as a slide. A held shell is also a **battering ram** — walking it into an enemy defeats it. The plain side-touch **kick** is unchanged, so players get both a fast reflex kick and a deliberate carry.

## 2. Controls

| Input | Condition | Effect |
|---|---|---|
| side-touch shell | idle shell, not held | **kick** (existing) |
| `E` | touching an idle shell, hands empty | **grab** → lift it |
| `E` | already carrying | **throw** → slide in facing direction |

`E` (`pygame.K_e`) is currently unused. **Down/↓ is deliberately left free for warp pipes** (next feature).

## 3. Behavior rules

- Only an **idle shell** (`state=="shell"`, not `held`) can be grabbed. A walking Koopa must be stomped first; a sliding shell must be re-stomped to a stop first.
- **Reach:** grab succeeds when `player.rect` inflated by ~(10,6) overlaps the shell (a little grace so you don't have to be pixel-perfect).
- **Carry:** the held shell's position is slaved to the hero each frame (chest height, just ahead in the facing direction). Full run/jump, no slowdown. Its own physics/AI are suspended while held.
- **Battering ram:** a held shell that overlaps another live enemy defeats it (+score); you keep carrying.
- **Held shell is safe to its carrier:** `handle_enemies` ignores the shell you hold; it never "wakes."
- **Throw:** clears `carrying`, sets `held=False`, `state="slide"`, `direction=facing`, and `kick_cooldown` — funneling into the existing slide path (wall-bounce, chain-kill, score, no self-hit during cooldown).
- **Drop on damage:** if the hero takes a hit (or dies) while carrying, the shell drops to an **idle shell** on the ground — no double penalty.
- One shell at a time.

## 4. Architecture & files (small; reuses the slide/chain-kill machinery)

- **`game/entities/koopa.py`** — add `self.held = False`; `update()` early-returns while `held` (no gravity/motion).
- **`game/entities/player.py`** — add `self.carrying = None`.
- **`game/game.py`**:
  - `handle_events`: `elif event.key == pygame.K_e and state=="PLAYING": self.grab_or_throw()`.
  - `grab_or_throw()` — throw if carrying, else try to grab the first touching idle shell.
  - `throw_shell()` — funnel into slide (as above) + `sfx.play("throw"|"stomp")`.
  - `drop_shell()` — release to idle shell (used on damage/respawn).
  - `handle_carry()` — slave the held shell to the hero and run battering-ram collisions; called each frame while `PLAYING`.
  - `handle_enemies` — skip the carried/held shell.
  - `lose_life()` — `drop_shell()` before respawn (the held Koopa would otherwise be orphaned, since respawn keeps the level's enemies).
- **Art:** none new — the held shell is the existing shell art drawn at the hero's hands (re-drawn on top of the player so it reads as "carried").

## 5. Constants (`settings.py`)

Reuses `SHELL_SPEED`, `SHELL_KICK_COOLDOWN`, `KOOPA_SCORE`. Optional small additions:
```python
GRAB_REACH = (10, 6)     # rect inflation for grab range
CARRY_AHEAD = 6          # px the held shell leads the hero in the facing dir
```

## 6. Testing (TDD)

- **`test_koopa.py`**: a `held` Koopa skips `update()` (no gravity).
- **`test_game.py`**: `E` grabs a touching idle shell (`carrying` set, `held` true); a second `E` throws it (slide, `direction==facing`, cooldown set, not held); a **carried shell battering-rams** a Goomba; **taking damage drops** the shell to idle; you **can't grab a walking Koopa**.
- **Smoke (headless):** stomp→shell, press-E grab, move, press-E throw → it slides and chain-kills; 300-frame soak with a grab/throw, no crash.

## 7. Success criteria

You can stomp a Koopa, walk up and press `E` to scoop the shell, carry it across a gap, bash a Goomba with it on the way, then press `E` to fire it down a lane of enemies — and the old quick-kick still works untouched. No new dependencies; the state machine and drops are covered by tests.
