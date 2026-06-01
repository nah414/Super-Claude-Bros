"""Headless traversal bot: holds right, jumps to clear gaps and stomp enemies
ahead. Mechanical proxy for level completability (not a fun-judge)."""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
from game.game import Game
from game.levelset import LEVELS


class Keys:
    def __init__(self):
        self.d = {}

    def __getitem__(self, k):
        return self.d.get(k, False)

    def set(self, k, v):
        self.d[k] = v


keys = Keys()
pygame.key.get_pressed = lambda: keys
keys.set(pygame.K_RIGHT, True)          # always advance right


def solid_at(level, px, py):
    return any(r.collidepoint(px, py) for r in level.solids)


def run_level(idx, max_frames=6000):
    g = Game()
    g.new_game()
    g.index = idx
    g.start_level()
    g.state = "PLAYING"
    p = g.player
    last_x, stuck, jump_hold = p.x, 0, 0
    deaths = 0
    for fr in range(max_frames):
        feet_y = p.rect.bottom + 4
        gap_near = (not solid_at(g.level, p.rect.right + 8, feet_y)
                    and not solid_at(g.level, p.rect.right + 44, feet_y))
        block_ahead = solid_at(g.level, p.rect.right + 3, p.rect.centery)
        enemy_ahead = any(e.alive and e.rect.left < p.rect.right + 50
                          and e.rect.right > p.rect.right
                          and abs(e.rect.centery - p.rect.centery) < 50
                          for e in g.level.enemies)
        if (gap_near or block_ahead or enemy_ahead) and p.on_ground:
            p.press_jump(g.now())
            jump_hold = 6
        elif jump_hold == 3 and gap_near and not p.on_ground:
            p.press_jump(g.now())           # double-jump to extend over a wide gap
        if jump_hold > 0:
            jump_hold -= 1
        prev_lives = g.lives
        g.update()
        if g.state == "LEVEL_COMPLETE":
            return True, fr, p.x, g.level.width_px, deaths
        if g.state == "GAME_OVER":
            return False, fr, p.x, g.level.width_px, deaths
        if g.lives < prev_lives:
            deaths += 1
        if p.x - last_x < 0.5:
            stuck += 1
        else:
            stuck, last_x = 0, p.x
        if stuck > 240:
            return False, fr, p.x, g.level.width_px, deaths
    return False, max_frames, p.x, g.level.width_px, deaths


if __name__ == "__main__":
    all_ok = True
    for i, name in enumerate(LEVELS):
        ok, fr, x, w, deaths = run_level(i)
        all_ok &= ok
        print(f"{'OK  ' if ok else 'FAIL'} {name:14s} frame={fr:5d} x={x:6.0f}/{w} deaths={deaths}")
    print("ALL COMPLETE" if all_ok else "SOME FAILED")
