from game import settings as S
from game import assets
from game.entities.entity import Entity


class BulletBill(Entity):
    """A cannon shot: flies dead straight (no gravity), stompable, hurts on contact."""

    def __init__(self, x, y, direction):
        super().__init__(x - S.BULLET_SIZE // 2, y - S.BULLET_SIZE // 2, S.BULLET_SIZE, S.BULLET_SIZE)
        self.direction = direction
        self.vx = S.BULLET_SPEED * direction
        self.life = S.BULLET_LIFE
        self.score = S.BULLET_SCORE

    def update(self, level):
        self.x += self.vx
        self.life -= 1
        if self.life <= 0 or self.x < -50 or self.x > level.width_px + 50:
            self.alive = False

    def draw(self, surface, camera):
        assets.draw_bullet(surface, camera.apply(self.rect), self.direction)
