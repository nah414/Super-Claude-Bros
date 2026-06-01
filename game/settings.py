"""Single source of truth for every tunable constant."""
import os
import sys

# --- Window ---
WIDTH, HEIGHT = 960, 600
TILE = 40
FPS = 60
TITLE = "Claude's Platformer"

# --- Colors (Anthropic brand) ---
ORANGE    = (217, 119, 87)   # #d97757  hero, sparks, accents
CREAM     = (250, 249, 245)  # #faf9f5  sky / light
SAGE      = (120, 140, 93)   # #788c5d  ground / platforms
BLUE      = (106, 155, 204)  # #6a9bcc  secondary accents
INK       = (20, 20, 19)     # #141413  outlines / text
LIGHTGRAY = (232, 230, 220)  # #e8e6dc  subtle fills
MIDGRAY   = (176, 174, 165)  # #b0aea5  used question block

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

# --- Gameplay ---
START_LIVES = 3
PIT_DEATH_Y = HEIGHT + 80   # falling below this = death


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
