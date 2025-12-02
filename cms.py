# cms.py
from dataclasses import dataclass
from typing import List, Optional
import random

def multiply_shift_hash(x: int, seed: int, w: int) -> int:
    a = (seed * 0x9E3779B97F4A7C15) & ((1 << 64) - 1)
    x = (x ^ (seed * 0xBF58476D1CE4E5B9)) & ((1 << 64) - 1)
    z = (a * (x | 1)) & ((1 << 64) - 1)
    return ((z >> 32) ^ (z & 0xFFFFFFFF)) % w

@dataclass
class CMS:
    w: int
    d: int
    seeds: List[int]
    table: List[int]
    total_updates: int = 0          # 累计 ||f||_1
    row_totals: Optional[List[int]] = None  # 每行累计（用于 CMM & CU）

    @classmethod
    def from_eps_delta(cls, eps: float, delta: float, seed: int = 1):
        import math
        w = int(math.ceil(2.718281828 / eps))
        d = int(math.ceil(math.log(1.0 / delta)))
        rng = random.Random(seed)
        seeds = [rng.getrandbits(64) for _ in range(d)]
        table = [0] * (w * d)
        row_totals = [0] * d                      # <-- 初始化 row_totals
        return cls(w=w, d=d, seeds=seeds, table=table, row_totals=row_totals)

    def _idx(self, r: int, key: int) -> int:
        h = multiply_shift_hash(key, self.seeds[r], self.w)
        return r * self.w + h

    # 基线更新
    def update(self, key: int, c: int = 1) -> None:
        for r in range(self.d):
            self.table[self._idx(r, key)] += c
            self.row_totals[r] += c               # 逐行累计
        self.total_updates += c

    # 保守更新（CU）
    def update_cu(self, key: int, c: int = 1) -> None:
        idxs = [self._idx(r, key) for r in range(self.d)]
        vals = [self.table[idx] for idx in idxs]
        m = min(vals)
        for r, (idx, v) in enumerate(zip(idxs, vals)):
            if v == m:
                self.table[idx] += c
                self.row_totals[r] += c           # 只给被加的行累计
        self.total_updates += c

    # 估计器
    def query_min(self, key: int) -> int:
        return min(self.table[self._idx(r, key)] for r in range(self.d))

    def query_mean(self, key: int) -> float:
        return sum(self.table[self._idx(r, key)] for r in range(self.d)) / self.d

    def query_cmm(self, key: int) -> float:
        ests = []
        for r in range(self.d):
            v = self.table[self._idx(r, key)]
            coll = (self.row_totals[r] - v) / max(1, (self.w - 1))  # 每行碰撞估计
            ests.append(max(0.0, v - coll))
        return min(ests)

    # 合并
    def merge_inplace(self, other: "CMS"):
        assert self.w == other.w and self.d == other.d and len(self.table) == len(other.table)
        for i in range(len(self.table)):
            self.table[i] += other.table[i]
        for r in range(self.d):                    # <-- 合并 row_totals
            self.row_totals[r] += other.row_totals[r]
        self.total_updates += other.total_updates
