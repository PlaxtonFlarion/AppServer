#   ____                _ _     _       _
#  / ___|__ _ _ __   __| (_) __| | __ _| |_ ___
# | |   / _` | '_ \ / _` | |/ _` |/ _` | __/ _ \
# | |__| (_| | | | | (_| | | (_| | (_| | ||  __/
#  \____\__,_|_| |_|\__,_|_|\__,_|\__,_|\__\___|
#
import asyncio
import time
import httpx
import random
import typing
from loguru import logger
from fastapi import Request
from fastapi.responses import JSONResponse
from schemas.cognitive import (
    HealRequest, HealResponse
)
from services.domain.standard import signature
from services.domain.self_healing.parsing import (
    AndroidXmlParser, WebDomParser
)
from services.infrastructure.vector.zilliz import Zilliz
from services.infrastructure.llm.llm_groq import LLMGroq
from utils import const


async def delivery(url: str, json: dict, **kwargs) -> dict:
    expire_at = int(time.time()) + random.randint(3600, 86400)
    token     = signature.sign_token("Heal", expire_at)
    headers   = {const.TOKEN_FORMAT: token}

    async with httpx.AsyncClient(headers=headers, timeout=60) as client:
        resp = await client.post(url, json=json, **kwargs)
        resp.raise_for_status()
        return resp.json()


async def heal_element(
    req: HealRequest,
    request: Request
) -> typing.Union[HealResponse, JSONResponse]:

    # 根据平台选择不同解析器，返回 ElementNode 列表
    logger.info(f"解析节点: {(app_platform := req.platform.strip().lower())}")
    match app_platform:
        case "android": node_list = AndroidXmlParser.parse(req.page_dump)
        case "web": node_list = WebDomParser.parse(req.page_dump)
        # 视情况扩展 iOS / 其他
        case _: raise ValueError(f"Unsupported platform: {req.platform}")

    query     = f"by={req.old_locator.by}, value={req.old_locator.value}"
    desc_list = [n.ensure_desc() for n in node_list]

    logger.info(f"向量生成: {query}")
    logger.info(f"向量生成: {len(desc_list)}")
    try:
        embedding_resp = await delivery(
            const.MODAL_TENSOR, json={"query": query, "elements": desc_list}
        )
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

    store: Zilliz     = request.app.state.store
    llm_groq: LLMGroq = request.app.state.llm_groq

    logger.info(f"维度匹配: [[v1], [v2], ...]")
    query_vec    = embedding_resp["query_vec"]
    page_vectors = embedding_resp["page_vectors"]

    logger.info(f"插入向量")
    await asyncio.gather(
        *(asyncio.to_thread(store.insert, vec, node.ensure_desc())
          for node, vec in zip(node_list, page_vectors))
    )

    k, top_k, beta = 5, 3, 1 - (alpha := 0.1)

    logger.info(f"向量召回: k={k}")
    retrieved = store.search(query_vec, k=k)

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

    candidate = [c["text"] for c in mapped_candidates]

    logger.info(f"结果重排")
    try:
        rerank_resp = await delivery(
            const.MODAL_RERANK, json={"query": query, "candidate": candidate}
        )
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

    rerank_scores = rerank_resp["scores"]
    for c, s in zip(mapped_candidates, rerank_scores):
        c["rerank_score"] = float(s)

    logger.info(f"融合模式: 向量({alpha * 100:.0f}%), CrossEncoder({beta * 100:.0f}%)")
    for c in mapped_candidates:
        c["final_score"] = alpha * c["vector_score"] + beta * c["rerank_score"]

    logger.info(f"取 top-k={top_k}")
    top_candidates = sorted(mapped_candidates, key=lambda x: x["final_score"], reverse=True)[:top_k]

    decision = await llm_groq.best_candidate(
        req.old_locator, top_candidates
    )
    index  = decision["index"]
    reason = decision["reason"]
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

    new_by      = "id" if element.resource_id else "text"
    new_value   = element.resource_id or element.text or ""
    new_locator = {"by": new_by, "value": new_value}
    logger.info(f"{new_locator}")

    return HealResponse(
        healed=True,
        confidence=confidence,
        new_locator=new_locator,
        details={
            "reason": reason,
            "candidates": top_candidates,
        }
    )


if __name__ == '__main__':
    pass
