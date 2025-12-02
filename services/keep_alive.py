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
from fastapi import (
    Request, HTTPException
)
from services import (
    signature, supabase
)
from utils import const


async def cpu_heavy_work() -> dict:
    """Render 保活"""

    def calc_primes() -> int:
        primes = []
        for i in range(10000, random.randint(20000, 30000)):
            for j in range(2, int(i ** 0.5) + 1):
                if i % j == 0: break
            else:
                primes.append(i)
        return sum(p * p for p in primes) & 0xFFFFFFFF

    def string_hash_ops() -> int:
        base_string = "CPUKeepAlive"
        hash_result = 0
        for i in range(random.randint(30000, 60000)):
            s = (base_string + str(i)).encode()
            h = int(hashlib.md5(s).hexdigest(), 16)
            hash_result ^= h
        return hash_result & 0xFFFFFFFF

    def sort_random_numbers() -> float:
        arr = [random.random() for _ in range(random.randint(100000, 300000))]
        arr.sort()
        return sum(math.log1p(v * 1000) for v in arr[:min(1000, len(arr))])

    task_map = {
        "calc" : calc_primes,
        "hash" : string_hash_ops,
        "sort" : sort_random_numbers
    }
    task = random.choice(list(task_map.keys()))
    func = task_map[task]

    start    = time.time()
    result   = func()
    duration = time.time() - start

    logger.info(f"🟢 Render online | target={task} | actual={duration:.2f}s")
    await asyncio.sleep(random.uniform(0.1, 1.0))

    return {
        "status"    : "pong",
        "task"      : task,
        "result"    : result,
        "duration"  : round(duration, 3),
        "timestamp" : time.time()
    }


async def single_query(request: "Request") -> dict:
    """Supabase 保活"""

    apikey        = request.headers.get("apikey")
    authorization = f"Bearer {apikey}"

    url     = f"{supabase.supabase_url}/rest/v1/{const.LICENSE_CODES}"
    params  = {"select": "id", "limit": 1}
    headers = {
        "apikey"        : apikey,
        "Authorization" : authorization
    }

    try:
        async with httpx.AsyncClient(headers=headers, timeout=90) as client:
            resp = await client.request("GET", url, params=params)
            resp.raise_for_status()

            logger.info("🟢 Supabase online")
            return {
                "status"      : "OK",
                "message"     : "Supabase online",
                "timestamp"   : int(time.time()),
                "http_status" : resp.status_code
            }

    except httpx.HTTPStatusError as e:
        logger.warning(f"🟡 Supabase offline: {e.response.status_code}")
        raise HTTPException(
            status_code=503,
            detail=f"Supabase offline ({e.response.status_code}): {e.response.text}"
        )

    except httpx.ConnectError as e:
        logger.error(f"🔴 Supabase connection error: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"Supabase unreachable: {str(e)}"
        )


async def predict_warmup(a: str, t: int, n: str) -> dict:
    """Modal 预热"""

    app_name, app_desc, *_ = a.lower().strip(), a, t, n

    expire_at = int(time.time()) + 86400
    token     = signature.sign_token(app_desc, expire_at)

    url     = f"https://plaxtonflarion--inference-inferenceservice-service.modal.run/"
    headers = {const.TOKEN_FORMAT: token}

    try:
        async with httpx.AsyncClient(headers=headers, timeout=90) as client:
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
        raise HTTPException(
            status_code=503,
            detail=f"Modal offline ({e.response.status_code}): {e.response.text}"
        )

    except httpx.ConnectError as e:
        logger.error(f"🔴 Modal connection error: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"Modal unreachable: {str(e)}"
        )


if __name__ == '__main__':
    pass
