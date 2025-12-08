# Database-CMS-CU-Project

A high-performance streaming frequency estimation system based on the **Count-Min Sketch (CMS)** data structure, implemented in Python.  
This project includes:

- A FastAPI-based **stream server** that exposes CMS as an online HTTP service  
- A **load client** that generates high-rate streaming updates  
- A correctness test with exact ground-truth comparison  
- Experiments evaluating error vs. ε, estimators, and Conservative Update  
- Throughput analysis vs. table width and CU overhead  
- Final plots and analysis used in the presentation

---

## 📌 Project Structure

```bash
cms/
├── benchmark.py        # Main benchmarking script for running accuracy and throughput experiments
├── cms.py              # Core implementation of the Count-Min Sketch data structure
├── load_client.py      # Streaming load generator (uniform and Zipf workloads)
├── plot_results.py     # Script for visualizing experimental results using Matplotlib
├── README.md           # Project documentation and usage instructions
├── run_all.ps1         # PowerShell script to run the full experiment pipeline (Windows)
├── run_sanity.py       # Sanity check script for basic correctness testing
├── stream_server.py    # FastAPI-based CMS streaming server implementation
├── test.py             # Correctness testing with ground-truth comparison
├── workloads.py        # Workload generators (uniform and Zipf distributions)
├── plots/              # Generated figures and visualization output
├── results/            # Raw experimental CSV results
└── __pycache__/
```

---

## 📘 Features

### ✔ Count-Min Sketch  
- Supports **min**, **mean**, and **CMM** estimators  
- Supports **Conservative Update (CU)**  
- Guaranteed no underestimation for min estimator  
- Error bound: `estimate ≤ true + ε·N`

### ✔ Stream Server (FastAPI)  
Exposes CMS via HTTP:

| Method | Endpoint         | Description |
|--------|------------------|-------------|
| POST   | `/reset`         | Reinitialize CMS (eps, delta, seed, CU) |
| POST   | `/update`        | Single update |
| POST   | `/batch_update`  | Batch updates |
| POST   | `/query`         | Query with estimator=`min|mean|cmm` |
| GET    | `/stats`         | Sketch parameters and total updates |

---

## 🚀 How to Run the Server

### 1. Install packages
```bash
pip install fastapi uvicorn
```

### 2. Start the server
```bash
uvicorn stream_server:app --host 0.0.0.0 --port 8000
```
The server will start on: http://127.0.0.1:8000

### 3. Run Uniform Load Test
```bash
python load_client.py --dist uniform --rate 1000 --duration 10
```

### 4. Run Zipf Load Test
```bash
python load_client.py --dist zipf --alpha 1.0 --rate 1000 --duration 10
```

## 🚀 Run the test(simple test)
```bash
python .\test.py
```
