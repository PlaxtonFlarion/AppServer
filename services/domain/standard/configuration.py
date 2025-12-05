#   ____             __ _                       _   _
#  / ___|___  _ __  / _(_) __ _ _   _ _ __ __ _| |_(_) ___  _ __
# | |   / _ \| '_ \| |_| |/ _` | | | | '__/ _` | __| |/ _ \| '_ \
# | |__| (_) | | | |  _| | (_| | |_| | | | (_| | |_| | (_) | | | |
#  \____\___/|_| |_|_| |_|\__, |\__,_|_|  \__,_|\__|_|\___/|_| |_|
#                         |___/
#

import json
from loguru import logger
from services.domain.standard import signature
from services.infrastructure.cache.redis_cache import RedisCache
from utils import (
    const, toolset
)


async def resolve_configuration(
    x_app_region: str,
    x_app_version: str,
    a: str,
    t: int,
    n: str,
    cache: "RedisCache"
) -> dict:

    app_name, app_desc, *_ = a.lower().strip(), a, t, n

    cache_key = f"Global Config:{app_desc}"

    if cached := await cache.redis_get(cache_key):
        logger.info(f"下发缓存全局配置 -> {cache_key}")
        return json.loads(cached)

    config      = toolset.resolve_template("data", const.CONFIGURATION)
    config_dict = json.loads(config.read_text(encoding=const.CHARSET))

    ttl = 86400

    license_info = {
        "configuration" : config_dict.get(app_desc, {}),
        "url"           : "",
        "ttl"           : ttl,
        "region"        : x_app_region,
        "version"       : x_app_version,
        "message"       : "Use global configuration"
    }

    signed_data = signature.signature_license(
        license_info, private_key=f"{app_name}_{const.BASE_PRIVATE_KEY}"
    )
    await cache.redis_set(cache_key, json.dumps(signed_data), ex=ttl)
    logger.info(f"Redis cache -> {cache_key}")

    logger.success(f"下发全局配置 -> Use global configuration")
    return signed_data


if __name__ == '__main__':
    pass
