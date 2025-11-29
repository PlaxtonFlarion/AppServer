#  ____            __                                             __  __ _     _     _ _
# |  _ \ ___ _ __ / _| ___  _ __ _ __ ___   __ _ _ __   ___ ___  |  \/  (_) __| | __| | | _____      ____ _ _ __ ___
# | |_) / _ \ '__| |_ / _ \| '__| '_ ` _ \ / _` | '_ \ / __/ _ \ | |\/| | |/ _` |/ _` | |/ _ \ \ /\ / / _` | '__/ _ \
# |  __/  __/ |  |  _| (_) | |  | | | | | | (_| | | | | (_|  __/ | |  | | | (_| | (_| | |  __/\ V  V / (_| | | |  __/
# |_|   \___|_|  |_|  \___/|_|  |_| |_| |_|\__,_|_| |_|\___\___| |_|  |_|_|\__,_|\__,_|_|\___| \_/\_/ \__,_|_|  \___|
#

import time
import typing
from loguru import logger
from fastapi import Request


async def performance_middleware(request: "Request", call_next: "typing.Callable") -> "typing.Any":
    """性能耗时中间件"""

    start    = time.time()
    response = await call_next(request)
    cost     = round((time.time() - start) * 1000, 2)

    logger.info(f"[{request.state.trace_id}] {request.url.path} {cost}ms")
    response.headers["X-Process-Time"] = str(cost)

    return response


if __name__ == '__main__':
    pass
