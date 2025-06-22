#   __  __       _
#  |  \/  | __ _(_)_ __
#  | |\/| |/ _` | | '_ \
#  | |  | | (_| | | | | |
#  |_|  |_|\__,_|_|_| |_|
#

from loguru import logger
from fastapi import (
    Request, Header, Query, FastAPI
)
from fastapi.responses import PlainTextResponse
from services import (
    azure, cron_job, keep_alive, loaders,
    redis_cache, signature, stencil
)
from common import (
    craft, models
)

app, cache = FastAPI(), redis_cache.RedisCache()
craft.init_logger()


@app.api_route("/", methods=["GET", "HEAD"])
async def index():
    return {"message": "App Server is live"}


@app.get("/status")
async def status():
    return {"ok": True}


@app.get("/cron-job-update")
async def cron_job_update():
    return await cron_job.update_cron_jobs()


@app.get("/keep-render-alive")
async def keep_render_alive():
    return await keep_alive.cpu_heavy_work()


@app.get("/keep-supabase-alive")
async def keep_supabase_alive():
    return await keep_alive.single_query()


@app.get("/global-configuration")
async def global_configuration(
        request: "Request",
        x_app_id: str = Header(..., alias="X-App-ID"),
        x_app_token: str = Header(..., alias="X-App-Token"),
        x_app_region: str = Header(..., alias="X-App-Region"),
        x_app_version: str = Header(..., alias="X-App-Version"),
        a: str = Query(..., alias="a"),
        t: int = Query(..., alias="t"),
        n: str = Query(..., alias="n"),
):
    logger.info(f"configuration request: {request.url}")

    return await loaders.resolve_configuration(
        x_app_id, x_app_token, x_app_region, x_app_version, a, t, n, cache
    )


@app.get("/bootstrap")
async def bootstrap(
        request: "Request",
        x_app_id: str = Header(..., alias="X-App-ID"),
        x_app_token: str = Header(..., alias="X-App-Token"),
        x_app_region: str = Header(..., alias="X-App-Region"),
        x_app_version: str = Header(..., alias="X-App-Version"),
        a: str = Query(..., alias="a"),
        t: int = Query(..., alias="t"),
        n: str = Query(..., alias="n"),
):
    logger.info(f"bootstrap request: {request.url}")

    await loaders.enforce_rate_limit(request)

    return await loaders.resolve_bootstrap(
        x_app_id, x_app_token, x_app_region, x_app_version, a, t, n
    )


@app.post(f"/sign")
async def sign(
        req: "models.LicenseRequest",
        x_app_id: str = Header(..., alias="X-App-ID"),
        x_app_token: str = Header(..., alias="X-App-Token"),
):
    logger.info(f"signature request: {req}")

    return signature.manage_signature(req, x_app_id, x_app_token)


@app.get("/template-meta")
async def template_meta(
        request: "Request",
        x_app_id: str = Header(..., alias="X-App-ID"),
        x_app_token: str = Header(..., alias="X-App-Token"),
        a: str = Query(..., alias="a"),
        t: int = Query(..., alias="t"),
        n: str = Query(..., alias="n"),
):
    logger.info(f"templates request: {request.url}")

    return await stencil.stencil_meta(
        x_app_id, x_app_token, a, t, n
    )


@app.get("/template-viewer", response_class=PlainTextResponse)
async def template_viewer(
        request: "Request",
        x_app_id: str = Header(..., alias="X-App-ID"),
        x_app_token: str = Header(..., alias="X-App-Token"),
        a: str = Query(..., alias="a"),
        t: int = Query(..., alias="t"),
        n: str = Query(..., alias="n"),
        page: str = Query(..., alias="page"),
):
    logger.info(f"templates request: {request.url}")

    return await stencil.stencil_viewer(
        x_app_id, x_app_token, a, t, n, page
    )


@app.get("/business-case")
async def business_case(
        request: "Request",
        x_app_id: str = Header(..., alias="X-App-ID"),
        x_app_token: str = Header(..., alias="X-App-Token"),
        a: str = Query(..., alias="a"),
        t: int = Query(..., alias="t"),
        n: str = Query(..., alias="n"),
        case: str = Query(..., alias="case"),
):
    logger.info(f"business request: {request.url}")

    return await stencil.stencil_case(
        x_app_id, x_app_token, a, t, n, case
    )


@app.get("/speech-meta")
async def speech_meta(
        request: "Request",
        x_app_id: str = Header(..., alias="X-App-ID"),
        x_app_token: str = Header(..., alias="X-App-Token"),
        a: str = Query(..., alias="a"),
        t: int = Query(..., alias="t"),
        n: str = Query(..., alias="n"),
):
    logger.info(f"voice request: {request.url}")

    return await azure.SpeechEngine.tts_meta(
        x_app_id, x_app_token, a, t, n
    )


@app.post("/speech-voice")
async def speech_voice(
        req: "models.SpeechRequest",
        x_app_id: str = Header(..., alias="X-App-ID"),
        x_app_token: str = Header(..., alias="X-App-Token"),
):
    logger.info(f"voice request: {req}")

    return await azure.SpeechEngine.tts_audio(
        req, x_app_id, x_app_token, cache
    )


if __name__ == '__main__':
    pass
