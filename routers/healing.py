#  _   _            _ _               ____             _
# | | | | ___  __ _| (_)_ __   __ _  |  _ \ ___  _   _| |_ ___ _ __
# | |_| |/ _ \/ _` | | | '_ \ / _` | | |_) / _ \| | | | __/ _ \ '__|
# |  _  |  __/ (_| | | | | | | (_| | |  _ < (_) | |_| | ||  __/ |
# |_| |_|\___|\__,_|_|_|_| |_|\__, | |_| \_\___/ \__,_|\__\___|_|
#                             |___/
#

from fastapi import APIRouter
from schemas.heal import HealRequest
from services.self_healing.candidate import SelfHealing

healing_router = APIRouter(tags=["Healing"])


@healing_router.post(path="/healing")
async def healing(
    req: "HealRequest",
    a: str,
    t: int,
    n: str
):
    """
    UI 元素自愈接口

    基于语义相似度自动寻找最可能的新控件，实现定位修复。
    """

    self_healing = SelfHealing()
    return await self_healing.heal_element(req, a, t, n)


if __name__ == '__main__':
    pass
