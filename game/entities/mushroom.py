from game import settings as S
from game import assets
from game.physics import move_and_collide
from game.entities.entity import Entity


class Mushroom(Entity):
    """Rises out of an 'M' box, then walks, reversing at walls. Grows the player."""

    def __init__(self, box_x, box_y):
        size = S.TILE - 8
        super().__init__(box_x + 4, box_y, size, size)
        self.target_y = box_y - size          # rise one mushroom-height out of the box
        self.emerging = True
        self.direction = 1
        self.score = S.MUSHROOM_SCORE

    def update(self, level):
        if self.emerging:
            self.y -= 2.0
            if self.y <= self.target_y:
                self.y = self.target_y
                self.emerging = False
            return
        self.vx = S.MUSHROOM_SPEED * self.direction
        self.vy = min(self.vy + S.GRAVITY, S.MAX_FALL)
        c = move_and_collide(self, level.solids)
        if c["left"] or c["right"]:
            self.direction *= -1

    def draw(self, surface, camera):
        assets.draw_mushroom(surface, camera.apply(self.rect))
