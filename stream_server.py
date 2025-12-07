# stream_server.py
"""
Simple HTTP stream server exposing a Count-Min Sketch (CMS) instance.

Endpoints:
- POST /reset      : (re)initialize CMS with eps, delta, use_cu
- POST /update     : single update (key, c)
- POST /batch_update : batch updates
- POST /query      : point query with estimator = min / mean / cmm
- GET  /stats      : basic sketch statistics
"""

from typing import List, Literal

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from threading import Lock

from cms import CMS 


# ----------Configuration & Global Status----------

# Default parameters (can be overridden using environment variables)
DEFAULT_EPS = float(os.getenv("CMS_EPS", "1e-3"))
DEFAULT_DELTA = float(os.getenv("CMS_DELTA", "1e-3"))
DEFAULT_SEED = int(os.getenv("CMS_SEED", "1"))
DEFAULT_USE_CU = os.getenv("CMS_USE_CU", "false").lower() == "true"

app = FastAPI(title="CMS Stream Server", version="0.1")

_cms_lock = Lock()
_cms: CMS | None = None
_use_cu: bool = DEFAULT_USE_CU


def _init_cms(eps: float = DEFAULT_EPS,
              delta: float = DEFAULT_DELTA,
              seed: int = DEFAULT_SEED,
              use_cu: bool = DEFAULT_USE_CU) -> None:
    """Initialize or reset the global CMS instance."""
    global _cms, _use_cu
    with _cms_lock:
        _cms = CMS.from_eps_delta(eps, delta, seed=seed)
        if _cms.row_totals is None:
            _cms.row_totals = [0] * _cms.d
        _use_cu = use_cu


_init_cms()


# ---------- Request/Response Model ----------

class ResetRequest(BaseModel):
    eps: float
    delta: float
    use_cu: bool = False
    seed: int = 1


class UpdateRequest(BaseModel):
    key: int
    c: int = 1


class BatchUpdateRequest(BaseModel):
    updates: List[UpdateRequest]


class QueryRequest(BaseModel):
    key: int
    estimator: Literal["min", "mean", "cmm"] = "min"


class QueryResponse(BaseModel):
    key: int
    estimator: str
    estimate: float
    total_updates: int


class StatsResponse(BaseModel):
    eps: float
    delta: float
    d: int
    w: int
    use_cu: bool
    total_updates: int


# ---------- Routing implementation ----------

@app.post("/reset")
def reset(req: ResetRequest):
    """reset CMS paremeters（eps, delta, use_cu, seed）."""
    _init_cms(eps=req.eps, delta=req.delta, seed=req.seed, use_cu=req.use_cu)
    return {
        "status": "ok",
        "message": f"CMS reset with eps={req.eps}, delta={req.delta}, use_cu={req.use_cu}, seed={req.seed}",
    }


@app.post("/update")
def update(req: UpdateRequest):
    """update single (i, c)."""
    if _cms is None:
        raise HTTPException(status_code=500, detail="CMS not initialized")
    with _cms_lock:
        if _use_cu:
            _cms.update_cu(req.key, req.c)
        else:
            _cms.update(req.key, req.c)
        total = _cms.total_updates
    return {"status": "ok", "total_updates": total}


@app.post("/batch_update")
def batch_update(req: BatchUpdateRequest):
    """Batch updates, suitable for load testing."""
    if _cms is None:
        raise HTTPException(status_code=500, detail="CMS not initialized")
    with _cms_lock:
        for u in req.updates:
            if _use_cu:
                _cms.update_cu(u.key, u.c)
            else:
                _cms.update(u.key, u.c)
        total = _cms.total_updates
    return {"status": "ok", "total_updates": total, "num_updates": len(req.updates)}


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    """Point queries support three estimators: min, mean, and cmm."""
    if _cms is None:
        raise HTTPException(status_code=500, detail="CMS not initialized")
    with _cms_lock:
        if req.estimator == "min":
            est = _cms.query_min(req.key)
        elif req.estimator == "mean":
            est = _cms.query_mean(req.key)
        elif req.estimator == "cmm":
            est = _cms.query_cmm(req.key)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown estimator: {req.estimator}")
        total = _cms.total_updates

    return QueryResponse(
        key=req.key,
        estimator=req.estimator,
        estimate=float(est),
        total_updates=total,
    )


@app.get("/stats", response_model=StatsResponse)
def stats():
    """Returns the current sketch state (d, w, whether it is CU, etc.)."""
    if _cms is None:
        raise HTTPException(status_code=500, detail="CMS not initialized")
    
    with _cms_lock:
        eps = DEFAULT_EPS 
        delta = DEFAULT_DELTA
        d = _cms.d
        w = _cms.w
        total = _cms.total_updates
        use_cu = _use_cu

    return StatsResponse(
        eps=eps,
        delta=delta,
        d=d,
        w=w,
        use_cu=use_cu,
        total_updates=total,
    )
