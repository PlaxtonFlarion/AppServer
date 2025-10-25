#   _  __                    _    _ _
#  | |/ /___  ___ _ __      / \  | (_)_   _____
#  | ' // _ \/ _ \ '_ \    / _ \ | | \ \ / / _ \
#  | . \  __/  __/ |_) |  / ___ \| | |\ V /  __/
#  |_|\_\___|\___| .__/  /_/   \_\_|_| \_/ \___|
#                |_|
#

import time
import httpx
import random
import asyncio
from loguru import logger
from services import supabase
from common import const


async def cpu_heavy_work() -> dict:
    """
    随机执行一个 CPU 密集型操作
    """

    def calc_primes() -> int:
        """计算一定区间内的质数数量"""
        primes = []
        for i in range(10000, random.randint(10200, 10800)):
            for j in range(2, int(i ** 0.5) + 1):
                if i % j == 0: break
            else:
                primes.append(i)
        return len(primes)

    def string_hash_ops() -> int:
        """字符串拼接 + 哈希反复计算"""
        base_string = "CPUKeepAlive"
        hash_result = 0
        for i in range(random.randint(20000, 30000)):
            hash_result ^= hash(base_string + str(i))
        return hash_result & 0xFFFFFFFF

    def sort_random_numbers() -> float:
        """生成随机数并排序取部分求和"""
        arr = [random.random() for _ in range(random.randint(200000, 300000))]
        arr.sort()
        return sum(arr[:10])

    task_map = {
        "prime" : calc_primes,
        "hash"  : string_hash_ops,
        "sort"  : sort_random_numbers
    }
    task = random.choice(list(task_map.keys()))
    func = task_map[task]

    start    = time.time()
    result   = func()
    duration = time.time() - start

    logger.info("🟢 Render online")
    await asyncio.sleep(random.randint(1, 3))

    return {
        "status"    : "pong",
        "task"      : task,
        "result"    : result,
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
