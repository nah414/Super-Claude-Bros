from game import settings as S


class Camera:
    def __init__(self, level_width_px):
        self.offset_x = 0
        self.level_width = level_width_px

    def update(self, target_rect):
        self.offset_x = target_rect.centerx - S.WIDTH // 3
        self.offset_x = max(0, min(self.offset_x, self.level_width - S.WIDTH))

    def apply(self, rect):
        return rect.move(-self.offset_x, 0)
