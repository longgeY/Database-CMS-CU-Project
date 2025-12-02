# workloads.py
import random
import math

class UniformKeys:
    def __init__(self, U: int, seed: int = 42):
        self.U = U
        self.rng = random.Random(seed)
    def sample(self) -> int:
        return self.rng.randrange(self.U)

class ZipfKeys:
    # 生成 1..U 的 Zipf 分布（alpha>0）
    def __init__(self, U: int, alpha: float, seed: int = 43):
        self.U = U
        self.alpha = alpha
        self.rng = random.Random(seed)
        # 预计算归一化常数
        self.cdf = []
        Z = 0.0
        for k in range(1, U + 1):
            Z += 1.0 / (k ** alpha)
            self.cdf.append(Z)
        for i in range(U):
            self.cdf[i] /= Z
    def sample(self) -> int:
        u = self.rng.random()
        # 二分查找 cdf
        lo, hi = 0, self.U - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if self.cdf[mid] >= u:
                hi = mid
            else:
                lo = mid + 1
        return lo + 1  # 键空间从 1 开始
