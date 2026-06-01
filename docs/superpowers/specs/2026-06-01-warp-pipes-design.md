# Warp Pipes + Bonus Vault — Design Spec

**Date:** 2026-06-01
**Status:** Design approved by user. Phase 3 mechanic. Chosen scope: **simple in-level teleport** (no multi-area system).

---

## 1. Vision

Stand on a **warp pipe** and tap **Down** to drop into a hidden **coin vault** built into a far, sealed corner of the same level map; a **return pipe** warps you back into the main path a few tiles ahead. The vault is optional — a reward + small shortcut. Showcased in an **underground** level (`level_3`) so it naturally reads as a cave vault.

## 2. Mechanic & controls

- New solid tiles: **`T`** = pipe mouth (rim), **`t`** = pipe shaft. A standard pipe is `TT` over `tt` (2 wide × 2 tall), standing on the floor.
- **Down / ↓ / S** while standing on a pipe mouth → teleport. Top-entry only (no side-entry pipes in v1).
- Teleport is instant: snap the hero (feet) to the destination tile, snap the camera, soft "pipe" sound + a brief "WARP" pop-up. A carried shell rides along (it's slaved to the hero).

## 3. Encoding (data-driven, in the level file)

Warps are declared in the header as tile coords, `entry -> destination`:

```
# warp: 40,11 -> 96,13     # stand on pipe mouth tile (40,11) -> feet land on top of tile (96,13)
# warp: 41,11 -> 96,13     # second mouth column of the 2-wide pipe
# warp: 111,11 -> 46,13    # vault return pipe -> back out at (46,13)
# warp: 112,11 -> 46,13
```

- `entry (ex,ey)` is a **trigger tile** (a pipe-mouth tile). Both mouth columns of a 2-wide pipe get a line so either foot position triggers.
- `dest (dx,dy)` is the tile the hero's **feet land on top of**: `player.x = dx*TILE`, `player.bottom = dy*TILE`.

## 4. Architecture & files

- **`game/entities/block.py`** — add `"T"`, `"t"` to `SOLID_KINDS` (pipes are solid).
- **`game/level.py`** — parse `# warp:` lines into `self.warps = [(trigger_rect, (dx, dy)), ...]`; expose `self.play_width = flag.rect.right if flag else width_px` so music tracks main-path progress, not the off-screen vault.
- **`game/game.py`** — a `Down` keypress calls `try_warp()`: if the hero is on the ground and a warp trigger sits under their feet, snap hero + camera to the destination, play sfx + pop-up. Music line uses `self.level.play_width`.
- **`game/assets.py`** — `draw_block` renders `T` (mouth, with an overhanging rim) and `t` (shaft) as a green pipe.
- **`game/settings.py`** — `PIPE` / `PIPE_DK` colors.
- **`levels/level_3.txt`** — a 2-tall entry pipe on solid ground (~col 40); a sealed coin vault at cols 95–114 (ceiling row 9, floor rows 13–14, walls cols 95 & 114, coins rows 10–12, return pipe cols 111–112); the four warp lines above.

## 5. Constants (`settings.py`)

```python
PIPE    = (84, 138, 74)
PIPE_DK = (54, 92, 50)
```

## 6. Testing (TDD)

- **`test_level.py`** (or new): a `# warp: a,b -> c,d` line parses into `(Rect(a*T, b*T, T, T), (c, d))`; `T`/`t` tiles become solids.
- **`test_game.py`**: tapping Down while a trigger is under the hero's feet moves the hero to `dx*T, dy*T-h`; tapping Down elsewhere does nothing; on_ground is required.
- **Smoke (headless):** drive the hero onto the entry pipe → Down → hero is in the vault region (x past the flag); onto the return pipe → Down → hero is back in the main path. **Traversal** of all 5 levels still completes (the bot ignores Down, so the pipe is just a jumpable obstacle).

## 7. Success criteria

In `level_3`, you can jump onto the pipe, tap Down, land in a coin-filled cave vault, scoop the coins, ride the return pipe back out ahead of where you entered — and every level still completes. No new dependencies; warp parsing and the teleport are covered by tests.
