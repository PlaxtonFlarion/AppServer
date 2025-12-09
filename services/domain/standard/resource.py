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
