"""One-shot: add the entry pipe + sealed coin vault + warps to level_3. Not committed."""
W = 116
path = "levels/level_3.txt"
with open(path, encoding="utf-8") as f:
    lines = [l.rstrip("\n") for l in f]
rows = [l for l in lines if not l.startswith("#") and l != ""]
grid = [list(r.ljust(W, ".")) for r in rows]   # 15 rows, padded to W


def put(r, c, ch):
    grid[r][c] = ch


def fill(r, c0, c1, ch):
    for c in range(c0, c1 + 1):
        put(r, c, ch)


# entry pipe at cols 40-41, mouth row 11, shaft row 12 (floor is rows 13-14)
assert grid[13][40] == "X" and grid[13][41] == "X", "entry pipe must stand on floor"
for c in (40, 41):
    put(11, c, "T")
    put(12, c, "t")

# sealed vault cols 95-114
fill(9, 95, 114, "X")                       # ceiling
fill(13, 95, 114, "X")
fill(14, 95, 114, "X")                       # floor
for r in range(9, 15):
    put(r, 95, "X")
    put(r, 114, "X")                         # walls
for r in (10, 11, 12):
    fill(r, 98, 109, "C")                     # coins
for c in (111, 112):
    put(11, c, "T")
    put(12, c, "t")                           # return pipe

warps = ["# warp: 40,11 -> 96,13", "# warp: 41,11 -> 96,13",
         "# warp: 111,11 -> 46,13", "# warp: 112,11 -> 46,13"]
out = ["# type: underground"] + warps + ["".join(r) for r in grid]
with open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(out) + "\n")
print("rebuilt", path, "->", len(grid), "rows x", W, "cols")
