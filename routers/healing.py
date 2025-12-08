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
from fastapi.responses import StreamingResponse
from schemas.cognitive import (
    HealRequest, HealResponse
)
from services.domain.self_heal.decision import Decision

healing_router = APIRouter(tags=["Healing"])


@healing_router.post(
    path="/self-heal",
    response_model=HealResponse,
    operation_id="self_heal"
)
async def self_heal(
    req: HealRequest,
    request: Request
):
    """
    UI 元素自愈接口

    基于语义相似度自动寻找最可能的新控件，实现定位修复。
    """

    return await Decision(req, request).heal_element()


@healing_router.post(
    path="/self-heal-stream",
    response_model=StreamingResponse,
    operation_id="self_heal_stream"
)
async def healing_stream(
    req: HealRequest,
    request: Request
):

    return StreamingResponse(
        Decision(req, request).heal_element_stream(), media_type="text/plain"
    )


if __name__ == '__main__':
    pass
