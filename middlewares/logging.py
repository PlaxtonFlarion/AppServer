#  _                      _               __  __ _     _     _ _
# | |    ___   __ _  __ _(_)_ __   __ _  |  \/  (_) __| | __| | | _____      ____ _ _ __ ___
# | |   / _ \ / _` |/ _` | | '_ \ / _` | | |\/| | |/ _` |/ _` | |/ _ \ \ /\ / / _` | '__/ _ \
# | |__| (_) | (_| | (_| | | | | | (_| | | |  | | | (_| | (_| | |  __/\ V  V / (_| | | |  __/
# |_____\___/ \__, |\__, |_|_| |_|\__, | |_|  |_|_|\__,_|\__,_|_|\___| \_/\_/ \__,_|_|  \___|
#             |___/ |___/         |___/
#

import typing
from loguru import logger
from fastapi import Request


async def log_requests(request: "Request", call_next: "typing.Callable") -> "typing.Any":
    """请求日志中间件"""

    logger.info(f"-> {request.method} {request.url}")

    response = await call_next(request)

    logger.info(f"<- {response.status_code} {request.url}")

    return response


if __name__ == '__main__':
    pass
