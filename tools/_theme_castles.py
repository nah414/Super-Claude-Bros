"""One-shot: give each world's castle a themed header + difficulty cannons. Not committed."""


def tower(g, col):
    assert g[13][col] == 'X', f"cannon needs floor at col {col}"
    g[11][col] = 'N'
    g[12][col] = 'N'


def retheme(path, new_type, cannons):
    src = [l.rstrip("\n") for l in open(path, encoding="utf-8")]
    body = [l for l in src if not l.startswith("#")]
    W = max(len(l) for l in body)
    g = [list(l.ljust(W, ".")) for l in body]
    for c in cannons:
        if g[13][c] == 'X' and g[11][c] == '.' and g[12][c] == '.':
            tower(g, c)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(["# type: " + new_type] + ["".join(r) for r in g]) + "\n")
    print(f"{path} -> {new_type}, +{len(cannons)} cannon(s)")


# level_4 (1-4) stays plain "castle"
retheme("levels/level_8.txt", "castle_sky", [])        # already has a cannon
retheme("levels/level_12.txt", "castle_sea", [80])
retheme("levels/level_16.txt", "castle_ice", [80])
retheme("levels/level_20.txt", "castle_haunt", [60, 80])
