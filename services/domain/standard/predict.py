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
from fastapi import Request
from schemas.cognitive import (
    PredictResponse, Mix
)
from services.domain.standard import signature
from services.infrastructure.cache.upstash import UpStash
from utils import const


async def resolve_proxy_predict(
    request: Request,
    a: str,
    t: int,
    n: str
) -> PredictResponse:

    app_name, app_desc, *_ = a.lower().strip(), a, t, n

    x_app_region  = request.state.x_app_region
    x_app_version = request.state.x_app_version

    cache_key = f"{app_desc}:Predict"

    cache: UpStash = request.app.state.cache

    if mixed := await cache.get(const.K_MIX): mix = Mix(**mixed)
    else: mix = Mix(**const.V_MIX)

    cur = mix.app.get("Modal", {}).get("inference", {}).get("enabled", False)
    logger.info(f"远程推理服务状态 -> {cur}")

    if cached := await cache.get(cache_key):
        cache_data = json.loads(base64.b64decode(json.loads(cached)["data"]))
        if (previous := cache_data["available"]) == cur:
            logger.success(f"下发缓存推理服务 -> {cache_key}")
            return json.loads(cached)
        logger.info(f"推理服务状态变更 -> Cached={previous} Remote={cur}")
        await cache.delete(cache_key)
    available = cur

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
        "url"           : const.MODAL_PREDICT,
        "ttl"           : ttl,
        "region"        : x_app_region,
        "version"       : x_app_version,
        "message"       : "Predict service online"
    }

    signed_data = signature.signature_license(
        license_info, private_key=f"{app_name}_{const.BASE_PRIVATE_KEY}"
    )
    await cache.set(cache_key, signed_data, ex=ttl)
    # await cache.set(cache_key, json.dumps(signed_data), ex=ttl)
    logger.info(f"Redis cache -> {cache_key}")

    logger.success(f"下发推理服务 -> Predict service online")
    return PredictResponse(**signed_data)


if __name__ == '__main__':
    pass
