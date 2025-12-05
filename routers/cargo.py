#   ____
#  / ___|__ _ _ __ __ _  ___
# | |   / _` | '__/ _` |/ _ \
# | |__| (_| | | | (_| | (_) |
#  \____\__,_|_|  \__, |\___/
#                 |___/
#

from fastapi import (
    APIRouter, Request, Query
)
from fastapi.responses import PlainTextResponse
from services.domain.standard import (
    bootstrap, configuration, download, predict, stencil
)

cargo_router = APIRouter(tags=["Cargo"])


@cargo_router.get(path="/global-configuration")
async def global_configuration(
    request: "Request",
    a: str = Query(..., alias="a"),
    t: int = Query(..., alias="t"),
    n: str = Query(..., alias="n")
):
    """
    获取全局配置。

    通过签名参数校验后，返回远程全局配置中心配置结果。
    """

    x_app_region  = request.state.x_app_region
    x_app_version = request.state.x_app_version
    cache         = request.app.state.cache

    return await configuration.resolve_configuration(
        x_app_region, x_app_version, a, t, n, cache
    )


@cargo_router.get(path="/bootstrap")
async def bootstrap(
    request: "Request",
    a: str = Query(..., alias="a"),
    t: int = Query(..., alias="t"),
    n: str = Query(..., alias="n")
):
    """
    客户端初始化配置接口。

    返回启动参数、区域设置、初始模板与缓存控制信息。
    """

    await request.app.state.cache.enforce_rate_limit(request)

    x_app_region  = request.state.x_app_region
    x_app_version = request.state.x_app_version
    cache         = request.app.state.cache

    return await bootstrap.resolve_bootstrap(
        x_app_region, x_app_version, a, t, n, cache
    )


@cargo_router.get(path="/proxy-predict")
async def proxy_predict(
    request: "Request",
    a: str = Query(..., alias="a"),
    t: int = Query(..., alias="t"),
    n: str = Query(..., alias="n")
):
    """
    代理推理请求接口。

    将客户端请求转发至 Modal/GPU 模型服务，支持 Token 校验。
    """

    x_app_region  = request.state.x_app_region
    x_app_version = request.state.x_app_version
    cache         = request.app.state.cache

    return await predict.resolve_proxy_predict(
        x_app_region, x_app_version, a, t, n, cache
    )


@cargo_router.get(path="/template-meta")
async def template_information(
    request: "Request",
    a: str = Query(..., alias="a"),
    t: int = Query(..., alias="t"),
    n: str = Query(..., alias="n")
):
    """
    模板元信息接口。

    返回所有模板的版本号、名称与下载地址。
    """

    x_app_region  = request.state.x_app_region
    x_app_version = request.state.x_app_version
    cache         = request.app.state.cache

    return await download.resolve_stencil_download(
        x_app_region, x_app_version, a, t, n, cache
    )


@cargo_router.get(path="/toolkit-meta")
async def toolkit_information(
    request: "Request",
    a: str = Query(..., alias="a"),
    t: int = Query(..., alias="t"),
    n: str = Query(..., alias="n"),
    platform: str = Query(..., alias="platform")
):
    """
    工具元信息接口。

    返回所有工具的版本号、名称与下载地址。
    """

    x_app_region  = request.state.x_app_region
    x_app_version = request.state.x_app_version
    cache         = request.app.state.cache

    return await download.resolve_toolkit_download(
        x_app_region, x_app_version, a, t, n, platform, cache
    )


@cargo_router.get(path="/model-meta")
async def model_information(
    request: "Request",
    a: str = Query(..., alias="a"),
    t: int = Query(..., alias="t"),
    n: str = Query(..., alias="n")
):
    """
    模型元信息接口。

    返回所有模型的版本号、名称与下载地址。
    """

    x_app_region  = request.state.x_app_region
    x_app_version = request.state.x_app_version
    cache         = request.app.state.cache

    return await download.resolve_model_download(
        x_app_region, x_app_version, a, t, n, cache
    )


@cargo_router.get(path="/template-viewer", response_class=PlainTextResponse)
async def template_viewer(
    a: str = Query(..., alias="a"),
    t: int = Query(..., alias="t"),
    n: str = Query(..., alias="n"),
    page: str = Query(..., alias="page")
):
    """
    单个模板内容查看接口。

    通过模板名获取其纯文本内容（如 HTML、JSON 模板等）。
    """

    return await stencil.stencil_viewer(a, t, n, page)


@cargo_router.get("/business-case")
async def business_case(
    a: str = Query(..., alias="a"),
    t: int = Query(..., alias="t"),
    n: str = Query(..., alias="n"),
    case: str = Query(..., alias="case")
):
    """
    获取业务用例指令集。

    根据 `case` 参数返回一组命令，用于客户端执行流程配置。
    """

    return await stencil.stencil_case(a, t, n, case)


if __name__ == '__main__':
    pass
