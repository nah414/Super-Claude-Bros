from game import settings as S
from game import assets
from game.entities.entity import Entity


class Coin(Entity):
    """A sunburst 'spark' collectible, centered in its tile."""

    def __init__(self, x, y):
        size = S.TILE // 2
        super().__init__(x + size // 2, y + size // 2, size, size)
        self.collected = False

    def draw(self, surface, camera):
        assets.draw_coin(surface, camera.apply(self.rect))
