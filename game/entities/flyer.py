import math
from game import settings as S
from game import assets
from game.entities.entity import Entity


class Flyer(Entity):
    """Hovering enemy: drifts horizontally, bobs vertically, ignores gravity. Stompable."""

    def __init__(self, x, y):
        super().__init__(x + 4, y + 4, S.TILE - 8, S.TILE - 12)
        self.origin_x = float(x + 4)
        self.base_y = float(y + 4)
        self.direction = -1
        self.phase = 0
        self.score = S.FLYER_SCORE

    def update(self, level):
        self.phase += 1
        self.x += S.FLYER_SPEED * self.direction
        if abs(self.x - self.origin_x) >= S.FLYER_RANGE:
            self.direction *= -1
        self.y = self.base_y + S.FLYER_BOB_AMP * math.sin(self.phase * 2 * math.pi / S.FLYER_BOB_PERIOD)

    def draw(self, surface, camera):
        assets.draw_flyer(surface, camera.apply(self.rect))
