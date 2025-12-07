# plot_results.py (aggregated CSV version)
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams["figure.dpi"] = 140
plt.rcParams["axes.grid"] = True

def load_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    if "use_cu" in df.columns:
        df["use_cu"] = df["use_cu"].astype(int)
    return df

def plot_error_vs_eps(df: pd.DataFrame, outdir: Path):
    for workload in sorted(df["workload"].unique()):
        for cu in sorted(df["use_cu"].unique()):
            sub = df[(df["workload"]==workload) & (df["use_cu"]==cu)]
            if sub.empty: 
                continue
            g = (sub.groupby("eps", as_index=False)
                    .agg({"med_min":"mean","med_mean":"mean","med_cmm":"mean"} )
                    .sort_values("eps"))
            fig, ax = plt.subplots(figsize=(7,4.5))
            ax.plot(g["eps"], g["med_min"],  marker="o", label="min (median abs err)")
            ax.plot(g["eps"], g["med_mean"], marker="o", label="mean (median abs err)")
            ax.plot(g["eps"], g["med_cmm"],  marker="o", label="cmm (median abs err)")
            ax.set_xscale("log")
            ax.set_xlabel("epsilon (log scale)")
            ax.set_ylabel("median absolute error")
            ax.set_title(f"Error vs epsilon — {workload}, CU={'on' if cu else 'off'}")
            ax.legend()
            out = outdir / f"error_vs_eps_{workload}_cu{cu}.png"
            fig.tight_layout(); fig.savefig(out); plt.close(fig)

def plot_rel_iqr_vs_eps(df: pd.DataFrame, outdir: Path):
    # 用 IQR 画阴影（相对误差你没有列；这里仍用绝对误差的 IQR，可选改为相对误差后再扩展）
    for workload in sorted(df["workload"].unique()):
        for cu in sorted(df["use_cu"].unique()):
            sub = df[(df["workload"]==workload) & (df["use_cu"]==cu)]
            if sub.empty: 
                continue
            g = (sub.groupby("eps", as_index=False)
                    .agg({"med_min":"mean","iqr_min":"mean",
                          "med_mean":"mean","iqr_mean":"mean",
                          "med_cmm":"mean","iqr_cmm":"mean"} )
                    .sort_values("eps"))
            x = g["eps"].values
            fig, ax = plt.subplots(figsize=(7,4.5))
            for name,color in [("min","#1f77b4"),("mean","#ff7f0e"),("cmm","#2ca02c")]:
                med = g[f"med_{name}"].values
                iqr = g[f"iqr_{name}"].values
                low, up = med - 0.5*iqr, med + 0.5*iqr
                ax.plot(x, med, marker="o", label=name, color=color)
                ax.fill_between(x, low, up, alpha=0.15, color=color)
            ax.set_xscale("log")
            ax.set_xlabel("epsilon (log scale)")
            ax.set_ylabel("median abs error (with IQR band)")
            ax.set_title(f"IQR bands vs epsilon — {workload}, CU={'on' if cu else 'off'}")
            ax.legend()
            out = outdir / f"iqr_vs_eps_{workload}_cu{cu}.png"
            fig.tight_layout(); fig.savefig(out); plt.close(fig)

def plot_throughput_vs_w(df: pd.DataFrame, outdir: Path):
    for workload in sorted(df["workload"].unique()):
        for cu in sorted(df["use_cu"].unique()):
            sub = df[(df["workload"]==workload) & (df["use_cu"]==cu)]
            if sub.empty: 
                continue
            g = (sub.groupby("w", as_index=False)
                    .agg({"updates_per_sec":"mean"})
                    .sort_values("w"))
            fig, ax = plt.subplots(figsize=(7,4.5))
            ax.plot(g["w"], g["updates_per_sec"], marker="o",
                    label=f"CU {'on' if cu else 'off'}")
            ax.set_xlabel("width w")
            ax.set_ylabel("updates/sec")
            ax.set_title(f"Throughput vs w — {workload}, CU={'on' if cu else 'off'}")
            ax.legend()
            out = outdir / f"throughput_vs_w_{workload}_cu{cu}.png"
            fig.tight_layout(); fig.savefig(out); plt.close(fig)

def plot_skew_sensitivity(df: pd.DataFrame, outdir: Path, fixed_eps=None):
    # 只对 zipf 有意义
    dfz = df[df["workload"]=="zipf"]
    if dfz.empty:
        return
    # 选择一个 eps（若未指定则取出现次数最多的）
    if fixed_eps is None:
        fixed_eps = dfz["eps"].mode().iloc[0]
    sub = dfz[(dfz["eps"]==fixed_eps) & (dfz["use_cu"]==1)]
    if sub.empty:
        return
    g = (sub.groupby("alpha", as_index=False)
            .agg({"med_min":"mean","med_mean":"mean","med_cmm":"mean"})
            .sort_values("alpha"))
    fig, ax = plt.subplots(figsize=(7,4.5))
    ax.plot(g["alpha"], g["med_min"],  marker="o", label="min")
    ax.plot(g["alpha"], g["med_mean"], marker="o", label="mean")
    ax.plot(g["alpha"], g["med_cmm"],  marker="o", label="cmm")
    ax.set_xlabel("Zipf alpha")
    ax.set_ylabel("median absolute error")
    ax.set_title(f"Skew sensitivity (eps={fixed_eps}) — zipf, CU=on")
    ax.legend()
    out = outdir / f"skew_sensitivity_zipf_cu1.png"
    fig.tight_layout(); fig.savefig(out); plt.close(fig)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="CSV (merged) file path")
    ap.add_argument("--outdir", default="plots")
    ap.add_argument("--skew_eps", type=float, default=None)
    args = ap.parse_args()

    outdir = Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)
    df = load_csv(Path(args.src))

    # 基本三类图
    plot_error_vs_eps(df, outdir)
    plot_rel_iqr_vs_eps(df, outdir)
    plot_throughput_vs_w(df, outdir)
    plot_skew_sensitivity(df, outdir, fixed_eps=args.skew_eps)

    print(f"[done] plots in {outdir}")

if __name__ == "__main__":
    main()
