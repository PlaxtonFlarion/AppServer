#   _                    _
#  | |    ___   __ _  __| | ___ _ __ ___
#  | |   / _ \ / _` |/ _` |/ _ \ '__/ __|
#  | |__| (_) | (_| | (_| |  __/ |  \__ \
#  |_____\___/ \__,_|\__,_|\___|_|  |___/
#

import json
import time
import base64
from loguru import logger
from services import (
    r2_storage, redis_cache, signature
)
from utils import (
    const, toolset
)


async def resolve_configuration(
    x_app_region: str,
    x_app_version: str,
    a: str,
    t: int,
    n: str,
    cache: "redis_cache.RedisCache"
) -> dict:

    app_name, app_desc, *_ = a.lower().strip(), a, t, n

    cache_key = f"Global Config:{app_desc}"

    if cached := await cache.redis_get(cache_key):
        logger.info(f"下发缓存全局配置 -> {cache_key}")
        return json.loads(cached)

    config      = toolset.resolve_template("data", const.CONFIGURATION)
    config_dict = json.loads(config.read_text(encoding=const.CHARSET))

    ttl = 86400

    license_info = {
        "configuration" : config_dict.get(app_desc, {}),
        "url"           : "",
        "ttl"           : ttl,
        "region"        : x_app_region,
        "version"       : x_app_version,
        "message"       : "Use global configuration"
    }

    signed_data = signature.signature_license(
        license_info, private_key=f"{app_name}_{const.BASE_PRIVATE_KEY}"
    )
    await cache.redis_set(cache_key, json.dumps(signed_data), ex=ttl)
    logger.info(f"Redis cache -> {cache_key}")

    logger.success(f"下发全局配置 -> Use global configuration")
    return signed_data


async def resolve_bootstrap(
    x_app_region: str,
    x_app_version: str,
    a: str,
    t: int,
    n: str,
    cache: "redis_cache.RedisCache"
) -> dict:

    app_name, app_desc, *_ = a.lower().strip(), a, t, n

    cache_key = f"Activation Node:{app_desc}"

    if cached := await cache.redis_get(cache_key):
        logger.success(f"下发缓存激活配置 -> {cache_key}")
        return json.loads(cached)

    ttl = 86400

    license_info = {
        "configuration" : {},
        "url"           : "https://api.appserverx.com/sign",
        "ttl"           : ttl,
        "region"        : x_app_region,
        "version"       : x_app_version,
        "message"       : "Use activation node"
    }

    signed_data = signature.signature_license(
        license_info, private_key=f"{app_name}_{const.BASE_PRIVATE_KEY}"
    )
    await cache.redis_set(cache_key, json.dumps(signed_data), ex=ttl)
    logger.info(f"Redis cache -> {cache_key}")

    logger.success(f"下发激活配置 -> Use activation node")
    return signed_data


async def resolve_proxy_predict(
    x_app_region: str,
    x_app_version: str,
    a: str,
    t: int,
    n: str,
    cache: "redis_cache.RedisCache"
) -> dict:

    app_name, app_desc, *_ = a.lower().strip(), a, t, n

    cache_key = f"Predict Server:{app_desc}"
    infer_key = f"Predict:{app_desc}"

    infer_data = await cache.redis_get(infer_key)
    current    = infer_data.get("available", False) if infer_data else False
    logger.info(f"远程推理服务状态 -> {current}")

    if cached := await cache.redis_get(cache_key):
        cache_data = json.loads(base64.b64decode(json.loads(cached)["data"]))
        if (previous := cache_data["available"]) == current:
            logger.success(f"下发缓存推理服务 -> {cache_key}")
            return json.loads(cached)
        logger.info(f"推理服务状态变更 -> Cached={previous} Remote={current}")
        await cache.redis_delete(cache_key)
    available = current

    ttl = 86400

    expire_at = int(time.time()) + ttl
    token     = signature.sign_token(app_desc, expire_at)

    license_info = {
        "configuration" : {},
        "available"     : available,
        "expire_at"     : expire_at,
        "timeout"       : 60.0,
        "content_type"  : "multipart/form-data",
        "auth_header"   : const.TOKEN_FORMAT,
        "token"         : token,
        "method"        : "POST",
        "url"           : "https://plaxtonflarion--inference-inferenceservice-predict.modal.run",
        "ttl"           : ttl,
        "region"        : x_app_region,
        "version"       : x_app_version,
        "message"       : "Predict service online"
    }

    signed_data = signature.signature_license(
        license_info, private_key=f"{app_name}_{const.BASE_PRIVATE_KEY}"
    )
    await cache.redis_set(cache_key, json.dumps(signed_data), ex=ttl)
    logger.info(f"Redis cache -> {cache_key}")

    logger.success(f"下发推理服务 -> Predict service online")
    return signed_data


async def resolve_stencil(
    x_app_region: str,
    x_app_version: str,
    a: str,
    t: int,
    n: str,
    cache: "redis_cache.RedisCache"
) -> dict:

    app_name, app_desc, *_ = a.lower().strip(), a, t, n

    cache_key = f"Template:{app_desc}"

    ttl = 86400

    if cached := await cache.redis_get(cache_key):
        logger.success(f"下发缓存模版元信息 -> {cache_key}")
        license_info = json.loads(cached)
    else:
        stencil_info = {
            "Framix": {
                "template_atom_total.html": {
                    "filename" : "template_atom_total.html",
                    "url"      : "https://appserver-u7hd.onrender.com/template-viewer"
                },
                "template_line_total.html": {
                    "filename" : "template_line_total.html",
                    "url"      : "https://appserver-u7hd.onrender.com/template-viewer"
                },
                "template_main_share.html": {
                    "filename" : "template_main_share.html",
                    "url"      : "https://appserver-u7hd.onrender.com/template-viewer"
                },
                "template_main_total.html": {
                    "filename" : "template_main_total.html",
                    "url"      : "https://appserver-u7hd.onrender.com/template-viewer"
                },
                "template_view_share.html": {
                    "filename" : "template_view_share.html",
                    "url"      : "https://appserver-u7hd.onrender.com/template-viewer"
                },
                "template_view_total.html": {
                    "filename" : "template_view_total.html",
                    "url"      : "https://appserver-u7hd.onrender.com/template-viewer"
                }
            },
            "Memrix": {
                "unity_template.html": {
                    "filename" : "unity_template.html",
                    "url"      : "https://appserver-u7hd.onrender.com/template-viewer"
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
        await cache.redis_set(cache_key, json.dumps(license_info), ex=ttl)
        logger.info(f"Redis cache -> {cache_key}")

    signed_data = signature.signature_license(
        license_info, private_key=f"{app_name}_{const.BASE_PRIVATE_KEY}"
    )

    logger.success(f"下发模版元信息 -> Available templates for client to choose")
    return signed_data


async def resolve_toolkit_download(
    x_app_region: str,
    x_app_version: str,
    a: str,
    t: int,
    n: str,
    platform: str,
    cache: "redis_cache.RedisCache"
) -> dict:

    app_name, app_desc, *_ = a.lower().strip(), a, t, n

    group     = "MacOS" if platform == "darwin" else "Windows"
    cache_key = f"Toolkit:{app_desc}:{group}"

    ttl = 86400

    if cached := await cache.redis_get(cache_key):
        logger.success(f"下发缓存工具元信息 -> {cache_key}")
        license_info = json.loads(cached)
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
        await cache.redis_set(cache_key, json.dumps(license_info), ex=ttl)
        logger.info(f"Redis cache -> {cache_key}")

    # 每次都重新签名 URL
    toolkit = license_info.get("toolkit", {})
    for name, tool in toolkit.items():
        if not (filename := tool.get("filename")):
            continue
        tool["url"] = await r2_storage.signed_url_for_stream(
            key=f"toolkit-store/{app_desc}/{group}/{filename}",
            expires_in=3600,
            disposition_filename=filename
        )

    signed_data = signature.signature_license(
        license_info, private_key=f"{app_name}_{const.BASE_PRIVATE_KEY}"
    )

    logger.success(f"下发工具元信息 -> Available models for client to choose")
    return signed_data


async def resolve_model_download(
    x_app_region: str,
    x_app_version: str,
    a: str,
    t: int,
    n: str,
    cache: "redis_cache.RedisCache"
) -> dict:

    app_name, app_desc, *_ = a.lower().strip(), a, t, n

    cache_key = f"Models:{app_desc}"

    ttl = 86400

    # 模型信息结构（不含签名 URL）
    faint_model = "Keras_Gray_W256_H256"
    color_model = "Keras_Hued_W256_H256"

    if cached := await cache.redis_get(cache_key):
        logger.success(f"下发缓存模型元信息 -> {cache_key}")
        license_info = json.loads(cached)
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
        await cache.redis_set(cache_key, json.dumps(license_info), ex=ttl)
        logger.info(f"Redis cache -> {cache_key}")

    # 每次都重新签名 URL
    for model in license_info["models"].values():
        model["url"] = await r2_storage.signed_url_for_stream(
            key=f"model-store/{model['filename']}",
            expires_in=3600,
            disposition_filename=model["filename"]
        )

    signed_data = signature.signature_license(
        license_info, private_key=f"{app_name}_{const.BASE_PRIVATE_KEY}"
    )

    logger.success(f"下发模型元信息 -> Available models for client to choose")
    return signed_data


if __name__ == '__main__':
    pass
