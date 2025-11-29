#     _    _ _             ____             _
#    / \  | (_)_   _____  |  _ \ ___  _   _| |_ ___ _ __
#   / _ \ | | \ \ / / _ \ | |_) / _ \| | | | __/ _ \ '__|
#  / ___ \| | |\ V /  __/ |  _ < (_) | |_| | ||  __/ |
# /_/   \_\_|_| \_/ \___| |_| \_\___/ \__,_|\__\___|_|
#

import time
from fastapi import (
    APIRouter, Query, Request
)
from fastapi.responses import HTMLResponse
from services import keep_alive

alive_router = APIRouter(tags=["Alive"])


@alive_router.api_route(path="/", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def index():
    """首页"""

    title       = f"App Server Status"
    subtitle    = f"App Server is Live"
    display     = f"🟢 服务运行中"
    update_time = f"{time.strftime('%Y-%m-%d %H:%M:%S')}"
    view_state  = f"查看状态 JSON"
    fx_desc     = f"Framix"
    fx_link     = f"https://github.com/PlaxtonFlarion/SoftwareCenter/blob/main/Assets/{fx_desc}/README.md"
    mx_desc     = f"Memrix"
    mx_link     = f"https://github.com/PlaxtonFlarion/SoftwareCenter/blob/main/Assets/{mx_desc}/README.md"
    footer      = f"Powered by AppServerX · TailwindCSS"

    html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />

        <!-- Tailwind CSS CDN -->
        <script src="https://cdn.tailwindcss.com"></script>

        <title>{title}</title>

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

            /* 3D 卡片核心样式 */
            .tilt-card {{
                transform-style: preserve-3d;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
                cursor: pointer;
                position: relative;
            }}
            .tilt-card::after {{
                content: "";
                position: absolute;
                inset: 0;
                border-radius: 12px;
                background: radial-gradient(circle at var(--x,50%) var(--y,50%), rgba(255,255,255,0.08), transparent 60%);
                transition: opacity 0.2s ease;
                opacity: 0;
            }}
            .tilt-card:hover::after {{
                opacity: 1;
            }}
            .tilt-card:active {{
                transform: scale(0.97) rotateX(0deg) rotateY(0deg) !important;
            }}
        </style>

    </head>

    <body class="bg-gray-950 min-h-screen flex items-center justify-center text-gray-200">

        <div class="w-full max-w-md p-8 bg-gray-900/60 backdrop-blur-lg rounded-2xl border border-gray-700 shadow-xl animate-[fadeIn_0.8s_ease-out]">

            <h1 class="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent text-center animate-[glow_4s_infinite]">
                {subtitle}
            </h1>

            <div class="mt-4 text-center text-green-400 font-semibold text-lg">
                {display}
            </div>

            <div class="mt-2 text-center text-gray-400 text-sm">
                {update_time}
            </div>

            <!-- 查看状态 -->
            <a href="/status" class="mt-6 w-full inline-block text-center py-2.5 rounded-lg bg-green-600 hover:bg-green-500 transition font-semibold">
                {view_state}
            </a>

            <!-- 3D 视差卡片 -->
            <div class="mt-8 grid grid-cols-2 gap-4 select-none">

                <!-- {fx_desc} 3D 卡片 -->
                <a href="{fx_link}" target="_blank" class="tilt-card p-4 rounded-xl border border-blue-600/40 bg-blue-600/10 hover:bg-blue-600/20 transition text-center font-semibold text-blue-300">
                    {fx_desc}
                </a>

                <!-- {mx_desc} 3D 卡片 -->
                <a href="{mx_link}" target="_blank" class="tilt-card p-4 rounded-xl border border-purple-600/40 bg-purple-600/10 hover:bg-purple-600/20 transition text-center font-semibold text-purple-300">
                    {mx_desc}
                </a>

            </div>

            <footer class="mt-6 text-center text-xs text-gray-500">
                {footer}
            </footer>
        </div>

        <!-- 3D 交互脚本 -->
        <script>
            document.querySelectorAll('.tilt-card').forEach(card => {{
                card.addEventListener('mousemove', e => {{
                    const rect = card.getBoundingClientRect();
                    const x = e.clientX - rect.left;
                    const y = e.clientY - rect.top;
                    const midX = rect.width / 2;
                    const midY = rect.height / 2;

                    const rotateX = (y - midY) / 12;
                    const rotateY = (midX - x) / 12;

                    card.style.transform = `rotateX(${{rotateX}}deg) rotateY(${{rotateY}}deg)`;

                    card.style.setProperty('--x', `${{(x / rect.width) * 100}}%`);
                    card.style.setProperty('--y', `${{(y / rect.height) * 100}}%`);
                }});

                card.addEventListener('mouseleave', () => {{
                    card.style.transform = 'rotateX(0deg) rotateY(0deg)';
                }});
            }});
        </script>

    </body>
    </html>
    """

    return HTMLResponse(content=html)


@alive_router.get(path="/status", response_class=HTMLResponse)
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


@alive_router.get(path="/keep-render-alive")
async def keep_render_alive():
    """
    防 Render 休眠接口。

    通过执行轻度 CPU 运算保持 Render 服务活跃。
    """

    return await keep_alive.cpu_heavy_work()


@alive_router.get(path="/keep-supabase-alive")
async def keep_supabase_alive(request: "Request"):
    """
    防 Supabase 休眠接口。

    通过轻量 SQL 查询避免 Supabase 因长期无访问进入休眠状态。
    """

    return await keep_alive.single_query(request)


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
