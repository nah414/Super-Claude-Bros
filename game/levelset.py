"""Pure level-sequence logic: order, World X-Y labels, music track per level."""
LEVELS = ["level_1.txt", "level_2.txt", "level_3.txt", "level_4.txt",
          "level_5.txt", "level_6.txt", "level_7.txt", "level_8.txt",
          "level_9.txt", "level_10.txt", "level_11.txt", "level_12.txt",
          "level_13.txt", "level_14.txt", "level_15.txt", "level_16.txt",
          "level_17.txt", "level_18.txt", "level_19.txt", "level_20.txt"]
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


def segment_track(x, width, segments=TRACKS):
    """Which track (1..segments) plays for horizontal position x in a level of
    the given pixel width. The level is split into `segments` equal slices."""
    if width <= 0:
        return 1
    seg = int(x // (width / segments))
    return max(1, min(segments, seg + 1))
