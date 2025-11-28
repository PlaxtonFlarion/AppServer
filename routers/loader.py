from loguru import logger
from fastapi import (
    APIRouter, Request, Header, Query
)
from services import loaders

router = APIRouter(tags=["Config"])


@router.get(path="/global-configuration")
async def global_configuration(
    request: "Request",
    x_app_region: str = Header(..., alias="X-App-Region"),
    x_app_version: str = Header(..., alias="X-App-Version"),
    a: str = Query(..., alias="a"),
    t: int = Query(..., alias="t"),
    n: str = Query(..., alias="n")
):
    """
    获取全局配置。

    通过签名参数校验后，返回远程全局配置中心配置结果。
    """
    logger.info(f"configuration request: {request.url}")

    return await loaders.resolve_configuration(
        x_app_region, x_app_version, a, t, n, request.app.state.cache
    )


@router.get(path="/bootstrap")
async def bootstrap(
    request: "Request",
    x_app_region: str = Header(..., alias="X-App-Region"),
    x_app_version: str = Header(..., alias="X-App-Version"),
    a: str = Query(..., alias="a"),
    t: int = Query(..., alias="t"),
    n: str = Query(..., alias="n")
):
    """
    客户端初始化配置接口。

    返回启动参数、区域设置、初始模板与缓存控制信息。
    """
    logger.info(f"bootstrap request: {request.url}")

    await request.app.state.cache.enforce_rate_limit(request)

    return await loaders.resolve_bootstrap(
        x_app_region, x_app_version, a, t, n, request.app.state.cache
    )


if __name__ == '__main__':
    pass
