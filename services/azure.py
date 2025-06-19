#      _
#     / \    _____   _ _ __ ___
#    / _ \  |_  / | | | '__/ _ \
#   / ___ \  / /| |_| | | |  __/
#  /_/   \_\/___|\__,_|_|  \___|
#

import io
import httpx
import typing
from loguru import logger
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from common import (
    utils, const
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
    async def tts_audio(ssml: str) -> "StreamingResponse":
        try:
            async with httpx.AsyncClient(headers=HEADERS, timeout=10) as client:
                response = await client.request("POST", azure_tts_url, content=ssml.encode(const.CHARSET))
                response.raise_for_status()
                return StreamingResponse(
                    io.BytesIO(response.content),
                    media_type="audio/mpeg",
                    headers={"Content-Disposition": 'inline; filename="speech.mp3"'}
                )
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ {e.response.status_code} {e.response.text}")
            raise HTTPException(status_code=500, detail=f"内部错误: {e}")

    @staticmethod
    async def build_ssml(
            speak: str,
            voice: str,
            rate: str,
            pitch: str,
            volume: str,
            style: typing.Optional[str] = None,
            style_degree: typing.Optional[str] = None
    ) -> str:

        logger.info(f"{voice} -> {speak}")

        prosody = f"<prosody rate='{rate}' pitch='{pitch}' volume='{volume}'>{speak}</prosody>"

        if style:
            style_tag = f"<mstts:express-as style='{style}'"
            if style_degree:
                style_tag += f" styledegree='{style_degree}'"
            style_tag += f">{prosody}</mstts:express-as>"
            body = style_tag
        else:
            body = prosody

        return f"""
        <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis'
               xmlns:mstts='http://www.w3.org/2001/mstts'
               xml:lang='zh-CN'>
            <voice name='{voice}'>{body}</voice>
        </speak>
        """.strip()



if __name__ == '__main__':
    pass
