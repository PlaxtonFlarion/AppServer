#   __  __           _      _
#  |  \/  | ___   __| | ___| |___
#  | |\/| |/ _ \ / _` |/ _ \ / __|
#  | |  | | (_) | (_| |  __/ \__ \
#  |_|  |_|\___/ \__,_|\___|_|___/
#

import typing
from pydantic import (
    BaseModel, Field
)


class LicenseRequest(BaseModel):
    a: str
    t: int
    n: str

    code: str
    castle: str

    license_id: typing.Optional[str] = None


class SpeechRequest(BaseModel):
    a: str
    t: int
    n: str

    speak: str = Field(..., description="文本内容")
    voice: str = Field("zh-CN-XiaoxiaoNeural", description="语音名称")
    
    waver: typing.Optional[str] = Field("mp3", description="输出格式")
    rater: typing.Optional[str] = Field("0%", description="语速，如 +20%、-10%")
    pitch: typing.Optional[str] = Field("0%", description="语调，如 +5%")
    
    volume: typing.Optional[str] = Field("default", description="音量，如 +0dB")
    manner: typing.Optional[str] = Field(None, description="情感风格，如 cheerful")
    degree: typing.Optional[str] = Field(None, description="风格强度，如 1.0, 2.0")


if __name__ == '__main__':
    pass
