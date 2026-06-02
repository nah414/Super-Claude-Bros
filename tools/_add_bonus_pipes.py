"""Add a classic 'enter a pipe -> bonus coin room -> return pipe' to a level.

Replicates the proven level_3 vault pattern: an entry pipe on the main path warps
into a sealed underground coin room appended off the right edge of the map; a return
pipe in the room warps you back onto the main path a few tiles past the entry. The
room sits past the goal flag, so `play_width` keeps music/progress on the main path.

Pipe tiles: 'T' = mouth (top), 't' = shaft. Warp triggers sit at the mouth row.
Warp header: `# warp: ex,ey -> dx,dy`  (dest dy = floor-top row; player lands ON it).
"""

PIPE_W = 2
ROOM_W = 18


def add_bonus(path, entry_col, floor_top, gap=2):
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    header = [l for l in lines if l.startswith("#")]
    keep_header = [l for l in header if "warp:" not in l]      # drop old warps, keep type
    grid_lines = [l for l in lines if l and not l.startswith("#")]

    W = max(len(r) for r in grid_lines)
    FT = floor_top
    CT = FT - 6                      # room ceiling row (interior 5 tall)
    RX = W + gap                     # room starts here (a gap past the map)
    NEWW = RX + ROOM_W
    grid = [list(r.ljust(NEWW, ".")) for r in grid_lines]

    def put(col, row, ch):
        grid[row][col] = ch

    # --- entry pipe on the main path (sits on the floor at FT) ---
    for dc in range(PIPE_W):
        put(entry_col + dc, FT - 2, "T")     # mouth
        put(entry_col + dc, FT - 1, "t")     # shaft

    # --- the bonus room (enclosed box at cols RX..RX+ROOM_W-1) ---
    for c in range(RX, RX + ROOM_W):
        put(c, CT, "X")                      # ceiling
        put(c, FT, "X")                      # floor
        put(c, FT + 1, "X")                  # floor (2 deep, matches main)
    for row in range(CT + 1, FT):
        put(RX, row, "X")                    # left wall
        put(RX + ROOM_W - 1, row, "X")       # right wall
    # coin pile (3 rows: walk-collect the lowest, jump for the rest)
    for row in (FT - 1, FT - 2, FT - 3):
        for c in range(RX + 3, RX + 13):
            put(c, row, "C")
    # return pipe near the right end of the room
    ret_col = RX + ROOM_W - 4
    for dc in range(PIPE_W):
        put(ret_col + dc, FT - 2, "T")
        put(ret_col + dc, FT - 1, "t")

    # --- warps: enter -> room left floor; return -> main path past the entry pipe ---
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
    info = add_bonus(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
    print(info)
