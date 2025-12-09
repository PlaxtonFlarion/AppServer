#  ____                       _
# / ___| _ __   ___  ___  ___| |__
# \___ \| '_ \ / _ \/ _ \/ __| '_ \
#  ___) | |_) |  __/  __/ (__| | | |
# |____/| .__/ \___|\___|\___|_| |_|
#       |_|
#

from fastapi import (
    APIRouter, Request, Query
)
from schemas.cognitive import (
    SpeechRequest, SpeechResponse
)

speech_router = APIRouter(tags=["Speech"])


@speech_router.get(
    path="/speech-meta",
    operation_id="api_speech_meta"
)
async def api_speech_meta(
    request: Request,
    a: str = Query(..., alias="a"),
    t: int = Query(..., alias="t"),
    n: str = Query(..., alias="n")
):
    """
    获取语音合成格式列表。

    返回可用的语音格式、语调模型与语言设置。
    """

    return await request.app.state.azure.tts_meta(
        request, a, t, n
    )


@speech_router.post(
    path="/speech-voice",
    response_model=SpeechResponse,
    operation_id="api_speech_voice"
)
async def api_speech_voice(
    req: SpeechRequest,
    request: Request
):
    """
    合成语音音频文件。

    提交语音内容与目标格式，返回可下载的音频文件或链接。
    """

    return await request.app.state.azure.tts_audio(
        req, request
    )


if __name__ == '__main__':
    pass
