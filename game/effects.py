import pygame
from game import settings as S
from game import assets


class ScorePopup:
    """Floating text that rises and fades at a world position."""
    LIFE = 42

    def __init__(self, x, y, text):
        self.x = float(x); self.y = float(y); self.text = text
        self.age = 0; self.alive = True

    def update(self):
        self.y -= 0.8
        self.age += 1
        if self.age >= self.LIFE:
            self.alive = False

    def draw(self, surface, camera, font):
        img = font.render(self.text, True, S.CREAM)
        img.set_alpha(max(0, 255 - int(255 * self.age / self.LIFE)))
        surface.blit(img, img.get_rect(center=(round(self.x) - camera.offset_x, round(self.y))))


class RisingToken:
    """A spark that pops out of a '?' box, rises, and fades."""
    LIFE = 22

    def __init__(self, x, y):
        self.x = float(x); self.y = float(y); self.age = 0; self.alive = True

    def update(self):
        self.y -= 2.4
        self.age += 1
        if self.age >= self.LIFE:
            self.alive = False

    def draw(self, surface, camera, font=None):
        r = pygame.Rect(round(self.x) - camera.offset_x - 8, round(self.y) - 8, 16, 16)
        assets.draw_coin(surface, r)
