import time
from loguru import logger
from fastapi import (
    Request, HTTPException
)
from common import (
    const, utils
)
from services import signature

env = utils.current_env(const.ACTIVATION_URL)
activation_url = env[const.ACTIVATION_URL]

BOOTSTRAP_RATE_LIMIT = {}


def enforce_rate_limit(request: "Request", limit: int = 5, window: int = 60) -> None:
    """
    对请求 IP 进行限流控制，防止过于频繁的访问。

    Parameters
    ----------
    request : Request
        当前的 HTTP 请求对象，需包含客户端 IP 地址字段。

    limit : int, optional
        在时间窗口内允许的最大请求次数，默认值为 5。

    window : int, optional
        滑动时间窗口的长度（单位：秒），默认值为 60 秒。

    Raises
    ------
    HTTPException
        若请求频率超过设定限制，返回 429 状态码（Too Many Requests）。

    Notes
    -----
    - 使用全局字典 `BOOTSTRAP_RATE_LIMIT` 存储每个 IP 的请求时间戳；
    - 在每次请求时，过滤掉时间窗口外的记录；
    - 如果保留的时间戳数量达到上限，立即拒绝请求；
    - 本函数适合用于登录、激活、验证码等敏感接口的请求节流。
    """
    ip, now = request.client.host, time.time()

    logger.info(f"ip address: {ip}")

    BOOTSTRAP_RATE_LIMIT.setdefault(ip, [])
    BOOTSTRAP_RATE_LIMIT[ip] = [
        t for t in BOOTSTRAP_RATE_LIMIT[ip] if now - t < window
    ]

    if len(BOOTSTRAP_RATE_LIMIT[ip]) >= limit:
        raise HTTPException(429, f"Too many requests")

    BOOTSTRAP_RATE_LIMIT[ip].append(now)


def resolve_bootstrap(
        x_app_id: str,
        x_app_token: str,
        x_app_region: str,
        x_app_version: str,
        a: str,
        t: int,
        n: str
) -> dict:
    """
    处理引导授权请求，校验签名并生成授权许可响应。

    Parameters
    ----------
    x_app_id : str
        客户端提交的应用 ID，用于身份识别和签名校验。

    x_app_token : str
        客户端签名内容，用于校验合法性。

    x_app_region : str
        客户端所属区域或节点标识。

    x_app_version : str
        客户端当前版本号。

    a : str
        应用名称（原始），用于确定私钥和公钥前缀。

    t : int
        时间戳，用于签名数据组成的一部分。

    n : str
        随机数或 nonce，参与签名构造。

    Returns
    -------
    dict
        返回签名后的授权许可信息，包括激活地址、版本、区域等元数据。

    Notes
    -----
    - 应用名 `a` 会被标准化（转小写）后作为公钥/私钥前缀；
    - 使用 `signature.verify_signature()` 验证客户端请求合法性；
    - 构造授权信息字典后，通过私钥签名生成最终结果；
    - 返回结构可作为服务端的响应 JSON 输出。

    Raises
    ------
    SignatureVerificationError
        如果签名校验失败，则中止流程并抛出异常（假设 `verify_signature` 内部处理）。
    """
    app_name, app_desc, *_ = a.lower().strip(), a, t, n

    signature.verify_signature(
        x_app_id, x_app_token, public_key=f"{app_name}_{const.BASE_PUBLIC_KEY}"
    )

    license_info = {
        "activation_url": activation_url,
        "region": x_app_region,
        "version": x_app_version,
        "ttl": 86400,
        "message": f"Use activation node"
    }

    return {
        "msg": "success",
        "sign": signature.signature_license(
            license_info, private_key=f"{app_name}_{const.BASE_PRIVATE_KEY}"
        )
    }


if __name__ == '__main__':
    pass