#   ____  ____    ____  _
#  |  _ \|___ \  / ___|| |_ ___  _ __ __ _  __ _  ___
#  | |_) | __) | \___ \| __/ _ \| '__/ _` |/ _` |/ _ \
#  |  _ < / __/   ___) | || (_) | | | (_| | (_| |  __/
#  |_| \_\_____| |____/ \__\___/|_|  \__,_|\__, |\___|
#                                          |___/
#

import boto3
import typing
import asyncio
from loguru import logger
from botocore.client import Config
from common import (
    const, utils
)

env = utils.current_env(
    const.R2_BUCKET_KEY, const.R2_BUCKET_USR, const.R2_BUCKET_PWD,
    const.R2_BUCKET_URL, const.R2_PUBLIC_URL
)

r2_bucket_key = env[const.R2_BUCKET_KEY]
r2_bucket_usr = env[const.R2_BUCKET_USR]
r2_bucket_pwd = env[const.R2_BUCKET_PWD]
r2_bucket_url = env[const.R2_BUCKET_URL]
r2_public_url = env[const.R2_PUBLIC_URL]

r2_client = boto3.client(
    "s3",
    endpoint_url=r2_bucket_url,
    aws_access_key_id=r2_bucket_usr,
    aws_secret_access_key=r2_bucket_pwd,
    config=Config(signature_version="s3v4"),
    region_name="auto"
)


async def upload_file(
        key: str,
        content: bytes,
        content_type: str,
        disposition_filename: str,
) -> str:
    """
    上传任意文件至 R2。默认设置为私有对象，可通过签名访问。
    """
    extra = {
        "ContentType": content_type,
        "ContentDisposition": f'inline; filename="{disposition_filename}"'
    }

    await asyncio.to_thread(
        r2_client.put_object, Bucket=const.BUCKET, Key=key, Body=content, **extra
    )
    logger.info(f"R2 上传完成 -> {key}")
    return key


async def signed_url_for_stream_or_download(
        key: str,
        expires_in: int,
        disposition_filename: str
) -> str:
    """
    生成支持播放 + 下载的签名 URL，Content-Disposition 为 inline。
    """
    signed_url = await asyncio.to_thread(
        r2_client.generate_presigned_url, "get_object",
        Params={
            "Bucket": const.BUCKET,
            "Key": key,
            "ResponseContentDisposition": f'inline; filename="{disposition_filename}"'
        },
        ExpiresIn=expires_in
    )
    logger.info(f"R2 签名完成 -> {key}")
    return signed_url


async def file_exists(key: str) -> typing.Optional[bool]:
    """
    检查文件是否已存在于 R2。
    """
    try:
        await asyncio.to_thread(
            r2_client.head_object, Bucket=const.BUCKET, Key=key
        )
        return True
    except r2_client.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        logger.error(f"R2 检查失败: {e}")


if __name__ == '__main__':
    pass
