#  ____                                      ____             _
# |  _ \ ___  ___  ___  _   _ _ __ ___ ___  |  _ \ ___  _   _| |_ ___ _ __
# | |_) / _ \/ __|/ _ \| | | | '__/ __/ _ \ | |_) / _ \| | | | __/ _ \ '__|
# |  _ <  __/\__ \ (_) | |_| | | | (_|  __/ |  _ < (_) | |_| | ||  __/ |
# |_| \_\___||___/\___/ \__,_|_|  \___\___| |_| \_\___/ \__,_|\__\___|_|
#

from fastapi import (
    APIRouter, Request, Query
)
from fastapi.responses import PlainTextResponse
from services.domain.standard.resource import (
    resolve_template_download,
    resolve_toolkit_download,
    resolve_model_download,
    stencil_viewer,
    stencil_case
)

resource_router = APIRouter(tags=["Resource"])


@resource_router.get(
    path="/template-meta",
    operation_id="api_template_meta"
)
async def api_template_meta(
    request: Request,
    a: str = Query(..., alias="a"),
    t: int = Query(..., alias="t"),
    n: str = Query(..., alias="n")
):
    """
    模板元信息接口。

    返回所有模板的版本号、名称与下载地址。
    """

    return await resolve_template_download(request, a, t, n)


@resource_router.get(
    path="/toolkit-meta",
    operation_id="api_toolkit_meta"
)
async def api_toolkit_meta(
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

    return await resolve_toolkit_download(request, a, t, n, platform)


@resource_router.get(
    path="/model-meta",
    operation_id="api_model_meta"
)
async def api_model_meta(
    request: Request,
    a: str = Query(..., alias="a"),
    t: int = Query(..., alias="t"),
    n: str = Query(..., alias="n")
):
    """
    模型元信息接口。

    返回所有模型的版本号、名称与下载地址。
    """

    return await resolve_model_download(request, a, t, n)


@resource_router.get(
    path="/template-viewer",
    response_class=PlainTextResponse,
    operation_id="api_template_viewer"
)
async def api_template_viewer(
    a: str = Query(..., alias="a"),
    t: int = Query(..., alias="t"),
    n: str = Query(..., alias="n"),
    page: str = Query(..., alias="page")
):
    """
    单个模板内容下载接口。

    通过模板名获取其纯文本内容（如 HTML、JSON 模板等）。
    """

    return await stencil_viewer(a, t, n, page)


@resource_router.get(
    path="/business-case",
    operation_id="api_business_case"
)
async def api_business_case(
    a: str = Query(..., alias="a"),
    t: int = Query(..., alias="t"),
    n: str = Query(..., alias="n"),
    case: str = Query(..., alias="case")
):
    """
    获取业务用例指令集。

    根据 `case` 参数返回一组命令，用于客户端执行流程配置。
    """

    return await stencil_case(a, t, n, case)


if __name__ == '__main__':
    pass
