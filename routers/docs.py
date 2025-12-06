#  ____
# |  _ \  ___   ___ ___
# | | | |/ _ \ / __/ __|
# | |_| | (_) | (__\__ \
# |____/ \___/ \___|___/
#

from fastapi import APIRouter
from fastapi.responses import (
    FileResponse, HTMLResponse
)
from utils import (
    const, toolset
)

docs_router = APIRouter(tags=["Docs"])


@docs_router.get(
    path="/openapi.json",
    operation_id="openapi_file",
    include_in_schema=False
)
async def openapi_file() -> FileResponse:
    """
    Export service OpenAPI JSON specification.

    用于返回当前服务的 `openapi.json` 文档定义文件，多用于文档渲染、SDK生成、
    API集成和测试工具导入等场景。

    Returns
    -------
    FileResponse
        返回 OpenAPI JSON 规范文件，可直接下载或用于前端文档加载。

    Notes
    -----
    - `include_in_schema=False`，该接口不会显示在自动文档中。
    - 可与自定义文档页 `/docs` 搭配使用，用于前端动态渲染 API 信息。
    - 对外部署时如包含敏感定义，建议配合权限/鉴权保护。
    """

    return FileResponse(path="openapi.json", media_type="application/json")


@docs_router.get(
    path="/docs",
    operation_id="custom_docs",
    include_in_schema=False
)
async def custom_docs() -> HTMLResponse:
    """
    Render custom API documentation UI.

    自定义文档页加载接口，用于返回本地静态文档页面，通过前端脚本动态请求
    `/openapi.json` 以生成可视化的 API 文档（非 Swagger 默认样式）。

    Returns
    -------
    HTMLResponse
        渲染后的 HTML 文档页面，包含自定义 API 展示界面。

    Notes
    -----
    - 支持完全自定义前端文档 UI，可展示 Schema、示例、请求模型等信息。
    - 可扩展功能包括交互式调试、JSON编辑器、代码生成、深色/浅色主题等。
    - 文档读取路径为 `static/api_docs.html`，可按需替换页面内容。
    """

    html = toolset.resolve_template("static", "api_docs.html")
    with open(html, "r", encoding=const.CHARSET) as f:
        html = f.read()

    return HTMLResponse(html)


if __name__ == '__main__':
    pass
