# benchmark.py
import argparse, time, csv, math, random
from collections import Counter
from typing import List, Tuple
from cms import CMS
from workloads import UniformKeys, ZipfKeys

def pct(vs: List[float], q: float) -> float:
    if not vs: return float('nan')
    s = sorted(vs)
    pos = (len(s)-1) * q
    lo, hi = int(math.floor(pos)), int(math.ceil(pos))
    if lo == hi: return s[lo]
    return s[lo] + (s[hi]-s[lo])*(pos-lo)

def summarize(errors: List[float]) -> Tuple[float,float,float]:
    return pct(errors, 0.5), (pct(errors, 0.75)-pct(errors, 0.25)), pct(errors, 0.95)

def run_one_trial(eps, delta, N, U, workload, alpha, use_cu, Q, seed):
    rng = random.Random(seed)

    # 构建 CMS
    cms = CMS.from_eps_delta(eps, delta, seed=seed)
    truth = Counter()

    hot_key, hot_count = 123456789, 1000
    for _ in range(hot_count):
        if use_cu: cms.update_cu(hot_key, 1)
        else:      cms.update(hot_key, 1)
    truth[hot_key] += hot_count

    # 选择工作负载
    if workload == 'uniform':
        gen = UniformKeys(U=U, seed=seed+1)
        sampler = lambda : gen.sample()
    elif workload == 'zipf':
        gen = ZipfKeys(U=U, alpha=alpha, seed=seed+1)
        sampler = lambda : gen.sample()
    else:
        raise ValueError("workload must be uniform|zipf")

    t0 = time.perf_counter()
    for _ in range(N):
        k = sampler()
        if use_cu: cms.update_cu(k, 1)
        else:      cms.update(k, 1)
        truth[k] += 1
    t1 = time.perf_counter()
    updates_per_sec = N / (t1 - t0 + 1e-9)

    seen_keys = list(truth.keys())
    if len(seen_keys) == 0:
        seen_sample = []
    else:
        seen_sample = [seen_keys[rng.randrange(len(seen_keys))] for _ in range(Q//2)]
    unseen_sample = [rng.randrange(1, U+1) for _ in range(Q - len(seen_sample))]
    query_keys = seen_sample + unseen_sample

    abs_err_min, abs_err_mean, abs_err_cmm = [], [], []
    t2 = time.perf_counter()
    for k in query_keys:
        true = truth[k]
        est_min  = cms.query_min(k)
        est_mean = cms.query_mean(k)
        est_cmm  = cms.query_cmm(k)

        abs_err_min.append(abs(est_min - true))
        abs_err_mean.append(abs(est_mean - true))
        abs_err_cmm.append(abs(est_cmm - true))
    t3 = time.perf_counter()
    qps = len(query_keys) / (t3 - t2 + 1e-9)

    med_min, iqr_min, p95_min   = summarize(abs_err_min)
    med_mean, iqr_mean, p95_mean= summarize(abs_err_mean)
    med_cmm, iqr_cmm, p95_cmm   = summarize(abs_err_cmm)

    return {
        "updates_per_sec": updates_per_sec,
        "qps": qps,
        "med_min": med_min, "iqr_min": iqr_min, "p95_min": p95_min,
        "med_mean": med_mean, "iqr_mean": iqr_mean, "p95_mean": p95_mean,
        "med_cmm": med_cmm, "iqr_cmm": iqr_cmm, "p95_cmm": p95_cmm,
        "w": cms.w, "d": cms.d
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eps", type=float, default=0.001)
    ap.add_argument("--delta", type=float, default=1e-3)
    ap.add_argument("--N", type=int, default=1000000, help="number of updates")
    ap.add_argument("--U", type=int, default=100000, help="key space size")
    ap.add_argument("--workload", type=str, choices=["uniform","zipf"], default="uniform")
    ap.add_argument("--alpha", type=float, default=1.0, help="zipf alpha")
    ap.add_argument("--use_cu", action="store_true", help="enable conservative update")
    ap.add_argument("--Q", type=int, default=2000, help="num queries for error stats")
    ap.add_argument("--trials", type=int, default=3)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out", type=str, default="results.csv")
    args = ap.parse_args()

    rows = []
    for t in range(args.trials):
        r = run_one_trial(
            eps=args.eps, delta=args.delta, N=args.N, U=args.U,
            workload=args.workload, alpha=args.alpha,
            use_cu=args.use_cu, Q=args.Q, seed=args.seed + t*100
        )
        r.update({
            "eps": args.eps, "delta": args.delta, "N": args.N, "U": args.U,
            "workload": args.workload, "alpha": args.alpha, "use_cu": int(args.use_cu),
            "trial": t
        })
        rows.append(r)
        print(f"[trial {t}] w={r['w']} d={r['d']}  u/s={r['updates_per_sec']:.0f}  qps={r['qps']:.0f}  "
              f"med_min={r['med_min']:.2f} med_cmm={r['med_cmm']:.2f}")

    fieldnames = ["trial","eps","delta","N","U","workload","alpha","use_cu","w","d",
                  "updates_per_sec","qps",
                  "med_min","iqr_min","p95_min",
                  "med_mean","iqr_mean","p95_mean",
                  "med_cmm","iqr_cmm","p95_cmm"]
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"[done] wrote {args.out}")

if __name__ == "__main__":
    main()
