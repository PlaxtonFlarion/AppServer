#   ____
#  / ___|___  _ __ ___  _ __ ___   ___  _ __
# | |   / _ \| '_ ` _ \| '_ ` _ \ / _ \| '_ \
# | |__| (_) | | | | | | | | | | | (_) | | | |
#  \____\___/|_| |_| |_|_| |_| |_|\___/|_| |_|
#

import json
import math
import time
import httpx
import random
import asyncio
import hashlib
from loguru import logger
from fastapi import (
    Request, HTTPException
)
from schemas.cognitive import LicenseResponse
from schemas.errors import BizError
from services.domain.standard import signature
from services.infrastructure.cache.upstash import UpStash
from services.infrastructure.db.supabase import Supabase
from utils import (
    const, toolset
)


# workflow: bootstrap
async def resolve_bootstrap(
    request: Request,
    a: str,
    t: int,
    n: str
) -> LicenseResponse:

    app_name, app_desc, *_ = a.lower().strip(), a, t, n

    x_app_region  = request.state.x_app_region
    x_app_version = request.state.x_app_version

    cache_key = f"{app_desc}:Activation"

    cache: UpStash = request.app.state.cache

    if cached := await cache.get(cache_key):
        logger.success(f"下发缓存激活配置 -> {cache_key}")
        signed_data = signature.signature_license(
            cached, private_key=f"{app_name}_{const.BASE_PRIVATE_KEY}"
        )
        return LicenseResponse(**signed_data)

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
    await cache.set(cache_key, license_info, ex=ttl)
    logger.info(f"Redis cache -> {cache_key}")

    logger.success(f"下发激活配置 -> Use activation node")
    return LicenseResponse(**signed_data)


# workflow: configuration
async def resolve_configuration(
    request: Request,
    a: str,
    t: int,
    n: str
) -> LicenseResponse:

    app_name, app_desc, *_ = a.lower().strip(), a, t, n

    x_app_region  = request.state.x_app_region
    x_app_version = request.state.x_app_version

    cache_key = f"{app_desc}:Configuration"

    cache: UpStash = request.app.state.cache

    if cached := await cache.get(cache_key):
        logger.info(f"下发缓存全局配置 -> {cache_key}")
        signed_data = signature.signature_license(
            cached, private_key=f"{app_name}_{const.BASE_PRIVATE_KEY}"
        )
        return LicenseResponse(**signed_data)

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
    await cache.set(cache_key, license_info, ex=ttl)
    logger.info(f"Redis cache -> {cache_key}")

    logger.success(f"下发全局配置 -> Use global configuration")
    return LicenseResponse(**signed_data)


# workflow: Keepalive Render
async def keepalive_render() -> dict:
    """Render 保活"""

    def calc_primes() -> int:
        primes = []
        for i in range(10000, random.randint(20000, 30000)):
            for j in range(2, int(i ** 0.5) + 1):
                if i % j == 0: break
            else:
                primes.append(i)
        return sum(p * p for p in primes) & 0xFFFFFFFF

    def string_hash_ops() -> int:
        base_string = "CPUKeepAlive"
        hash_result = 0
        for i in range(random.randint(30000, 60000)):
            s = (base_string + str(i)).encode()
            h = int(hashlib.md5(s).hexdigest(), 16)
            hash_result ^= h
        return hash_result & 0xFFFFFFFF

    def sort_random_numbers() -> float:
        arr = [random.random() for _ in range(random.randint(100000, 300000))]
        arr.sort()
        return sum(math.log1p(v * 1000) for v in arr[:min(1000, len(arr))])

    task_map = {
        "calc" : calc_primes,
        "hash" : string_hash_ops,
        "sort" : sort_random_numbers
    }
    task = random.choice(list(task_map.keys()))
    func = task_map[task]

    start    = time.time()
    result   = func()
    duration = time.time() - start

    logger.info(f"🟢 Render online | target={task} | actual={duration:.2f}s")
    await asyncio.sleep(random.uniform(0.1, 1.0))

    return {
        "status"    : "pong",
        "task"      : task,
        "result"    : result,
        "duration"  : round(duration, 3),
        "timestamp" : time.time()
    }


# workflow: Keepalive Supabase
async def keepalive_supabase(request: Request) -> dict:
    """Supabase 保活"""

    supabase: Supabase = request.app.state.supabase

    params  = {"select": "id", "limit": 1}

    try:
        async with httpx.AsyncClient(headers=supabase.headers, timeout=90) as client:
            resp = await client.request("GET", supabase.url, params=params)
            resp.raise_for_status()

            logger.info("🟢 Supabase online")
            return {
                "status"      : "OK",
                "message"     : "Supabase online",
                "timestamp"   : int(time.time()),
                "http_status" : resp.status_code
            }

    except httpx.HTTPStatusError as e:
        logger.warning(f"🟡 Supabase offline: {e.response.status_code}")
        raise BizError(
            status_code=503,
            detail=f"Supabase offline ({e.response.status_code}): {e.response.text}"
        )

    except httpx.ConnectError as e:
        logger.error(f"🔴 Supabase connection error: {e}")
        raise BizError(
            status_code=502,
            detail=f"Supabase unreachable: {str(e)}"
        )


# workflow: Keepalive Modal
async def keepalive_modal() -> dict:
    """Modal 保活"""

    expire_at = int(time.time()) + 86400
    token     = signature.sign_token("Modal", expire_at)
    headers   = {const.TOKEN_FORMAT: token}

    try:
        async with httpx.AsyncClient(headers=headers, timeout=90) as client:
            resp = await client.request("GET", const.MODAL_SERVICE)
            resp.raise_for_status()

            logger.info("🟢 Modal online")
            return {
                "status"      : "OK",
                "message"     : "Modal online",
                "timestamp"   : int(time.time()),
                "http_status" : resp.status_code
            }

    except httpx.HTTPStatusError as e:
        logger.warning(f"🟡 Modal offline: {e.response.status_code}")
        raise HTTPException(
            status_code=503,
            detail=f"Modal offline ({e.response.status_code}): {e.response.text}"
        )

    except httpx.ConnectError as e:
        logger.error(f"🔴 Modal connection error: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"Modal unreachable: {str(e)}"
        )


if __name__ == '__main__':
    pass
