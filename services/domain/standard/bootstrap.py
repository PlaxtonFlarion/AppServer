#  ____              _       _
# | __ )  ___   ___ | |_ ___| |_ _ __ __ _ _ __
# |  _ \ / _ \ / _ \| __/ __| __| '__/ _` | '_ \
# | |_) | (_) | (_) | |_\__ \ |_| | | (_| | |_) |
# |____/ \___/ \___/ \__|___/\__|_|  \__,_| .__/
#                                         |_|
#

import json
from loguru import logger
from services.domain.standard import signature
from services.infrastructure.cache.redis_cache import RedisCache
from utils import const


async def resolve_bootstrap(
    x_app_region: str,
    x_app_version: str,
    a: str,
    t: int,
    n: str,
    cache: "RedisCache"
) -> dict:

    app_name, app_desc, *_ = a.lower().strip(), a, t, n

    cache_key = f"Activation Node:{app_desc}"

    if cached := await cache.redis_get(cache_key):
        logger.success(f"下发缓存激活配置 -> {cache_key}")
        return json.loads(cached)

    ttl = 86400

    license_info = {
        "configuration" : {},
        "url"           : "https://api.appserverx.com/sign",
        "ttl"           : ttl,
        "region"        : x_app_region,
        "version"       : x_app_version,
        "message"       : "Use activation node"
    }

    signed_data = signature.signature_license(
        license_info, private_key=f"{app_name}_{const.BASE_PRIVATE_KEY}"
    )
    await cache.redis_set(cache_key, json.dumps(signed_data), ex=ttl)
    logger.info(f"Redis cache -> {cache_key}")

    logger.success(f"下发激活配置 -> Use activation node")
    return signed_data


if __name__ == '__main__':
    pass
