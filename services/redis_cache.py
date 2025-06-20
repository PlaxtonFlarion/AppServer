#   ____          _ _        ____           _
#  |  _ \ ___  __| (_)___   / ___|__ _  ___| |__   ___
#  | |_) / _ \/ _` | / __| | |   / _` |/ __| '_ \ / _ \
#  |  _ <  __/ (_| | \__ \ | |__| (_| | (__| | | |  __/
#  |_| \_\___|\__,_|_|___/  \____\__,_|\___|_| |_|\___|
#

import json
import typing
import redis.asyncio as aioredis
from loguru import logger
from common import (
    utils, const
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
            return json.loads(val)
        except Exception as e:
            logger.error(e)

    async def redis_delete(self, key: str) -> typing.Optional[int]:
        try:
            return await self.client.delete(self.make_key(key))
        except Exception as e:
            logger.error(e)


if __name__ == '__main__':
    pass
