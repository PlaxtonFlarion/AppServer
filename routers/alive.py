#     _    _ _
#    / \  | (_)_   _____
#   / _ \ | | \ \ / / _ \
#  / ___ \| | |\ V /  __/
# /_/   \_\_|_| \_/ \___|
#

import time
from fastapi import (
    APIRouter, Query, Request
)
from fastapi.responses import HTMLResponse
from services.domain.standard import keepalive
from utils import (
    const, toolset
)

alive_router = APIRouter(tags=["Alive"])


@alive_router.get(
    path="/",
    response_class=HTMLResponse,
    operation_id="index_get",
    include_in_schema=False
)
async def index_get():
    """首页 - 健康检查/存活检查"""

    html = toolset.resolve_template("static", "api_index.html")
    with open(html, "r", encoding=const.CHARSET) as f:
        html = f.read()

    return HTMLResponse(html)


@alive_router.head(
    path="/",
    operation_id="index_head",
    include_in_schema=False
)
async def index_head():
    """HEAD请求 - 无Body用于存活检测"""

    return ""


@alive_router.get(
    path="/status",
    response_class=HTMLResponse,
    operation_id="status",
    include_in_schema=False
)
async def status():
    """状态展示页面"""

    ts = int(time.time())
    dt = time.strftime('%Y-%m-%d %H:%M:%S')

    title       = f"Service Status"
    display     = f"🟢 服务正常运行"
    update_time = f"更新时间：{dt}"
    back_home   = f"返回首页"

    html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <script src="https://cdn.tailwindcss.com"></script>

        <title>{title}</title>
    </head>

    <body class="bg-gray-950 min-h-screen text-gray-200 flex items-center justify-center">

        <div class="w-full max-w-lg p-8 bg-gray-900/60 backdrop-blur-lg rounded-2xl border border-gray-700 shadow-xl">

            <h1 class="text-3xl font-bold text-center bg-gradient-to-r from-green-400 to-lime-400 text-transparent bg-clip-text">
                {title}
            </h1>

            <div class="mt-6 space-y-3 text-center">

                <p class="text-lg font-semibold text-green-400">
                    {display}
                </p>

                <div class="text-gray-400 text-sm">
                    {update_time}
                </div>

                <div class="mt-4 bg-gray-800/50 p-4 rounded-lg border border-gray-700 text-left text-sm font-mono">
                    <p><span class="text-gray-500">"ok":</span> <span class="text-green-400">true</span></p>
                    <p><span class="text-gray-500">"timestamp":</span> <span class="text-indigo-400">{ts}</span></p>
                </div>

                <a href="/" class="inline-block mt-6 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 transition">
                    {back_home}
                </a>

            </div>

        </div>

    </body>
    </html>
    """

    return HTMLResponse(html)


@alive_router.get(
    path="/keep-render-alive",
    operation_id="keep_render_alive"
)
async def keep_render_alive():
    """
    防 Render 休眠接口。

    通过执行轻度 CPU 运算保持 Render 服务活跃。
    """

    return await keepalive.cpu_heavy_work()


@alive_router.get(
    path="/keep-supabase-alive",
    operation_id="keep_supabase_alive"
)
async def keep_supabase_alive(
    request: Request
):
    """
    防 Supabase 休眠接口。

    通过轻量 SQL 查询避免 Supabase 因长期无访问进入休眠状态。
    """

    return await keepalive.single_query(request)


@alive_router.get(
    path="/keep-modal-alive",
    operation_id="keep_modal_alive"
)
async def keep_modal_alive(
    a: str = Query(..., alias="a"),
    t: int = Query(..., alias="t"),
    n: str = Query(..., alias="n")
):
    """
    定时触发，用于保持 Modal 容器存活状态，防止超时回收。
    """

    return await keepalive.predict_warmup(a, t, n)


if __name__ == '__main__':
    pass
