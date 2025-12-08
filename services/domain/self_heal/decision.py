#  ____            _     _
# |  _ \  ___  ___(_)___(_) ___  _ __
# | | | |/ _ \/ __| / __| |/ _ \| '_ \
# | |_| |  __/ (__| \__ \ | (_) | | | |
# |____/ \___|\___|_|___/_|\___/|_| |_|
#

import time
import httpx
import typing
import random
import asyncio
from loguru import logger
from fastapi import Request
from schemas.cognitive import (
    HealRequest, HealResponse
)
from services.domain.standard import signature
from services.domain.self_heal.parsing import (
    AndroidXmlParser, WebDomParser
)
from services.infrastructure.vector.zilliz import Zilliz
from services.infrastructure.llm.llm_groq import LLMGroq
from utils import const


class Decision(object):

    def __init__(self, req: HealRequest, request: Request):
        self.req: HealRequest  = req

        self.store: Zilliz     = request.app.state.store
        self.llm_groq: LLMGroq = request.app.state.llm_groq

        self.k     = 5
        self.top_k = 3
        self.alpha = 0.1
        self.beta  = 1 - self.alpha

    @staticmethod
    async def delivery(url: str, json: dict, **kwargs) -> dict:
        expire_at = int(time.time()) + random.randint(3600, 86400)
        token     = signature.sign_token("Heal", expire_at)
        headers   = {const.TOKEN_FORMAT: token}
        async with httpx.AsyncClient(headers=headers, timeout=60) as client:
            resp = await client.post(url, json=json, **kwargs)
            resp.raise_for_status()
            return resp.json()

    async def parse_tree(self) -> list:
        logger.info(f"解析节点: {(app_platform := self.req.platform.strip().lower())}")
        match app_platform:
            case "android": node_list = AndroidXmlParser.parse(self.req.page_dump)
            case "web": node_list = WebDomParser.parse(self.req.page_dump)
            case _: raise ValueError(f"Unsupported platform: {self.req.platform}")

        return node_list

    async def transform(self, node_list: list) -> tuple[str, list, list[list]]:
        query     = f"by={self.req.old_locator.by}, value={self.req.old_locator.value}"
        desc_list = [n.ensure_desc() for n in node_list]

        logger.info(f"修复定位: {query}")
        logger.info(f"节点数量: {len(desc_list)}")
        embedding_resp = await self.delivery(
            const.MODAL_TENSOR, json={"query": query, "elements": desc_list}
        )

        logger.info(f"维度匹配: [[v1], [v2], ...]")
        query_vec    = embedding_resp["query_vec"]
        page_vectors = embedding_resp["page_vectors"]

        return query, query_vec, page_vectors

    async def burning(self, node_list: list, page_vectors: list[list]) -> None:
        logger.info(f"写入向量: {str(self.store)}")
        await asyncio.gather(
            *(asyncio.to_thread(self.store.insert, vec, node.ensure_desc())
              for node, vec in zip(node_list, page_vectors))
        )

    async def recall(self, query_vec: list, node_list: list) -> tuple[list[dict], list[str]]:
        logger.info(f"向量召回: K={self.k}")
        retrieved = self.store.search(query_vec, k=self.k)

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

        return mapped_candidates, [c["text"] for c in mapped_candidates]

    async def rerank(self, query: str, candidate: list[str], mapped_candidates: list[dict]):
        logger.info(f"结果重排: Top-K={self.top_k}")
        logger.info(f"融合模式: 向量({self.alpha * 100:.0f}%), CrossEncoder({self.beta * 100:.0f}%)")
        rerank_resp = await self.delivery(
            const.MODAL_RERANK, json={"query": query, "candidate": candidate}
        )

        for c, s in zip(mapped_candidates, rerank_resp["scores"]):
            c["rerank_score"] = float(s)

        for c in mapped_candidates:
            c["final_score"] = self.alpha * c["vector_score"] + self.beta * c["rerank_score"]

        return sorted(mapped_candidates, key=lambda x: x["final_score"], reverse=True)[:self.top_k]

    async def llm_decision(self, top_candidates: list[dict]) -> HealResponse:
        logger.info(f"模型决策: {str(self.llm_groq)}")
        decision = await self.llm_groq.best_candidate(
            self.req.old_locator, top_candidates
        )

        index, reason = decision["index"], decision["reason"]

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

    async def heal_element(self) -> HealResponse:
        node_list = await self.parse_tree()

        query, query_vec, page_vectors = await self.transform(node_list)

        await self.burning(node_list, page_vectors)

        mapped_candidates, candidate = await self.recall(query_vec, node_list)

        top_candidates = await self.rerank(query, candidate, mapped_candidates)

        return await self.llm_decision(top_candidates)

    async def heal_element_stream(self) -> typing.AsyncGenerator[str, None]:
        fmt   : typing.Callable[[str], str] = lambda x: f"\n\033[38;5;81m▶ {x}\033[0m\n"      # 青色标题
        ok    : typing.Callable[[str], str] = lambda x: f"\033[38;5;120m✔ {x}\033[0m\n"       # 绿色成功
        info  : typing.Callable[[str], str] = lambda x: f"\033[38;5;245m• {x}\033[0m\n"       # 灰色信息
        block : typing.Callable[[str], str] = lambda x: f"\033[48;5;57;38;5;230m {x} \033[0m" # 反色结果

        try:
            t0 = time.time()

            # ===== Step 1 =====
            yield fmt(f"📩 [1/6] 解析页面结构中...\n")
            node_list = await self.parse_tree()
            yield ok(f"📨 完成 -> 检测到节点数 {len(node_list)}") + info("✓ 页面结构树构建成功\n")

            # ===== Step 2 =====
            yield fmt(f"📩 [2/6] 生成语义向量 Embedding...\n")
            query, query_vec, page_vectors = await self.transform(node_list)
            yield ok(f"📨 完成 -> Embedding 生成完毕") + info("✓ 已进入向量计算阶段\n")

            # ===== Step 3 =====
            yield fmt(f"📩 [3/6] 写入向量存储中...\n")
            await self.burning(node_list, page_vectors)
            yield ok(f"📨 完成 -> 向量入库成功\n")

            # ===== Step 4 =====
            yield fmt(f"📩 [4/6] 向量召回 K 查询中...\n")
            mapped_candidates, candidate = await self.recall(query_vec, node_list)
            yield ok(f"📨 完成 -> 召回 {len(mapped_candidates)} 个候选") + info("✓ 语义检索完成\n")

            # ===== Step 5 =====
            yield fmt(f"📩 [5/6] CrossEncoder 重排中...\n")
            top_candidates = await self.rerank(query, candidate, mapped_candidates)
            yield ok(f"📨 完成 -> Top-K={len(top_candidates)}\n")

            # ===== Step 6 =====
            yield fmt(f"📩 [6/6] LLM 参与最终决策中...\n")
            result = await self.llm_decision(top_candidates)
            yield ok(f"📨 完成 -> LLM 评估完成\n")

            # ========= Result Block =========
            yield "\n\033[38;5;45m════ FINAL RESULT ════\033[0m\n"
            yield block(f"Heal       : {'SUCCESS' if result.healed else 'FAILED'}") + "\n"
            yield block(f"Confidence : {result.confidence:.2f}") + "\n"
            yield info("智能定位已输出 JSON 结构👇") + "\n\n"

            yield result.model_dump_json(indent=2)

            yield f"\n\n⏱ 总耗时: {time.time() - t0:.2f}s\n"

        except Exception as e:
            yield f"\033[31m[FATAL ERROR] {e}\033[0m\n"


if __name__ == '__main__':
    pass
