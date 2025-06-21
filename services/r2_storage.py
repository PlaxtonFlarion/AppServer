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


async def upload_audio(
        key: str,
        content: bytes,
        content_type: str,
        disposition_filename: typing.Optional[str] = None,
) -> str:
    """
    上传音频至 R2，并返回 CDN 可访问链接。
    """
    extra = {
        "ContentType": content_type,
        "ACL": "public-read"
    }
    if disposition_filename:
        extra["ContentDisposition"] = f'inline; filename="{disposition_filename}"'

    await asyncio.to_thread(
        r2_client.put_object, Bucket=const.BUCKET, Key=key, Body=content, **extra
    )
    return f"{r2_public_url.rstrip('/')}/{key}"


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
