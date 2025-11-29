#  ____                       _       ____             _
# / ___| _ __   ___  ___  ___| |__   |  _ \ ___  _   _| |_ ___ _ __
# \___ \| '_ \ / _ \/ _ \/ __| '_ \  | |_) / _ \| | | | __/ _ \ '__|
#  ___) | |_) |  __/  __/ (__| | | | |  _ < (_) | |_| | ||  __/ |
# |____/| .__/ \___|\___|\___|_| |_| |_| \_\___/ \__,_|\__\___|_|
#       |_|
#

from loguru import logger
from common import models
from fastapi import (
    APIRouter, Request, Query
)
from services import azure

speech_router = APIRouter(tags=["Speech"])


@speech_router.get(path="/speech-meta")
async def speech_meta(
    a: str = Query(..., alias="a"),
    t: int = Query(..., alias="t"),
    n: str = Query(..., alias="n")
):
    """
    获取语音合成格式列表。

    返回可用的语音格式、语调模型与语言设置。
    """

    return await azure.SpeechEngine.tts_meta(a, t, n)


@speech_router.post(path="/speech-voice")
async def speech_voice(
    req: "models.SpeechRequest",
    request: "Request",
):
    """
    合成语音音频文件。

    提交语音内容与目标格式，返回可下载的音频文件或链接。
    """
    logger.info(f"voice request: {req}")

    cache = request.app.state.cache

    return await azure.SpeechEngine.tts_audio(req, cache)


if __name__ == '__main__':
    pass
