#  _     _     __  __    ____
# | |   | |   |  \/  |  / ___|_ __ ___   __ _
# | |   | |   | |\/| | | |  _| '__/ _ \ / _` |
# | |___| |___| |  | | | |_| | | | (_) | (_| |
# |_____|_____|_|  |_|  \____|_|  \___/ \__, |
#                                          |_|
#

import json
import typing
import asyncio
from loguru import logger
from fastapi import Request
from groq import Groq
from groq.types.chat import (
    ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam
)
from schemas.cognitive import (
    Locator, Mix
)
from services.infrastructure.cache.upstash import UpStash
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

    async def best_candidate(self, request: Request, old_locator: Locator, candidates: list[dict]) -> dict:
        if not candidates: return {"index": -1, "reason": "没有候选元素。"}

        cand_desc = ""
        for i, c in enumerate(candidates):
            cand_desc += f"[{i}]\nscore={c['final_score']:.4f}\ntext={c['text']}\n"

        prompt = f"""
你是自动化测试中的元素自愈专家。

旧定位：
- by: {old_locator.by}
- value: {old_locator.value}

候选列表（已按相似度排序）：
{cand_desc}

请只返回 JSON:
{{
  "index": <整数, -1 表示不选>,
  "reason": "<原因>"
}}
"""

        logger.info(prompt)

        cache: UpStash = request.app.state.cache

        if mixed := await cache.get(const.K_MIX): mix = Mix(**mixed)
        else: mix = Mix(**const.V_MIX)

        cur = mix.app.get("Groq", {}).get("llm", {}).get("name", None)
        self.llm_groq_model = cur
        logger.info(f"远程三方大模型 -> {self.llm_groq_model}")

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

        try:
            data = json.loads(content)
            return {
                "index"  : int(data.get("index", -1)),
                "reason" : data.get("reason", "")
            }
        except (AttributeError, TypeError, json.JSONDecodeError):
            return {
                "index"  : 0,
                "reason" : "解析失败，默认选择第一个"
            }


if __name__ == '__main__':
    pass
