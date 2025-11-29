#  _____                    _   _               __  __ _     _     _ _
# | ____|_  _____ ___ _ __ | |_(_) ___  _ __   |  \/  (_) __| | __| | | _____      ____ _ _ __ ___
# |  _| \ \/ / __/ _ \ '_ \| __| |/ _ \| '_ \  | |\/| | |/ _` |/ _` | |/ _ \ \ /\ / / _` | '__/ _ \
# | |___ >  < (_|  __/ |_) | |_| | (_) | | | | | |  | | | (_| | (_| | |  __/\ V  V / (_| | | |  __/
# |_____/_/\_\___\___| .__/ \__|_|\___/|_| |_| |_|  |_|_|\__,_|\__,_|_|\___| \_/\_/ \__,_|_|  \___|
#                    |_|
#

import typing
from loguru import logger
from fastapi import Request
from fastapi.responses import JSONResponse


async def exception_middleware(request: "Request", call_next: "typing.Callable") -> "typing.Any":
    """全局异常中间件"""

    try:
        return await call_next(request)
    except Exception as e:
        logger.exception(f"[{request.state.trace_id}] ❌ Unhandled Exception: {e}")
        return JSONResponse(
            content={
                "error"    : "internal error",
                "details"  : str(e),
                "trace_id" : request.state.trace_id
            },
            status_code=500
        )


if __name__ == '__main__':
    pass
