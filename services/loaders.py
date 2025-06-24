#   _                    _
#  | |    ___   __ _  __| | ___ _ __ ___
#  | |   / _ \ / _` |/ _` |/ _ \ '__/ __|
#  | |__| (_) | (_| | (_| |  __/ |  \__ \
#  |_____\___/ \__,_|\__,_|\___|_|  |___/
#

import json
import time
from loguru import logger
from fastapi import (
    Request, HTTPException
)
from common import (
    const, utils
)
from services import (
    redis_cache, signature
)

BOOTSTRAP_RATE_LIMIT = {}

env = utils.current_env(
    const.SHARED_SECRET
)

shared_secret = env[const.SHARED_SECRET]


async def enforce_rate_limit(request: "Request", limit: int = 5, window: int = 60) -> None:
    """
    对请求 IP 进行限流控制，防止过于频繁的访问。

    Parameters
    ----------
    request : Request
        当前的 HTTP 请求对象，需包含客户端 IP 地址字段。

    limit : int, optional
        在时间窗口内允许的最大请求次数，默认值为 5。

    window : int, optional
        滑动时间窗口的长度（单位：秒），默认值为 60 秒。

    Raises
    ------
    HTTPException
        若请求频率超过设定限制，返回 429 状态码（Too Many Requests）。

    Notes
    -----
    - 使用全局字典 `BOOTSTRAP_RATE_LIMIT` 存储每个 IP 的请求时间戳；
    - 在每次请求时，过滤掉时间窗口外的记录；
    - 如果保留的时间戳数量达到上限，立即拒绝请求；
    - 本函数适合用于登录、激活、验证码等敏感接口的请求节流。
    """
    ip, now = request.client.host, time.time()

    logger.info(f"ip address: {ip}")

    BOOTSTRAP_RATE_LIMIT.setdefault(ip, [])
    BOOTSTRAP_RATE_LIMIT[ip] = [
        t for t in BOOTSTRAP_RATE_LIMIT[ip] if now - t < window
    ]

    if len(BOOTSTRAP_RATE_LIMIT[ip]) >= limit:
        raise HTTPException(429, f"Too many requests")

    BOOTSTRAP_RATE_LIMIT[ip].append(now)


async def resolve_configuration(
        x_app_id: str,
        x_app_token: str,
        x_app_region: str,
        x_app_version: str,
        a: str,
        t: int,
        n: str,
        cache: "redis_cache.RedisCache"
) -> dict:

    app_name, app_desc, *_ = a.lower().strip(), a, t, n

    signature.verify_signature(
        x_app_id, x_app_token, public_key=f"{app_name}_{const.BASE_PUBLIC_KEY}"
    )

    cache_key = f"Global Config:{app_desc}"

    if cached := await cache.redis_get(cache_key):
        logger.info(f"下发缓存全局配置 -> {cache_key}")
        return json.loads(cached)

    config = utils.resolve_template("data", const.CONFIGURATION)
    config_dict = json.loads(config.read_text(encoding=const.CHARSET))

    license_info = {
        "configuration": config_dict.get(app_desc) or config_dict.get("Static", {}),
        "online": {},
        "url": f"",
        "ttl": 86400,
        "region": x_app_region,
        "version": x_app_version,
        "message": f"Use global configuration"
    }

    signed_data = signature.signature_license(
        license_info, private_key=f"{app_name}_{const.BASE_PRIVATE_KEY}"
    )
    await cache.redis_set(cache_key, json.dumps(signed_data), ex=license_info["ttl"])
    logger.info(f"Redis cache -> {cache_key}")

    logger.success(f"下发全局配置 -> Use global configuration")
    return signed_data


async def resolve_bootstrap(
        x_app_id: str,
        x_app_token: str,
        x_app_region: str,
        x_app_version: str,
        a: str,
        t: int,
        n: str,
        cache: "redis_cache.RedisCache"
) -> dict:

    app_name, app_desc, *_ = a.lower().strip(), a, t, n

    signature.verify_signature(
        x_app_id, x_app_token, public_key=f"{app_name}_{const.BASE_PUBLIC_KEY}"
    )

    cache_key = f"Activation Node:{app_desc}"

    if cached := await cache.redis_get(cache_key):
        logger.success(f"下发缓存激活配置 -> {cache_key}")
        return json.loads(cached)

    license_info = {
        "configuration": {},
        "online": {},
        "url": f"https://api.appserverx.com/sign",
        "ttl": 86400,
        "region": x_app_region,
        "version": x_app_version,
        "message": f"Use activation node"
    }

    signed_data = signature.signature_license(
        license_info, private_key=f"{app_name}_{const.BASE_PRIVATE_KEY}"
    )
    await cache.redis_set(cache_key, json.dumps(signed_data), ex=license_info["ttl"])
    logger.info(f"Redis cache -> {cache_key}")

    logger.success(f"下发激活配置 -> Use activation node")
    return signed_data


async def resolve_predict(
        x_app_id: str,
        x_app_token: str,
        x_app_region: str,
        x_app_version: str,
        a: str,
        t: int,
        n: str,
        cache: "redis_cache.RedisCache"
) -> dict:

    app_name, app_desc, *_ = a.lower().strip(), a, t, n

    signature.verify_signature(
        x_app_id, x_app_token, public_key=f"{app_name}_{const.BASE_PUBLIC_KEY}"
    )

    cache_key = f"Predict Server:{app_desc}"

    if cached := await cache.redis_get(cache_key):
        logger.success(f"下发缓存推理服务 -> {cache_key}")
        return json.loads(cached)

    expire_at = int(time.time()) + 180  # 3分钟有效期
    token = signature.sign_token(app_desc, expire_at, shared_secret)

    online = {
        "token": token,
        "expire_at": expire_at,
        "file_key": "",
        "upload_url": "",
        "commit_url": ""
    }

    license_info = {
        "configuration": {},
        "online": online,
        "url": f"https://plaxtonflarion--inference-inferenceservice-predict.modal.run",
        "ttl": 86400,
        "region": x_app_region,
        "version": x_app_version,
        "message": f"Online predict service"
    }

    signed_data = signature.signature_license(
        license_info, private_key=f"{app_name}_{const.BASE_PRIVATE_KEY}"
    )
    await cache.redis_set(cache_key, json.dumps(signed_data), ex=license_info["ttl"])
    logger.info(f"Redis cache -> {cache_key}")

    logger.success(f"下发推理服务 -> Online predict service")
    return signed_data


if __name__ == '__main__':
    pass
