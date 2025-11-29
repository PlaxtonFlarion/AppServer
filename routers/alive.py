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


@alive_router.api_route(path="/", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def index():
    """首页"""

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

            <a href="/status" class="mt-6 w-full inline-block text-center py-2.5 rounded-lg bg-green-600 hover:bg-green-500 transition font-semibold">
                查看状态 JSON
            </a>

            <footer class="mt-6 text-center text-xs text-gray-500">
                Powered by AppServer · TailwindCSS
            </footer>
        </div>

    </body>
    </html>
    """

    return HTMLResponse(content=html)


@alive_router.get(path="/status", response_class=HTMLResponse)
async def status():
    """状态展示页面"""

    ts = int(time.time())
    dt = time.strftime('%Y-%m-%d %H:%M:%S')

    html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <script src="https://cdn.tailwindcss.com"></script>

        <title>Service Status</title>
    </head>

    <body class="bg-gray-950 min-h-screen text-gray-200 flex items-center justify-center">

        <div class="w-full max-w-lg p-8 bg-gray-900/60 backdrop-blur-lg rounded-2xl border border-gray-700 shadow-xl">

            <h1 class="text-3xl font-bold text-center bg-gradient-to-r from-green-400 to-lime-400 text-transparent bg-clip-text">
                Service Status
            </h1>

            <div class="mt-6 space-y-3 text-center">

                <p class="text-lg font-semibold text-green-400">
                    🟢 服务正常运行
                </p>

                <div class="text-gray-400 text-sm">
                    更新时间：{dt}
                </div>

                <div class="mt-4 bg-gray-800/50 p-4 rounded-lg border border-gray-700 text-left text-sm font-mono">
                    <p><span class="text-gray-500">"ok":</span> <span class="text-green-400">true</span></p>
                    <p><span class="text-gray-500">"timestamp":</span> <span class="text-indigo-400">{ts}</span></p>
                </div>

                <a href="/" class="inline-block mt-6 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 transition">
                    返回首页
                </a>

            </div>

        </div>

    </body>
    </html>
    """

    return HTMLResponse(html)


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
