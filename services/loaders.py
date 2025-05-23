import time
from loguru import logger
from fastapi import (
    Request, HTTPException
)
from services import signature

BOOTSTRAP_RATE_LIMIT = {}


def enforce_rate_limit(request: "Request", limit: int = 5, window: int = 60) -> None:
    ip = request.client.host
    now = time.time()

    logger.info(f"ip address: {ip}")

    BOOTSTRAP_RATE_LIMIT.setdefault(ip, [])
    BOOTSTRAP_RATE_LIMIT[ip] = [
        t for t in BOOTSTRAP_RATE_LIMIT[ip] if now - t < window
    ]

    if len(BOOTSTRAP_RATE_LIMIT[ip]) >= limit:
        raise HTTPException(status_code=429, detail="Too many requests")

    BOOTSTRAP_RATE_LIMIT[ip].append(now)


def resolve_bootstrap(
        x_app_id: str,
        x_app_token: str,
        x_app_region: str,
        x_app_version: str,
        public_key_file: str
) -> dict:

    signature.verify_signature(x_app_id, x_app_token, public_key_file)

    return {
        "activation_url": f"https://license-server-s68o.onrender.com/sign",
        "region": x_app_region,
        "version": x_app_version,
        "ttl": 86400,
        "message": "Use default activation node"
    }


if __name__ == '__main__':
    pass