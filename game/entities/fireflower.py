from game import settings as S
from game import assets
from game.entities.entity import Entity


class FireFlower(Entity):
    """Emerges from an 'M' box and stays put; collected -> fire power."""

    def __init__(self, box_x, box_y):
        size = S.TILE - 8
        super().__init__(box_x + 4, box_y, size, size)
        self.target_y = box_y - size
        self.emerging = True
        self.score = S.FLOWER_SCORE

    def update(self, level):
        if self.emerging:
            self.y -= 2.0
            if self.y <= self.target_y:
                self.y = self.target_y
                self.emerging = False

    def draw(self, surface, camera):
        assets.draw_fireflower(surface, camera.apply(self.rect))
