from game import settings as S
from game.level import Level

MAP = "......\n..C...\nP.G..F\nXXXXXX\n"


def test_parses_map(tmp_path):
    p = tmp_path / "lvl.txt"
    p.write_text(MAP)
    level = Level(str(p))

    assert len(level.blocks) == 6          # six 'X' ground tiles
    assert len(level.coins) == 1
    assert len(level.enemies) == 1
    assert level.flag is not None
    assert level.player_spawn == (0, 2 * S.TILE)   # 'P' at col 0, row 2
    assert len(level.solids) == 6          # solids derived from blocks
