"""Single source of truth for every tunable constant."""
import os
import sys

# --- Window ---
WIDTH, HEIGHT = 960, 600
TILE = 40
FPS = 60
TITLE = "Super Claude Bros"

# --- Colors (Anthropic brand) ---
ORANGE    = (217, 119, 87)   # #d97757  hero, sparks, accents
CREAM     = (250, 249, 245)  # #faf9f5  light / text
SAGE      = (120, 140, 93)   # #788c5d  (legacy accent)
BLUE      = (106, 155, 204)  # #6a9bcc  secondary accents
INK       = (20, 20, 19)     # #141413  outlines
LIGHTGRAY = (232, 230, 220)  # #e8e6dc  subtle fills
MIDGRAY   = (176, 174, 165)  # #b0aea5  used boxes / rims

# --- Night theme ---
NIGHT       = (20, 20, 19)   # sky / background (#141413)
GROUND_DARK = (40, 46, 36)   # ground / platform fill
GROUND_EDGE = (72, 86, 58)   # lit top edge
BRICK_DARK  = (74, 72, 66)   # brick fill
MOON        = (232, 230, 210)

# --- Physics (pixels, pixels/frame @ 60 FPS) ---
GRAVITY       = 0.8
MAX_FALL      = 16.0
MOVE_ACCEL    = 0.5
MAX_WALK      = 4.0
MAX_RUN       = 6.5
FRICTION      = 0.4
SKID_DECEL    = 0.8
JUMP_VELOCITY = -14.0
JUMP_CUTOFF   = -4.0
STOMP_BOUNCE  = -8.0

# --- Double-jump ---
DOUBLE_TAP_MS        = 300
DOUBLE_JUMP_VELOCITY = -12.0

# --- Player power sizes (w, h) ---
PLAYER_SMALL    = (30, 44)
PLAYER_BIG      = (38, 62)
POWER_INVULN_MS = 1500

# --- Mushroom ---
MUSHROOM_SPEED = 1.6
MUSHROOM_SCORE = 1000

# --- Flyer ---
FLYER_SPEED      = 1.8
FLYER_BOB_AMP    = 12
FLYER_BOB_PERIOD = 90
FLYER_RANGE      = 120
FLYER_SCORE      = 200

# --- Scoring ---
TOKEN_SCORE      = 100
STOMP_SCORE      = 200
BONUS_LIFE_EVERY = 100

# --- Gameplay ---
START_LIVES = 3
PIT_DEATH_Y = HEIGHT + 80   # falling below this = death

# --- Audio ---
SAMPLE_RATE = 44100
MUSIC_VOLUME = 0.5

# --- Underground theme ---
CAVE_BG     = (12, 12, 14)
CAVE_GROUND = (46, 44, 52)
CAVE_EDGE   = (96, 92, 110)
CAVE_CEIL   = (28, 26, 34)


def resource_path(rel):
    """Resolve a data file path for both source runs and PyInstaller bundles.

    When frozen by PyInstaller (one-file), bundled data is unpacked to a temp
    dir exposed as sys._MEIPASS. From source, paths resolve relative to the
    project root (this file's parent's parent), so the game works regardless of
    the current working directory.
    """
    base = getattr(sys, "_MEIPASS",
                   os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base, rel)
