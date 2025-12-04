#  ______ _ _ _       ____  _
# |__  (_) | (_)____ / ___|| |_ ___  _ __ ___
#   / /| | | | |_  / \___ \| __/ _ \| '__/ _ \
#  / /_| | | | |/ /   ___) | || (_) | | |  __/
# /____|_|_|_|_/___| |____/ \__\___/|_|  \___|
#

import asyncio
import hashlib
import pymilvus
from utils import (
    const, toolset
)

env = toolset.current_env(
    const.ZILLIZ_URL, const.ZILLIZ_KEY
)

zilliz_url = env[const.ZILLIZ_URL]
zilliz_key = env[const.ZILLIZ_KEY]


class ZillizStore(object):

    def __init__(self, name: str = "healer_elements"):
        pymilvus.connections.connect(
            alias="default", uri=zilliz_url, token=zilliz_key, timeout=30
        )
        self.client = pymilvus.Collection(name)
        self.client.load()

    async def insert(self, vector: list[float], text: str) -> None:
        fp   = hashlib.md5(text.encode("UTF-8")).hexdigest()
        expr = f'fingerprint == "{fp}"'
        res  = self.client.query(expr=expr, limit=1, output_fields=["id"])
        if len(res) > 0: return print(f"🔁 Skip duplicate: {text}")

        await asyncio.to_thread(
            self.client.insert,
            data={"vector": vector, "text": text, "fingerprint": fp},
            timeout=30
        )
        return await asyncio.to_thread(self.client.flush)

    async def search(self, vector: list[float], k: int) -> list[dict]:
        results = await asyncio.to_thread(
            self.client.search,
            data=[vector],
            anns_field="vector",
            param={"metric_type": "COSINE", "params": {}},
            limit=k,
            output_fields=["text"]
        )

        hits = results[0]
        return [
            {
                "score" : float(hit.score),
                "text"  : hit.entity.get("text")
            }
            for hit in hits
        ]


if __name__ == '__main__':
    pass
