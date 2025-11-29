#     _    _ _             ____             _
#    / \  | (_)_   _____  |  _ \ ___  _   _| |_ ___ _ __
#   / _ \ | | \ \ / / _ \ | |_) / _ \| | | | __/ _ \ '__|
#  / ___ \| | |\ V /  __/ |  _ < (_) | |_| | ||  __/ |
# /_/   \_\_|_| \_/ \___| |_| \_\___/ \__,_|\__\___|_|
#

import time
from fastapi import (
    APIRouter, Query
)
from fastapi.responses import HTMLResponse
from services import keep_alive

alive_router = APIRouter(tags=["Alive"])


@alive_router.api_route(path="/", response_class=HTMLResponse)
async def index():
    """
    Tailwind CSS 美化首页
    """

    html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />

        <!-- Tailwind CSS CDN -->
        <script src="https://cdn.tailwindcss.com"></script>

        <title>App Server Status</title>

        <style>
            @keyframes fadeIn {{
                0% {{ opacity: 0; transform: translateY(10px); }}
                100% {{ opacity: 1; transform: translateY(0); }}
            }}

            @keyframes glow {{
                0% {{ filter: drop-shadow(0 0 2px #60a5fa); }}
                50% {{ filter: drop-shadow(0 0 12px #a78bfa); }}
                100% {{ filter: drop-shadow(0 0 2px #60a5fa); }}
            }}
        </style>
    </head>

    <body class="bg-gray-950 min-h-screen flex items-center justify-center text-gray-200">

        <div class="w-full max-w-md p-8 bg-gray-900/60 backdrop-blur-lg rounded-2xl border border-gray-700 shadow-xl animate-[fadeIn_0.8s_ease-out]">

            <h1 class="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent text-center animate-[glow_4s_infinite]">
                App Server is Live
            </h1>

            <div class="mt-4 text-center text-green-400 font-semibold text-lg">
                🟢 服务运行中
            </div>

            <div class="mt-2 text-center text-gray-400 text-sm">
                {time.strftime('%Y-%m-%d %H:%M:%S')}
            </div>

            <a href="/status"
               class="mt-6 w-full inline-block text-center py-2.5 rounded-lg
                      bg-green-600 hover:bg-green-500 transition font-semibold">
                查看状态 JSON
            </a>

            <footer class="mt-6 text-center text-xs text-gray-500">
                Powered by FastAPI · TailwindCSS
            </footer>
        </div>

    </body>
    </html>
    """

    return HTMLResponse(content=html)


@alive_router.get(path="/status")
async def status():
    """
    简单状态接口。

    用于快速确认服务可达性，返回固定 OK 响应。
    """

    return {"ok": True, "timestamp": int(time.time())}


@alive_router.get(path="/keep-render-alive")
async def keep_render_alive():
    """
    防 Render 休眠接口。

    通过执行轻度 CPU 运算保持 Render 服务活跃。
    """

    return await keep_alive.cpu_heavy_work()


@alive_router.get(path="/keep-supabase-alive")
async def keep_supabase_alive():
    """
    防 Supabase 休眠接口。

    通过轻量 SQL 查询避免 Supabase 因长期无访问进入休眠状态。
    """

    return await keep_alive.single_query()


@alive_router.get(path="/keep-modal-alive")
async def keep_modal_alive(
    a: str = Query(..., alias="a"),
    t: int = Query(..., alias="t"),
    n: str = Query(..., alias="n")
):
    """
    定时触发，用于保持 Modal 容器存活状态，防止超时回收。
    """

    return await keep_alive.predict_warmup(a, t, n)


if __name__ == '__main__':
    pass
