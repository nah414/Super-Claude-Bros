import os
import pygame
from game import settings as S
from game.level import Level

LEVEL = """# type: underground
# warp: 3,2 -> 7,5
XX..TT..XX
XXXXXXXXXX
"""


def _write(tmp, text):
    p = os.path.join(tmp, "w.txt")
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    return p


def test_warp_parses_to_trigger_and_dest(tmp_path):
    lvl = Level(_write(str(tmp_path), LEVEL))
    assert len(lvl.warps) == 1
    trig, dest = lvl.warps[0]
    assert trig == pygame.Rect(3 * S.TILE, 2 * S.TILE, S.TILE, S.TILE)
    assert dest == (7, 5)


def test_pipe_tiles_are_solid(tmp_path):
    lvl = Level(_write(str(tmp_path), LEVEL))
    assert any(b.kind == "T" for b in lvl.blocks)
    assert pygame.Rect(4 * S.TILE, 0, S.TILE, S.TILE) in lvl.solids
