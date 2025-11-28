from loguru import logger
from fastapi import (
    APIRouter, Request, Query
)
from fastapi.responses import PlainTextResponse
from services import (
    loaders, stencil
)

router = APIRouter(tags=["Loader"])


@router.get(path="/global-configuration")
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
    logger.info(f"configuration request: {request.url}")

    return await loaders.resolve_configuration(
        request.state.x_app_region, request.state.x_app_version, a, t, n, request.app.state.cache
    )


@router.get(path="/bootstrap")
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
    logger.info(f"bootstrap request: {request.url}")

    await request.app.state.cache.enforce_rate_limit(request)

    return await loaders.resolve_bootstrap(
        request.state.x_app_region, request.state.x_app_version, a, t, n, request.app.state.cache
    )


@router.get(path="/template-meta")
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
    logger.info(f"template request: {request.url}")

    return await loaders.resolve_stencil(
        request.state.x_app_region, request.state.x_app_version, a, t, n, request.app.state.cache
    )


@router.get(path="/toolkit-meta")
async def toolkit_information(
    request: "Request",
    a: str = Query(..., alias="a"),
    t: int = Query(..., alias="t"),
    n: str = Query(..., alias="n"),
    platform: str = Query(..., alias="platform")
):
    logger.info(f"toolkit request: {request.url}")

    return await loaders.resolve_toolkit_download(
        request.state.x_app_region, request.state.x_app_version, a, t, n, platform, request.app.state.cache
    )


@router.get(path="/model-meta")
async def model_information(
    request: "Request",
    a: str = Query(..., alias="a"),
    t: int = Query(..., alias="t"),
    n: str = Query(..., alias="n")
):
    logger.info(f"model request: {request.url}")

    return await loaders.resolve_model_download(
        request.state.x_app_region, request.state.x_app_version, a, t, n, request.app.state.cache
    )


@router.get(path="/template-viewer", response_class=PlainTextResponse)
async def template_viewer(
    request: "Request",
    a: str = Query(..., alias="a"),
    t: int = Query(..., alias="t"),
    n: str = Query(..., alias="n"),
    page: str = Query(..., alias="page")
):
    """
    单个模板内容查看接口。

    通过模板名获取其纯文本内容（如 HTML、JSON 模板等）。
    """
    logger.info(f"templates request: {request.url}")

    return await stencil.stencil_viewer(
        a, t, n, page
    )


@router.get("/business-case")
async def business_case(
    request: "Request",
    a: str = Query(..., alias="a"),
    t: int = Query(..., alias="t"),
    n: str = Query(..., alias="n"),
    case: str = Query(..., alias="case")
):
    """
    获取业务用例指令集。

    根据 `case` 参数返回一组命令，用于客户端执行流程配置。
    """
    logger.info(f"business request: {request.url}")

    return await stencil.stencil_case(
        a, t, n, case
    )


if __name__ == '__main__':
    pass
