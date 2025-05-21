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
    # 模拟 CPU 占用
    _ = sum(i * i for i in range(10000))

    # 模拟 IO 操作（假装读取某配置）
    asyncio.sleep(0.5)  # 延迟 0.5 秒

    return {
        "status": "pong",
        "timestamp": time.time(),
        "uptime_check": True
    }


@app.post(f"/sign/{const.APP_FX['app']}")
async def sign_fx(req: "utils.LicenseRequest"):
    return utils.handle_signature(req, const.APP_FX)


@app.post(f"/sign/{const.APP_MX['app']}")
async def sign_mx(req: "utils.LicenseRequest"):
    return utils.handle_signature(req, const.APP_MX)


if __name__ == '__main__':
    pass
