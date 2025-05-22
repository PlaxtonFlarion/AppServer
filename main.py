#   __  __       _
#  |  \/  | __ _(_)_ __
#  | |\/| |/ _` | | '_ \
#  | |  | | (_| | | | | |
#  |_|  |_|\__,_|_|_| |_|
#

from fastapi import (
    Header, FastAPI
)
from services import (
    cron_job, signature
)
from common import const

app = FastAPI()


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


@app.post(f"/sign")
async def sign(
        req: "signature.LicenseRequest",
        x_app_id: str = Header(..., alias="X-App-ID"),
        x_app_token: str = Header(..., alias="X-App-Token"),
):
    signature.verify_signature(x_app_token)


@app.post(f"/sign/{const.APP_FX['app']}")
async def sign_fx(req: "signature.LicenseRequest"):
    return signature.handle_signature(req, const.APP_FX)


@app.post(f"/sign/{const.APP_MX['app']}")
async def sign_mx(req: "signature.LicenseRequest"):
    return signature.handle_signature(req, const.APP_MX)


if __name__ == '__main__':
    pass
