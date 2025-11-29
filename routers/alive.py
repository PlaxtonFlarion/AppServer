#     _    _ _             ____             _
#    / \  | (_)_   _____  |  _ \ ___  _   _| |_ ___ _ __
#   / _ \ | | \ \ / / _ \ | |_) / _ \| | | | __/ _ \ '__|
#  / ___ \| | |\ V /  __/ |  _ < (_) | |_| | ||  __/ |
# /_/   \_\_|_| \_/ \___| |_| \_\___/ \__,_|\__\___|_|
#

from fastapi import APIRouter
from services import keep_alive

alive_router = APIRouter(tags=["Alive"])


@alive_router.api_route(path="/", methods=["GET", "HEAD"])
async def index():
    """
    健康检查接口。

    返回服务状态标识信息，常用于存活性探测或 Render 运行时检测。
    """

    return {"message": "App Server is live"}


@alive_router.get(path="/status")
async def status():
    """
    简单状态接口。

    用于快速确认服务可达性，返回固定 OK 响应。
    """

    return {"ok": True}


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
async def keep_modal_alive():
    """
    定时触发，用于保持 Modal 容器存活状态，防止超时回收。
    """

    return await keep_alive.predict_warmup()


if __name__ == '__main__':
    pass
