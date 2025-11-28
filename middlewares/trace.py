import uuid
import typing
from loguru import logger
from fastapi import Request


async def trace_middleware(
    request: "Request",
    call_next: typing.Callable
) -> typing.Any:
    """
    Trace-ID 中间件
    """

    request.state.trace_id = (trace_id := str(uuid.uuid4()))
    logger.info(f"[{trace_id}] → Incoming {request.method} {request.url}")

    response = await call_next(request)

    response.headers["X-Trace-ID"] = trace_id
    logger.info(f"[{trace_id}] ← Outgoing {response.status_code}")

    return response


if __name__ == '__main__':
    pass
