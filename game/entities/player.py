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
        self.power = "small"
        self.air_jumped = False
        self.last_jump_ms = -100000
        self.invuln_until = 0

    # --- jumping ---
    def press_jump(self, now_ms):
        gap = now_ms - self.last_jump_ms
        self.last_jump_ms = now_ms
        if self.on_ground:
            self.vy = S.JUMP_VELOCITY
            self.on_ground = False
            self.air_jumped = False
        elif not self.air_jumped and gap <= S.DOUBLE_TAP_MS:
            self.vy = S.DOUBLE_JUMP_VELOCITY
            self.air_jumped = True

    def release_jump(self):
        if self.vy < S.JUMP_CUTOFF:          # released while still rising fast
            self.vy = S.JUMP_CUTOFF

    # --- power state ---
    def grow(self):
        if self.power == "small":
            old_h = self.h
            self.w, self.h = S.PLAYER_BIG
            self.y -= (self.h - old_h)       # keep feet planted
            self.power = "big"

    def take_damage(self, now_ms):
        if now_ms < self.invuln_until:
            return False                      # invulnerable: ignore
        if self.power == "big":
            old_h = self.h
            self.w, self.h = S.PLAYER_SMALL
            self.y += (old_h - self.h)
            self.power = "small"
            self.invuln_until = now_ms + S.POWER_INVULN_MS
            return False                      # shrank, survived
        return True                           # small + vulnerable -> life lost

    # --- per-frame ---
    def update(self, level):
        self._horizontal(pygame.key.get_pressed())
        self.vy = min(self.vy + S.GRAVITY, S.MAX_FALL)
        contacts = move_and_collide(self, level.solids)
        self.on_ground = contacts["bottom"]
        if self.on_ground:
            self.air_jumped = False          # reset double-jump on landing

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
        # flicker while invulnerable
        t = pygame.time.get_ticks()
        if t < self.invuln_until and (t // 100) % 2 == 0:
            return
        assets.draw_player(surface, camera.apply(self.rect), self.facing, self.power)
