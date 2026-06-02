from game import settings as S
from game import assets
from game.entities.entity import Entity


class BossShot(Entity):
    """A fireball the boss lobs at the player; flies straight, despawns after a while."""

    def __init__(self, x, y, direction):
        super().__init__(x, y - S.BOSS_SHOT_SIZE // 2, S.BOSS_SHOT_SIZE, S.BOSS_SHOT_SIZE)
        self.vx = S.BOSS_SHOT_SPEED * direction
        self.life = S.BOSS_SHOT_LIFE

    def update(self, level):
        self.x += self.vx
        self.life -= 1
        if self.life <= 0:
            self.alive = False

    def draw(self, surface, camera):
        assets.draw_boss_shot(surface, camera.apply(self.rect))
