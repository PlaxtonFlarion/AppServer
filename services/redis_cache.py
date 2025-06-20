#   ____          _ _        ____           _
#  |  _ \ ___  __| (_)___   / ___|__ _  ___| |__   ___
#  | |_) / _ \/ _` | / __| | |   / _` |/ __| '_ \ / _ \
#  |  _ <  __/ (_| | \__ \ | |__| (_| | (__| | | |  __/
#  |_| \_\___|\__,_|_|___/  \____\__,_|\___|_| |_|\___|
#

import redis
from common import (
    utils, const
)

env = utils.current_env(
    const.REDIS_CACHE_URL, const.REDIS_CACHE_KEY
)

redis_cache_url = env[const.REDIS_CACHE_URL]
redis_cache_key = env[const.REDIS_CACHE_KEY]

redis_client: "redis.Redis" = redis.Redis.from_url(
    redis_cache_url,
    decode_responses=True,
    encoding=const.CHARSET
)


class RedisCache(object):

    def __init__(self, client: "redis.Redis", prefix: str = ""):
        self.client = client
        self.prefix = prefix

    def set(self, key, value, ex=60):
        return self.client.set(self.prefix + key, value, ex=ex)

    def get(self, key):
        return self.client.get(self.prefix + key)

    def delete(self, key):
        return self.client.delete(self.prefix + key)


if __name__ == '__main__':
    pass
