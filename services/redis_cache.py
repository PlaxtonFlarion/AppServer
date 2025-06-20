#   ____          _ _        ____           _
#  |  _ \ ___  __| (_)___   / ___|__ _  ___| |__   ___
#  | |_) / _ \/ _` | / __| | |   / _` |/ __| '_ \ / _ \
#  |  _ <  __/ (_| | \__ \ | |__| (_| | (__| | | |  __/
#  |_| \_\___|\__,_|_|___/  \____\__,_|\___|_| |_|\___|
#

import json
import redis
import typing
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
        self.client = redis.Redis.from_url(
            redis_cache_url,
            decode_responses=True,
            encoding=const.CHARSET
        )
        self.prefix = prefix

    async def make_key(self, key: str) -> str:
        return f"{self.prefix}{key}"

    async def redis_set(self, key: str, value: typing.Any, ex: int = 60) -> bool:
        try:
            val = json.dumps(value)
            return bool(await self.client.set(await self.make_key(key), val, ex=ex))
        except (json.JSONDecodeError, TypeError):
            return False

    async def redis_get(self, key: str) -> typing.Optional[typing.Union[dict, list, str, int, float]]:
        val = await self.client.get(await self.make_key(key))
        try:
            return json.loads(val)
        except (json.JSONDecodeError, TypeError):
            return val

    async def redis_delete(self, key: str) -> int:
        return await self.client.delete(await self.make_key(key))


if __name__ == '__main__':
    pass
