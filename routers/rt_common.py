#   ____                                        ____             _
#  / ___|___  _ __ ___  _ __ ___   ___  _ __   |  _ \ ___  _   _| |_ ___ _ __
# | |   / _ \| '_ ` _ \| '_ ` _ \ / _ \| '_ \  | |_) / _ \| | | | __/ _ \ '__|
# | |__| (_) | | | | | | | | | | | (_) | | | | |  _ < (_) | |_| | ||  __/ |
#  \____\___/|_| |_| |_|_| |_| |_|\___/|_| |_| |_| \_\___/ \__,_|\__\___|_|
#

from fastapi import (
    APIRouter, Request, Query
)
from fastapi.responses import (
    HTMLResponse, FileResponse
)
from services.domain.standard.common import (
    resolve_bootstrap,
    resolve_configuration,
    keepalive_render,
    keepalive_supabase,
    keepalive_modal
)
from utils import (
    const, toolset
)

common_router = APIRouter(tags=["Common"])


@common_router.get(
    path="/",
    response_class=HTMLResponse,
    operation_id="api_index_get",
    include_in_schema=False
)
async def api_index_get():
    """首页 - 健康检查/存活检查"""

    html = toolset.resolve_template("static", "api_index.html")
    with open(html, "r", encoding=const.CHARSET) as f:
        html = f.read()

    return HTMLResponse(html)


@common_router.head(
    path="/",
    operation_id="api_index_head",
    include_in_schema=False
)
async def api_index_head():
    """HEAD请求 - 无Body用于存活检测"""

    return ""


@common_router.get(
    path="/status",
    response_class=HTMLResponse,
    operation_id="api_status",
    include_in_schema=False
)
async def api_status():
    """状态展示页面"""

    html = toolset.resolve_template("static", "api_status.html")
    with open(html, "r", encoding=const.CHARSET) as f:
        html = f.read()

    return HTMLResponse(html)


@common_router.get(
    path="/docs",
    operation_id="api_docs",
    include_in_schema=False
)
async def api_docs() -> HTMLResponse:
    """Render custom API documentation UI."""

    html = toolset.resolve_template("static", "api_docs.html")
    with open(html, "r", encoding=const.CHARSET) as f:
        html = f.read()

    return HTMLResponse(html)


@common_router.get(
    path="/openapi.json",
    operation_id="api_openapi_file",
    include_in_schema=False
)
async def api_openapi_file() -> FileResponse:
    """Export service OpenAPI JSON specification."""

    return FileResponse(path="openapi.json", media_type="application/json")


@common_router.get(
    path="/bootstrap",
    operation_id="api_bootstrap"
)
async def api_bootstrap(
    request: Request,
    a: str = Query(..., alias="a"),
    t: int = Query(..., alias="t"),
    n: str = Query(..., alias="n")
):
    """
    客户端初始化配置接口。

    返回启动参数、区域设置、初始模板与缓存控制信息。
    """

    return await resolve_bootstrap(request, a, t, n)


@common_router.get(
    path="/global-configuration",
    operation_id="api_global_configuration"
)
async def api_global_configuration(
    request: Request,
    a: str = Query(..., alias="a"),
    t: int = Query(..., alias="t"),
    n: str = Query(..., alias="n")
):
    """
    获取全局配置。

    通过签名参数校验后，返回远程全局配置中心配置结果。
    """

    return await resolve_configuration(request, a, t, n)


@common_router.get(
    path="/keepalive-render",
    operation_id="api_keepalive_render"
)
async def api_keepalive_render():
    """
    防 Render 休眠接口。

    通过执行轻度 CPU 运算保持 Render 服务活跃。
    """

    return await keepalive_render()


@common_router.get(
    path="/keepalive-supabase",
    operation_id="api_keepalive_supabase"
)
async def api_keepalive_supabase(
    request: Request
):
    """
    防 Supabase 休眠接口。

    通过轻量 SQL 查询避免 Supabase 因长期无访问进入休眠状态。
    """

    return await keepalive_supabase(request)


@common_router.get(
    path="/keepalive-modal",
    operation_id="api_keepalive_modal"
)
async def api_keepalive_modal():
    """
    定时触发，用于保持 Modal 容器存活状态，防止超时回收。
    """

    return await keepalive_modal()


if __name__ == '__main__':
    pass
