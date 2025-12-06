#   ____                  _ _   _
#  / ___|___   __ _ _ __ (_) |_(_)_   _____
# | |   / _ \ / _` | '_ \| | __| \ \ / / _ \
# | |__| (_) | (_| | | | | | |_| |\ V /  __/
#  \____\___/ \__, |_| |_|_|\__|_| \_/ \___|
#             |___/
#

import json
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


class Locator(BaseModel):
    by: str
    value: str


class HealRequest(BaseModel):
    app_id: str                              # 包名 or 域名
    page_id: str                             # Activity / URL / 路由
    platform: str                            # "android" / "web" / "ios"
    old_locator: "Locator"                   # 用例里原始定位
    page_dump: str                           # 整个页面的 dump：Android XML / Web HTML
    screenshot: typing.Optional[str] = None  # base64 PNG，可选
    context: typing.Optional[dict] = None    # 例如 intent、用例ID 等


class HealResponse(BaseModel):
    healed: bool                        # 是否成功自愈
    confidence: float                   # 置信度 [0,1]
    new_locator: typing.Optional[dict]  # 新定位信息，例如 {"by": "bounds", "value": "[..]"}
    details: dict = {}                  # 调试信息 / 候选列表等


class ElementNode(BaseModel):
    id: typing.Optional[str] = None
    text: typing.Optional[str] = None
    content_desc: typing.Optional[str] = None
    resource_id: typing.Optional[str] = None
    xpath: typing.Optional[str] = None
    class_name: typing.Optional[str] = None
    bounds: list[int] = Field(default_factory=list)
    extra: dict = Field(default_factory=dict)
    desc: typing.Optional[str] = None

    def __str__(self) -> str:
        return f"<ElementNode {self.class_name} text='{self.text}' id='{self.resource_id}'>"

    __repr__ = __str__

    def ensure_desc(self) -> str:
        if not self.desc:
            self.desc = self.create_desc()
        return self.desc

    def create_desc(self) -> str:
        parts = [
            f"text={self.text or ''}",
            f"content_desc={self.content_desc or ''}",
            f"resource_id={self.resource_id or ''}",
            f"xpath={self.xpath or ''}",
            f"class_name={self.class_name or ''}",
            f"bounds={json.dumps(self.bounds)}",
            f"extra={json.dumps(self.extra, ensure_ascii=False)}",
        ]
        return " | ".join(parts)

    def to_dict(self) -> dict:
        return {
            "id"           : self.id,
            "text"         : self.text,
            "content_desc" : self.content_desc,
            "resource_id"  : self.resource_id,
            "xpath"        : self.xpath,
            "class_name"   : self.class_name,
            "bounds"       : self.bounds,
            "extra"        : self.extra,
            "desc"         : self.ensure_desc(),
        }


if __name__ == '__main__':
    pass

