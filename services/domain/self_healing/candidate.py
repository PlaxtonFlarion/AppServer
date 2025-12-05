#   ____                _ _     _       _
#  / ___|__ _ _ __   __| (_) __| | __ _| |_ ___
# | |   / _` | '_ \ / _` | |/ _` |/ _` | __/ _ \
# | |__| (_| | | | | (_| | | (_| | (_| | ||  __/
#  \____\__,_|_| |_|\__,_|_|\__,_|\__,_|\__\___|
#

import time
import httpx
import typing
from loguru import logger
from fastapi import Request
from starlette.responses import JSONResponse

from schemas.cognitive import (
    HealRequest, HealResponse
)
from services.domain.standard import signature
from services.domain.self_healing.parsing import AndroidXmlParser
from services.infrastructure.vector.zilliz import ZillizStore
from services.infrastructure.llm.llm_groq import llm_choose_best_candidate
from utils import const


async def post_embedding(headers: dict, text_list: list) -> dict:
    url = f"https://plaxtonflarion--embedding-embeddingservice-embedding.modal.run/"
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            url, headers=headers, json={"texts": text_list}, timeout=60
        )
        resp.raise_for_status()
        return resp.json()


async def post_rerank(headers: dict, query: str, candidate: list) -> dict:
    url = f"https://plaxtonflarion--embedding-embeddingservice-rerank.modal.run/"
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            url, headers=headers, json={"query": query, "candidate": candidate}, timeout=60
        )
        resp.raise_for_status()
        return resp.json()


async def heal_element(
    req: "HealRequest",
    request: "Request",
    a: str,
    t: int,
    n: str
) -> typing.Union["HealResponse", "JSONResponse"]:

    app_name, app_desc, *_ = a.lower().strip(), a, t, n

    store: "ZillizStore" = request.app.state.store

    expire_at = int(time.time()) + 86400
    token     = signature.sign_token(app_desc, expire_at)
    headers   = {const.TOKEN_FORMAT: token}

    logger.info(f"解析节点")
    node_list = AndroidXmlParser.parse(req.page_dump)
    desc_list = [n.ensure_desc() for n in node_list]

    logger.info(f"向量生成")
    embedding_resp = await post_embedding(headers, desc_list)
    logger.info(f"[[v1], [v2], ...] 维度匹配")
    page_vectors = embedding_resp["vectors"]

    logger.info(f"插入向量")
    for node, vec in zip(node_list, page_vectors):
        await store.insert(vec, node.ensure_desc())

    logger.info(f"构建 old locator 文本 embedding")
    query     = f"by={req.old_locator.by}, value={req.old_locator.value}"
    try:
        query_vec = (await post_embedding(headers, [query]))["vectors"][0]
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

    logger.info(f"向量召回 {(k := 5)}")
    retrieved = await store.search(query_vec, k=k)

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

    # expire_at = int(time.time()) + 86400
    # token     = signature.sign_token(app_desc, expire_at)
    # headers   = {const.TOKEN_FORMAT: token}

    candidate = [c["text"] for c in mapped_candidates]

    logger.info(f"结果重排")
    try:
        rerank_resp = await post_rerank(headers, query, candidate)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

    rerank_scores = rerank_resp["scores"]
    for c, s in zip(mapped_candidates, rerank_scores):
        c["rerank_score"] = float(s)

    logger.info(f"融合得分: 20% 用向量召回，80% 用 CrossEncoder")
    alpha = 0.2
    for c in mapped_candidates:
        c["final_score"] = alpha * c["vector_score"] + (1 - alpha) * c["rerank_score"]

    logger.info(f"取 top-3")
    top_candidates = sorted(mapped_candidates, key=lambda x: x["final_score"], reverse=True)[:3]

    decision = await llm_choose_best_candidate(req.old_locator, top_candidates)
    index    = decision["index"]
    reason   = decision["reason"]
    logger.info(f"LLM 选择最佳: {decision}")

    if index < 0 or index >= len(top_candidates):
        return HealResponse(
            healed=False,
            confidence=0.0,
            new_locator=None,
            details={
                "reason": reason,
                "candidates": top_candidates
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
            "reason": reason,
            "candidates": top_candidates,
        }
    )


if __name__ == '__main__':
    pass
