#   ____  ____    ____  _
#  |  _ \|___ \  / ___|| |_ ___  _ __ __ _  __ _  ___
#  | |_) | __) | \___ \| __/ _ \| '__/ _` |/ _` |/ _ \
#  |  _ < / __/   ___) | || (_) | | | (_| | (_| |  __/
#  |_| \_\_____| |____/ \__\___/|_|  \__,_|\__, |\___|
#                                          |___/
#

import os
import json
import boto3
import typing
import zipfile
from pathlib import Path
from loguru import logger
from botocore.client import Config
from botocore.exceptions import ClientError
from boto3.s3.transfer import TransferConfig
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from utils import (
    const, toolset
)

env = toolset.current_env(
    const.R2_BUCKET_KEY, const.R2_BUCKET_USR, const.R2_BUCKET_PWD,
    const.R2_BUCKET_URL, const.R2_PUBLIC_URL
)

r2_bucket_key = env[const.R2_BUCKET_KEY]
r2_bucket_usr = env[const.R2_BUCKET_USR]
r2_bucket_pwd = env[const.R2_BUCKET_PWD]
r2_bucket_url = env[const.R2_BUCKET_URL]
r2_public_url = env[const.R2_PUBLIC_URL]


class R2Storage(object):

    def __init__(self):
        self.r2_bucket_url = r2_bucket_url
        self.r2_public_url = r2_public_url

        self.r2_client = boto3.client(
            "s3",
            endpoint_url=r2_bucket_url,
            aws_access_key_id=r2_bucket_usr,
            aws_secret_access_key=r2_bucket_pwd,
            config=Config(signature_version="s3v4"),
            region_name="auto"
        )

    def upload_file(
        self,
        key: str,
        content: bytes,
        content_type: str,
        disposition_filename: str
    ) -> str:
        """
        上传任意文件至 R2。默认设置为私有对象，可通过签名访问。
        """
        extra = {
            "ContentType"        : content_type,
            "ContentDisposition" : f'inline; filename="{disposition_filename}"'
        }

        self.r2_client.put_object(
            Bucket=const.BUCKET, Key=key, Body=content, **extra
        )
        logger.info(f"📤 R2 上传完成 -> {key}")

        return key

    def signed_url_for_stream(
        self,
        key: str,
        expires_in: int,
        disposition_filename: str
    ) -> str:
        """
        生成支持播放 + 下载的签名 URL，Content-Disposition 为 inline。
        """
        signed_url = self.r2_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": const.BUCKET,
                "Key": key,
                "ResponseContentDisposition": f'inline; filename="{disposition_filename}"'
            },
            ExpiresIn=expires_in
        )
        logger.info(f"R2 签名完成 -> {key}")

        return signed_url

    def file_exists(
        self,
        key: str
    ) -> typing.Optional[bool]:
        """
        检查文件是否已存在于 R2。
        """
        try:
            self.r2_client.head_object(Bucket=const.BUCKET, Key=key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            logger.error(f"R2 检查失败: {e}")

    def compress_and_upload_folder(
        self,
        folder_path: str,
        r2_prefix: str,
        display_name: str,
        *,
        bucket: str = const.BUCKET
    ) -> dict:
        """
        压缩指定文件夹并上传至 R2 存储。

        Parameters
        ----------
        folder_path : str
            本地文件夹的路径。

        r2_prefix : str
            上传到 R2 的目标路径前缀（如 "model-store"）。

        display_name : str
            用作压缩包文件名和归档相对路径的命名。

        bucket : str, optional
            R2 的存储桶名称，默认使用全局 const.BUCKET。

        Returns
        -------
        dict
            文件元数据信息。
        """
        folder_path = Path(folder_path)
        if not folder_path.exists() or not folder_path.is_dir():
            raise FileNotFoundError(f"❌ 目录不存在: {folder_path}")

        file_count = sum(len(files) for _, _, files in os.walk(folder_path))
        if file_count == 0:
            raise ValueError(f"❌ 目录为空，无法压缩上传: {folder_path}")

        zip_name = f"{display_name}.zip"
        zip_path = Path("/tmp") / zip_name

        try:
            # 压缩目录
            logger.info(f"📦 压缩目录 {folder_path} 到 {zip_path}")
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(folder_path):
                    for file in files:
                        abs_path = os.path.join(root, file)
                        rel_path = os.path.relpath(abs_path, folder_path)
                        zipf.write(abs_path, arcname=os.path.join(display_name, rel_path))
            logger.success(f"✅ 目录已压缩为 {zip_path}")

            # 上传配置
            config = TransferConfig(
                multipart_threshold=50 * 1024 * 1024,
                multipart_chunksize=50 * 1024 * 1024
            )
            r2_key = f"{r2_prefix.rstrip('/')}/{zip_name}"

            logger.info(f"🚀 上传到 R2: {bucket}/{r2_key}")
            self.r2_client.upload_file(
                Filename=str(zip_path),
                Bucket=bucket,
                Key=r2_key,
                ExtraArgs={
                    "ContentType": "application/zip",
                    "ContentDisposition": f'attachment; filename="{zip_name}"'
                },
                Config=config
            )
            logger.success(f"✅ 上传成功: {r2_key}")

            # 构建元信息
            metadata = toolset.generate_metadata(zip_path, display_name)
            logger.success(metadata)

            return metadata

        finally:
            # 清理临时压缩包
            if zip_path.exists():
                os.remove(zip_path)
                logger.info(f"🧹 本地压缩文件已清理: {zip_path}")

    def upload_openapi(self, app: "FastAPI") -> None:
        """服务启动时生成最新 Swagger 并上传至 R2"""

        r2_key = "docs/swagger/openapi.json"

        schema = get_openapi(
            title=app.title, version=app.version, routes=app.routes
        )

        self.upload_file(
            key=r2_key,
            content=json.dumps(schema, indent=2).encode(),
            content_type="application/json",
            disposition_filename="swagger.json"
        )


if __name__ == '__main__':
    pass
