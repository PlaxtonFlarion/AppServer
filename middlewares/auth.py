#     _         _   _
#    / \  _   _| |_| |__
#   / _ \| | | | __| '_ \
#  / ___ \ |_| | |_| | | |
# /_/   \_\__,_|\__|_| |_|
#

import typing
from fastapi import Request
from schemas.cognitive import Mix
from schemas.errors import AuthorizationError
from services.domain.standard import signature
from services.infrastructure.cache.upstash import UpStash
from utils import const


async def jwt_auth_middleware(
    request: Request,
    call_next: typing.Callable
) -> typing.Any:
    """鉴权中间件"""

    cache: UpStash = request.app.state.cache

    mix = Mix(**await cache.get(const.MIX))

    public_paths = cached if (cached := mix.white_list) else const.PUBLIC_PATHS

    if request.url.path in public_paths:
        return await call_next(request)

    x_app_id      = request.headers.get("X-App-ID")
    x_app_token   = request.headers.get("X-App-Token")
    x_app_region  = request.headers.get("X-App-Region")
    x_app_version = request.headers.get("X-App-Version")

    if not x_app_id or not x_app_token:
        raise AuthorizationError(
            status_code=401, detail="Unauthorized"
        )

    try:
        signature.verify_jwt(x_app_id, x_app_token)
    except Exception as e:
        raise AuthorizationError(
            status_code=403, detail=str(e)
        )

    request.state.x_app_id      = x_app_id
    request.state.x_app_token   = x_app_token
    request.state.x_app_region  = x_app_region
    request.state.x_app_version = x_app_version

    return await call_next(request)


if __name__ == '__main__':
    pass
