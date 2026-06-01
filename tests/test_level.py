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


def test_parses_mushroom_box_and_flyer(tmp_path):
    from game.entities.flyer import Flyer
    p = tmp_path / "lvl.txt"
    p.write_text("..M..\n..Y..\nP...F\nXXXXX\n")
    level = Level(str(p))
    assert "M" in [b.kind for b in level.blocks]        # mushroom box is a solid block
    assert any(isinstance(e, Flyer) for e in level.enemies)


def test_area_type_header(tmp_path):
    p = tmp_path / "l.txt"
    p.write_text("# type: underground\nP..F\nXXXX\n")
    assert Level(str(p)).area_type == "underground"
    p2 = tmp_path / "l2.txt"
    p2.write_text("P..F\nXXXX\n")
    assert Level(str(p2)).area_type == "overworld"
