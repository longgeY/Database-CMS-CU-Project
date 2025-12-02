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

### 1. Start the server
```bash
uvicorn stream_server:app --host 0.0.0.0 --port 8000

The server will start on:
```bash
[uvicorn stream_server:app --host 0.0.0.0 --port 8000
](http://127.0.0.1:8000
)

