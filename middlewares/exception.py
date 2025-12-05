#  _____                    _   _
# | ____|_  _____ ___ _ __ | |_(_) ___  _ __
# |  _| \ \/ / __/ _ \ '_ \| __| |/ _ \| '_ \
# | |___ >  < (_|  __/ |_) | |_| | (_) | | | |
# |_____/_/\_\___\___| .__/ \__|_|\___/|_| |_|
#                    |_|
#

import uuid
import typing
from loguru import logger
from fastapi import (
    Request, HTTPException
)
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


async def exception_middleware(
    request   : "Request",
    call_next : "typing.Callable"
) -> "typing.Any":
    """全局异常中间件"""

    # 保证 trace_id 存在（防止没有 trace 中间件时报错）
    trace_id = getattr(request.state, "trace_id", str(uuid.uuid4()))
    request.state.trace_id = trace_id

    try:
        return await call_next(request)
    except HTTPException as e:
        # 自定义处理 HTTPException
        logger.warning(
            f"[{trace_id}] ⚠️ HTTPException {e.status_code}"
            f"{request.method} {request.url.path} → {e.detail}"
        )
        return JSONResponse(
            content={
                "error"    : e.detail,
                "type"     : "HTTPException",
                "trace_id" : trace_id
            },
            status_code=e.status_code
        )

    except RequestValidationError as e:
        # 参数验证异常（Query / Body / Header）
        logger.warning(
            f"[{trace_id}] ⚠️ ValidationError {request.method} "
            f"{request.url.path} → {e.errors()}"
        )
        return JSONResponse(
            content={
                "error"    : "validation error",
                "details"  : e.errors(),
                "type"     : "RequestValidationError",
                "trace_id" : trace_id
            },
            status_code=422
        )

    except Exception as e:
        # 所有未处理的异常
        logger.exception(
            f"[{trace_id}] ❌ Unhandled Exception in {request.method} {request.url.path}: {e}"
        )
        return JSONResponse(
            content={
                "error"    : "internal server error",
                "details"  : str(e),
                "type"     : e.__class__.__name__,
                "trace_id" : trace_id
            },
            status_code=500
        )


if __name__ == '__main__':
    pass
