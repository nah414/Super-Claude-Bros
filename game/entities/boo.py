from game import settings as S
from game import assets
from game.entities.entity import Entity


class Boo(Entity):
    """A shy ghost: freezes when the player faces it, hunts when looked away from.
    Ignores gravity and terrain; stomp-proof (fireball it or outmaneuver it)."""

    stomp_proof = True

    def __init__(self, x, y):
        super().__init__(x + 5, y + 5, 30, 30)
        self.frozen = True
        self.facing = -1
        self.score = S.BOO_SCORE

    def chase(self, player):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = max(1.0, (dx * dx + dy * dy) ** 0.5)
        if dist > S.BOO_CHASE_RANGE:                    # player far/off-screen -> stay dormant
            self.frozen = True                          # (keeps a bonus-room Boo from roaming out)
            return
        to_boo = 1 if self.rect.centerx >= player.rect.centerx else -1
        self.facing = -to_boo                          # look at the player
        self.frozen = (player.facing == to_boo)        # player looking toward it -> shy
        if not self.frozen:
            self.x += S.BOO_SPEED * dx / dist
            self.y += S.BOO_SPEED * dy / dist

    def draw(self, surface, camera):
        assets.draw_boo(surface, camera.apply(self.rect), self.frozen, self.facing)
