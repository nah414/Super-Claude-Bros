"""Add a classic 'enter a pipe -> full-screen bonus stage -> return pipe' to a level.

An entry pipe on the main path warps into a sealed, screen-sized room appended off
the right edge of the map: a tall coin chamber with a platform ledge and two
world-themed enemies, plus a return pipe that pops you back onto the main path a few
tiles past the entry. The room sits well past the goal flag, so `play_width` keeps
music/progress on the main path, and the wide gap keeps a chasing room-enemy (Boo)
dormant until you actually warp in.

Pipe tiles: 'T' = mouth (top), 't' = shaft. Warp triggers sit at the mouth row.
Warp header: `# warp: ex,ey -> dx,dy`  (dest dy = floor-top row; player lands ON it).
"""

PIPE_W = 2
ROOM_W = 24            # ~full screen wide (screen is 24 tiles)
GAP = 16              # blank columns between the map and the room (keeps room enemies off-path)


def add_bonus(path, entry_col, floor_top, enemies="GK", gap=GAP):
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    keep_header = [l for l in lines if l.startswith("#") and "warp:" not in l]   # keep type, drop warps
    grid_lines = [l for l in lines if l and not l.startswith("#")]

    W = max(len(r) for r in grid_lines)
    FT = floor_top
    CT = 1                                   # ceiling near the top of the screen -> room fills it
    RX = W + gap
    NEWW = RX + ROOM_W
    grid = [list(r.ljust(NEWW, ".")) for r in grid_lines]

    def put(col, row, ch):
        grid[row][col] = ch

    # --- entry pipe on the main path (sits on the floor at FT) ---
    for dc in range(PIPE_W):
        put(entry_col + dc, FT - 2, "T")
        put(entry_col + dc, FT - 1, "t")

    # --- the bonus stage: a tall enclosed box (cols RX..RX+ROOM_W-1, rows CT..FT+1) ---
    for c in range(RX, RX + ROOM_W):
        put(c, CT, "X")                      # ceiling
        put(c, FT, "X")                      # floor
        put(c, FT + 1, "X")                  # floor (2 deep, matches main)
    for row in range(CT + 1, FT):
        put(RX, row, "X")                    # left wall
        put(RX + ROOM_W - 1, row, "X")       # right wall

    # a platform ledge mid-room (something to jump for / perch on)
    for c in range(RX + 10, RX + 15):
        put(c, FT - 5, "=")

    # coin field — three rows spread up the chamber (skip the ledge row FT-5)
    for row in (FT - 9, FT - 7, FT - 2):
        for c in range(RX + 3, RX + 19):
            put(c, row, "C")

    # return pipe near the right end of the room
    ret_col = RX + ROOM_W - 4
    for dc in range(PIPE_W):
        put(ret_col + dc, FT - 2, "T")
        put(ret_col + dc, FT - 1, "t")

    # two themed enemies (placed last so they sit cleanly over coins):
    # one on the floor, one mid-air (ground foes fall to the floor; flyers/ghosts hover)
    put(RX + 6, FT - 1, enemies[0])
    put(RX + 16, FT - 6, enemies[1])

    # --- warps: enter -> room floor (left); return -> main path past the entry pipe ---
    room_landing = (RX + 2, FT)
    main_exit = (entry_col + PIPE_W + 1, FT)
    warps = []
    for dc in range(PIPE_W):
        warps.append(f"# warp: {entry_col + dc},{FT - 2} -> {room_landing[0]},{room_landing[1]}")
    for dc in range(PIPE_W):
        warps.append(f"# warp: {ret_col + dc},{FT - 2} -> {main_exit[0]},{main_exit[1]}")

    out = keep_header + warps + ["".join(r) for r in grid]
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    return dict(entry=(entry_col, FT - 2), room_landing=room_landing,
                ret=(ret_col, FT - 2), main_exit=main_exit, room_cols=(RX, RX + ROOM_W - 1))


if __name__ == "__main__":
    import sys
    enemies = sys.argv[4] if len(sys.argv) > 4 else "GK"
    print(add_bonus(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), enemies))
