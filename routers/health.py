from fastapi import APIRouter, Request


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


if __name__ == '__main__':
    pass
