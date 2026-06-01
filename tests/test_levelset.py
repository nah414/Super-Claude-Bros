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


def test_segment_track_advances_across_the_level():
    assert L.segment_track(0, 5000) == 1
    assert L.segment_track(999, 5000) == 1
    assert L.segment_track(1000, 5000) == 2
    assert L.segment_track(4999, 5000) == 5
    assert L.segment_track(99999, 5000) == 5      # clamped past the end
