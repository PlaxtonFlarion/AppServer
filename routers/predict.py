from loguru import logger
from fastapi import (
    APIRouter, Request, Header, Query
)
from services import loaders

router = APIRouter(tags=["Predict"])


@router.get(path="/proxy-predict")
async def proxy_predict(
    request: "Request",
    x_app_region: str = Header(..., alias="X-App-Region"),
    x_app_version: str = Header(..., alias="X-App-Version"),
    a: str = Query(..., alias="a"),
    t: int = Query(..., alias="t"),
    n: str = Query(..., alias="n")
):
    """
    代理推理请求接口。

    将客户端请求转发至 Modal/GPU 模型服务，支持 Token 校验。
    """
    logger.info(f"predict request: {request.url}")

    return await loaders.resolve_proxy_predict(
        x_app_region, x_app_version, a, t, n, request.app.state.cache
    )


if __name__ == '__main__':
    pass
