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
    BaseModel, Field, ConfigDict
)


class LicenseRequest(BaseModel):
    """
    License Creation Request

    Parameters
    ----------
    a : str
        应用标识，可用于区分调用来源。
    t : int
        请求时间戳（Unix 秒），用于与签名校验关联。
    n : str
        设备或节点唯一名称（client_id / node_name）。
    code : str
        授权码或凭证验证码，用于后台校验合法性。
    castle : str
        环境标识，例如 "prod" / "test" / "dev"。
    license_id : str, optional
        续期时可携带的已有 license ID，没有则视为新申请。
    """

    a: str = Field(..., description="应用标识，例如应用名称或客户端ID")
    t: int = Field(..., description="请求时间戳(Unix)，用于签名验权")
    n: str = Field(..., description="节点Device/Client标识，用于区分请求发起者")
    code: str = Field(..., description="授权码，用于生成license的秘钥凭证")
    castle: str = Field(..., description="环境标识，例如 prod/test/dev")
    license_id: typing.Optional[str] = Field(None, description="续期时传入旧LicenseID，新生成可不传")

    model_config = ConfigDict(from_attributes=True)


class LicenseResponse(BaseModel):
    """
    License Response

    Parameters
    ----------
    data : str
        Base64编码后的授权载荷(JSON)，需要客户端解码以获取完整内容。
    signature : str
        Base64编码的签名，用于验证license完整性与合法来源。
    """

    data: str = Field(..., description="Base64编码后的 License 数据载荷(JSON encoded)")
    signature: str = Field(..., description="Base64编码的数字签名，用于校验授权合法性")

    model_config = ConfigDict(from_attributes=True)


class PredictResponse(BaseModel):
    """
    Predict Service License Response

    Parameters
    ----------
    configuration : dict
        推理服务配置内容（预留字段，默认为空对象）。
    available : bool
        推理服务是否可用。
    expire_at : int
        license 到期时间戳 (Unix Time)。
    timeout : float
        请求最大等待时间，单位秒。
    content_type : str
        推理 API 期望的 Content-Type。
    auth_header : str
        鉴权头格式，例如 "Bearer {token}"。
    token : str
        生成的访问签名 Token。
    method : str
        推理调用使用的请求方法（通常 POST）。
    url : str
        推理服务调用地址。
    ttl : int
        当前 license 有效期秒数。
    region : str
        服务区域标识，例如 "us-east-1"。
    version : str
        推理服务版本号。
    message : str
        返回状态信息。
    """

    configuration: dict[str, typing.Any] = Field({}, description="推理配置对象")
    available: bool = Field(..., description="推理服务是否可用")
    expire_at: int = Field(..., description="过期时间戳")
    timeout: float = Field(60.0, description="推理请求超时(秒)")
    content_type: str = Field("multipart/form-data", description="请求内容类型")
    auth_header: str = Field(..., description="鉴权头格式")
    token: str = Field(..., description="签名 Token")
    method: str = Field("POST", description="请求方式")
    url: str = Field(..., description="推理调用地址")
    ttl: int = Field(..., description="剩余有效期(秒)")
    region: str = Field(..., description="区域标识")
    version: str = Field(..., description="版本号")
    message: str = Field("Predict service online", description="响应状态消息")

    model_config = ConfigDict(from_attributes=True)


class SpeechRequest(BaseModel):
    """
    Speech Request

    Parameters
    ----------
    a : str
        应用ID签名字段（参与鉴权）
    t : int
        时间戳（秒级）
    n : str
        随机nonce，防重放
    speak : str
        文本内容，将合成为语音
    voice : str, default: "zh-CN-XiaoxiaoNeural"
        使用的语音名称
    waver : str, optional, default: "mp3"
        输出音频格式，如 `mp3` / `wav`
    rater : str, optional, default: "0%"
        语速设置，例如 `+20%`、`-10%`
    pitch : str, optional, default: "0%"
        音调设置，如 `+5%`
    volume : str, optional, default: "default"
        音量设置，例 `+0dB`
    manner : str, optional
        情绪表达方式，如 `cheerful`
    degree : str, optional
        风格强度，如 `1.0`, `2.0`
    """

    a: str = Field(..., description="应用ID签名字段")
    t: int = Field(..., description="时间戳(秒级)，用于请求校验")
    n: str = Field(..., description="随机nonce，防重复请求")
    speak: str = Field(..., description="文本内容，将被合成为音频")
    voice: str = Field("zh-CN-XiaoxiaoNeural", description="语音名称")
    waver: typing.Optional[str] = Field("mp3", description="输出音频格式，如 mp3/wav")
    rater: typing.Optional[str] = Field("0%", description="语速，如 +20%、-10%")
    pitch: typing.Optional[str] = Field("0%", description="语调，如 +5%")
    volume: typing.Optional[str] = Field("default", description="音量，如 +0dB")
    manner: typing.Optional[str] = Field(None, description="情感风格，如 cheerful")
    degree: typing.Optional[str] = Field(None, description="风格强度，如 1.0、2.0")

    model_config = ConfigDict(from_attributes=True)


class SpeechResponse(BaseModel):
    """
    Response Model (Return Speech Audio URL)

    Parameters
    ----------
    url : str
        语音文件的签名下载地址，用于客户端直接访问。
    """
    url: str = Field(
        ...,
        description="语音音频文件签名下载地址，用于直接访问音频资源",
        examples=["https://cdn.xxx.com/audio/20250101/voice_xxx.wav?token=abc123"]
    )

    model_config = ConfigDict(from_attributes=True)


class Locator(BaseModel):
    """
    Locator

    Parameters
    ----------
    by : str
        定位方式，如 `id` / `xpath` / `css` / `bounds`
    value : str
        与定位方式匹配的值
    """
    by: str = Field(..., description="定位方式，如 id/xpath/css/bounds")
    value: str = Field(..., description="定位值")

    model_config = ConfigDict(from_attributes=True)


class HealRequest(BaseModel):
    """
    Healing Request

    Parameters
    ----------
    app_id : str
        应用ID，例如包名/域名
    page_id : str
        页面唯一ID，比如 Activity/URL/路由
    platform : str
        运行平台，可为 `android` `ios` `web`
    old_locator : Locator
        原始定位信息对象
    page_dump : str
        页面结构信息，Android为XML，Web为HTML
    screenshot : str, optional
        页面截图(Base64 PNG，可选)
    context : dict, optional
        上下文，例如测试用例ID、intent、自定义参数
    """

    app_id: str = Field(..., description="应用ID，如包名/域名")
    page_id: str = Field(..., description="页面ID，例如 Activity/URL/路由")
    platform: str = Field(..., description="android/web/ios")
    old_locator: Locator = Field(..., description="原始定位对象")
    page_dump: str = Field(..., description="页面dump：Android XML / Web HTML")
    screenshot: typing.Optional[str] = Field(None, description="base64截图(可选)")
    context: typing.Optional[dict] = Field(None, description="上下文信息，例如intent/测试ID")

    model_config = ConfigDict(from_attributes=True)


class HealResponse(BaseModel):
    """
    Healing Response

    Returns
    -------
    healed : bool
        是否成功修复定位
    confidence : float
        置信度 [0,1]
    new_locator : dict, optional
        修复后定位信息，如 {"by":"bounds","value":"[100,200][300,400]"}
    details : dict
        调试信息、候选定位、评分等
    """

    healed: bool = Field(..., description="是否成功自愈")
    confidence: float = Field(..., description="置信度 0~1")
    new_locator: typing.Optional[dict] = Field(
        None, description="新定位对象，例如 {'by':'bounds','value':'[100,200][300,400]'}"
    )
    details: dict = Field(
        default_factory=dict,
        description="调试信息/候选列表等"
    )

    model_config = ConfigDict(from_attributes=True)


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

    model_config = ConfigDict(from_attributes=True)


class Mix(BaseModel):

    app: dict[str, typing.Any] = Field(default_factory=dict)
    white_list: list[str] = Field(default_factory=list)
    rate_config: dict[str, typing.Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


if __name__ == '__main__':
    pass

