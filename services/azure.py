#      _
#     / \    _____   _ _ __ ___
#    / _ \  |_  / | | | '__/ _ \
#   / ___ \  / /| |_| | | |  __/
#  /_/   \_\/___|\__,_|_|  \___|
#

import httpx
from loguru import logger
from common import (
    utils, const
)
from services import signature

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

    def __init__(self, x_app_id: str, x_app_token: str, a: str, t: int, n: str):
        self.x_app_id = x_app_id
        self.x_app_token = x_app_token
        self.a = a
        self.t = t
        self.n = n

    async def authorization(self) -> None:
        app_name, app_desc, *_ = self.a.lower().strip(), self.a, self.t, self.n

        signature.verify_signature(
            self.x_app_id, self.x_app_token, public_key=f"{app_name}_{const.BASE_PUBLIC_KEY}"
        )

    async def tts_audio(self, speak: str, voice: str) -> bytes:
        await self.authorization()

        ssml = f"""
        <speak version='1.0' xml:lang='zh-CN'>
            <voice name='{voice}'>{speak}</voice>
        </speak>
        """

        logger.info(f"{voice} -> {speak}")

        async with httpx.AsyncClient(headers=HEADERS, timeout=10) as client:
            response = await client.request(
                "POST", azure_tts_url, content=ssml.encode(const.CHARSET)
            )
            return response.content


if __name__ == '__main__':
    pass
