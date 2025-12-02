#   ____
#  / ___|___  _ __ ___
# | |   / _ \| '__/ _ \
# | |__| (_) | | |  __/
#  \____\___/|_|  \___|
#

from services.self_healing.candidate import generate_candidates
from services.self_healing.scoring   import score_candidates
from services.self_healing.decision  import make_decision
from services.self_healing.baseline  import BaselineStore
from schemas import heal


class SelfHealingCore(object):

    def __init__(self):
        self.baseline: "BaselineStore" = BaselineStore()

    async def heal(self, req: "heal.HealRequest") -> dict:
        # 1) 尝试拉取历史基线（可用于增强评分）
        page_baseline = await self.baseline.get_page_baseline(req.app_id, req.page_id)

        # 2) 候选生成
        candidates = list(generate_candidates(req.old_locator, req.elements))
        if not candidates:
            return {
                "healed"      : False,
                "confidence"  : 0.0,
                "new_locator" : None,
                "details"     : [],
                "reason"      : "No candidates found"
            }

        # 3) 评分
        scored = await score_candidates(req, candidates)

        # 4) 选最佳
        healed, confidence, best = make_decision(scored)

        if not healed or not best:
            return {
                "healed"      : False,
                "confidence"  : confidence,
                "new_locator" : None,
                "details"     : scored,
                "reason"      : "Confidence too low"
            }

        # best candidate 数据
        element = best["candidate"]   # 真正的控件信息 dict

        # 5) 选择 by/value（智能选择）
        new_locator_by, new_locator_value = self.infer_best_locator(element)

        new_locator = {
            "by"    : new_locator_by,
            "value" : new_locator_value,
        }

        # 6) 写入基线
        await self.baseline.update_baseline(
            app_id=req.app_id,
            page_id=req.page_id,
            old_locator=req.old_locator,
            new_locator=new_locator,
            extra_meta={"confidence": confidence},
        )

        # 7) 输出
        return {
            "healed"      : True,
            "confidence"  : confidence,
            "new_locator" : new_locator,
            "details"     : scored,
        }

    @staticmethod
    def infer_best_locator(element: dict) -> tuple[str, str]:
        """
        智能推断最靠谱的 locator 策略
        优先级：
        1. resource_id
        2. content_desc
        3. text
        4. class + bounds
        """

        if rid := element.get("resource_id"):
            return "id", rid

        if desc := element.get("content_desc"):
            return "desc", desc

        if text := element.get("text"):
            return "text", text

        # 最后兜底
        cls    = element.get("class_name", "View")
        bounds = element.get("bounds", [])

        return "bounds", f"{cls}:{bounds}"


if __name__ == '__main__':
    pass
