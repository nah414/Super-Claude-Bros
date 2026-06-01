from game import settings as S
from game import assets
from game.physics import move_and_collide
from game.entities.entity import Entity


class Goomba(Entity):
    """Walker enemy: paces left/right, reverses at walls, dies on stomp."""
    SPEED = 1.5

    def __init__(self, x, y):
        super().__init__(x + 4, y + S.TILE // 2, S.TILE - 8, S.TILE // 2)
        self.direction = -1

    def update(self, level):
        self.vx = self.SPEED * self.direction
        self.vy = min(self.vy + S.GRAVITY, S.MAX_FALL)
        contacts = move_and_collide(self, level.solids)
        if contacts["left"] or contacts["right"]:
            self.direction *= -1
        elif contacts["bottom"]:
            # ledge detection: turn around rather than walk off a pit edge
            ahead_x = self.rect.right + 1 if self.direction > 0 else self.rect.left - 1
            foot_y = self.rect.bottom + 2
            if not any(s.collidepoint(ahead_x, foot_y) for s in level.solids):
                self.direction *= -1

    def draw(self, surface, camera):
        assets.draw_goomba(surface, camera.apply(self.rect))
