from collections import Counter
from cms import CMS
from workloads import UniformKeys

def main():
    eps, delta = 0.001, 1e-3   
    cms = CMS.from_eps_delta(eps, delta, seed=1)
    truth = Counter()

    # 重键 1000 次
    key = 123456789
    for _ in range(1000):
        cms.update(key, 1)
        truth[key] += 1

    # 均匀 10k（先小一点看效果）
    U, N = 10000, 10_000
    uni = UniformKeys(U=U, seed=7)
    for _ in range(N):
        k = uni.sample()
        cms.update_cu(k, 1)
        truth[k] += 1

    test_keys = [key, 42, 777, 9999]
    print("key\ttrue\tmin\tmean\tcmm")
    for k in test_keys:
        print(k, truth[k], cms.query_min(k), round(cms.query_mean(k),2), round(cms.query_cmm(k),2), sep="\t")

if __name__ == "__main__":
    main()
