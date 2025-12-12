#  _   _           _            _
# | | | |_ __  ___| |_ __ _ ___| |__
# | | | | '_ \/ __| __/ _` / __| '_ \
# | |_| | |_) \__ \ || (_| \__ \ | | |
#  \___/| .__/|___/\__\__,_|___/_| |_|
#       |_|
#

import json
import typing
import redis.asyncio as aioredis
from utils import (
    const, toolset
)

env = toolset.current_env(
    const.REDIS_CACHE_URL, const.REDIS_CACHE_KEY
)

redis_cache_url = env[const.REDIS_CACHE_URL]
redis_cache_key = env[const.REDIS_CACHE_KEY]


class UpStash(object):

    def __init__(self):
        self.client = aioredis.Redis.from_url(
            url=f"rediss://default:{redis_cache_key}@{redis_cache_url}",
            decode_responses=True,
            encoding=const.CHARSET
        )

    async def get(self, key: str) -> typing.Optional[typing.Union[dict, list, str, int, float]]:
        if (val := await self.client.get(key)) is None:
            return None
        try:
            return json.loads(val)
        except (json.JSONDecodeError, TypeError):
            return val

    async def set(self, key: str, value: typing.Any, ex: int = 60) -> typing.Optional[bool]:
        val = json.dumps(value, ensure_ascii=False)
        return bool(await self.client.set(key, val, ex=ex))

    async def delete(self, key: str) -> typing.Optional[int]:
        return await self.client.delete(key)


if __name__ == '__main__':
    pass
