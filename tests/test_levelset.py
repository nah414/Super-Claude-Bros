from game import levelset as L


def test_world_label():
    assert L.world_label(0) == "1-1"
    assert L.world_label(3) == "1-4"
    assert L.world_label(4) == "2-1"


def test_track_number_cycles_every_5():
    assert L.track_number(0) == 1
    assert L.track_number(4) == 5
    assert L.track_number(5) == 1


def test_next_index_ends_at_none():
    assert L.next_index(0) == 1
    assert L.next_index(L.level_count() - 1) is None
