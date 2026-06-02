"""One-shot: author World 2 levels (2-1 reskin, new 2-2/2-3, castle 2-4). Not committed."""
W, H = 88, 15


def blank():
    return [['.'] * W for _ in range(H)]


def fill(g, r, c0, c1, ch):
    for c in range(c0, c1 + 1):
        g[r][c] = ch


def tower(g, col, height=2, floor=13):
    assert g[floor][col] == 'X', f"cannon/tower needs floor at col {col}"
    for k in range(height):
        g[floor - 1 - k][col] = 'N'


def write(path, header, g):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join([header] + ["".join(r) for r in g]) + "\n")


def sky_floor(g, gaps):
    fill(g, 13, 0, W - 1, 'X')
    fill(g, 14, 0, W - 1, 'X')
    for c0, c1 in gaps:
        fill(g, 13, c0, c1, '.')
        fill(g, 14, c0, c1, '.')


# ---------- 2-1: reskin level_5 to sky (gentle intro: no cannons yet) ----------
src = [l.rstrip("\n") for l in open("levels/level_5.txt", encoding="utf-8")]
body = [l for l in src if not l.startswith("#")]
g = [list(l.ljust(W, ".")) for l in body]
write("levels/level_5.txt", "# type: sky", g)

# ---------- 2-2: level_6 (sky) ----------
g = blank()
sky_floor(g, [(20, 22), (44, 45), (66, 68)])
fill(g, 10, 30, 33, '=')
fill(g, 10, 54, 57, '=')
tower(g, 38)
tower(g, 60)
g[9][26] = 'M'
g[12][2] = 'P'
g[12][14] = 'G'
g[12][50] = 'K'
g[12][72] = 'G'
g[8][84] = 'F'
write("levels/level_6.txt", "# type: sky", g)

# ---------- 2-3: level_7 (sky, harder) ----------
g = blank()
sky_floor(g, [(16, 17), (30, 32), (50, 51), (64, 66)])
fill(g, 10, 20, 22, '=')
fill(g, 10, 38, 40, '=')
fill(g, 10, 56, 58, '=')
tower(g, 24)
tower(g, 44)
tower(g, 60)
g[9][8] = 'M'
g[12][2] = 'P'
g[12][12] = 'K'
g[12][36] = 'G'
g[12][70] = 'K'
g[8][84] = 'F'
write("levels/level_7.txt", "# type: sky", g)

# ---------- 2-4: level_8 = the castle (from level_4) + a cannon in the arena ----------
src = [l.rstrip("\n") for l in open("levels/level_4.txt", encoding="utf-8")]
body = [l for l in src if not l.startswith("#")]
g = [list(l.ljust(W, ".")) for l in body]
if g[13][80] == 'X':
    tower(g, 80)                              # Bullet Bills during the boss fight
write("levels/level_8.txt", "# type: castle", g)

print("wrote level_5 (reskin) + level_6, level_7, level_8")
