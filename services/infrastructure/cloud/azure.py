#      _
#     / \    _____   _ _ __ ___
#    / _ \  |_  / | | | '__/ _ \
#   / ___ \  / /| |_| | | |  __/
#  /_/   \_\/___|\__,_|_|  \___|
#

import json
import httpx
import typing
import hashlib
from loguru import logger
from fastapi import Request
from schemas.cognitive import SpeechRequest
from services.domain.standard import signature
from services.infrastructure.cache.upstash import UpStash
from services.infrastructure.storage.r2_storage import R2Storage
from utils import (
    const, toolset
)

env = toolset.current_env(
    const.AZURE_TTS_URL, const.AZURE_TTS_KEY
)

azure_tts_url = env[const.AZURE_TTS_URL]
azure_tts_key = env[const.AZURE_TTS_KEY]


class Azure(object):

    def __init__(self):
        self.headers = {
            "User-Agent"                : "AzureTTSClient",
            "Content-Type"              : "application/ssml+xml",
            "X-Microsoft-OutputFormat"  : "audio-16khz-128kbitrate-mono-mp3",
            "Ocp-Apim-Subscription-Key" : azure_tts_key
        }

    @staticmethod
    async def tts_meta(a: str, t: int, n: str) -> dict:
        app_name, app_desc, *_ = a.lower().strip(), a, t, n

        license_info = {
            "mode": {"enabled": False, "formats": ["mp3"]}
        }

        signed_data = signature.signature_license(
            license_info, private_key=f"{app_name}_{const.BASE_PRIVATE_KEY}"
        )

        return signed_data

    async def tts_audio(self, req: "SpeechRequest", request: "Request") -> "typing.Any":
        logger.info(f"{req.voice} -> {req.speak}")

        cache_key = "speech:" + hashlib.md5(
            f"{req.voice}|{req.speak}".encode(const.CHARSET)
        ).hexdigest()

        cache: "UpStash" = request.app.state.cache
        r2: "R2Storage"  = request.app.state.r2

        # 👉 优先读取 Redis（只存储对象 Key）
        if cached := await cache.redis_get(cache_key):
            cached   = json.loads(cached)
            r2_key   = cached["key"]
            filename = f"speech.{req.waver}"

            signed_url = r2.signed_url_for_stream(
                key=r2_key, expires_in=3600, disposition_filename=filename
            )
            logger.info(f"下发缓存签名 URL -> {signed_url}")
            return {"url": signed_url}

        # 👉 构建 R2 Key 和文件名
        r2_key   = f"speech-cache/{cache_key}.{req.waver}"
        filename = f"speech.{req.waver}"

        # 👉 如果 Cloudflare R2 已存在，生成签名 URL
        if r2.file_exists(r2_key):
            await cache.redis_set(cache_key, json.dumps({"key": r2_key}), ex=86400)
            logger.info(f"Redis cache -> {r2_key}")

            signed_url = r2.signed_url_for_stream(
                key=r2_key, expires_in=3600, disposition_filename=filename
            )
            logger.info(f"下发 R2 签名 URL -> {signed_url}")
            return {"url": signed_url}

        # 👉 生成 SSML
        prosody = f"<prosody rate='{req.rater}' pitch='{req.pitch}' volume='{req.volume}'>{req.speak}</prosody>"

        if req.manner:
            manner_tag = f"<mstts:express-as style='{req.manner}'"
            if req.degree:
                manner_tag += f" styledegree='{req.degree}'"
            manner_tag += f">{prosody}</mstts:express-as>"
            body = manner_tag
        else:
            body = prosody

        ssml = f"""
            <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis'
                   xmlns:mstts='http://www.w3.org/2001/mstts'
                   xml:lang='zh-CN'>
                <voice name='{req.voice}'>{body}</voice>
            </speak>
        """.strip()

        # 👉 音频格式配置
        waver_map = {
            "mp3": {
                "waver" : "audio-16khz-128kbitrate-mono-mp3",
                "mime"  : "audio/mpeg",
                "ext"   : "mp3"
            },
            "wav": {
                "waver" : "riff-16khz-16bit-mono-pcm",
                "mime"  : "audio/wav",
                "ext"   : "wav"
            },
            "ogg": {
                "waver" : "ogg-16khz-16bit-mono-opus",
                "mime"  : "audio/ogg",
                "ext"   : "ogg"
            }
        }

        cfg     = waver_map.get(req.waver.lower(), waver_map["mp3"])
        headers = self.headers.copy() | {"X-Microsoft-OutputFormat": cfg["waver"]}

        async with httpx.AsyncClient(headers=headers, timeout=10) as client:
            resp = await client.request("POST", azure_tts_url, content=ssml.encode(const.CHARSET))
            resp.raise_for_status()

            audio_bytes = resp.content
            filename    = f"speech.{cfg['ext']}"
            media_type  = cfg["mime"]

            # 👉 上传至 Cloudflare R2
            r2.upload_file(
                key=r2_key,
                content=audio_bytes,
                content_type=media_type,
                disposition_filename=filename
            )

            # 👉 写入 Redis 缓存（只存 Key）
            await cache.redis_set(cache_key, json.dumps({"key": r2_key}), ex=86400)
            logger.info(f"Redis cache -> {r2_key}")

            # 👉 生成签名 URL（每次请求都重新生成）
            signed_url = r2.signed_url_for_stream(
                key=r2_key, expires_in=3600, disposition_filename=filename
            )

            logger.info(f"上传并下发签名 URL -> {signed_url}")
            return {"url": signed_url}


if __name__ == '__main__':
    pass
