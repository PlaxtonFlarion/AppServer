#   ____                _ _     _       _
#  / ___|__ _ _ __   __| (_) __| | __ _| |_ ___
# | |   / _` | '_ \ / _` | |/ _` |/ _` | __/ _ \
# | |__| (_| | | | | (_| | | (_| | (_| | ||  __/
#  \____\__,_|_| |_|\__,_|_|\__,_|\__,_|\__\___|
#

import time
import httpx
from loguru import logger
from llm.llm_groq import llm_choose_best_candidate
from schemas.heal import (
    HealRequest, HealResponse
)
from services import signature
from services.self_healing import parsing
from vectors.zilliz_store import ZillizStore
from utils import const


class SelfHealing(object):

    def __init__(self):
        self.store: "ZillizStore" = ZillizStore()

    @staticmethod
    async def embedding_batch(url: str, headers: dict, text_list: list) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.request(
                "POST", url, headers=headers, json={"texts": text_list}, timeout=60
            )
            return resp.json()

    @staticmethod
    async def rerank_candidates(url: str, headers: dict, query: str, candidate: list) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.request(
                "POST", url, headers=headers, json={"query": query, "candidate": candidate}, timeout=60
            )
            return resp.json()

    async def heal_element(self, request: "HealRequest", a: str, t: int, n: str) -> "HealResponse":
        app_name, app_desc, *_ = a.lower().strip(), a, t, n

        expire_at = int(time.time()) + 86400
        token     = signature.sign_token(app_desc, expire_at)

        url     = f"https://plaxtonflarion--inference-inferenceservice-embedding.modal.run/"
        headers = {const.TOKEN_FORMAT: token}

        # 解析XML节点
        node_list = parsing.parse_xml_dump(request.page_dump)
        desc_list = [n.ensure_desc() for n in node_list]

        # === 批量向量生成 ===
        embedding_resp = await self.embedding_batch(url, headers, desc_list)
        page_vectors   = embedding_resp["vectors"]  # [[v1], [v2], ...] 维度匹配 node_list

        # 🚀 批量插入向量
        for node, vec in zip(node_list, page_vectors):
            text = node.ensure_desc()
            await self.store.insert(vec, text)  # 插入Zilliz向量库

        # 构建 old locator 文本 embedding
        query     = f"by={request.old_locator.by}, value={request.old_locator.value}"
        query_vec = (await self.embedding_batch(url, headers, [query]))["vectors"][0]

        # --- 向量召回 ---
        retrieved = await self.store.search(query_vec, k=5)

        mapped_candidates: list[dict] = []
        for r in retrieved:
            logger.info(f"召回: {r}")
            for ele in node_list:
                if ele.create_desc() == r["text"]:
                    mapped_candidates.append({
                        "element"      : ele,
                        "text"         : r["text"],
                        "vector_score" : float(r["score"]),
                    })
                    break

        # --- 结果重排 ---
        expire_at = int(time.time()) + 86400
        token     = signature.sign_token(app_desc, expire_at)

        url     = f"https://plaxtonflarion--inference-inferenceservice-rerank.modal.run/"
        headers = {const.TOKEN_FORMAT: token}

        candidate = [c["text"] for c in mapped_candidates]

        rerank_resp   = await self.rerank_candidates(url, headers, query, candidate)
        rerank_scores = rerank_resp["scores"]

        for c, s in zip(mapped_candidates, rerank_scores):
            c["rerank_score"] = float(s)

        # --- 融合得分 ---
        alpha = 0.2  # 20% 用向量召回，80% 用 CrossEncoder
        for c in mapped_candidates:
            c["final_score"] = alpha * c["vector_score"] + (1 - alpha) * c["rerank_score"]

        # --- Stage 3：取 top-3 ---
        top_candidates = sorted(mapped_candidates, key=lambda x: x["final_score"], reverse=True)[:3]

        # 5) LLM 选择最佳
        decision = await llm_choose_best_candidate(request.old_locator, top_candidates)
        index    = decision["index"]
        reason   = decision["reason"]
        logger.info(f"LLM 选择最佳: {decision}")

        if index < 0 or index >= len(top_candidates):
            return HealResponse(
                healed=False,
                confidence=0.0,
                new_locator=None,
                details={
                    "reason"     : reason,
                    "candidates" : top_candidates
                }
            )

        chosen     = top_candidates[index]
        element    = chosen["element"]
        confidence = chosen["final_score"]

        new_by    = "id" if element.resource_id else "text"
        new_value = element.resource_id or element.text or ""

        return HealResponse(
            healed=True,
            confidence=confidence,
            new_locator={"by": new_by, "value": new_value},
            details={
                "reason"     : reason,
                "candidates" : top_candidates,
            }
        )


if __name__ == '__main__':
    pass
