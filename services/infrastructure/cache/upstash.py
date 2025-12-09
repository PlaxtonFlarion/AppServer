#  _   _           _            _
# | | | |_ __  ___| |_ __ _ ___| |__
# | | | | '_ \/ __| __/ _` / __| '_ \
# | |_| | |_) \__ \ || (_| \__ \ | | |
#  \___/| .__/|___/\__\__,_|___/_| |_|
#       |_|
#

import json
import time
import typing
import redis.asyncio as aioredis
from fastapi import (
    Request, HTTPException
)
from utils import (
    const, toolset
)

env = toolset.current_env(
    const.REDIS_CACHE_URL, const.REDIS_CACHE_KEY
)

redis_cache_url = env[const.REDIS_CACHE_URL]
redis_cache_key = env[const.REDIS_CACHE_KEY]


class UpStash(object):

    def __init__(self, prefix: str = "app:"):
        self.client = aioredis.Redis.from_url(
            url=f"rediss://default:{redis_cache_key}@{redis_cache_url}",
            decode_responses=True,
            encoding=const.CHARSET
        )
        self.prefix = prefix

    def redis_make_key(self, key: str) -> str:
        return f"{self.prefix}{key}"

    async def redis_set(self, key: str, value: typing.Any, ex: int = 60) -> typing.Optional[bool]:
        val = json.dumps(value)
        return bool(await self.client.set(self.redis_make_key(key), val, ex=ex))

    async def redis_get(self, key: str) -> typing.Optional[typing.Union[dict, list, str, int, float]]:
        if (val := await self.client.get(self.redis_make_key(key))) is None:
            return None
        try:
            return json.loads(val)
        except (json.JSONDecodeError, TypeError):
            return val

    async def redis_delete(self, key: str) -> typing.Optional[int]:
        return await self.client.delete(self.redis_make_key(key))


if __name__ == '__main__':
    pass
