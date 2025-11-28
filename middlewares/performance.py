import time
import typing
from loguru import logger
from fastapi import Request


async def performance_middleware(
    request: "Request",
    call_next: typing.Callable
) -> typing.Callable:
    """
    性能耗时中间件
    """

    start    = time.time()
    response = await call_next(request)
    cost     = round((time.time() - start) * 1000, 2)

    logger.info(f"[{request.state.trace_id}] {request.url.path} {cost}ms")
    response.headers["X-Process-Time"] = str(cost)

    return response


if __name__ == '__main__':
    pass
