import pygame
from game import settings as S


class Cannon:
    """A Bill Blaster firing point: fires toward an in-range player on a cooldown."""

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, S.TILE, S.TILE)
        self.timer = S.BULLET_COOLDOWN

    def tick(self, player_cx):
        """Advance one frame. Returns +1/-1 (fire direction toward player) or None."""
        if self.timer > 0:
            self.timer -= 1
            return None
        dist = player_cx - self.rect.centerx
        if S.BULLET_MIN_DIST < abs(dist) < S.BULLET_MAX_DIST:
            self.timer = S.BULLET_COOLDOWN
            return 1 if dist > 0 else -1
        return None
