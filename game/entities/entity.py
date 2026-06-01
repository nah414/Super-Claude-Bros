import pygame


class Entity:
    """Base for everything that lives in the world."""

    def __init__(self, x, y, w, h):
        self.x = float(x)
        self.y = float(y)
        self.w = w
        self.h = h
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True

    @property
    def rect(self):
        return pygame.Rect(round(self.x), round(self.y), self.w, self.h)

    def update(self, level):
        pass

    def draw(self, surface, camera):
        pass
