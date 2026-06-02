import math
from game import settings as S
from game import assets
from game.entities.entity import Entity


class CheepCheep(Entity):
    """A drifting fish: glides horizontally, bobs vertically, ignores gravity. Stompable."""

    def __init__(self, x, y):
        super().__init__(x + 4, y + 4, S.TILE - 8, S.TILE - 12)
        self.origin_x = float(x + 4)
        self.base_y = float(y + 4)
        self.direction = -1
        self.phase = 0
        self.score = S.CHEEP_SCORE

    def update(self, level):
        self.phase += 1
        self.x += S.CHEEP_SPEED * self.direction
        if abs(self.x - self.origin_x) >= S.CHEEP_RANGE:
            self.direction *= -1
        self.y = self.base_y + S.CHEEP_BOB_AMP * math.sin(self.phase * 2 * math.pi / S.CHEEP_BOB_PERIOD)

    def draw(self, surface, camera):
        assets.draw_cheep(surface, camera.apply(self.rect), self.direction)
