import typing
from loguru import logger
from fastapi import Request
from fastapi.responses import JSONResponse
from services.signature import verify_jwt


async def jwt_auth_middleware(
    request: "Request",
    call_next: typing.Callable,
) -> typing.Any:
    """
    鉴权中间件
    """

    if request.url.path in {"/", "/status"}: return await call_next(request)

    x_app_id    = request.headers.get("X-App-ID")
    x_app_token = request.headers.get("X-App-Token")

    if not x_app_id or not x_app_token:
        return JSONResponse(
            content={
                "error"    : "missing headers",
                "trace_id" : getattr(request.state, "trace_id", None)
            },
            status_code=401,
        )

    # 调用 verify_jwt
    try:
        payload = verify_jwt(x_app_id, x_app_token)
    except Exception as e:
        logger.warning(f"[{getattr(request.state, 'trace_id', '-')}] ❌ JWT error: {e}")
        return JSONResponse(
            content={
                "error"    : str(e),
                "trace_id" : getattr(request.state, "trace_id", None)
            },
            status_code=403,
        )

    # 鉴权成功 → 注入 request.state
    request.state.jwt_payload = payload
    request.state.x_app_id    = x_app_id
    request.state.x_app_token = x_app_token

    # 继续处理请求
    return await call_next(request)


if __name__ == '__main__':
    pass
