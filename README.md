Count-Min Sketch (CMS) Streaming System
A full implementation and evaluation framework for Count-Min Sketch (CMS), including:
Core CMS with min, mean, and CMM estimators
Conservative Updating (CU)
Synthetic workload generator (Uniform & Zipf)
Benchmark pipeline (error, skew, throughput)
FastAPI-based streaming server
Load generator for online testing
Visualization tools for all experimental results
This project provides a reproducible system for studying CMS accuracy–throughput tradeoffs in high-rate data streams.

cms/
│
├── cms.py               # Core CMS implementation
├── benchmark.py         # Synthetic benchmark runner
├── plot_results.py      # Visualization for all CSV outputs
├── workloads.py         # Workload generators (Uniform, Zipf)
├── run_sanity.py        # Quick correctness test
├── run_all.ps1          # Full batch benchmark script
│
├── stream_server.py     # FastAPI streaming server exposing CMS
├── load_client.py       # HTTP load generator for online testing
│
├── results/             # Generated experiment CSVs
└── plots/               # Plots (error, IQR, skew, throughput)

🚀 Features
✔ Count-Min Sketch

Configurable via eps, delta

Supports min, mean, CMM estimators

Uses row totals for CMM

Mergeable sketches for distributed processing

✔ Conservative Updating (CU)

Only increments counters equal to the current minimum.
Greatly reduces positive bias under skew.

✔ Streaming Server (FastAPI)

Expose CMS through REST APIs:

POST /reset

POST /update

POST /batch_update

POST /query

GET /stats

Suitable for real-time ingest experiments.

✔ Benchmark & Plotting

Evaluate:

Error vs epsilon

Estimator stability

Skew sensitivity

Throughput vs width

CU on/off comparison

Plots include median, IQR, and p95 curves.
