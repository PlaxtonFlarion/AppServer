from fastapi import APIRouter, Request, Header, Query
from fastapi.responses import PlainTextResponse
from loguru import logger
from services import loaders, stencil

router = APIRouter(tags=["Download"])


@router.get(path="/template-meta")
async def template_information(
    request: "Request",
    x_app_region: str = Header(..., alias="X-App-Region"),
    x_app_version: str = Header(..., alias="X-App-Version"),
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
        x_app_region, x_app_version, a, t, n, request.app.state.cache
    )


@router.get(path="/toolkit-meta")
async def toolkit_information(
    request: "Request",
    x_app_region: str = Header(..., alias="X-App-Region"),
    x_app_version: str = Header(..., alias="X-App-Version"),
    a: str = Query(..., alias="a"),
    t: int = Query(..., alias="t"),
    n: str = Query(..., alias="n"),
    platform: str = Query(..., alias="platform")
):
    logger.info(f"toolkit request: {request.url}")

    return await loaders.resolve_toolkit_download(
        x_app_region, x_app_version, a, t, n, platform, request.app.state.cache
    )


@router.get(path="/model-meta")
async def model_information(
    request: "Request",
    x_app_region: str = Header(..., alias="X-App-Region"),
    x_app_version: str = Header(..., alias="X-App-Version"),
    a: str = Query(..., alias="a"),
    t: int = Query(..., alias="t"),
    n: str = Query(..., alias="n")
):
    logger.info(f"model request: {request.url}")

    return await loaders.resolve_model_download(
        x_app_region, x_app_version, a, t, n, request.app.state.cache
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

