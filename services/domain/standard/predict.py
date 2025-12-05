#  ____               _ _      _
# |  _ \ _ __ ___  __| (_) ___| |_
# | |_) | '__/ _ \/ _` | |/ __| __|
# |  __/| | |  __/ (_| | | (__| |_
# |_|   |_|  \___|\__,_|_|\___|\__|
#

import json
import time
import base64
from loguru import logger
from services.domain.standard import signature
from services.infrastructure.cache.redis_cache import RedisCache
from utils import const


async def resolve_proxy_predict(
    x_app_region: str,
    x_app_version: str,
    a: str,
    t: int,
    n: str,
    cache: "RedisCache"
) -> dict:

    app_name, app_desc, *_ = a.lower().strip(), a, t, n

    cache_key = f"Predict Server:{app_desc}"
    infer_key = f"Predict:{app_desc}"

    infer_data = await cache.redis_get(infer_key)
    current    = infer_data.get("available", False) if infer_data else False
    logger.info(f"远程推理服务状态 -> {current}")

    if cached := await cache.redis_get(cache_key):
        cache_data = json.loads(base64.b64decode(json.loads(cached)["data"]))
        if (previous := cache_data["available"]) == current:
            logger.success(f"下发缓存推理服务 -> {cache_key}")
            return json.loads(cached)
        logger.info(f"推理服务状态变更 -> Cached={previous} Remote={current}")
        await cache.redis_delete(cache_key)
    available = current

    ttl = 86400

    expire_at = int(time.time()) + ttl
    token     = signature.sign_token(app_desc, expire_at)

    license_info = {
        "configuration" : {},
        "available"     : available,
        "expire_at"     : expire_at,
        "timeout"       : 60.0,
        "content_type"  : "multipart/form-data",
        "auth_header"   : const.TOKEN_FORMAT,
        "token"         : token,
        "method"        : "POST",
        "url"           : "https://plaxtonflarion--inference-inferenceservice-predict.modal.run",
        "ttl"           : ttl,
        "region"        : x_app_region,
        "version"       : x_app_version,
        "message"       : "Predict service online"
    }

    signed_data = signature.signature_license(
        license_info, private_key=f"{app_name}_{const.BASE_PRIVATE_KEY}"
    )
    await cache.redis_set(cache_key, json.dumps(signed_data), ex=ttl)
    logger.info(f"Redis cache -> {cache_key}")

    logger.success(f"下发推理服务 -> Predict service online")
    return signed_data


if __name__ == '__main__':
    pass
