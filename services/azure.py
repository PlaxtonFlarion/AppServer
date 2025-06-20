#      _
#     / \    _____   _ _ __ ___
#    / _ \  |_  / | | | '__/ _ \
#   / ___ \  / /| |_| | | |  __/
#  /_/   \_\/___|\__,_|_|  \___|
#

import io
import json
from pathlib import Path

import httpx
import base64
import typing
import hashlib
from loguru import logger
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from services import (
    r2_storage, redis_cache, signature
)
from common import (
    const, models, utils
)

env = utils.current_env(
    const.AZURE_TTS_URL, const.AZURE_TTS_KEY
)

azure_tts_url = env[const.AZURE_TTS_URL]
azure_tts_key = env[const.AZURE_TTS_KEY]

HEADERS = {
    "User-Agent": "AzureTTSClient",
    "Content-Type": "application/ssml+xml",
    "X-Microsoft-OutputFormat": "audio-16khz-128kbitrate-mono-mp3",
    "Ocp-Apim-Subscription-Key": azure_tts_key
}


class SpeechEngine(object):

    @staticmethod
    async def tts_meta(
            x_app_id: str,
            x_app_token: str,
            a: str,
            t: int,
            n: str,
    ) -> dict:

        app_name, app_desc, *_ = a.lower().strip(), a, t, n

        signature.verify_signature(
            x_app_id, x_app_token, public_key=f"{app_name}_{const.BASE_PUBLIC_KEY}"
        )

        return {
            "formats": ["mp3"]
        }

    @staticmethod
    async def tts_audio(
            req: "models.SpeechRequest",
            x_app_id: str,
            x_app_token: str,
            cache: "redis_cache.RedisCache"
    ) -> typing.Any:

        # app_name, app_desc = req.a.lower().strip(), req.a

        # signature.verify_signature(
        #     x_app_id, x_app_token, public_key=f"{app_name}_{const.BASE_PUBLIC_KEY}"
        # )

        logger.info(f"{req.voice} -> {req.speak}")

        cache_key = "speech:" + hashlib.md5(
            f"{req.voice}|{req.speak}".encode(const.CHARSET)
        ).hexdigest()

        try:
            # 👉 优先读取 Redis
            if cached := await cache.redis_get(cache_key):
                cached = json.loads(cached)
                logger.info(f"下发缓存 URL -> {(cache_url := cached['url'])}")
                return {"url": cache_url}

            # 👉 构建 Cloudflare R2 的对象路径
            r2_key = f"speech-cache/{cache_key}.{req.waver}"
            r2_url = f"{r2_storage.r2_public_url}/{r2_key}"

            # 👉 如果 Cloudflare R2 中已存在，直接返回 URL
            if r2_storage.file_exists(r2_key):
                logger.info(f"R2 已存在 -> {r2_key}")
                await cache.redis_set(
                    cache_key, json.dumps(link := {"url": r2_url}), ex=86400
                )
                return link

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
                    "waver": "audio-16khz-128kbitrate-mono-mp3",
                    "mime": "audio/mpeg",
                    "ext": "mp3"
                },
                "wav": {
                    "waver": "riff-16khz-16bit-mono-pcm",
                    "mime": "audio/wav",
                    "ext": "wav"
                },
                "ogg": {
                    "waver": "ogg-16khz-16bit-mono-opus",
                    "mime": "audio/ogg",
                    "ext": "ogg"
                }
            }

            cfg = waver_map.get(req.waver.lower(), waver_map["mp3"])
            HEADERS["X-Microsoft-OutputFormat"] = cfg["waver"]

            async with httpx.AsyncClient(headers=HEADERS, timeout=10) as client:
                response = await client.request("POST", azure_tts_url, content=ssml.encode(const.CHARSET))
                response.raise_for_status()

                audio_bytes = response.content

                # 👉 上传 Cloudflare R2
                url = r2_storage.upload_audio(
                    key=r2_key,
                    content=audio_bytes,
                    content_type=cfg["mime"],
                    disposition_filename=f"speech.{cfg['ext']}"
                )

                # 👉 写入 Redis 缓存
                await cache.redis_set(cache_key, json.dumps(link := {"url": url}), ex=86400)
                logger.info(f"上传并下发 URL -> {url}")
                return link

        except httpx.HTTPStatusError as e:
            logger.error(f"❌ {e.response.status_code} {e.response.text}")
            raise HTTPException(status_code=500, detail=f"内部错误: {e}")


if __name__ == '__main__':
    pass
