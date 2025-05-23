import time
from loguru import logger
from fastapi import (
    Request, HTTPException
)
from common import const
from services import signature

BOOTSTRAP_RATE_LIMIT = {}


def enforce_rate_limit(request: "Request", limit: int = 5, window: int = 60) -> None:
    ip, now = request.client.host, time.time()

    logger.info(f"ip address: {ip}")

    BOOTSTRAP_RATE_LIMIT.setdefault(ip, [])
    BOOTSTRAP_RATE_LIMIT[ip] = [
        t for t in BOOTSTRAP_RATE_LIMIT[ip] if now - t < window
    ]

    if len(BOOTSTRAP_RATE_LIMIT[ip]) >= limit:
        raise HTTPException(429, f"Too many requests")

    BOOTSTRAP_RATE_LIMIT[ip].append(now)


def resolve_bootstrap(
        x_app_id: str,
        x_app_token: str,
        x_app_region: str,
        x_app_version: str,
        a: str,
        t: int,
        n: str
) -> dict:

    app_name, app_desc, *_ = a.lower().strip(), a, t, n

    signature.verify_signature(
        x_app_id, x_app_token, public_key=f"{app_name}_{const.BASE_PUBLIC_KEY}"
    )

    license_info = {
        "activation_url": f"https://license-server-s68o.onrender.com/sign",
        "region": x_app_region,
        "version": x_app_version,
        "ttl": 86400,
        "message": f"Use activation node"
    }

    return signature.signature_license(
        license_info, private_key=f"{app_name}_{const.BASE_PRIVATE_KEY}"
    )


if __name__ == '__main__':
    pass