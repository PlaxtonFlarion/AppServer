#   _  __                    _    _ _
#  | |/ /___  ___ _ __      / \  | (_)_   _____
#  | ' // _ \/ _ \ '_ \    / _ \ | | \ \ / / _ \
#  | . \  __/  __/ |_) |  / ___ \| | |\ V /  __/
#  |_|\_\___|\___| .__/  /_/   \_\_|_| \_/ \___|
#                |_|

import time
import typing
import asyncio
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


if __name__ == '__main__':
    pass
