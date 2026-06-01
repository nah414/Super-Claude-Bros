from game import settings as S
from game import assets
from game.entities.entity import Entity


class Flag(Entity):
    """Finish pole. The 'F' marker is its top; the pole hangs down 5 tiles."""

    def __init__(self, x, y):
        super().__init__(x + S.TILE // 2 - 4, y, 8, S.TILE * 5)

    def draw(self, surface, camera):
        assets.draw_flag(surface, camera.apply(self.rect))
