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
JUMP_VELOCITY = -14.5
JUMP_CUTOFF   = -4.0
STOMP_BOUNCE  = -8.0

# --- Double-jump ---
DOUBLE_TAP_MS        = 300
DOUBLE_JUMP_VELOCITY = -12.0

# --- Player power sizes (w, h) ---
PLAYER_SMALL    = (30, 44)
PLAYER_BIG      = (38, 62)
# crouch sizes (same width, shorter) — big ducks to ~1 tile so it can tuck low
PLAYER_SMALL_DUCK = (30, 30)
PLAYER_BIG_DUCK   = (38, 40)
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

# --- Fire power ---
FIRE             = (235, 96, 56)
FIREBALL_SPEED   = 7.0
FIREBALL_BOUNCE  = -7.0
FIREBALL_LIFE    = 150
FIRE_COOLDOWN_MS = 300
MAX_FIREBALLS    = 2
FIREBALL_SCORE   = 200
FLOWER_SCORE     = 1000

# --- Koopa ---
KOOPA_SPEED         = 1.3
SHELL_SPEED         = 6.0
SHELL_KICK_COOLDOWN = 12       # frames the kicker is safe right after a kick
KOOPA_SCORE         = 200
KOOPA_SHELL         = (96, 156, 76)

# --- Pipes ---
PIPE    = (84, 138, 74)
PIPE_DK = (54, 92, 50)

# --- Castle / Boss ---
CASTLE_BG     = (26, 16, 18)
CASTLE_GROUND = (54, 42, 46)
CASTLE_EDGE   = (122, 74, 64)
LAVA          = (226, 94, 38)
LAVA_GLOW     = (250, 176, 80)
BOSS_SIZE          = (58, 58)
BOSS_HP            = 3
BOSS_SPEED         = 1.1
BOSS_FLASH         = 30        # frames of invuln after a fireball hit
BOSS_SHOT_SIZE     = 18
BOSS_SHOT_SPEED    = 4.5
BOSS_SHOT_LIFE     = 150
BOSS_SHOT_COOLDOWN = 90        # frames between boss shots
BOSS_SCORE         = 5000
# per-world boss flavor (index = world-1); scales difficulty + identity
BOSS_COLORS = [(96, 156, 76), (96, 140, 200), (76, 170, 160), (170, 205, 228),
               (150, 110, 180), (210, 120, 80), (120, 130, 150), (210, 170, 80)]
BOSS_TITLES = ["IRON KOOPA", "GALE KOOPA", "TIDE KOOPA", "FROST KOOPA",
               "PHANTOM KOOPA", "EMBER KOOPA", "STORM KOOPA", "KING KOOPA"]
# themed castle skins (visuals only — physics stay "castle": dry, lava, normal movement)
CASTLE_SKINS = {
    "castle":       {"bg": (26, 16, 18), "ground": (54, 42, 46), "edge": (122, 74, 64), "glow": (200, 70, 30)},
    "castle_sky":   {"bg": (44, 32, 60), "ground": (70, 60, 88), "edge": (150, 138, 178), "glow": (180, 120, 90)},
    "castle_sea":   {"bg": (12, 30, 44), "ground": (40, 64, 74), "edge": (96, 144, 152), "glow": (60, 150, 160)},
    "castle_ice":   {"bg": (34, 50, 70), "ground": (86, 110, 134), "edge": (190, 214, 234), "glow": (120, 170, 210)},
    "castle_haunt": {"bg": (30, 20, 42), "ground": (56, 42, 64), "edge": (118, 90, 128), "glow": (150, 90, 150)},
    "castle_factory": {"bg": (28, 30, 36), "ground": (80, 84, 94), "edge": (150, 156, 168), "glow": (180, 140, 80)},
    "castle_caldera": {"bg": (40, 14, 12), "ground": (58, 36, 32), "edge": (170, 80, 44), "glow": (230, 90, 30)},
    "castle_keep": {"bg": (16, 10, 16), "ground": (48, 36, 48), "edge": (180, 150, 70), "glow": (150, 40, 50)},
}

# --- Sky (World 2) ---
SKY_TOP    = (58, 44, 92)      # dusk gradient top
SKY_BOTTOM = (224, 146, 92)    # warm horizon
SKY_GROUND = (90, 76, 110)
SKY_EDGE   = (196, 168, 150)
CLOUD      = (244, 238, 240)
CANNON     = (40, 40, 46)
# Bullet Bills
BULLET_SPEED    = 3.4
BULLET_SIZE     = 26
BULLET_LIFE     = 360
BULLET_SCORE    = 200
BULLET_COOLDOWN = 150          # frames between a cannon's shots
BULLET_MIN_DIST = 70           # don't fire if the player is closer than this
BULLET_MAX_DIST = 520          # ...or farther than this

# --- Water (World 3) ---
WATER_TOP    = (40, 110, 140)
WATER_BOTTOM = (14, 30, 70)
SEABED       = (58, 86, 96)
SEABED_EDGE  = (110, 150, 140)
BUBBLE       = (210, 236, 240)
SWIM_GRAVITY  = 0.28           # gentle sink (vs GRAVITY)
SWIM_MAX_SINK = 3.0            # slow terminal sink speed
SWIM_STROKE   = -5.0           # upward push per stroke
# Cheep-Cheep
CHEEP_COLOR      = (236, 112, 122)
CHEEP_SPEED      = 1.4
CHEEP_BOB_AMP    = 16
CHEEP_BOB_PERIOD = 110
CHEEP_RANGE      = 150
CHEEP_SCORE      = 200

# --- Ice (World 4) ---
ICE_SKY      = (150, 196, 224)
ICE_GROUND   = (198, 222, 236)
ICE_EDGE     = (236, 248, 255)
SNOW         = (224, 240, 250)
ICE_FRICTION = 0.05            # slippery: barely decelerates (vs FRICTION)
FROST_SPEED  = 1.2
FROST_SCORE  = 200

# --- Haunted (World 5) ---
HAUNT_BG     = (38, 26, 56)
HAUNT_GROUND = (60, 44, 66)
HAUNT_EDGE   = (120, 90, 130)
FOG          = (180, 168, 200)
MOON_PALE    = (216, 208, 230)
BOO_SPEED = 1.3
BOO_SCORE = 200

# --- Factory (World 6) ---
FACTORY_BG     = (30, 32, 38)
FACTORY_GROUND = (74, 78, 86)
FACTORY_EDGE   = (140, 146, 158)
BELT           = (54, 58, 66)
BELT_LIGHT     = (150, 156, 168)
CONVEYOR_SPEED = 2.0           # how fast a belt carries a grounded hero
COG_SPEED      = 1.4
COG_SCORE      = 200

# --- Caldera (World 7) ---
CALDERA_BG      = (40, 16, 14)
CALDERA_GROUND  = (52, 36, 34)
CALDERA_EDGE    = (152, 72, 42)
LAVA_RISE_SPEED = 0.25         # px/frame the lava sea climbs
BUBBLE_INTERVAL = 110          # frames between lava bubbles
BUBBLE_VY       = -10.0
BUBBLE_SIZE     = 22

# --- Koopa Keep (World 8 finale) ---
KEEP_BG     = (18, 12, 18)
KEEP_GROUND = (46, 34, 44)
KEEP_EDGE   = (132, 62, 72)


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
