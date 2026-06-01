# Super Claude Bros — Phase 1: World Engine + Music — Design Spec

**Date:** 2026-06-01
**Status:** Design approved; user authorized proceeding through build (incl. parallel work once architecture is mapped).
**Builds on:** the completed base + Night Update. First phase of the full-game roadmap (later phases: enemy roster, power-ups & mechanics, boss/castle, water, content).

---

## 1. Vision

Turn the single-level game into a **sequenced, themed, multi-level game with looping music** — the foundation every later phase builds on. Reuses all existing entities; adds **no** new enemies/power-ups (those are Phases 2-3). The refined Claude **Spark Hero** (done) stars throughout.

## 2. Goals

- Play through **5 levels in sequence** (World X-Y labels), advancing on the flag; finish all → victory.
- **Two themed area types** — overworld (moonlit) + underground (cave) — chosen per level via a data header.
- **Screens & flow:** title → level-intro card → play → level-complete → next/victory; game-over.
- **5 looping music tracks**, one per level cycling every 5 (`track = level % 5`), pre-rendered procedurally.
- Lives/score/tokens **persist across levels**; death respawns at the current level's start.
- Pure sequence logic is **unit-tested**; every level is **completable** (traversal bot).

## 3. Non-Goals (later phases)

New enemies, Fire Flower/Star, warp pipes, moving platforms, boss/castle gameplay, swimming.

---

## 4. Level file format (data-driven)

Optional first line header, then the ASCII grid (unchanged tiles `X = B ? M C G Y P F`):

```
# type: underground
................
...
XXXXXXXXXXXXXXXX
```

- `Level` parses the `# type:` header → `self.area_type` (`"overworld"` default | `"underground"`). Lines starting with `#` are metadata, not grid rows.

## 5. `levelset.py` — pure sequence logic (unit-tested)

```python
LEVELS = ["level_1.txt", "level_2.txt", "level_3.txt", "level_4.txt", "level_5.txt"]

def level_count() -> int                  # len(LEVELS)
def level_file(index) -> str              # LEVELS[index]
def world_label(index) -> str             # "1-1","1-2","1-3","1-4","2-1" (world=index//4+1, stage=index%4+1)
def track_number(index) -> int            # (index % 5) + 1   -> 1..5
def next_index(index) -> int | None       # index+1, or None if last (-> game complete)
```

## 6. `music.py` — `MusicManager`

- `__init__()`: no-op safe if `pygame.mixer` not initialized (`enabled` flag).
- `play_for_level(index)`: load `music/track_{track_number(index)}.wav` via `pygame.mixer.music`, `play(loops=-1)`; tracks current track to avoid restarting the same one.
- `stop()`: stop music (used on title/game-over).
- Volume kept gentle (~0.5). Degrades silently with no audio.

## 7. `tools/make_music.py` — pre-render the 5 tracks

Pure-stdlib synth (like `sound.py`): each track = a seamless ~8-12s loop of warm pad chords + a soft four-on-the-floor kick + an arpeggio + a simple bassline, in a different key/tempo/mood per track (5 "soft synthwave/EDM" moods). Writes int16 mono 44.1 kHz WAVs to `music/track_1.wav … track_5.wav` (committed as data, bundled via `--add-data`). Seamless loop = whole-number bar lengths and fade-free wrap.

## 8. Game states & flow

State machine (extends current): `TITLE → LEVEL_INTRO → PLAYING → LEVEL_COMPLETE → (LEVEL_INTRO | GAME_COMPLETE)` and `PLAYING → GAME_OVER`.

- **TITLE:** Spark Hero + "SUPER CLAUDE BROS" + "Press ENTER". Enter → new game (reset stats, index 0).
- **LEVEL_INTRO:** "WORLD X-Y" card ~1.2s (timer), music for that level starts; → PLAYING.
- **PLAYING:** as today, on the current level.
- **LEVEL_COMPLETE:** flag reached → brief banner; `next_index` → next LEVEL_INTRO, or `None` → GAME_COMPLETE.
- **GAME_OVER / GAME_COMPLETE:** banner; Enter → TITLE.
- **Persistence:** score/tokens/lives carry across levels; reset only on new game. Death → respawn at current level start (reload current level, keep stats); 0 lives → GAME_OVER.

## 9. Area theming (`assets.py`, `settings.py`)

- `draw_background(surface, camera, area_type)` and `draw_block(surface, rect, kind, used, area_type)` branch on type.
- **overworld:** current moonlit night (sky `NIGHT`, moon, stars, sage-dark ground).
- **underground:** cave — flat very-dark sky, a dim ceiling band, cooler/greyer ground tint, no moon/stars.
- `castle` / `underwater` enum values reserved; fall back to overworld visuals until their phases.
- Underground palette constants added to `settings.py`.

## 10. Architecture & files

**New:** `game/levelset.py`, `game/music.py`, `tools/make_music.py`, `music/track_1..5.wav`, `levels/level_1..5.txt`, `tests/test_levelset.py`.
**Modified:** `game/game.py` (states/screens/level-advance/music/persistent stats), `game/level.py` (`# type:` header → `area_type`), `game/assets.py` (area-type background/blocks + title/intro helpers), `game/settings.py` (underground palette, level/music config), `game/hud.py` (dynamic World X-Y), `tests/test_level.py` (header parse), `README.md`, `.gitignore` (keep `music/*.wav`; build/dist ignored).
**Reused unchanged:** all entities (player/goomba/flyer/coin/block/mushroom/flag), physics, camera, effects, sound, scoring.

## 11. Starter content

5 completable levels mixing overworld + underground, gentle difficulty ramp, using existing entities. Labeled World 1-1..1-4, 2-1. Each verified by the traversal bot.

## 12. Testing

- **Unit (TDD):** `test_levelset.py` — `world_label` (0→"1-1", 4→"2-1"), `track_number` (0→1, 4→5, 5→1), `next_index` (last→None); `test_level.py` extended for the `# type:` header.
- **Run/observe:** theming per area, the screen flow, music playback + switching.
- **Bot:** traversal confirms each of the 5 levels is completable.

## 13. Success criteria

From the title screen, the player presses Enter, sees "WORLD 1-1" with music, plays a moonlit level, reaches the flag, advances (new music) through 5 levels across overworld + underground, and on finishing the last sees a victory screen — with lives/score carried across, every level beatable, music looping per level and cycling every 5, and the sequence logic covered by tests.
