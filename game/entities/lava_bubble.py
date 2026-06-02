from game import settings as S
from game import assets
from game.entities.entity import Entity


class LavaBubble(Entity):
    """A blob spat up from the lava sea: arcs under gravity, hurts on contact."""

    def __init__(self, x, y):
        super().__init__(x - S.BUBBLE_SIZE // 2, y - S.BUBBLE_SIZE, S.BUBBLE_SIZE, S.BUBBLE_SIZE)
        self.spawn_y = float(y)
        self.vy = S.BUBBLE_VY

    def update(self, level):
        self.vy = min(self.vy + S.GRAVITY, S.MAX_FALL)
        self.y += self.vy
        if self.y > self.spawn_y:          # fell back into the lava
            self.alive = False

    def draw(self, surface, camera):
        assets.draw_lava_bubble(surface, camera.apply(self.rect))
