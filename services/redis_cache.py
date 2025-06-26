#   ____          _ _        ____           _
#  |  _ \ ___  __| (_)___   / ___|__ _  ___| |__   ___
#  | |_) / _ \/ _` | / __| | |   / _` |/ __| '_ \ / _ \
#  |  _ <  __/ (_| | \__ \ | |__| (_| | (__| | | |  __/
#  |_| \_\___|\__,_|_|___/  \____\__,_|\___|_| |_|\___|
#

import json
import time
import typing
import redis.asyncio as aioredis
from fastapi import (
    Request, HTTPException
)
from loguru import logger
from common import (
    const, utils
)

env = utils.current_env(
    const.REDIS_CACHE_URL, const.REDIS_CACHE_KEY
)

redis_cache_url = env[const.REDIS_CACHE_URL]
redis_cache_key = env[const.REDIS_CACHE_KEY]


class RedisCache(object):

    def __init__(self, prefix: str = "app:"):
        self.client = aioredis.Redis.from_url(
            url=f"rediss://default:{redis_cache_key}@{redis_cache_url}",
            decode_responses=True,
            encoding=const.CHARSET
        )
        self.prefix = prefix

    def make_key(self, key: str) -> str:
        return f"{self.prefix}{key}"

    async def redis_set(self, key: str, value: typing.Any, ex: int = 60) -> typing.Optional[bool]:
        try:
            val = json.dumps(value)
            return bool(await self.client.set(self.make_key(key), val, ex=ex))
        except Exception as e:
            logger.error(e)

    async def redis_get(self, key: str) -> typing.Optional[typing.Union[dict, list, str, int, float]]:
        val = await self.client.get(self.make_key(key))
        try:
            return json.loads(val) if val else None
        except Exception as e:
            logger.error(e)

    async def redis_delete(self, key: str) -> typing.Optional[int]:
        try:
            return await self.client.delete(self.make_key(key))
        except Exception as e:
            logger.error(e)

    async def enforce_rate_limit(self, request: "Request", limit: int = 5, window: int = 60) -> None:
        ip = request.client.host
        timestamp = int(time.time())
        key = self.make_key(f"rate_limit:{ip}:{timestamp // window}")

        count = await self.client.incr(key)
        if count == 1:
            await self.client.expire(key, window)

        if count > limit:
            raise HTTPException(status_code=429, detail="Too many requests")


if __name__ == '__main__':
    pass
