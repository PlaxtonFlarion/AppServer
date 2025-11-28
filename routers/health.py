from loguru import logger
from fastapi import (
    APIRouter, Request
)
from services import keep_alive

router = APIRouter(tags=["Health"])


@router.api_route(path="/", methods=["GET", "HEAD"])
async def index():
    """
    健康检查接口。

    返回服务状态标识信息，常用于存活性探测或 Render 运行时检测。
    """
    return {"message": "App Server is live"}


@router.get(path="/status")
async def status():
    """
    简单状态接口。

    用于快速确认服务可达性，返回固定 OK 响应。
    """
    return {"ok": True}


@router.get(path="/keep-render-alive")
async def keep_render_alive(
    request: "Request"
):
    """
    防 Render 休眠接口。

    通过执行轻度 CPU 运算保持 Render 服务活跃。
    """
    logger.info(f"keep request: {request.url}")

    return await keep_alive.cpu_heavy_work()


@router.get(path="/keep-supabase-alive")
async def keep_supabase_alive(
    request: "Request"
):
    """
    防 Supabase 休眠接口。

    通过轻量 SQL 查询避免 Supabase 因长期无访问进入休眠状态。
    """
    logger.info(f"keep request: {request.url}")

    return await keep_alive.single_query()


@router.get(path="/keep-modal-alive")
async def keep_modal_alive(
    request: "Request"
):
    """
    定时触发，用于保持 Modal 容器存活状态，防止超时回收。
    """
    logger.info(f"keep request: {request.url}")

    return await keep_alive.predict_warmup()


if __name__ == '__main__':
    pass
