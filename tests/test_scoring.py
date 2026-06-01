from game.scoring import bonus_lives


def test_bonus_lives():
    assert bonus_lives(99, 100) == 1
    assert bonus_lives(100, 101) == 0
    assert bonus_lives(95, 205) == 2
    assert bonus_lives(0, 0) == 0
