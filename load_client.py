# load_client.py
import time
import random
import requests
import argparse

import numpy as np  # Used for Zipf sampling (pip install numpy)

SERVER_URL = "http://127.0.0.1:8000/update"

# Default configuration
DEFAULT_RATE_PER_SEC = 1000       # Updates per second
DEFAULT_DURATION_SEC = 10         # Total running time (seconds)
KEY_SPACE = 100_000               # Key space [0, KEY_SPACE)
_ZIPF_CDF = None
_ZIPF_ALPHA = None


def sample_uniform() -> int:
    """Uniform distribution: each key has equal probability."""
    return random.randint(0, KEY_SPACE - 1)


def sample_zipf(alpha: float) -> int:
    """
    Truncated Zipf(α) sampling on the key range [0, KEY_SPACE).

    We construct a discrete distribution with:
        P(i) ∝ (i+1)^(-alpha)  for i = 0, 1, ..., KEY_SPACE-1
    and sample using inverse transform sampling.
    """
    global _ZIPF_CDF, _ZIPF_ALPHA

    # (Re)build CDF if alpha changed or not initialized
    if _ZIPF_CDF is None or _ZIPF_ALPHA != alpha:
        ks = np.arange(1, KEY_SPACE + 1, dtype=np.float64)  # 1..KEY_SPACE
        pmf = ks ** (-alpha)
        pmf /= pmf.sum()
        _ZIPF_CDF = np.cumsum(pmf)
        _ZIPF_ALPHA = alpha

    u = random.random()
    idx = np.searchsorted(_ZIPF_CDF, u)
    # idx is in [0, KEY_SPACE-1]
    return int(idx)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dist",
        choices=["uniform", "zipf"],
        default="uniform",
        help="Key distribution: uniform or zipf (default: uniform)",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=1.0,
        help="Zipf distribution alpha (only used when --dist zipf)",
    )
    parser.add_argument(
        "--rate",
        type=int,
        default=DEFAULT_RATE_PER_SEC,
        help="Update rate (updates per second)",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=DEFAULT_DURATION_SEC,
        help="Total running time (seconds)",
    )
    args = parser.parse_args()

    rate = args.rate
    duration = args.duration
    dist = args.dist
    alpha = args.alpha

    interval = 1.0 / rate        # Target interval between requests
    end_time = time.time() + duration

    sent = 0
    print(f"Starting load generator:")
    print(f"  distribution = {dist}, alpha = {alpha if dist == 'zipf' else '-'}")
    print(f"  rate         = {rate} updates/s")
    print(f"  duration     = {duration} s")
    print(f"  key space    = [0, {KEY_SPACE})")

    start_all = time.time()

    while time.time() < end_time:
        start_loop = time.time()

        # Select key according to the chosen distribution
        if dist == "uniform":
            key = sample_uniform()
        else:
            key = sample_zipf(alpha)

        payload = {
            "key": int(key),
            "c": 1,
        }

        try:
            # Send POST request to /update endpoint
            r = requests.post(SERVER_URL, json=payload, timeout=1.0)
            # Uncomment if you want to see server responses:
            # print(r.json())
        except Exception as e:
            print("Request error:", e)

        sent += 1

        # Rate control to maintain target throughput
        elapsed = time.time() - start_loop
        sleep_time = interval - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)

    total_time = time.time() - start_all
    print(f"Done. Total updates sent: {sent}")
    print(f"Average throughput: {sent / total_time:.2f} updates/s")


if __name__ == "__main__":
    main()
