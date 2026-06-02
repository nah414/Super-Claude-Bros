"""One-shot: write level_4 as the World 1-4 castle (boss arena). Not committed."""
W, H = 88, 15
grid = [['.'] * W for _ in range(H)]


def fill(r, c0, c1, ch):
    for c in range(c0, c1 + 1):
        grid[r][c] = ch


def col(c, r0, r1, ch):
    for r in range(r0, r1 + 1):
        grid[r][c] = ch


fill(1, 0, W - 1, 'X')                       # ceiling
fill(13, 0, W - 1, 'X')
fill(14, 0, W - 1, 'X')                       # floor (rows 13-14)
for c0, c1 in [(17, 18), (40, 41)]:           # 2-wide lava pools in floor gaps
    fill(13, c0, c1, 'L')
    fill(14, c0, c1, 'L')
col(86, 1, 14, 'X')
col(87, 1, 14, 'X')                           # right wall: bounds the boss + blocks running past
grid[10][24] = 'M'
grid[10][28] = 'M'                            # two power boxes => guaranteed fire by the arena
grid[12][2] = 'P'                             # spawn
grid[12][72] = 'Z'                            # the Iron Koopa

out = ['# type: castle'] + [''.join(r) for r in grid]
with open("levels/level_4.txt", "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(out) + "\n")
print("wrote levels/level_4.txt:", H, "rows x", W, "cols")
