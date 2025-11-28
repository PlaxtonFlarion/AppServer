from loguru import logger
from common import models
from fastapi import (
    APIRouter, Request, Query
)
from services import azure

router = APIRouter(tags=["Speech"])


@router.get(path="/speech-meta")
async def speech_meta(
    request: "Request",
    a: str = Query(..., alias="a"),
    t: int = Query(..., alias="t"),
    n: str = Query(..., alias="n")
):
    """
    获取语音合成格式列表。

    返回可用的语音格式、语调模型与语言设置。
    """
    logger.info(f"voice request: {request.url}")

    return await azure.SpeechEngine.tts_meta(
        a, t, n
    )


@router.post(path="/speech-voice")
async def speech_voice(
    req: "models.SpeechRequest",
    request: "Request",
):
    """
    合成语音音频文件。

    提交语音内容与目标格式，返回可下载的音频文件或链接。
    """
    logger.info(f"voice request: {req}")

    return await azure.SpeechEngine.tts_audio(
        req, request.app.state.cache
    )


if __name__ == '__main__':
    pass
