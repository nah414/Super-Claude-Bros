from game import settings as S
from game.entities.block import Block, SOLID_KINDS
from game.entities.coin import Coin
from game.entities.goomba import Goomba
from game.entities.flyer import Flyer
from game.entities.flag import Flag


class Level:
    def __init__(self, path):
        self.blocks = []
        self.coins = []
        self.enemies = []
        self.flag = None
        self.player_spawn = (0, 0)
        self._load(path)
        self.width_px = self.cols * S.TILE
        self.solids = [b.rect for b in self.blocks]

    def _load(self, path):
        self.area_type = "overworld"
        with open(path, encoding="utf-8") as f:
            raw = [line.rstrip("\n") for line in f]
        rows = []
        for line in raw:
            if line.startswith("#"):
                if "type:" in line:
                    self.area_type = line.split("type:", 1)[1].strip()
                continue
            if line != "":
                rows.append(line)
        self.rows = len(rows)
        self.cols = max((len(r) for r in rows), default=0)
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                x, y = i * S.TILE, j * S.TILE
                if ch in SOLID_KINDS:
                    self.blocks.append(Block(x, y, ch))
                elif ch == "C":
                    self.coins.append(Coin(x, y))
                elif ch == "G":
                    self.enemies.append(Goomba(x, y))
                elif ch == "Y":
                    self.enemies.append(Flyer(x, y))
                elif ch == "F":
                    self.flag = Flag(x, y)
                elif ch == "P":
                    self.player_spawn = (x, y)

    def draw(self, surface, camera):
        for b in self.blocks:
            b.draw(surface, camera, self.area_type)
        for c in self.coins:
            if not c.collected:
                c.draw(surface, camera)
        if self.flag:
            self.flag.draw(surface, camera)
        for e in self.enemies:
            if e.alive:
                e.draw(surface, camera)
