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
from schemas.errors import (
    AuthorizationError, BizError
)


async def exception_middleware(
    request: Request,
    call_next: typing.Callable
) -> typing.Any:
    """全局异常中间件"""

    trace_id = getattr(request.state, "trace_id", str(uuid.uuid4()))
    request.state.trace_id = trace_id

    try:
        return await call_next(request)

    except (AuthorizationError, BizError) as e:
        logger.error(
            f"[{trace_id}] ⚠️ {e.status_code} {request.method} {request.url.path} → {e.detail}"
        )
        return JSONResponse(
            content={
                "error"    : e.message,
                "details"  : e.detail,
                "type"     : e.__class__.__name__,
                "trace_id" : trace_id
            },
            status_code=e.status_code
        )

    except HTTPException as e:
        logger.error(
            f"[{trace_id}] ⚠️ {e.status_code} {request.method} {request.url.path} → {e.detail}"
        )
        return JSONResponse(
            content={
                "error"    : "http exception",
                "details"  : e.detail,
                "type"     : e.__class__.__name__,
                "trace_id" : trace_id
            },
            status_code=e.status_code
        )

    except RequestValidationError as e:
        logger.error(
            f"[{trace_id}] ⚠️ {request.method} {request.url.path} → {e.errors()}"
        )
        return JSONResponse(
            content={
                "error"    : "validation error",
                "details"  : e.errors(),
                "type"     : e.__class__.__name__,
                "trace_id" : trace_id
            },
            status_code=422
        )

    except Exception as e:
        logger.error(
            f"[{trace_id}] ❌ Unhandled Exception: {e}"
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
