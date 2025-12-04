#  ____                     _         _               ____             _
# |  _ \ ___ _ __ _ __ ___ (_)___ ___(_) ___  _ __   |  _ \ ___  _   _| |_ ___ _ __
# | |_) / _ \ '__| '_ ` _ \| / __/ __| |/ _ \| '_ \  | |_) / _ \| | | | __/ _ \ '__|
# |  __/  __/ |  | | | | | | \__ \__ \ | (_) | | | | |  _ < (_) | |_| | ||  __/ |
# |_|   \___|_|  |_| |_| |_|_|___/___/_|\___/|_| |_| |_| \_\___/ \__,_|\__\___|_|
#

from loguru import logger
from fastapi import APIRouter
from schemas.model import LicenseRequest
from services import signature

permission_router = APIRouter(tags=["Permission"])


@permission_router.post(path="/sign")
async def sign(
    req: "LicenseRequest"
):
    """
    授权签名接口。

    根据请求信息生成签名证书（License 文件），支持客户端激活验证。
    """
    logger.info(f"signature request: {req}")

    return signature.manage_signature(req)


if __name__ == '__main__':
    pass
