#  ____  _                   _                    ____             _
# / ___|(_) __ _ _ __   __ _| |_ _   _ _ __ ___  |  _ \ ___  _   _| |_ ___ _ __
# \___ \| |/ _` | '_ \ / _` | __| | | | '__/ _ \ | |_) / _ \| | | | __/ _ \ '__|
#  ___) | | (_| | | | | (_| | |_| |_| | | |  __/ |  _ < (_) | |_| | ||  __/ |
# |____/|_|\__, |_| |_|\__,_|\__|\__,_|_|  \___| |_| \_\___/ \__,_|\__\___|_|
#          |___/
#

from loguru import logger
from fastapi import (
    APIRouter, Request
)
from schemas.cognitive import (
    LicenseRequest, LicenseResponse
)
from services.domain.standard import signature

signature_router = APIRouter(tags=["Signature"])


@signature_router.post(
    path="/sign",
    response_model=LicenseResponse,
    operation_id="api_sign"
)
async def api_sign(
    req: LicenseRequest,
    request: Request,
):
    """
    授权签名接口。

    根据请求信息生成签名证书（License 文件），支持客户端激活验证。
    """
    logger.info(f"signature request: {req}")

    return signature.manage_signature(req, request)


if __name__ == '__main__':
    pass
