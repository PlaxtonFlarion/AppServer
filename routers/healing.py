#  _   _            _ _               ____             _
# | | | | ___  __ _| (_)_ __   __ _  |  _ \ ___  _   _| |_ ___ _ __
# | |_| |/ _ \/ _` | | | '_ \ / _` | | |_) / _ \| | | | __/ _ \ '__|
# |  _  |  __/ (_| | | | | | | (_| | |  _ < (_) | |_| | ||  __/ |
# |_| |_|\___|\__,_|_|_|_| |_|\__, | |_| \_\___/ \__,_|\__\___|_|
#                             |___/
#

from loguru import logger
from fastapi import APIRouter
from schemas.heal import HealRequest
from services.self_healing.candidate import SelfHealingCore

healing_router = APIRouter(tags=["Healing"])


@healing_router.post(path="/healing")
async def healing(
    req: "HealRequest",
    a: str,
    t: int,
    n: str
):

    logger.info(f"healing request: {req}")

    self_healing_core = SelfHealingCore()
    return await self_healing_core.heal_element(req, a, t, n)


if __name__ == '__main__':
    pass
