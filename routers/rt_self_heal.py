#  ____       _  __   _   _            _   ____             _
# / ___|  ___| |/ _| | | | | ___  __ _| | |  _ \ ___  _   _| |_ ___ _ __
# \___ \ / _ \ | |_  | |_| |/ _ \/ _` | | | |_) / _ \| | | | __/ _ \ '__|
#  ___) |  __/ |  _| |  _  |  __/ (_| | | |  _ < (_) | |_| | ||  __/ |
# |____/ \___|_|_|   |_| |_|\___|\__,_|_| |_| \_\___/ \__,_|\__\___|_|
#

from fastapi import (
    APIRouter, Request
)
from fastapi.responses import StreamingResponse
from schemas.cognitive import (
    HealRequest, HealResponse
)
from services.domain.self_heal.decision import Decision

self_heal_router = APIRouter(tags=["SelfHeal"])


@self_heal_router.post(
    path="/self-heal",
    response_model=HealResponse,
    operation_id="api_self_heal"
)
async def api_self_heal(
    req: HealRequest,
    request: Request
):
    """
    UI 元素自愈接口，一次性返回最终结果

    基于语义相似度自动寻找最可能的新控件，实现定位修复。
    """

    return await Decision(req, request).heal_element()


@self_heal_router.post(
    path="/self-heal-stream",
    response_class=StreamingResponse,
    operation_id="api_self_heal_stream"
)
async def api_self_heal_stream(
    req: HealRequest,
    request: Request
):
    """
    UI 元素自愈 — 流式返回执行日志与最终决策

    StreamingResponse 文本流输出:
        [1] 解析节点 …
        [2] 生成向量 …
        [3] 召回 …
        [4] 重排 …
        [完成] 返回 JSON 结果
    """

    return StreamingResponse(
        Decision(req, request).heal_element_stream(),
        media_type="text/plain; charset=utf-8"
    )


if __name__ == '__main__':
    pass
