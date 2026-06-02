from game import settings as S
from game import assets
from game.entities.entity import Entity

SOLID_KINDS = ("X", "=", "B", "?", "M", "T", "t", "N")


class Block(Entity):
    def __init__(self, x, y, kind):
        super().__init__(x, y, S.TILE, S.TILE)
        self.kind = kind
        self.used = False     # for '?'/'M' boxes once bumped

    def draw(self, surface, camera, area_type="overworld"):
        assets.draw_block(surface, camera.apply(self.rect), self.kind, self.used, area_type)
