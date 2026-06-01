from game import settings as S
from game import assets
from game.physics import move_and_collide
from game.entities.entity import Entity


class Fireball(Entity):
    """A bouncing projectile thrown by Fire-Claude. Defeats enemies on contact."""
    SIZE = 16

    def __init__(self, x, y, direction):
        super().__init__(x - self.SIZE // 2, y, self.SIZE, self.SIZE)
        self.vx = S.FIREBALL_SPEED * direction
        self.vy = 2.0
        self.life = S.FIREBALL_LIFE
        self.score = S.FIREBALL_SCORE

    def update(self, level):
        self.life -= 1
        if self.life <= 0:
            self.alive = False
            return
        self.vy = min(self.vy + S.GRAVITY, S.MAX_FALL)
        c = move_and_collide(self, level.solids)
        if c["bottom"]:
            self.vy = S.FIREBALL_BOUNCE          # bounce up off the ground
        if c["left"] or c["right"]:
            self.alive = False                   # die on a wall

    def draw(self, surface, camera):
        assets.draw_fireball(surface, camera.apply(self.rect))
