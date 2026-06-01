"""Pure level-sequence logic: order, World X-Y labels, music track per level."""
LEVELS = ["level_1.txt", "level_2.txt", "level_3.txt", "level_4.txt", "level_5.txt"]
TRACKS = 5


def level_count():
    return len(LEVELS)


def level_file(index):
    return LEVELS[index]


def world_label(index):
    return f"{index // 4 + 1}-{index % 4 + 1}"


def track_number(index):
    return index % TRACKS + 1


def next_index(index):
    nxt = index + 1
    return nxt if nxt < len(LEVELS) else None
