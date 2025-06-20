#      _
#     / \    _____   _ _ __ ___
#    / _ \  |_  / | | | '__/ _ \
#   / ___ \  / /| |_| | | |  __/
#  /_/   \_\/___|\__,_|_|  \___|
#

import io
import httpx
from loguru import logger
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from services import signature
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
            x_app_token: str
    ) -> "StreamingResponse":
        app_name, app_desc = req.a.lower().strip(), req.a

        signature.verify_signature(
            x_app_id, x_app_token, public_key=f"{app_name}_{const.BASE_PUBLIC_KEY}"
        )

        logger.info(f"{req.voice} -> {req.speak}")

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

        try:
            async with httpx.AsyncClient(headers=HEADERS, timeout=10) as client:
                response = await client.request("POST", azure_tts_url, content=ssml.encode(const.CHARSET))
                response.raise_for_status()
                logger.info(f"下发音频 -> {cfg}")
                return StreamingResponse(
                    io.BytesIO(response.content),
                    headers={"Content-Disposition": f'inline; filename="speech.{cfg["ext"]}"'},
                    media_type=cfg["mime"]
                )
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ {e.response.status_code} {e.response.text}")
            raise HTTPException(status_code=500, detail=f"内部错误: {e}")


if __name__ == '__main__':
    pass
