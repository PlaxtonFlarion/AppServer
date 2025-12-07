#  _   _            _ _
# | | | | ___  __ _| (_)_ __   __ _
# | |_| |/ _ \/ _` | | | '_ \ / _` |
# |  _  |  __/ (_| | | | | | | (_| |
# |_| |_|\___|\__,_|_|_|_| |_|\__, |
#                             |___/
#

from fastapi import (
    APIRouter, Request
)
from schemas.cognitive import (
    HealRequest, HealResponse
)
from services.domain.self_healing.candidate import heal_element

healing_router = APIRouter(tags=["Healing"])


@healing_router.post(
    path="/healing",
    response_model=HealResponse,
    operation_id="healing"
)
async def healing(
    req: HealRequest,
    request: Request
):
    """
    UI 元素自愈接口

    基于语义相似度自动寻找最可能的新控件，实现定位修复。
    """

    return await heal_element(req, request)


if __name__ == '__main__':
    pass
