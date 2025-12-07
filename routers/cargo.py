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

from schemas.cognitive import PredictResponse
from services.domain.standard import (
    bootstrap, configuration, download, predict, stencil
)

cargo_router = APIRouter(tags=["Cargo"])


@cargo_router.get(
    path="/global-configuration",
    operation_id="global-configuration"
)
async def global_configuration(
    request: Request,
    a: str = Query(..., alias="a"),
    t: int = Query(..., alias="t"),
    n: str = Query(..., alias="n")
):
    """
    获取全局配置。

    通过签名参数校验后，返回远程全局配置中心配置结果。
    """

    return await configuration.resolve_configuration(request, a, t, n)


@cargo_router.get(
    path="/bootstrap",
    operation_id="application_bootstrap"
)
async def application_bootstrap(
    request: Request,
    a: str = Query(..., alias="a"),
    t: int = Query(..., alias="t"),
    n: str = Query(..., alias="n")
):
    """
    客户端初始化配置接口。

    返回启动参数、区域设置、初始模板与缓存控制信息。
    """

    await request.app.state.cache.enforce_rate_limit(request)

    return await bootstrap.resolve_bootstrap(request, a, t, n)


@cargo_router.get(
    path="/proxy-predict",
    response_model=PredictResponse,
    operation_id="proxy-predict"
)
async def proxy_predict(
    request: Request,
    a: str = Query(..., alias="a"),
    t: int = Query(..., alias="t"),
    n: str = Query(..., alias="n")
):
    """
    代理推理请求接口。

    将客户端请求转发至 Modal/GPU 模型服务，支持 Token 校验。
    """

    return await predict.resolve_proxy_predict(request, a, t, n)


@cargo_router.get(
    path="/template-meta",
    operation_id="template_information"
)
async def template_information(
    request: Request,
    a: str = Query(..., alias="a"),
    t: int = Query(..., alias="t"),
    n: str = Query(..., alias="n")
):
    """
    模板元信息接口。

    返回所有模板的版本号、名称与下载地址。
    """

    return await download.resolve_stencil_download(request, a, t, n)


@cargo_router.get(
    path="/toolkit-meta",
    operation_id="toolkit_information"
)
async def toolkit_information(
    request: Request,
    a: str = Query(..., alias="a"),
    t: int = Query(..., alias="t"),
    n: str = Query(..., alias="n"),
    platform: str = Query(..., alias="platform")
):
    """
    工具元信息接口。

    返回所有工具的版本号、名称与下载地址。
    """

    return await download.resolve_toolkit_download(request,  a, t, n, platform)


@cargo_router.get(
    path="/model-meta",
    operation_id="model_information"
)
async def model_information(
    request: Request,
    a: str = Query(..., alias="a"),
    t: int = Query(..., alias="t"),
    n: str = Query(..., alias="n")
):
    """
    模型元信息接口。

    返回所有模型的版本号、名称与下载地址。
    """

    return await download.resolve_model_download(request, a, t, n)


@cargo_router.get(
    path="/template-viewer",
    response_class=PlainTextResponse,
    operation_id="template-viewer"
)
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


@cargo_router.get(
    path="/business-case",
    operation_id="business_case"
)
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
