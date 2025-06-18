#   ____  _                  _ _
#  / ___|| |_ ___ _ __   ___(_) |
#  \___ \| __/ _ \ '_ \ / __| | |
#   ___) | ||  __/ | | | (__| | |
#  |____/ \__\___|_| |_|\___|_|_|
#

import json
from fastapi import HTTPException
from common import (
    const, utils
)
from services import signature


async def stencil_meta(
        x_app_id: str,
        x_app_token: str,
        a: str,
        t: int,
        n: str,
) -> dict:
    app_name, app_desc, *_ = a.lower().strip(), a, t, n

    signature.verify_signature(
        x_app_id, x_app_token, public_key=f"{app_name}_{const.BASE_PUBLIC_KEY}"
    )

    version_file = utils.resolve_template("html", const.TEMPLATE_VERSION)
    version_dict = json.loads(version_file.read_text(encoding=const.CHARSET))
    return version_dict.get(app_desc, {})


async def stencil_viewer(
        x_app_id: str,
        x_app_token: str,
        a: str,
        t: int,
        n: str,
        page: str,
) -> str:
    app_name, app_desc, *_ = a.lower().strip(), a, t, n

    signature.verify_signature(
        x_app_id, x_app_token, public_key=f"{app_name}_{const.BASE_PUBLIC_KEY}"
    )

    html_template = utils.resolve_template("html", page)
    return html_template.read_text(encoding=const.CHARSET)


async def stencil_case(
        x_app_id: str,
        x_app_token: str,
        a: str,
        t: int,
        n: str,
        case: str,
) -> str:
    app_name, app_desc, *_ = a.lower().strip(), a, t, n

    signature.verify_signature(
        x_app_id, x_app_token, public_key=f"{app_name}_{const.BASE_PUBLIC_KEY}"
    )

    try:
        business_file = utils.resolve_template("case", case)
        return json.loads(business_file.read_text(encoding=const.CHARSET))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"文件不存在")
    except json.JSONDecodeError:
        raise HTTPException(status_code=422, detail=f"文件格式错误")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"内部错误: {e}")


if __name__ == '__main__':
    pass
