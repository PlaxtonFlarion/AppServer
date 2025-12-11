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
    HealRequest, HealResponse, Mix
)
from services.domain.standard import signature
from services.domain.self_heal.parsing import (
    AndroidXmlParser, WebDomParser
)
from services.infrastructure.cache.upstash import UpStash
from services.infrastructure.llm.llm_groq import LLMGroq
from services.infrastructure.vector.zilliz import Zilliz
from utils import const


class Decision(object):

    def __init__(self, req: HealRequest, request: Request):
        self.req: HealRequest = req
        self.request: Request = request

        self.cache: UpStash    = request.app.state.cache
        self.store: Zilliz     = request.app.state.store
        self.llm_groq: LLMGroq = request.app.state.llm_groq

        self.k     = 5
        self.top_k = 3
        self.beta  = 0.9
        self.alpha = 1 - self.beta

    async def delivery(self, url: str, json: dict, **kwargs) -> dict:
        if mixed := await self.cache.get(const.K_MIX): mix = Mix(**mixed)
        else: mix = Mix(**const.V_MIX)

        cur = mix.app.get("Modal", {}).get("DNS", const.DNS)
        logger.info(f"远程域名服务地址 -> {cur}")

        expire_at = int(time.time()) + random.randint(3600, 86400)
        token     = signature.sign_token("Heal", expire_at)
        headers   = {const.TOKEN_FORMAT: token}
        async with httpx.AsyncClient(headers=headers, timeout=60) as client:
            resp = await client.post(cur + url, json=json, **kwargs)
            resp.raise_for_status()
            return resp.json()

    async def load_model_from_cache(self) -> None:
        if mixed := await self.cache.get(const.K_MIX): mix = Mix(**mixed)
        else: mix = Mix(**const.V_MIX)

        cur = mix.app.get("Groq", {}).get("llm", {}).get("name", None)
        self.llm_groq.llm_groq_model = cur

    async def parse_tree(self) -> list:
        logger.info(f"解析节点: {(app_platform := self.req.platform.strip().lower())}")
        match app_platform:
            case "android": node_list = AndroidXmlParser.parse(self.req.page_dump)
            case "web": node_list = WebDomParser.parse(self.req.page_dump)
            case _: raise ValueError(f"Unsupported platform: {self.req.platform}")

        return node_list

    async def transform(self, node_list: list) -> tuple[dict, str, list, list[list]]:
        query     = f"by={self.req.old_locator.by}, value={self.req.old_locator.value}"
        desc_list = [n.ensure_desc() for n in node_list]

        # 🔥 1) LLM智能路由决策
        router = query + "\n" + "\n".join(desc_list[:10])
        meta   = await self.llm_groq.route(router)

        emb_mode   = meta.get("embedding")
        self.beta  = meta.get("rerank_weight")
        self.alpha = 1 - self.beta
        logger.info(f"路由策略: {meta}")

        # 🔥 2) 根据 router 输出动态选择 Emb
        match emb_mode:
            case "bge-en": embed_url, alt_embed_url = const.TENSOR_EN_EP, const.TENSOR_ZH_EP
            case "bge-zh": embed_url, alt_embed_url = const.TENSOR_ZH_EP, const.TENSOR_EN_EP
            case _: embed_url, alt_embed_url = const.TENSOR_EN_EP, const.TENSOR_ZH_EP
        meta["alt_embed_url"] = alt_embed_url

        logger.info(f"修复定位: {query}")
        logger.info(f"节点数量: {len(desc_list)}")
        embedding_resp = await self.delivery(
            embed_url, json={"query": query, "elements": desc_list}
        )

        logger.info(f"维度匹配: [[v1], [v2], ...]")
        query_vec    = embedding_resp["query_vec"]
        page_vectors = embedding_resp["page_vectors"]

        return meta, query, query_vec, page_vectors

    async def burning(self, node_list: list, page_vectors: list[list]) -> None:
        logger.info(f"写入向量: {str(self.store)}")
        await asyncio.gather(
            *(asyncio.to_thread(self.store.insert, vec, node.ensure_desc())
              for node, vec in zip(node_list, page_vectors))
        )

    async def recall(self, query_vec: list, node_list: list, meta: dict) -> tuple[list[dict], list[str]]:

        # ---- 工具：合并召回结果（去重且保序） ----
        def merge_results(a: list[dict], b: list[dict]) -> list[dict]:
            seen = set()
            merged = []
            for x in a + b:
                if x["text"] not in seen:
                    seen.add(x["text"])
                    merged.append(x)
            return merged[:self.k]  # 截断 top-k

        # ---- 第一轮召回 ----
        res_begin = self.store.search(query_vec, k=self.k)

        # ---- 单路策略（无需 fallback）----
        if meta.get("search") == "single":
            retrieved = res_begin
        else:
            # ---- 双路 fallback：找语义最接近 query 的节点作为种子更合理 ----
            seed = node_list[0].ensure_desc()

            embedding_resp = await self.delivery(
                meta["alt_embed_url"],
                json={"query": seed, "elements": []}
            )
            alt_vec = embedding_resp["query_vec"]
            res_alt = self.store.search(alt_vec, k=self.k)

            retrieved = merge_results(res_begin, res_alt)

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
            const.CROSS_ENC_EP, json={"query": query, "candidate": candidate}
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
        await self.load_model_from_cache()

        node_list = await self.parse_tree()

        meta, query, query_vec, page_vectors = await self.transform(node_list)

        await self.burning(node_list, page_vectors)

        mapped_candidates, candidate = await self.recall(query_vec, node_list, meta)

        top_candidates = await self.rerank(query, candidate, mapped_candidates)

        return await self.llm_decision(top_candidates)

    async def heal_element_stream(self) -> typing.AsyncGenerator[str, None]:
        fmt   : typing.Callable[[str], str] = lambda x: f"\n\033[38;5;81m▶ {x}\033[0m\n"
        ok    : typing.Callable[[str], str] = lambda x: f"\033[38;5;120m✔ {x}\033[0m\n"
        info  : typing.Callable[[str], str] = lambda x: f"\033[38;5;245m• {x}\033[0m\n"
        block : typing.Callable[[str], str] = lambda x: f"\033[48;5;57;38;5;230m {x} \033[0m"
        stamp : typing.Callable[
            [float], str
        ] = lambda x: f"\033[38;5;141m time={time.time() - x:.2f}s\033[0m\n"

        async def typewriter(text: str, speed: float = 0.1) -> typing.AsyncGenerator[str, None]:
            """逐字符流式输出"""
            for ch in text:
                yield ch; await asyncio.sleep(speed)

        await self.load_model_from_cache()

        t0, step = time.time(), 0

        try:
            # ===== Step 1 =====
            step += 1
            yield fmt(f"📩 [{step}/6] 解析页面结构中...\n")
            t = time.time()
            node_list = await self.parse_tree()
            yield ok(f"  └ done. nodes={len(node_list)},{stamp(t)}")
            yield info("------------------------------------------------------------\n")

            # ===== Step 2 =====
            step += 1
            yield fmt(f"📩 [{step}/6] 生成语义向量 Embedding...\n")
            t = time.time()
            meta, query, query_vec, page_vectors = await self.transform(node_list)
            yield ok(f"  └ done. dim={len(query_vec)}, vectors={len(page_vectors)},{stamp(t)}")
            yield info("------------------------------------------------------------\n")

            # ===== Step 3 =====
            step += 1
            yield fmt(f"📩 [{step}/6] 写入向量存储中...\n")
            t = time.time()
            await self.burning(node_list, page_vectors)
            yield ok(f"  └ done. db_insert={len(page_vectors)},{stamp(t)}")
            yield info("------------------------------------------------------------\n")

            # ===== Step 4 =====
            step += 1
            yield fmt(f"📩 [{step}/6] 向量召回 K 查询中...\n")
            t = time.time()
            mapped_candidates, candidate = await self.recall(query_vec, node_list, meta)
            yield ok(f"  └ done. retrieved={len(mapped_candidates)},{stamp(t)}")
            yield info("------------------------------------------------------------\n")

            # ===== Step 5 =====
            step += 1
            yield fmt(f"📩 [{step}/6] CrossEncoder 重排中...\n")
            t = time.time()
            top_candidates = await self.rerank(query, candidate, mapped_candidates)
            yield ok(f"  └ done. top_k={len(top_candidates)},{stamp(t)}")
            yield info("------------------------------------------------------------\n")

            # ===== Step 6 =====
            step += 1
            yield fmt(f"📩 [{step}/6] LLM 参与最终决策中...\n")
            t = time.time()
            result = await self.llm_decision(top_candidates)
            yield ok(f"  └ done. healed={result.healed}, confidence={result.confidence:.4f},{stamp(t)}")
            yield info("============================================================\n\n")

            # ========= Result Block =========
            yield "\n\033[38;5;45m════ FINAL RESULT ════\033[0m\n"
            yield block(f"Heal       : {'SUCCESS' if result.healed else 'FAILED'}") + "\n"
            yield block(f"Confidence : {result.confidence:.2f}")
            yield "\n\033[38;5;45m══════════════════════\033[0m\n"
            yield info("智能定位已输出 JSON 结构👇") + "\n\n"

            yield result.model_dump_json(indent=4)

            yield f"\n\n🏁 Total: {time.time() - t0:.2f}s\n"

        except Exception as e:
            yield f"\033[31m[FATAL ERROR] ❌ {e}\033[0m\n"
            logger.error(f"[FATAL ERROR] ❌ {e}")


if __name__ == '__main__':
    pass
