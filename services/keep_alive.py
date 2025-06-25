#   _  __                    _    _ _
#  | |/ /___  ___ _ __      / \  | (_)_   _____
#  | ' // _ \/ _ \ '_ \    / _ \ | | \ \ / / _ \
#  | . \  __/  __/ |_) |  / ___ \| | |\ V /  __/
#  |_|\_\___|\___| .__/  /_/   \_\_|_| \_/ \___|
#                |_|
#

import time
import httpx
import typing
import asyncio
from loguru import logger
from services import supabase
from common import const


async def cpu_heavy_work() -> dict:
    primes = []
    for num in range(10000, 10200):
        for i in range(2, num):
            if num % i == 0:
                break
        else:
            primes.append(num)

    await asyncio.sleep(1)

    return {
        "status": "pong", "cpu_cycles": len(primes), "timestamp": time.time()
    }


async def single_query() -> typing.Any:
    sup = supabase.Supabase("", "", const.LICENSE_CODES)
    return await asyncio.to_thread(sup.keep_alive)


async def predict_warmup() -> None:
    url = f"https://plaxtonflarion--inference-inferenceservice-service.modal.run/"
    
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.request("GET", url)
            resp.raise_for_status()
            logger.info(f"Ping Modal 成功: {resp.json()}")
            return resp.json()
    except Exception as e:
        logger.warning(f"Ping Modal 失败: {e}")
        return {"status": "error", "detail": str(e)}


if __name__ == '__main__':
    pass
