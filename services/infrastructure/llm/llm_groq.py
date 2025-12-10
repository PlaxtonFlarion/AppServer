#  _     _     __  __    ____
# | |   | |   |  \/  |  / ___|_ __ ___   __ _
# | |   | |   | |\/| | | |  _| '__/ _ \ / _` |
# | |___| |___| |  | | | |_| | | | (_) | (_| |
# |_____|_____|_|  |_|  \____|_|  \___/ \__, |
#                                          |_|
#

import re
import json
import typing
import asyncio
from loguru import logger
from groq import Groq
from groq.types.chat import (
    ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam
)
from schemas.cognitive import Locator
from utils import (
    const, toolset
)

env = toolset.current_env(
    const.GROQ_LLM_KEY
)

groq_llm_key = env[const.GROQ_LLM_KEY]


class LLMGroq(object):

    def __init__(self):
        self.llm_groq_client: Groq = Groq(api_key=groq_llm_key)
        self.llm_groq_model: typing.Optional[str] = None

    def __str__(self) -> str:
        return f"<LLM Groq {self.llm_groq_model}>"

    __repr__ = __str__

    async def route(self, text: str) -> dict:
        prompt = const.R_PROMPT.format(text=text)
        logger.info(prompt)

        resp = await asyncio.to_thread(
            self.llm_groq_client.chat.completions.create,
            model=self.llm_groq_model,
            messages=[
                ChatCompletionSystemMessageParam(
                    role="system",
                    content="你是严格的 JSON 输出 AI，不得输出除 JSON 外的内容。"
                ),
                ChatCompletionUserMessageParam(
                    role="user",
                    content=prompt
                )
            ],
            temperature=0.2
        )

        content = resp.choices[0].message.content.strip()
        content = re.sub(r"```json|```", "", content).strip()

        try:
            data = json.loads(content)
            return {
                "lang"          : data.get("lang", "en"),
                "embedding"     : data.get("embedding", "bge-en"),
                "search"        : data.get("search", "single"),
                "rerank_weight" : float(data.get("rerank_weight", 0.9)),
                "reason"        : data.get("reason", "fallback-default")
            }
        except Exception as e:
            logger.error(f"[JSON Parse Failed] {e}")
            return {
                "lang"          : "en",
                "embedding"     : "bge-en",
                "search"        : "single",
                "rerank_weight" : 0.9,
                "reason"        : "解析失败，使用默认策略"
            }

    async def best_candidate(self, old_locator: Locator, candidates: list[dict]) -> dict:
        if not candidates: return {"index": -1, "reason": "没有候选元素。"}

        cand_desc = ""
        for i, c in enumerate(candidates):
            cand_desc += f"[{i}]\nscore={c['final_score']:.4f}\ntext={c['text']}\n"

        prompt = const.F_PROMPT.format(
            by=old_locator.by, value=old_locator.value, cand_desc=cand_desc
        )
        logger.info(prompt)

        resp = await asyncio.to_thread(
            self.llm_groq_client.chat.completions.create,
            model=self.llm_groq_model,
            messages=[
                ChatCompletionSystemMessageParam(
                    role="system",
                    content="你是一个严谨的 UI 元素自愈模型，只返回 JSON。"
                ),
                ChatCompletionUserMessageParam(
                    role="user",
                    content=prompt
                )
            ],
            temperature=0.1
        )

        content = resp.choices[0].message.content.strip()
        content = re.sub(r"```json|```", "", content).strip()

        try:
            data = json.loads(content)
            return {
                "index"  : int(data.get("index", -1)),
                "reason" : data.get("reason", "")
            }
        except Exception as e:
            logger.error(f"[JSON Parse Failed] {e}")
            return {
                "index"  : 0,
                "reason" : "解析失败，默认选择第一个"
            }


if __name__ == '__main__':
    pass
