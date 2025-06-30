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
    """
    健康检查接口。

    返回服务状态标识信息，常用于存活性探测或 Render 运行时检测。
    """
    return {"message": "App Server is live"}


@app.get("/status")
async def status():
    """
    简单状态接口。

    用于快速确认服务可达性，返回固定 OK 响应。
    """
    return {"ok": True}


@app.get("/cron-job-update")
async def cron_job_update():
    """
    触发定时任务刷新。

    通常用于 Render 定期拉取任务配置或执行后台调度。
    """
    return await cron_job.update_cron_jobs()


@app.get("/keep-render-alive")
async def keep_render_alive():
    """
    防 Render 休眠接口。

    通过执行轻度 CPU 运算保持 Render 服务活跃。
    """
    return await keep_alive.cpu_heavy_work()


@app.get("/keep-supabase-alive")
async def keep_supabase_alive():
    """
    防 Supabase 休眠接口。

    通过轻量 SQL 查询避免 Supabase 因长期无访问进入休眠状态。
    """
    return await keep_alive.single_query()


@app.get("/keep-modal-alive")
async def keep_modal_alive():
    """
    定时触发，用于保持 Modal 容器存活状态，防止超时回收。
    """
    return await keep_alive.predict_warmup()


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
    """
    获取全局配置。

    通过签名参数校验后，返回远程全局配置中心配置结果。
    """
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
    """
    客户端初始化配置接口。

    返回启动参数、区域设置、初始模板与缓存控制信息。
    """
    logger.info(f"bootstrap request: {request.url}")

    await cache.enforce_rate_limit(request)

    return await loaders.resolve_bootstrap(
        x_app_id, x_app_token, x_app_region, x_app_version, a, t, n, cache
    )


@app.get("/proxy-predict")
async def proxy_predict(
        request: "Request",
        x_app_id: str = Header(..., alias="X-App-ID"),
        x_app_token: str = Header(..., alias="X-App-Token"),
        x_app_region: str = Header(..., alias="X-App-Region"),
        x_app_version: str = Header(..., alias="X-App-Version"),
        a: str = Query(..., alias="a"),
        t: int = Query(..., alias="t"),
        n: str = Query(..., alias="n"),
):
    """
    代理推理请求接口。

    将客户端请求转发至 Modal/GPU 模型服务，支持 Token 校验。
    """
    logger.info(f"predict request: {request.url}")

    return await loaders.resolve_proxy_predict(
        x_app_id, x_app_token, x_app_region, x_app_version, a, t, n, cache
    )


@app.get("/toolkit-meta")
async def toolkit_information(
        request: "Request",
        x_app_id: str = Header(..., alias="X-App-ID"),
        x_app_token: str = Header(..., alias="X-App-Token"),
        x_app_region: str = Header(..., alias="X-App-Region"),
        x_app_version: str = Header(..., alias="X-App-Version"),
        a: str = Query(..., alias="a"),
        t: int = Query(..., alias="t"),
        n: str = Query(..., alias="n"),
        platform: str = Query(..., alias="platform"),
):
    logger.info(f"toolkit request: {request.url}")

    return await loaders.resolve_toolkit_download(
        x_app_id, x_app_token, x_app_region, x_app_version, a, t, n, platform, cache
    )


@app.get("/model-meta")
async def model_information(
        request: "Request",
        x_app_id: str = Header(..., alias="X-App-ID"),
        x_app_token: str = Header(..., alias="X-App-Token"),
        x_app_region: str = Header(..., alias="X-App-Region"),
        x_app_version: str = Header(..., alias="X-App-Version"),
        a: str = Query(..., alias="a"),
        t: int = Query(..., alias="t"),
        n: str = Query(..., alias="n"),
):
    logger.info(f"model request: {request.url}")

    return await loaders.resolve_model_download(
        x_app_id, x_app_token, x_app_region, x_app_version, a, t, n, cache
    )


@app.post(f"/sign")
async def sign(
        req: "models.LicenseRequest",
        x_app_id: str = Header(..., alias="X-App-ID"),
        x_app_token: str = Header(..., alias="X-App-Token"),
):
    """
    授权签名接口。

    根据请求信息生成签名证书（License 文件），支持客户端激活验证。
    """
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
    """
    模板元信息接口。

    返回所有模板的版本号、名称与下载地址。
    """
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
    """
    单个模板内容查看接口。

    通过模板名获取其纯文本内容（如 HTML、JSON 模板等）。
    """
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
    """
    获取业务用例指令集。

    根据 `case` 参数返回一组命令，用于客户端执行流程配置。
    """
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
    """
    获取语音合成格式列表。

    返回可用的语音格式、语调模型与语言设置。
    """
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
    """
    合成语音音频文件。

    提交语音内容与目标格式，返回可下载的音频文件或链接。
    """
    logger.info(f"voice request: {req}")

    return await azure.SpeechEngine.tts_audio(
        req, x_app_id, x_app_token, cache
    )


if __name__ == '__main__':
    pass
