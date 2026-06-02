from game import settings as S
from game import assets
from game.physics import move_and_collide
from game.entities.entity import Entity


class Boss(Entity):
    """The Iron Koopa: armored (stomp-proof), paces and lobs shots, falls to 3 fireballs."""

    def __init__(self, x, y):
        super().__init__(x, y + S.TILE - S.BOSS_SIZE[1], *S.BOSS_SIZE)
        self.direction = -1
        self.hp = S.BOSS_HP
        self.flash = 0
        self.speed = S.BOSS_SPEED
        self.shot_cd = S.BOSS_SHOT_COOLDOWN
        self.shot_timer = self.shot_cd
        self.color = S.BOSS_COLORS[0]
        self.title = S.BOSS_TITLES[0]
        self.score = S.BOSS_SCORE

    def set_tier(self, world):
        """Scale stats + identity to the world (1-based)."""
        self.hp = S.BOSS_HP + (world - 1) // 2
        if world >= 8:
            self.hp += 2                                  # the King: an extra-tough finale
        self.speed = S.BOSS_SPEED + (world - 1) * 0.10
        self.shot_cd = max(54, S.BOSS_SHOT_COOLDOWN - (world - 1) * 7)   # ~20% less frequent than before
        self.shot_timer = self.shot_cd
        self.color = S.BOSS_COLORS[(world - 1) % len(S.BOSS_COLORS)]
        self.title = S.BOSS_TITLES[(world - 1) % len(S.BOSS_TITLES)]

    def hit(self):
        """Take one fireball. Returns True if this blow defeats it."""
        if self.flash > 0:
            return False                  # brief invuln between hits
        self.hp -= 1
        self.flash = S.BOSS_FLASH
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def update(self, level):
        if self.flash > 0:
            self.flash -= 1
        if self.shot_timer > 0:
            self.shot_timer -= 1
        self.vx = self.speed * self.direction
        self.vy = min(self.vy + S.GRAVITY, S.MAX_FALL)
        c = move_and_collide(self, level.solids)
        if c["left"] or c["right"]:
            self.direction *= -1
        elif c["bottom"]:
            ahead = self.rect.right + 1 if self.direction > 0 else self.rect.left - 1
            if not any(s.collidepoint(ahead, self.rect.bottom + 2) for s in level.solids):
                self.direction *= -1            # don't pace into a lava pit

    def ready_to_shoot(self):
        if self.shot_timer <= 0:
            self.shot_timer = self.shot_cd
            return True
        return False

    def draw(self, surface, camera):
        assets.draw_boss(surface, camera.apply(self.rect), self.direction, self.flash > 0, self.color)
