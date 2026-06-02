"""One-shot: author World 6 factory levels (6-1/6-2/6-3) + metal castle 6-4. Not committed."""
W, H = 88, 15


def base():
    g = [['.'] * W for _ in range(H)]
    for c in range(W):
        g[13][c] = 'X'
        g[14][c] = 'X'
    g[12][2] = 'P'
    g[8][84] = 'F'
    return g


def gap(g, c0, c1):
    for c in range(c0, c1 + 1):
        g[13][c] = '.'
        g[14][c] = '.'


def belt(g, c0, c1, ch):
    for c in range(c0, c1 + 1):
        g[13][c] = ch          # belt sits on the surface row; row 14 stays solid support


def plat(g, c0, c1):
    for c in range(c0, c1 + 1):
        g[10][c] = '='


def write(path, g):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(["# type: factory"] + ["".join(r) for r in g]) + "\n")


# 6-1
g = base()
belt(g, 10, 16, '>')
belt(g, 30, 36, '<')
belt(g, 50, 56, '>')
gap(g, 22, 23)
gap(g, 44, 45)
gap(g, 64, 66)
plat(g, 18, 20)
plat(g, 46, 48)
g[9][8] = 'M'
g[9][40] = 'M'
g[12][26] = 'R'
g[12][60] = 'R'
g[12][72] = 'G'
write("levels/level_21.txt", g)

# 6-2
g = base()
belt(g, 8, 14, '>')
belt(g, 24, 30, '<')
belt(g, 42, 48, '>')
belt(g, 58, 64, '<')
gap(g, 18, 19)
gap(g, 36, 38)
gap(g, 54, 55)
gap(g, 70, 71)
plat(g, 32, 34)
plat(g, 50, 52)
g[9][6] = 'M'
g[9][40] = 'M'
g[12][22] = 'R'
g[12][46] = 'R'
g[12][66] = 'R'
g[12][30] = 'K'
write("levels/level_22.txt", g)

# 6-3
g = base()
belt(g, 8, 13, '>')
belt(g, 20, 25, '<')
belt(g, 34, 39, '>')
belt(g, 48, 53, '<')
belt(g, 62, 67, '>')
gap(g, 16, 17)
gap(g, 30, 32)
gap(g, 44, 45)
gap(g, 58, 59)
gap(g, 74, 75)
plat(g, 26, 28)
plat(g, 40, 42)
g[9][6] = 'M'
g[9][36] = 'M'
g[9][64] = 'M'
g[12][24] = 'R'          # mid-platform (not right before a gap)
g[12][38] = 'R'
g[12][52] = 'R'
g[12][66] = 'R'
g[12][80] = 'G'
write("levels/level_23.txt", g)

# 6-4 metal castle (from level_4)
src = [l.rstrip("\n") for l in open("levels/level_4.txt", encoding="utf-8")]
body = [l for l in src if not l.startswith("#")]
g = [list(l.ljust(W, ".")) for l in body]
if g[13][80] == 'X':
    g[11][80] = 'N'
    g[12][80] = 'N'                                       # an arena cannon
with open("levels/level_24.txt", "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(["# type: castle_factory"] + ["".join(r) for r in g]) + "\n")

print("wrote level_21/22/23 (factory) + level_24 (metal castle)")
