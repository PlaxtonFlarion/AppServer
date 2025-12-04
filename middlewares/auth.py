#     _         _   _       __  __ _     _     _ _
#    / \  _   _| |_| |__   |  \/  (_) __| | __| | | _____      ____ _ _ __ ___
#   / _ \| | | | __| '_ \  | |\/| | |/ _` |/ _` | |/ _ \ \ /\ / / _` | '__/ _ \
#  / ___ \ |_| | |_| | | | | |  | | | (_| | (_| | |  __/\ V  V / (_| | | |  __/
# /_/   \_\__,_|\__|_| |_| |_|  |_|_|\__,_|\__,_|_|\___| \_/\_/ \__,_|_|  \___|
#

import typing
from loguru import logger
from fastapi import Request
from fastapi.responses import JSONResponse
from services import signature


async def jwt_auth_middleware(request: "Request", call_next: "typing.Callable") -> "typing.Any":
    """鉴权中间件"""

    if request.url.path in {
        "/", "/status", "/keep-render-alive", "/keep-supabase-alive", "/keep-modal-alive", "healing"
    }: return await call_next(request)

    x_app_id      = request.headers.get("X-App-ID")
    x_app_token   = request.headers.get("X-App-Token")
    x_app_region  = request.headers.get("X-App-Region")
    x_app_version = request.headers.get("X-App-Version")

    if not x_app_id or not x_app_token:
        return JSONResponse(
            content={
                "error"    : "missing headers",
                "trace_id" : getattr(request.state, "trace_id", None)
            },
            status_code=401
        )

    try:
        payload = signature.verify_jwt(x_app_id, x_app_token)
    except Exception as e:
        logger.warning(f"[{getattr(request.state, 'trace_id', '-')}] ❌ JWT error: {e}")
        return JSONResponse(
            content={
                "error"    : str(e),
                "trace_id" : getattr(request.state, "trace_id", None)
            },
            status_code=403
        )

    request.state.jwt_payload   = payload
    request.state.x_app_id      = x_app_id
    request.state.x_app_token   = x_app_token
    request.state.x_app_region  = x_app_region
    request.state.x_app_version = x_app_version

    return await call_next(request)


if __name__ == '__main__':
    pass
