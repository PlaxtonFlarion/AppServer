#  _                      _
# | |    ___   __ _  __ _(_)_ __   __ _
# | |   / _ \ / _` |/ _` | | '_ \ / _` |
# | |__| (_) | (_| | (_| | | | | | (_| |
# |_____\___/ \__, |\__, |_|_| |_|\__, |
#             |___/ |___/         |___/
#

import typing
from loguru import logger
from fastapi import Request


async def logging_middleware(
    request: Request,
    call_next: typing.Callable
) -> typing.Any:
    """请求日志中间件"""

    logger.info(f"-> {request.method} {request.url}")

    response = await call_next(request)

    logger.info(f"<- {response.status_code} {request.url}")

    return response


if __name__ == '__main__':
    pass
