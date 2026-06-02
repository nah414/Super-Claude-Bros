"""One-shot: author World 8 'Koopa Keep' gauntlet (8-1/8-2/8-3) + throne castle 8-4. Not committed."""
W, H = 88, 15


def base(gaps):
    g = [['.'] * W for _ in range(H)]
    for c in range(W):
        g[13][c] = 'X'
        g[14][c] = 'X'
    for c0, c1 in gaps:
        for c in range(c0, c1 + 1):
            g[13][c] = '.'
            g[14][c] = '.'
    g[12][2] = 'P'
    g[8][84] = 'F'
    return g


def lava(g, c0, c1):
    for c in range(c0, c1 + 1):
        g[13][c] = 'L'
        g[14][c] = 'L'


def tower(g, col):
    g[11][col] = 'N'
    g[12][col] = 'N'


def plat(g, r, c0, c1):
    for c in range(c0, c1 + 1):
        g[r][c] = '='


def write(path, g):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(["# type: keep"] + ["".join(r) for r in g]) + "\n")


# 8-1
g = base([(40, 42)])
lava(g, 20, 21)
lava(g, 60, 61)
tower(g, 30)
tower(g, 52)
plat(g, 10, 24, 27)
plat(g, 10, 64, 67)
g[9][8] = 'M'
g[9][36] = 'M'
g[12][14] = 'K'
g[12][48] = 'K'
g[12][70] = 'K'
write("levels/level_29.txt", g)

# 8-2
g = base([(28, 30), (58, 59)])
lava(g, 16, 17)
lava(g, 44, 45)
lava(g, 72, 73)
tower(g, 24)
tower(g, 50)
tower(g, 66)
plat(g, 10, 34, 37)
plat(g, 10, 52, 55)
g[9][8] = 'M'
g[9][40] = 'M'
g[12][12] = 'K'
g[12][38] = 'K'
g[12][80] = 'K'
write("levels/level_30.txt", g)

# 8-3
g = base([(22, 24), (46, 47), (66, 68)])
lava(g, 14, 15)
lava(g, 34, 35)
lava(g, 56, 57)
tower(g, 19)             # cannons mid-platform, clear of gap/lava edges
tower(g, 40)
tower(g, 62)
g[9][8] = 'M'
g[9][38] = 'M'
g[12][12] = 'K'
g[12][52] = 'K'
g[12][72] = 'K'
write("levels/level_31.txt", g)

# 8-4 throne castle (from level_4) + two arena cannons
src = [l.rstrip("\n") for l in open("levels/level_4.txt", encoding="utf-8")]
body = [l for l in src if not l.startswith("#")]
g = [list(l.ljust(W, ".")) for l in body]
for c in (60, 80):
    if g[13][c] == 'X' and g[11][c] == '.':
        g[11][c] = 'N'
        g[12][c] = 'N'
with open("levels/level_32.txt", "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(["# type: castle_keep"] + ["".join(r) for r in g]) + "\n")

print("wrote level_29/30/31 (keep) + level_32 (throne)")
