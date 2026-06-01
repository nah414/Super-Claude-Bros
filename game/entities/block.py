from game import settings as S
from game import assets
from game.entities.entity import Entity

SOLID_KINDS = ("X", "=", "B", "?")


class Block(Entity):
    def __init__(self, x, y, kind):
        super().__init__(x, y, S.TILE, S.TILE)
        self.kind = kind
        self.used = False     # for '?' blocks once bumped

    def draw(self, surface, camera):
        assets.draw_block(surface, camera.apply(self.rect), self.kind, self.used)
