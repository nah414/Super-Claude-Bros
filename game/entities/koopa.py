from game import settings as S
from game import assets
from game.physics import move_and_collide
from game.entities.entity import Entity


class Koopa(Entity):
    """Turtle enemy with a walk -> shell -> slide state machine.

    Stomp a walking Koopa and it withdraws into an idle shell. Touch the idle
    shell from the side to kick it: it slides fast, bounces off walls, and bowls
    over other enemies. Stomp a sliding shell to stop it. A live (idle or
    sliding) shell still hurts you from the side.
    """

    def __init__(self, x, y):
        super().__init__(x + 6, y + S.TILE - 28, 28, 28)
        self.state = "walk"
        self.direction = -1
        self.kick_cooldown = 0
        self.score = S.KOOPA_SCORE

    def player_hit(self, from_top, player_cx):
        """Resolve a player collision; mutate state and return the outcome."""
        if self.state == "walk":
            if from_top:
                self.state = "shell"
                self.vx = 0.0
                return "stomp"
            return "hurt"
        if self.state == "shell":
            if from_top:
                return "bounce"
            # kicked from the side -> slide away from the player
            self.state = "slide"
            self.direction = 1 if player_cx <= self.rect.centerx else -1
            self.kick_cooldown = S.SHELL_KICK_COOLDOWN
            return "kick"
        # slide
        if from_top:
            self.state = "shell"
            self.vx = 0.0
            return "stomp_stop"
        return "hurt"

    def update(self, level):
        if self.kick_cooldown > 0:
            self.kick_cooldown -= 1
        self.vy = min(self.vy + S.GRAVITY, S.MAX_FALL)
        if self.state == "walk":
            self.vx = S.KOOPA_SPEED * self.direction
            c = move_and_collide(self, level.solids)
            if c["left"] or c["right"]:
                self.direction *= -1
            elif c["bottom"]:
                # ledge detection (same as Goomba): turn at a pit edge
                ahead = self.rect.right + 1 if self.direction > 0 else self.rect.left - 1
                if not any(s.collidepoint(ahead, self.rect.bottom + 2) for s in level.solids):
                    self.direction *= -1
        elif self.state == "slide":
            self.vx = S.SHELL_SPEED * self.direction
            c = move_and_collide(self, level.solids)
            if c["left"] or c["right"]:
                self.direction *= -1            # bounce off walls; NO ledge-detect (falls into pits)
        else:  # shell (idle)
            self.vx = 0.0
            move_and_collide(self, level.solids)
        if self.y > S.PIT_DEATH_Y:
            self.alive = False

    def draw(self, surface, camera):
        assets.draw_koopa(surface, camera.apply(self.rect), self.state, self.direction)
