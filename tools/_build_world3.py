"""One-shot: author World 3 levels (3 underwater + castle 3-4). Not committed."""
W, H = 88, 15


def water_base():
    g = [['.'] * W for _ in range(H)]
    for c in range(W):
        g[0][c] = 'X'          # ceiling (so strokes don't fling you off-screen)
        g[13][c] = 'X'
        g[14][c] = 'X'         # seabed (can't sink to death)
    g[11][2] = 'P'             # spawn near the seabed
    g[6][84] = 'F'             # flag pole spans rows 6-10 (the swim channel)
    return g


def coral(g, col, top):
    for r in range(top, 13):
        g[r][col] = 'X'


def write(path, header, g):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join([header] + ["".join(r) for r in g]) + "\n")


# 3-1: sparse intro (short coral only)
g = water_base()
coral(g, 30, 10)
coral(g, 56, 10)
for c in (20, 68):
    g[4][c] = 'H'           # fish above the mid-channel
g[10][44] = 'H'             # ...and one below
for c in range(38, 43):
    g[8][c] = 'C'
write("levels/level_9.txt", "# type: water", g)

# 3-2: one tall coral to swim over + more fish
g = water_base()
coral(g, 26, 10)
coral(g, 44, 7)
coral(g, 62, 10)
for c in (16, 70):
    g[4][c] = 'H'
for c in (34, 52):
    g[10][c] = 'H'
write("levels/level_10.txt", "# type: water", g)

# 3-3: two tall corals + dense fish
g = water_base()
coral(g, 24, 7)
coral(g, 40, 10)
coral(g, 56, 7)
coral(g, 72, 10)
for c in (14, 38, 78):
    g[4][c] = 'H'
for c in (48, 64):
    g[10][c] = 'H'
write("levels/level_11.txt", "# type: water", g)

# 3-4: castle (from level_4) + Iron Koopa
src = [l.rstrip("\n") for l in open("levels/level_4.txt", encoding="utf-8")]
body = [l for l in src if not l.startswith("#")]
g = [list(l.ljust(W, ".")) for l in body]
write("levels/level_12.txt", "# type: castle", g)

print("wrote level_9, level_10, level_11 (water) + level_12 (castle)")
