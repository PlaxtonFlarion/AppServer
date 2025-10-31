#   _  __                    _    _ _
#  | |/ /___  ___ _ __      / \  | (_)_   _____
#  | ' // _ \/ _ \ '_ \    / _ \ | | \ \ / / _ \
#  | . \  __/  __/ |_) |  / ___ \| | |\ V /  __/
#  |_|\_\___|\___| .__/  /_/   \_\_|_| \_/ \___|
#                |_|
#

import math
import time
import httpx
import random
import asyncio
import hashlib
from loguru import logger
from services import supabase
from common import const


async def cpu_heavy_work() -> dict:
    """
    智能自适应CPU密集任务
        - 动态调整计算规模
        - 确保运行时间 ≈ target_time（秒）
    """

    def calc_primes() -> int:
        """计算一定区间内的质数数量"""
        close = (start := 10000) + scale
        prime = []

        for i in range(start, close):
            for j in range(2, int(i ** 0.5) + 1):
                if i % j == 0: break
            else:
                prime.append(i)
        return sum(p * p for p in prime) & 0xFFFFFFFF

    def string_hash_ops() -> int:
        """字符串拼接 + 哈希反复计算"""
        common = "CPUKeepAlive_Adaptive"
        result = 0

        for i in range(scale):
            s = (common + str(i)).encode()
            h = int(hashlib.md5(s).hexdigest(), 16)
            result ^= h
        return result & 0xFFFFFFFF

    def sort_random_numbers() -> float:
        """生成随机数并排序取部分求和"""
        arr = [random.random() for _ in range(scale)]
        arr.sort()
        return sum(math.log1p(v * 1000) for v in arr[:min(1000, len(arr))])

    funcs = [
        calc_primes, string_hash_ops, sort_random_numbers
    ]
    scale = 10000
    final = 0.0

    target_time = random.uniform(0.5, 1.5)

    for _ in range(6):
        func  = random.choice(funcs)
        begin = time.perf_counter()
        func()

        if (cost := time.perf_counter() - begin) == 0: cost = 0.001

        scale = int(scale * (target_time / cost))
        final = cost

        if abs(cost - target_time) < 0.1: break

    random.choice(funcs)(); duration = final

    logger.info(f"🟢 Render online | target={target_time:.2f}s | actual={duration:.2f}s")

    await asyncio.sleep(random.uniform(1.0, 3.0))

    return {
        "status"    : "pong",
        "duration"  : round(duration, 3),
        "timestamp" : time.time()
    }


async def single_query() -> dict:
    sup = supabase.Supabase("", "", const.LICENSE_CODES)

    return await asyncio.to_thread(sup.keep_alive)


async def predict_warmup() -> dict:
    url = f"https://plaxtonflarion--inference-inferenceservice-service.modal.run/"

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.request("GET", url)
            resp.raise_for_status()
            logger.info("🟢 Modal online")
            return {
                "status"      : "OK",
                "message"     : "Modal online",
                "timestamp"   : int(time.time()),
                "http_status" : resp.status_code
            }

    except httpx.HTTPStatusError as e:
        logger.warning(f"🟡 Modal offline: {e.response.status_code}")
        return {
            "status"      : "ERROR",
            "message"     : f"Modal offline: {e.response.text}",
            "timestamp"   : int(time.time()),
            "http_status" : e.response.status_code
        }

    except Exception as e:
        logger.error(f"🔴 Modal connection error: {e}")
        return {
            "status"    : "ERROR",
            "message"   : f"Modal connection error: {str(e)}",
            "timestamp" : int(time.time())
        }


if __name__ == '__main__':
    pass
