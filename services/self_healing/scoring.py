#  ____                 _
# / ___|  ___ ___  _ __(_)_ __   __ _
# \___ \ / __/ _ \| '__| | '_ \ / _` |
#  ___) | (_| (_) | |  | | | | | (_| |
# |____/ \___\___/|_|  |_|_| |_|\__, |
#                               |___/
#

import typing
from schemas import heal
from services.self_healing import similarity

# 默认权重（未来可用 Baseline / 配置平台动态调整）
WEIGHTS = {
    "id": 0.5,
    "text": 0.3,
    "layout": 0.2,
}


async def score_candidates(
    req: "heal.HealRequest",
    candidates: list[dict]
) -> list[dict[str, typing.Any]]:

    old        = req.old_locator
    ctx_text   = req.context.get("text", "")
    ctx_bounds = req.context.get("bounds")

    scored = []

    for c in candidates:
        # 这些字段都要有容错，否则前端空字符串会让评分爆炸
        c_id     = c.get("resource_id") or ""
        c_text   = c.get("text") or ""
        c_bounds = c.get("bounds")

        s1 = similarity.str_sim(old.value or "", c_id)
        s2 = similarity.str_sim(ctx_text, c_text)
        s3 = similarity.iou(ctx_bounds, c_bounds)

        score = (WEIGHTS["id"] * s1 + WEIGHTS["text"] * s2 + WEIGHTS["layout"] * s3)

        scored.append({
            "candidate" : c,
            "score"     : score,
            "scores"    : {
                "id_score"     : s1,
                "text_score"   : s2,
                "layout_score" : s3,
            }
        })

    # 按分数排序，方便你前端直接取第一个做判断
    scored.sort(key=lambda x: x["score"], reverse=True)

    return scored


if __name__ == '__main__':
    pass
