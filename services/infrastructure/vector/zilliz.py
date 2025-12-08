#  ______ _ _ _
# |__  (_) | (_)____
#   / /| | | | |_  /
#  / /_| | | | |/ /
# /____|_|_|_|_/___|
#

import hashlib
import pymilvus
from loguru import logger
from utils import (
    const, toolset
)

env = toolset.current_env(
    const.ZILLIZ_URL, const.ZILLIZ_KEY
)

zilliz_url = env[const.ZILLIZ_URL]
zilliz_key = env[const.ZILLIZ_KEY]


class Zilliz(object):

    def __init__(self):
        pymilvus.connections.connect(
            alias="default", uri=zilliz_url, token=zilliz_key, timeout=30
        )
        self.client = pymilvus.Collection("healer_elements")
        self.client.load()

    def __str__(self) -> str:
        return f"<{self.client.name}>"

    __repr__ = __str__

    def insert(self, vector: list[float], text: str) -> None:
        fp   = hashlib.md5(text.encode(const.CHARSET)).hexdigest()
        expr = f'fingerprint == "{fp}"'
        res  = self.client.query(expr=expr, limit=1, output_fields=["id"])
        if len(res) > 0: return logger.info(f"🔁 Duplicate ignored | fp={fp[:10]}...")

        self.client.insert(
            data={"vector": vector, "text": text, "fingerprint": fp}, timeout=30
        )
        self.client.flush()
        return logger.info(
            f"🟢 Inserted vector ✓ | dim={len(vector)} | fp={fp[:10]}..."
        )

    def search(self, vector: list[float], k: int) -> list[dict]:
        results = self.client.search(
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
