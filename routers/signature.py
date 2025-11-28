from loguru import logger
from fastapi import APIRouter
from common import models
from services import signature

router = APIRouter(tags=["Signature"])


@router.post(path="/sign")
async def sign(
    req: "models.LicenseRequest"
):
    """
    授权签名接口。

    根据请求信息生成签名证书（License 文件），支持客户端激活验证。
    """
    logger.info(f"signature request: {req}")

    return signature.manage_signature(req)


if __name__ == '__main__':
    pass
