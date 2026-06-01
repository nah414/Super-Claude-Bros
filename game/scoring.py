"""Pure scoring helpers."""
from game import settings as S


def bonus_lives(old_tokens, new_tokens, every=S.BONUS_LIFE_EVERY):
    """How many life thresholds were crossed going from old_tokens to new_tokens."""
    return new_tokens // every - old_tokens // every
