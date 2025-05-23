#   __  __       _
#  |  \/  | __ _(_)_ __
#  | |\/| |/ _` | | '_ \
#  | |  | | (_| | | | | |
#  |_|  |_|\__,_|_|_| |_|
#

from loguru import logger
from fastapi import (
    Request, Header, FastAPI
)
from services import (
    cron_job, loaders, signature
)
from common import (
    const, craft
)

app, *_ = FastAPI(), craft.init_logger()


@app.api_route("/", methods=["GET", "HEAD"])
async def index():
    return {"message": "License Server is live"}


@app.get("/status")
async def status():
    return {"ok": True}


@app.get("/cron-job-update")
async def cron_job_update():
    return await cron_job.update_cron_jobs()


@app.get("/keep-render-alive")
async def keep_render_alive():
    return await cron_job.cpu_heavy_work()


@app.get("/bootstrap")
async def bootstrap(
    request: "Request",
    x_app_id: str = Header(..., alias="X-App-ID"),
    x_app_token: str = Header(..., alias="X-App-Token"),
    x_app_region: str = Header(..., alias="X-App-Region"),
    x_app_version: str = Header(..., alias="X-App-Version")
):
    logger.warning(x_app_region)
    logger.warning(x_app_version)
    loaders.enforce_rate_limit(request)
    return loaders.resolve_bootstrap(x_app_region, x_app_version)


@app.post(f"/sign")
async def sign(
        req: "signature.LicenseRequest",
        x_app_id: str = Header(default=None, alias="X-App-ID"),
        x_app_token: str = Header(default=None, alias="X-App-Token")
):
    logger.info(f"signing request: {req}")

    return signature.handle_signature(
        req,
        x_app_id,
        x_app_token,
        const.APP_FX["private_key"],
        const.APP_FX["public_key"],
        const.APP_FX
    )


if __name__ == '__main__':
    pass
