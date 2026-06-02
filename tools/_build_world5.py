"""One-shot: author World 5 haunted levels (5-1/5-2/5-3) + castle 5-4. Not committed."""
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


def plat(g, c0, c1):
    for c in range(c0, c1 + 1):
        g[10][c] = '='


def write(path, g):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(["# type: haunted"] + ["".join(r) for r in g]) + "\n")


# 5-1
g = base([(24, 25), (50, 52), (70, 71)])
plat(g, 30, 33)
plat(g, 58, 61)
g[9][10] = 'M'
g[9][36] = 'M'
g[7][18] = 'O'
g[7][44] = 'O'
g[12][64] = 'G'
write("levels/level_17.txt", g)

# 5-2
g = base([(20, 21), (36, 38), (54, 55), (68, 70)])
plat(g, 26, 29)
plat(g, 44, 47)
plat(g, 60, 62)
g[9][8] = 'M'
g[9][32] = 'M'
g[7][16] = 'O'
g[6][40] = 'O'
g[8][60] = 'O'
g[12][50] = 'K'
write("levels/level_18.txt", g)

# 5-3
g = base([(18, 19), (32, 34), (48, 49), (62, 64), (76, 77)])
plat(g, 24, 26)
plat(g, 40, 42)
plat(g, 56, 58)
g[9][6] = 'M'
g[9][28] = 'M'
g[9][52] = 'M'
g[7][14] = 'O'
g[6][38] = 'O'
g[8][54] = 'O'
g[7][70] = 'O'
g[12][44] = 'G'
write("levels/level_19.txt", g)

# 5-4 castle (from level_4)
src = [l.rstrip("\n") for l in open("levels/level_4.txt", encoding="utf-8")]
body = [l for l in src if not l.startswith("#")]
g = [list(l.ljust(W, ".")) for l in body]
with open("levels/level_20.txt", "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(["# type: castle"] + ["".join(r) for r in g]) + "\n")

print("wrote level_17/18/19 (haunted) + level_20 (castle)")
