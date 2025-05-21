#   __  __       _
#  |  \/  | __ _(_)_ __
#  | |\/| |/ _` | | '_ \
#  | |  | | (_| | | | | |
#  |_|  |_|\__,_|_|_| |_|
#

import asyncio
from fastapi import FastAPI
from common import (
    utils, const
)

app = FastAPI()


@app.api_route("/", methods=["GET", "HEAD"])
async def index():
    return {"message": "License Server is live"}


@app.get("/status")
async def status():
    return {"ok": True}


@app.get("/ping")
async def ping():
    # 模拟密集 CPU 运算（素数计算）
    def cpu_heavy_work():
        primes = []
        for num in range(10000, 10200):
            for i in range(2, num):
                if num % i == 0:
                    break
            else:
                primes.append(num)
        return len(primes)

    cpu_result = cpu_heavy_work()

    # 模拟异步 IO 操作
    await asyncio.sleep(1)

    return {
        "status": "pong",
        "cpu_cycles": cpu_result,
        "timestamp": time.time()
    }


@app.post(f"/sign/{const.APP_FX['app']}")
async def sign_fx(req: "utils.LicenseRequest"):
    return utils.handle_signature(req, const.APP_FX)


@app.post(f"/sign/{const.APP_MX['app']}")
async def sign_mx(req: "utils.LicenseRequest"):
    return utils.handle_signature(req, const.APP_MX)


if __name__ == '__main__':
    pass
