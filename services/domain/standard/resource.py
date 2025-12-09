#  ____
# |  _ \ ___  ___  ___  _   _ _ __ ___ ___
# | |_) / _ \/ __|/ _ \| | | | '__/ __/ _ \
# |  _ <  __/\__ \ (_) | |_| | | | (_|  __/
# |_| \_\___||___/\___/ \__,_|_|  \___\___|
#

import json
from loguru import logger
from fastapi import Request
from schemas.cognitive import LicenseResponse
from schemas.errors import BizError
from services.domain.standard import signature
from services.infrastructure.cache.upstash import UpStash
from services.infrastructure.storage.r2_storage import R2Storage
from utils import (
    const, toolset
)


async def resolve_template_download(
    request: Request,
    a: str,
    t: int,
    n: str
) -> LicenseResponse:
    """
    📦 模板文件列表下发接口（带签名 License 元信息返回）

    客户端可调用该接口获取可用的 HTML/业务模板清单，
    用于后续通过 /template-viewer 拉取具体模版内容。
    结果支持 Redis 缓存，加速多次访问。

    Workflow
    --------
    1) 从请求头解析客户端 region/version 信息
    2) 根据 app_desc 构建缓存 key，先尝试 Redis 命中
    3) 若无缓存则动态生成模板元信息并写入 Redis (TTL=1天)
    4) 使用私钥对返回内容进行签名，客户端可校验防篡改
    5) 返回 `LicenseResponse` → { data(base64), signature(base64) }

    Parameters
    ----------
    request : Request
        FastAPI 请求对象，需携带 `x_app_region` 与 `x_app_version`
        （在上游 Auth Middleware 中注入 request.state）
    a : str
        应用名称，如 "Framix" / "Memrix"，用于匹配模板资源
    t : int
        业务参数预留字段（版本/环境扩展）
    n : str
        预留扩展参数（业务 tag/渠道号 等）

    ==== Notes: Caching ====
    -------
    Redis key - {app_desc}:Template
    Cache TTL - 86400s (1 day)
    命中直接返回，不再重复构建字典

    Returns
    -------
    LicenseResponse
        - data      : base64(encoded JSON)
        - signature : base64(RSA signature)
        JSON 内部实际结构示例:

        {
            "template": {
                "template_atom_total.html": {
                    "filename": "template_atom_total.html",
                    "url": "https://api.appserverx.com/template-viewer"
                },
                ...
            },
            "ttl": 86400,
            "region": "<client-region>",
            "version": "<client-version>",
            "message": "Available templates for client to choose"
        }

    Raises
    ------
    无显式业务异常，鉴权与 JSONError 将交给全局中间件处理
    """

    app_name, app_desc, *_ = a.lower().strip(), a, t, n

    x_app_region  = request.state.x_app_region
    x_app_version = request.state.x_app_version

    cache_key = f"{app_desc}:Template"

    ttl = 86400

    cache: UpStash = request.app.state.cache

    if cached := await cache.get(cache_key):
        logger.success(f"下发缓存模版元信息 -> {cache_key}")
        license_info = cached
    else:
        stencil_info = {
            "Framix": {
                "template_atom_total.html": {
                    "filename" : "template_atom_total.html",
                    "url"      : "https://api.appserverx.com/template-viewer"
                },
                "template_line_total.html": {
                    "filename" : "template_line_total.html",
                    "url"      : "https://api.appserverx.com/template-viewer"
                },
                "template_main_share.html": {
                    "filename" : "template_main_share.html",
                    "url"      : "https://api.appserverx.com/template-viewer"
                },
                "template_main_total.html": {
                    "filename" : "template_main_total.html",
                    "url"      : "https://api.appserverx.com/template-viewer"
                },
                "template_view_share.html": {
                    "filename" : "template_view_share.html",
                    "url"      : "https://api.appserverx.com/template-viewer"
                },
                "template_view_total.html": {
                    "filename" : "template_view_total.html",
                    "url"      : "https://api.appserverx.com/template-viewer"
                }
            },
            "Memrix": {
                "unity_template.html": {
                    "filename" : "unity_template.html",
                    "url"      : "https://api.appserverx.com/template-viewer"
                }
            }
        }

        license_info = {
            "template" : stencil_info.get(app_desc, {}),
            "ttl"      : ttl,
            "region"   : x_app_region,
            "version"  : x_app_version,
            "message"  : "Available templates for client to choose"
        }
        await cache.set(cache_key, license_info, ex=ttl)
        logger.info(f"Redis cache -> {cache_key}")

    signed_data = signature.signature_license(
        license_info, private_key=f"{app_name}_{const.BASE_PRIVATE_KEY}"
    )

    logger.success(f"下发模版元信息 -> Available templates for client to choose")
    return LicenseResponse(**signed_data)


async def resolve_toolkit_download(
    request: Request,
    a: str,
    t: int,
    n: str,
    platform: str
) -> LicenseResponse:
    """
    🛠 工具包下载索引元信息下发接口（含签名 License 返回）

    根据应用标识与客户端平台（MacOS/Windows）返回对应可下载工具列表，
    通过 R2 Cloudflare 存储提供临时有效签名下载链接。
    接口支持 Redis 缓存，减少重复构建及提高响应性能。

    Workflow
    --------
    1) 识别平台 → Windows / MacOS
    2) 构建 Redis Key: {app}:{platform}:Toolkit
    3) 若缓存存在直接返回；否则装载工具元数据并写入缓存
    4) 生成临时下载链接（Cloudflare R2 Signed URL，有效期 1h）
    5) 加签封装为 LicenseResponse → 客户端可验签防篡改

    Parameters
    ----------
    request : Request
        FastAPI 请求对象，上游 Auth Middleware 会注入：
        - request.state.x_app_region
        - request.state.x_app_version
    a : str
        App 名称，如 Framix/Memrix，用于匹配工具资源
    t : int
        时间戳/nonce 等业务字段（扩展保留）
    n : str
        业务扩展字段，例如渠道号或用户标识
    platform : str
        平台标识：`darwin` → MacOS，否则视为 Windows

    ==== Notes: Caching ====
    -------
    Redis Key - {App}:{Windows|MacOS}:Toolkit
    Cache TTL - 86400s (1 Day)
    生成下载 URL 时不缓存，确保每次返回的是有效签名链接

    Returns
    -------
    LicenseResponse (Base64 `data` + Base64 `signature`)
        解码后实际结构示例:

        {
            "toolkit": {
                "ffmpeg": {
                    "filename": "ffmpeg.zip",
                    "version": "7.0.2",
                    "size": 52182661,
                    "hash": "sha256...",
                    "updated_at": "2025-06-30T21:56:48",
                    "url": "https://r2-signed-url...."   # 自动生成
                },
                ...
            },
            "ttl": 86400,
            "region": "<client-region>",
            "version": "<client-version>",
            "message": "Available toolkits for client to choose"
        }

    Notes
    -----
    - `filename` 必须存在才会生成 URL
    - URL 有效期 1h，客户端需按需刷新
    - 建议客户端比对 `hash/version` 判断是否需要更新

    Raises
    ------
    - BizError/AuthorizationError → 走全局异常中间件统一返回
    """

    app_name, app_desc, *_ = a.lower().strip(), a, t, n

    x_app_region  = request.state.x_app_region
    x_app_version = request.state.x_app_version

    group     = "MacOS" if platform == "darwin" else "Windows"
    cache_key = f"{app_desc}:{group}:Toolkit"

    ttl = 86400

    cache: UpStash = request.app.state.cache
    r2: R2Storage  = request.app.state.r2

    if cached := await cache.get(cache_key):
        logger.success(f"下发缓存工具元信息 -> {cache_key}")
        license_info = cached
    else:
        toolkit_info = {
            "Framix": {
                "Windows": {
                    "ffmpeg": {
                        "filename"   : "ffmpeg.zip",
                        "version"    : "7.0.2",
                        "size"       : 118373052,
                        "hash"       : "cdf8a3496c164e1b1af48acb48e4cd234971124104309b3d38d971ae07eea5ea",
                        "updated_at" : "2025-06-30T21:57:56"
                    },
                    "platform-tools": {
                        "filename"   : "platform-tools.zip",
                        "version"    : "35.0.2",
                        "size"       : 6700723,
                        "hash"       : "efd7d6f33ca7c27b93eb41c3988c88a2e9f8110704976097995ac75b460d2b83",
                        "updated_at" : "2025-06-30T21:57:58"
                    }
                },
                "MacOS": {
                    "ffmpeg": {
                        "filename"   : "ffmpeg.zip",
                        "version"    : "7.0.2",
                        "size"       : 52182661,
                        "hash"       : "f775f868cf864302714ae28cb0794b7be10aaa477d079fe82dfb56ad8449bc92",
                        "updated_at" : "2025-06-30T21:56:48"
                    },
                    "platform-tools": {
                        "filename"   : "platform-tools.zip",
                        "version"    : "35.0.2",
                        "size"       : 13335059,
                        "hash"       : "ee590efd0dada7b7ce64f51424e5e70425c94d26f386d5b3f75b163f06cbdbc1",
                        "updated_at" : "2025-06-30T21:56:54"
                    }
                }
            },

            "Memrix": {
                "Windows": {
                    "platform-tools": {
                        "filename"   : "platform-tools.zip",
                        "version"    : "35.0.2",
                        "size"       : 6700723,
                        "hash"       : "efd7d6f33ca7c27b93eb41c3988c88a2e9f8110704976097995ac75b460d2b83",
                        "updated_at" : "2025-08-03T15:31:14"
                    },
                    "perfetto-kit": {
                        "filename"   : "perfetto-kit.zip",
                        "version"    : "51.2",
                        "size"       : 58050500,
                        "hash"       : "d9427fe1a2adb76b4745b90d19fa86151df6849bcec9ef4286b38ec78f39cd38",
                        "updated_at" : "2025-08-03T15:31:43"
                    }
                },
                "MacOS": {
                    "platform-tools": {
                        "filename"   : "platform-tools.zip",
                        "version"    : "35.0.2",
                        "size"       : 13335059,
                        "hash"       : "ee590efd0dada7b7ce64f51424e5e70425c94d26f386d5b3f75b163f06cbdbc1",
                        "updated_at" : "2025-08-03T15:31:48"
                    },
                    "perfetto-kit": {
                        "filename"   : "perfetto-kit.zip",
                        "version"    : "51.2",
                        "size"       : 8309465,
                        "hash"       : "1f1cf884549ea86b8faf546fff39b5fd26703a1651e7f20012f173251d062b7d",
                        "updated_at" : "2025-08-03T15:31:51"
                    }
                }
            }
        }

        license_info = {
            "toolkit" : toolkit_info.get(app_desc, {}).get(group, {}),
            "ttl"     : ttl,
            "region"  : x_app_region,
            "version" : x_app_version,
            "message" : "Available toolkits for client to choose"
        }
        await cache.set(cache_key, license_info, ex=ttl)
        logger.info(f"Redis cache -> {cache_key}")

    # 每次都重新签名 URL
    toolkit = license_info.get("toolkit", {})
    for name, tool in toolkit.items():
        if not (filename := tool.get("filename")):
            continue
        tool["url"] = r2.signed_url_for_stream(
            key=f"toolkit-store/{app_desc}/{group}/{filename}",
            expires_in=3600,
            disposition_filename=filename
        )

    signed_data = signature.signature_license(
        license_info, private_key=f"{app_name}_{const.BASE_PRIVATE_KEY}"
    )

    logger.success(f"下发工具元信息 -> Available models for client to choose")
    return LicenseResponse(**signed_data)


async def resolve_model_download(
    request: Request,
    a: str,
    t: int,
    n: str
) -> LicenseResponse:
    """
    🤖 模型资源下载索引下发接口（带 License 签名）

    向客户端返回当前可用推理模型列表（含大小/版本/哈希/更新时间），
    并动态生成 Cloudflare R2 临时下载签名 URL，支持断点续传/直链下载。
    结果使用 LicenseResponse 包装签名，保证链接元信息防篡改与授权校验稳定性。

    Workflow
    --------
    1) 拼装缓存 Key → {App}:Models
    2) 若 Redis 已缓存，直接读取返回
    3) 若无缓存 → 载入模型元信息并写入缓存
    4) 为每个模型生成 1 小时有效的签名下载 URL
    5) 再对所有参数整体签名 → LicenseResponse 返回

    Parameters
    ----------
    request : Request
        FastAPI Request 实例，中间件注入:
        - request.state.x_app_region   (客户端区域/节点)
        - request.state.x_app_version  (客户端版本)
    a : str
        应用名 (如 Framix / Memrix) 用于构建私钥及缓存隔离
    t : int
        业务 use-case 字段，可作为 timestamp 或 nonce 保留使用
    n : str
        客户或 UserId 标识，可用于未来个性化模型分发控制

    ==== Notes: Caching ====
    -------
    Redis Key - {App}:Models
    Cache TTL - 86400s = 1day
    ⚠ URL 不缓存，每次请求重新生成签名 URL，保证有效性

    Returns
    -------
    LicenseResponse
        Base64(data) + Base64(signature)

        💡 解码后结构示例:

        {
            "models": {
                "Keras_Gray_W256_H256": {
                    "filename": "Keras_Gray_W256_H256.zip",
                    "version": "1.0.0",
                    "size": 361578087,
                    "hash": "sha256...",
                    "updated_at": "2025-06-27T03:24:24",
                    "url": "https://r2.signed-download/..."  # 1h有效
                },
                ...
            },
            "ttl": 86400,
            "region": "Global",
            "version": "v1.0.0",
            "message": "Available models for client to choose"
        }

    Notes
    -----
    - 可通过 hash/version 做客户端本地模型缓存校验
    - 大模型下载场景建议搭配 Streaming / Range Header 断点续传
    - License 与签名机制可接入授权/付费/灰度模型分发策略

    Raises
    ------
    BizError / AuthorizationError
        由全局中间件统一捕获返回 JSON
    """

    app_name, app_desc, *_ = a.lower().strip(), a, t, n

    x_app_region  = request.state.x_app_region
    x_app_version = request.state.x_app_version

    cache_key = f"{app_desc}:Models"

    ttl = 86400

    # 模型信息结构（不含签名 URL）
    faint_model = "Keras_Gray_W256_H256"
    color_model = "Keras_Hued_W256_H256"

    cache: UpStash = request.app.state.cache
    r2: R2Storage  = request.app.state.r2

    if cached := await cache.get(cache_key):
        logger.success(f"下发缓存模型元信息 -> {cache_key}")
        license_info = cached
    else:
        license_info = {
            "models": {
                faint_model: {
                    "filename"   : f"{faint_model}.zip",
                    "version"    : "1.0.0",
                    "size"       : 361578087,
                    "hash"       : "ad8fbadcc50eed6c175370e409732faf6bb230fec75374df07fe356e583ff6a8",
                    "updated_at" : "2025-06-27T03:24:24"
                },
                color_model: {
                    "filename"   : f"{color_model}.zip",
                    "version"    : "1.0.0",
                    "size"       : 372520325,
                    "hash"       : "78dd1c9167f1072ba5c7b0f8fd411545573529e2cbffe51cdd667f230871f249",
                    "updated_at" : "2025-06-27T03:29:22"
                }
            },
            "ttl"     : ttl,
            "region"  : x_app_region,
            "version" : x_app_version,
            "message" : "Available models for client to choose"
        }

        await cache.set(cache_key, license_info, ex=ttl)
        logger.info(f"Redis cache -> {cache_key}")

    # 每次都重新签名 URL
    for model in license_info["models"].values():
        model["url"] = r2.signed_url_for_stream(
            key=f"model-store/{model['filename']}",
            expires_in=3600,
            disposition_filename=model["filename"]
        )

    signed_data = signature.signature_license(
        license_info, private_key=f"{app_name}_{const.BASE_PRIVATE_KEY}"
    )

    logger.success(f"下发模型元信息 -> Available models for client to choose")
    return LicenseResponse(**signed_data)


async def stencil_viewer(
    a: str,
    t: int,
    n: str,
    page: str
) -> str:
    """
    📄 模板 HTML 内容查看接口

    根据应用标识参数解析模板路径，并读取对应的 HTML 文件内容，用于前端展示或动态渲染页面。

    Parameters
    ----------
    a : str
        应用名称，内部会进行标准化处理 (lower + strip) 用作路径解析。
    t : int
        版本号或模板类型扩展字段（保留字段，暂未使用）。
    n : str
        备用命名或业务扩展字段（保留字段，暂未使用）。
    page : str
        需要读取的 HTML 文件名，例如 `"index.html"`。

    Returns
    -------
    str
        目标 HTML 文件的完整文本内容。

    Raises
    ------
    BizError(404)
        当传入的文件名不存在或无法解析模板路径时抛出。
    """

    app_name, app_desc, *_ = a.lower().strip(), a, t, n

    try:
        html_template = toolset.resolve_template("html", page)
        return html_template.read_text(encoding=const.CHARSET)

    except FileNotFoundError:
        raise BizError(status_code=404, detail=f"文件名不存在: {page}")


async def stencil_case(
    a: str,
    t: int,
    n: str,
    case: str
) -> str:
    """
    📦 业务 Case Stencil 获取接口

    根据应用参数定位业务模板文件，并读取指定 Case 的 JSON 数据，
    多用于 Mock 测试数据、业务用例展示、案例库抽样等场景。

    Parameters
    ----------
    a : str
        应用名称，将会进行标准化处理作为目录索引。
    t : int
        业务模板版本/类型标识（预留字段，可用于版本路由）。
    n : str
        扩展业务字段（保留字段，用于未来横向扩展）。
    case : str
        Case 模板文件名，例如 `"login_case.json"`。

    Returns
    -------
    dict
        转换后的 JSON 结构数据，适用于 API 响应或用例展示。

    Raises
    ------
    BizError(404)
        当 Case 文件不存在时抛出业务异常。
    """

    app_name, app_desc, *_ = a.lower().strip(), a, t, n

    try:
        business_file = toolset.resolve_template("case", case)
        return json.loads(business_file.read_text(encoding=const.CHARSET))

    except FileNotFoundError:
        raise BizError(status_code=404, detail=f"文件名不存在: {case}")


if __name__ == '__main__':
    pass
