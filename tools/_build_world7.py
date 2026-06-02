"""One-shot: author World 7 caldera levels (7-1/7-2/7-3) + molten castle 7-4. Not committed."""
W, H = 88, 15


def blank():
    return [['.'] * W for _ in range(H)]


def floor(g, c0, c1, rows=(12, 13, 14)):
    for r in rows:
        for c in range(c0, c1 + 1):
            g[r][c] = 'X'


def steps(g, seq):
    """seq: (row, c0, c1) platform islands (width ~5, 2-col gaps, gentle steps)."""
    for row, c0, c1 in seq:
        for c in range(c0, c1 + 1):
            g[row][c] = '='


def write(path, g):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(["# type: caldera"] + ["".join(r) for r in g]) + "\n")


def caldera(path, seq, boxes):
    g = blank()
    floor(g, 0, 5)
    g[12][2] = 'P'
    steps(g, seq)
    for r, c in boxes:
        g[r][c] = 'M'
    g[6][82] = 'F'                              # flag pole over the final island
    write(path, g)


# width-5 islands, 2-col gaps, +-1 row steps, trending up to the row-7 finish
SEQ = [(11, 8, 12), (10, 15, 19), (9, 22, 26), (10, 29, 33), (9, 36, 40),
       (8, 43, 47), (9, 50, 54), (8, 57, 61), (9, 64, 68), (8, 71, 75), (7, 78, 84)]
caldera("levels/level_25.txt", SEQ, [])      # no floating boxes (they block the hop path)

SEQ2 = [(11, 8, 12), (10, 15, 19), (9, 22, 26), (9, 29, 33), (8, 36, 40),
        (9, 43, 47), (8, 50, 54), (9, 57, 61), (8, 64, 68), (8, 71, 75), (7, 78, 84)]
caldera("levels/level_26.txt", SEQ2, [])

SEQ3 = [(11, 8, 12), (10, 15, 19), (9, 22, 26), (8, 29, 33), (9, 36, 40),
        (8, 43, 47), (9, 50, 54), (8, 57, 61), (9, 64, 68), (8, 71, 75), (7, 78, 84)]
caldera("levels/level_27.txt", SEQ3, [])

# 7-4 molten castle (from level_4)
src = [l.rstrip("\n") for l in open("levels/level_4.txt", encoding="utf-8")]
body = [l for l in src if not l.startswith("#")]
g = [list(l.ljust(W, ".")) for l in body]
if g[13][80] == 'X':
    g[11][80] = 'N'
    g[12][80] = 'N'
with open("levels/level_28.txt", "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(["# type: castle_caldera"] + ["".join(r) for r in g]) + "\n")

print("wrote level_25/26/27 (caldera) + level_28 (molten castle)")
