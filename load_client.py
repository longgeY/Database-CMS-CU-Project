# load_client.py
import time
import random
import requests

SERVER_URL = "http://127.0.0.1:8000/update"

# 配置
RATE_PER_SEC = 1000       # 每秒 1000 次更新
DURATION_SEC = 10         # 总共跑 10 秒
KEY_SPACE = 100_000       # Uniform 的 key 空间 [0, KEY_SPACE)

def main():
    interval = 1.0 / RATE_PER_SEC  # 两次请求之间的目标间隔
    end_time = time.time() + DURATION_SEC

    sent = 0
    print(f"Starting load: uniform keys, {RATE_PER_SEC}/s, {DURATION_SEC}s")

    while time.time() < end_time:
        start_loop = time.time()

        # 生成一个 Uniform key
        key = random.randint(0, KEY_SPACE - 1)

        payload = {
            "key": key,
            "c": 1
        }

        try:
            # 发送 POST /update
            r = requests.post(SERVER_URL, json=payload, timeout=1.0)
            # 如果你想看返回，可以打印 r.json()
            # print(r.json())
        except Exception as e:
            print("request error:", e)

        sent += 1

        # 控制速率：尽量接近 1000/s
        elapsed = time.time() - start_loop
        sleep_time = interval - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)

    print(f"Done. Total updates sent: {sent}")

if __name__ == "__main__":
    main()

