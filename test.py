import requests
import random
from collections import defaultdict

BASE = "http://127.0.0.1:8000"

def reset_cms(eps=1e-3, delta=1e-3, use_cu=False, seed=1):
    r = requests.post(f"{BASE}/reset", json={
        "eps": eps,
        "delta": delta,
        "use_cu": use_cu,
        "seed": seed,
    })
    print("reset:", r.json())

def test_small():
    reset_cms(eps=1e-3, delta=1e-3, use_cu=False)

    true_count = defaultdict(int)

    NUM_UPDATES = 5000
    KEY_SPACE = 100

    for _ in range(NUM_UPDATES):
        k = random.randint(0, KEY_SPACE - 1)
        true_count[k] += 1
        requests.post(f"{BASE}/update", json={"key": k, "c": 1})

    test_keys = random.sample(list(true_count.keys()), 20)

    max_err = 0
    under_count = 0

    for k in test_keys:
        truth = true_count[k]
        resp = requests.post(f"{BASE}/query", json={
            "key": k,
            "estimator": "min"  
        }).json()
        est = resp["estimate"]
        err = est - truth
        print(f"key={k}, truth={truth}, est={est}, err={err}")
        if est < truth:
            under_count += 1
        max_err = max(max_err, err)

    print("underestimation count =", under_count)
    print("max error =", max_err)

if __name__ == "__main__":
    test_small()
