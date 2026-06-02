from game import settings as S
from game import assets
from game.physics import move_and_collide
from game.entities.entity import Entity


class Cog(Entity):
    """A marching factory robot: paces with ledge detection, stompable."""

    def __init__(self, x, y):
        super().__init__(x + 5, y + S.TILE - 28, 26, 28)
        self.direction = -1
        self.score = S.COG_SCORE

    def update(self, level):
        self.vx = S.COG_SPEED * self.direction
        self.vy = min(self.vy + S.GRAVITY, S.MAX_FALL)
        c = move_and_collide(self, level.solids)
        if c["left"] or c["right"]:
            self.direction *= -1
        elif c["bottom"]:
            ahead = self.rect.right + 1 if self.direction > 0 else self.rect.left - 1
            if not any(s.collidepoint(ahead, self.rect.bottom + 2) for s in level.solids):
                self.direction *= -1

    def draw(self, surface, camera):
        assets.draw_cog(surface, camera.apply(self.rect), self.direction)
