import pygame
from game import settings as S
from game import assets
from game.physics import move_and_collide
from game.entities.entity import Entity


class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, S.PLAYER_SMALL[0], S.PLAYER_SMALL[1])
        self.on_ground = False
        self.facing = 1
        self.power = "small"      # extension point for power-ups

    def start_jump(self):
        if self.on_ground:
            self.vy = S.JUMP_VELOCITY
            self.on_ground = False

    def end_jump(self):
        if self.vy < S.JUMP_CUTOFF:      # released while still rising fast
            self.vy = S.JUMP_CUTOFF

    def update(self, level):
        self._horizontal(pygame.key.get_pressed())
        self.vy = min(self.vy + S.GRAVITY, S.MAX_FALL)
        contacts = move_and_collide(self, level.solids)
        self.on_ground = contacts["bottom"]

    def _horizontal(self, keys):
        left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        run = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        top = S.MAX_RUN if run else S.MAX_WALK
        if right and not left:
            self.facing = 1
            self.vx += S.SKID_DECEL if self.vx < 0 else S.MOVE_ACCEL
            self.vx = min(self.vx, top)
        elif left and not right:
            self.facing = -1
            self.vx -= S.SKID_DECEL if self.vx > 0 else S.MOVE_ACCEL
            self.vx = max(self.vx, -top)
        else:
            if self.vx > 0:
                self.vx = max(0.0, self.vx - S.FRICTION)
            else:
                self.vx = min(0.0, self.vx + S.FRICTION)

    def draw(self, surface, camera):
        assets.draw_player(surface, camera.apply(self.rect), self.facing, self.power)
