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
        self.ducking = False
        self.air_jumped = False
        self.last_jump_ms = -100000
        self.invuln_until = 0
        self.last_fire_ms = -100000
        self.carrying = None             # a held Koopa shell, or None

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

    def swim_stroke(self):
        self.vy = S.SWIM_STROKE              # a fixed upward push per tap (water only)

    # --- power state ---
    def unstick(self, solids):
        """Eject the hitbox from any solid it overlaps, pushing out the shallowest way.

        A power change resizes the box (grow: +width to the right, +height upward),
        which can leave the hero embedded in a wall or ceiling. If left embedded, the
        velocity-sign collision resolver snaps the hero to the solid's FAR side on the
        next move (teleport-through) and wedges them — the World-8 'frozen' bug. Run
        this right after every resize so each frame starts from a valid position.
        """
        if not solids:
            return
        for _ in range(4):                   # a few passes settle corners / stacked tiles
            r = self.rect
            hit = next((s for s in solids if r.colliderect(s)), None)
            if hit is None:
                return
            pen_left  = r.right - hit.left   # move LEFT this far to clear
            pen_right = hit.right - r.left   # move RIGHT this far to clear
            pen_up    = r.bottom - hit.top   # move UP this far to clear
            pen_down  = hit.bottom - r.top   # move DOWN this far to clear
            m = min(pen_left, pen_right, pen_up, pen_down)
            if m == pen_up:
                self.y -= pen_up             # lift out onto the surface
            elif m == pen_down:
                self.y += pen_down           # lower out from under a ceiling
            elif m == pen_left:
                self.x -= pen_left
            else:
                self.x += pen_right

    def _resize_keep_feet(self, size):
        """Set (w, h) while keeping the feet (rect bottom) planted. Bottom-anchored so
        it is correct whether the hero is currently standing OR crouched."""
        bottom = self.y + self.h
        self.w, self.h = size
        self.y = bottom - self.h

    def grow(self, solids=None):
        if self.power == "small":
            self._resize_keep_feet(S.PLAYER_BIG)
            self.power = "big"
            self.ducking = False
            self.unstick(solids)             # never finish a resize embedded in a wall

    def become_fire(self, solids=None):
        if self.power == "small":
            self._resize_keep_feet(S.PLAYER_BIG)
        self.power = "fire"
        self.ducking = False
        self.unstick(solids)

    def can_shoot(self, now_ms):
        return self.power == "fire" and now_ms - self.last_fire_ms >= S.FIRE_COOLDOWN_MS

    def record_fire(self, now_ms):
        self.last_fire_ms = now_ms

    def take_damage(self, now_ms):
        if now_ms < self.invuln_until:
            return False                      # invulnerable: ignore
        if self.power == "fire":
            self.power = "big"                # tier-drop: fire -> big (same size)
            self.invuln_until = now_ms + S.POWER_INVULN_MS
            return False
        if self.power == "big":
            self._resize_keep_feet(S.PLAYER_SMALL)
            self.power = "small"
            self.ducking = False
            self.invuln_until = now_ms + S.POWER_INVULN_MS
            return False
        return True                           # small + vulnerable -> life lost

    # --- ducking ---
    def _stand_size(self):
        return S.PLAYER_BIG if self.power in ("big", "fire") else S.PLAYER_SMALL

    def _duck_size(self):
        return S.PLAYER_BIG_DUCK if self.power in ("big", "fire") else S.PLAYER_SMALL_DUCK

    def _stand_fits(self, solids):
        """Is there headroom to return to full standing height (feet planted)?"""
        sw, sh = self._stand_size()
        bottom = self.y + self.h
        test = pygame.Rect(round(self.x), round(bottom - sh), sw, sh)
        return not any(test.colliderect(s) for s in solids)

    def _update_duck(self, keys, solids):
        want = ((keys[pygame.K_DOWN] or keys[pygame.K_s])
                and self.on_ground and not getattr(self, "_water", False))
        if want and not self.ducking:
            self._resize_keep_feet(self._duck_size())   # crouch: shorter, feet planted
            self.ducking = True
        elif self.ducking and not want:
            if self._stand_fits(solids):                # only stand if there's headroom
                self._resize_keep_feet(self._stand_size())
                self.ducking = False
            # else: a ceiling is overhead -> stay crouched (classic behavior)

    # --- per-frame ---
    def update(self, level):
        area = getattr(level, "area_type", "")
        self._ice = area == "ice"
        self._water = area == "water"
        keys = pygame.key.get_pressed()
        self._update_duck(keys, level.solids)
        self._horizontal(keys)
        if self._water:
            self.vy = min(self.vy + S.SWIM_GRAVITY, S.SWIM_MAX_SINK)
        else:
            self.vy = min(self.vy + S.GRAVITY, S.MAX_FALL)
        contacts = move_and_collide(self, level.solids)
        self.on_ground = contacts["bottom"]
        if self.on_ground:
            self.air_jumped = False          # reset double-jump on landing

    def _horizontal(self, keys):
        # no walking while crouched — slide to a stop (friction), classic feel
        left = (keys[pygame.K_LEFT] or keys[pygame.K_a]) and not self.ducking
        right = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and not self.ducking
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
            fr = S.ICE_FRICTION if getattr(self, "_ice", False) else S.FRICTION
            if self.vx > 0:
                self.vx = max(0.0, self.vx - fr)
            else:
                self.vx = min(0.0, self.vx + fr)

    def draw(self, surface, camera):
        # flicker while invulnerable
        t = pygame.time.get_ticks()
        if t < self.invuln_until and (t // 100) % 2 == 0:
            return
        assets.draw_player(surface, camera.apply(self.rect), self.facing, self.power, self.ducking)
